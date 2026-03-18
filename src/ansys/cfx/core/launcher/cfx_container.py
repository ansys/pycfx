# Copyright (C) 2023 - 2026 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""Provides a module for launching and configuring local CFX Docker container runs.

Notes
-----

For configuration information, see the :func:`configure_container_dict` function. For a
list of additional Docker container run configuration options that can also be specified
through the ``container_dict`` argument for the
:func:`~ansys.cfx.core.launcher.launcher.launch_cfx()` function, see `Docker run`_ in the *Docker
SDK for Python* containers documentation

For the CFX Docker container to be able to find license information, the license file or server
needs to be specified through the ``ANSYSLMD_LICENSE_FILE`` environment variable, or the
``license_server`` argument for the ``container_dict`` (see :func:`configure_container_dict`).

.. _Docker run: https://docker-py.readthedocs.io/en/stable/containers.html#docker.models.\
containers.ContainerCollection.run

Examples
--------
Launch a CFX Docker container with the system default configuration:

>>> import ansys.cfx.core as pycfx
>>> session = pycfx.launch_cfx(start_container=True)

Launch with a custom configuration, using ``cfx_image`` and ``host_mount_path``,
which are arguments for the :func:`configure_container_dict` function. ``auto_remove`` is
an argument for `Docker run`_:

>>> import ansys.cfx.core as pycfx
>>> custom_config = {}
>>> custom_config.update(cfx_image='custom_cfx:v25.2.3', host_mount_path='/testing',
...   auto_remove=False)
>>> session = pycfx.launch_cfx(container_dict=custom_config)

Get the default CFX Docker container configuration and then launch with the customized
configuration:

>>> import ansys.cfx.core as pycfx
>>> config_dict = pycfx.launch_cfx(start_container=True, dry_run=True)
Docker container run configuration information:
config_dict =
{'auto_remove': True,
 'command': ['-py', '-sifile /mnt/pycfx/serverinfo-lpqsdldw.txt'],
 'detach': True,
 'environment': {'ANSYSLMD_LICENSE_FILE': '2048@licenseserver.com',
                 'REMOTING_PORTS': '54000/portspan=2'},
 'cfx_image': 'ghcr.io/ansys/pycfx:v25.2.3',
 'labels': {'test_name': 'none'},
 'ports': {'54000': 54000},
 'volumes': ['/home/user/.local/share/ansys_cfx_core/examples:/mnt/pycfx'],
 'working_dir': '/mnt/pycfx'}
>>> config_dict.update(image_name='custom_cfx', image_tag='v25.2.3', mem_limit='1g')
>>> session = pycfx.launch_cfx(container_dict=config_dict)
"""

import copy
import logging
import os
from pathlib import Path, PurePosixPath
import re
import tempfile
from typing import List, Optional, Union

import docker

import ansys.cfx.core as pycfx
from ansys.cfx.core.launcher.launcher_utils import is_linux
from ansys.cfx.core.session import _parse_server_info_file
from ansys.cfx.core.utils.cfx_version import CFXVersion
from ansys.cfx.core.utils.execution import timeout_loop
from ansys.cfx.core.utils.networking import get_free_port

logger = logging.getLogger("pycfx.launcher")
DEFAULT_CONTAINER_MOUNT_PATH = "/mnt/pycfx"


class CFXCommandNotSpecified(ValueError):
    """Raised when a CFX session command is not specified."""

    def __init__(self):
        super().__init__("Specify either 'cfx5pre' or 'cfx5solve' or 'cfdpost'.")


class CFXImageNameTagNotSpecified(ValueError):
    """Raised when the CFX image name or image tag is not specified."""

    def __init__(self):
        super().__init__("Specify either 'cfx_image' or 'image_tag' and 'image_name'.")


class ServerInfoFileError(ValueError):
    """Raised when the server information file is not given properly."""

    def __init__(self):
        super().__init__(
            "Specify server information file using the 'container_server_info_file' argument or "
            "in the 'container_dict'."
        )


class LicenseServerNotSpecified(KeyError):
    """Raised when the license server is not specified."""

    def __init__(self):
        super().__init__(
            "Specify a license server using the 'ANSYSLMD_LICENSE_FILE' environment variable or "
            "in the 'container_dict'."
        )


def _get_host_and_container_mount_paths(volumes_string: str) -> tuple[str, str]:
    # Split from the right at the first colon
    if ":" not in volumes_string:
        raise ValueError("Invalid volume string: missing ':' separator")
    host_mount_path, container_mount_path = volumes_string.rsplit(":", 1)
    return host_mount_path, container_mount_path


def configure_container_dict(
    args: List[str],
    host_mount_path: Optional[Union[str, Path]] = None,
    container_mount_path: Optional[Union[str, Path]] = None,
    timeout: int = 240,
    port: Optional[int] = None,
    license_server: Optional[str] = None,
    container_server_info_file: Optional[Union[str, Path]] = None,
    remove_server_info_file: bool = True,
    cfx_image: Optional[str] = None,
    image_name: Optional[str] = None,
    image_tag: Optional[str] = None,
    has_remote_server: bool = True,
    **container_dict,
) -> tuple[dict, int, int, Path, bool]:
    """Parse the following parameters and set up the container configuration file.

    Parameters
    ----------
    args : List[str]
        List of CFX launch arguments.
    host_mount_path : Union[str, Path], default: None
        Existing path in the host operating system that is available inside the container.
    container_mount_path : Union[str, Path], default: None
        Path inside the container where the host mount path is mounted to.
    timeout : int, default: None
        Time limit in seconds for the CFX container to start. When ``None``, 30 seconds is used.
    port : int, default: None
        Port for CFX container to use.
    license_server : str, default: None
        License server for Ansys CFX to use.
    container_server_info_file : Union[str, Path], default: None
        Name of the server information file for CFX to write on the ``host_mount_path`` argument.
    remove_server_info_file : bool, default: True
        Whether to automatically delete the server information file after PyCFX has
        finished using it.
    has_remote_server : bool, default: True
        Whether to create a server information file for server and client communication setup.
    cfx_image : str, default: None
        Specifies full image name for Docker container run, with the format
        ``"image_name:image_tag"``. The ``image_tag`` and ``image_name`` parameters
        are ignored if the ``cfx_image`` parameter has been specified.
    image_name : str, default: None
        Ignored if the ``cfx_image`` parameter has been specified.
    image_tag : str, default: None
        Ignored if the ``cfx_image`` parameter has been specified.
    **container_dict
        Additional keyword arguments that can be specified. They are treated as Docker container
        run options to be passed directly to the Docker run execution. See the following examples
        and `Docker run`_ documentation.

    Returns
    -------
    cfx_image : str
    container_dict : dict
    timeout : int
    port : int
    host_server_info_file : Path
    remove_server_info_file: bool

    Raises
    ------
    LicenseServerNotSpecified
        If license server is not specified through an environment variable or in
        ``container_dict``.
    ServerInfoFileError
        If server information file is specified through both a command-line argument inside
        ``container_dict`` and the  ``container_server_info_file`` parameter.
    CFXImageNameTagNotSpecified
        If ``cfx_image`` or ``image_tag`` and ``image_name`` are not specified.
    CFXCommandNotSpecified
        If ``cfx_cmd`` is not specified.

    Notes
    -----
    This function should usually not be called directly. It is automatically used by the
    :func:`~ansys.cfx.core.launcher.launcher.launch_cfx()` function.

    For a list of additional Docker container run configuration options that can also be specified
    using ``container_dict``, see `Docker run`_ documentation.

    See also the :func:`start_cfx_container` function.
    """

    if "cfx_cmd" not in container_dict:
        raise CFXCommandNotSpecified()

    if (
        container_dict
        and "environment" in container_dict
        and os.getenv("PYCFX_HIDE_LOG_SECRETS") == "1"
    ):
        container_dict_h = container_dict.copy()
        container_dict_h.pop("environment")
        logger.debug(f"container_dict before processing: {container_dict_h}")
        del container_dict_h
    else:
        logger.debug(f"container_dict before processing: {container_dict}")

    if not host_mount_path:
        host_mount_path = pycfx.EXAMPLES_PATH
    elif "volumes" in container_dict:
        logger.warning(
            "'volumes' keyword specified in 'container_dict', but "
            "it is going to be overwritten by specified 'host_mount_path'."
        )
        container_dict.pop("volumes")

    host_mount_path_obj = Path(host_mount_path)
    host_mount_path_obj.mkdir(parents=True, exist_ok=True)

    if not container_mount_path:
        container_mount_path = os.getenv("PYCFX_CONTAINER_MOUNT_PATH", DEFAULT_CONTAINER_MOUNT_PATH)
    elif "volumes" in container_dict:
        logger.warning(
            "'volumes' keyword specified in 'container_dict', but "
            "it is going to be overwritten by specified 'container_mount_path'."
        )
        container_dict.pop("volumes")

    if is_linux():
        if "user" not in container_dict:
            container_dict.update(user=f"{os.getuid()}:{os.getgid()}")

    cfx_version = None
    if not image_tag:
        image_tag = os.getenv("CFX_IMAGE_TAG", "v26.1.0")
    if cfx_version := re.match(r"^v(\d+(?:\.\d+)+)", image_tag):
        cfx_version = cfx_version.group(1)
    if cfx_version and CFXVersion(cfx_version) < CFXVersion.v261:
        if "pid_mode" not in container_dict:
            container_dict.update(pid_mode="host")

    if "volumes" not in container_dict:
        container_dict.update(volumes=[f"{host_mount_path}:{container_mount_path}"])
    else:
        logger.debug(f"container_dict['volumes']: {container_dict['volumes']}")
        if len(container_dict["volumes"]) != 1:
            logger.debug(
                "Multiple volumes being mounted in the Docker container. "
                "Using the first mount as the working directory for CFX."
            )
        volumes_string = container_dict["volumes"][0]
        host_mount_path, container_mount_path = _get_host_and_container_mount_paths(volumes_string)
        logger.debug(f"host_mount_path: {host_mount_path}")
        logger.debug(f"container_mount_path: {container_mount_path}")

    if "ports" not in container_dict:
        if not port:
            port = get_free_port()
        container_dict.update(ports={str(port): port})  # container port : host port
    else:
        # Take the specified 'port', OR the first port value from the specified 'ports', for
        # CFX to use.
        if not port:
            port = next(iter(container_dict["ports"].values()))

    if "environment" not in container_dict:
        if not license_server:
            license_server = os.getenv("ANSYSLMD_LICENSE_FILE")

        if not license_server:
            raise LicenseServerNotSpecified()
        container_dict.update(
            environment={
                "ANSYSLMD_LICENSE_FILE": license_server,
                "REMOTING_PORTS": f"{port}/portspan=2",
                "CUE_UNIX_DOMAIN_SOCKET_DIR": container_mount_path,
            }
        )

    if "labels" not in container_dict:
        test_name = os.getenv("PYCFX_TEST_NAME", "none")
        container_dict.update(
            labels={"test_name": test_name},
        )

    if "working_dir" not in container_dict:
        container_dict.update(
            working_dir=container_mount_path,
        )

    if has_remote_server:
        if "command" in container_dict:
            for v in container_dict["command"]:
                if v.startswith("-sifile"):
                    if container_server_info_file:
                        raise ServerInfoFileError()
                    container_server_info_file = PurePosixPath(v.replace("-sifile", "")).name
                    logger.debug(
                        f"Found server info file specification for {container_server_info_file}."
                    )

        if container_server_info_file:
            container_server_info_file = (
                PurePosixPath(container_mount_path) / PurePosixPath(container_server_info_file).name
            )
        else:
            fd, sifile = tempfile.mkstemp(suffix=".txt", prefix="serverinfo-", dir=host_mount_path)
            os.close(fd)
            container_server_info_file = PurePosixPath(container_mount_path) / Path(sifile).name

    if not cfx_image:
        if not image_tag:
            image_tag = os.getenv("CFX_IMAGE_TAG", "v26.1.0")
        if not image_name:
            image_name = os.getenv("CFX_IMAGE_NAME", "ghcr.io/ansys/pycfx")
        cfx_image = f"{image_name}:{image_tag}"

    container_dict["cfx_image"] = cfx_image

    if has_remote_server:
        cfx_commands = [container_dict["cfx_cmd"], f"-sifile {container_server_info_file}"] + args
    else:
        cfx_commands = [container_dict["cfx_cmd"]] + args
    container_dict.pop("cfx_cmd")

    container_dict_default = {}
    container_dict_default.update(
        command=" ".join(cfx_commands),
        detach=True,
        auto_remove=True,
    )

    for k, v in container_dict_default.items():
        if k not in container_dict:
            container_dict[k] = v

    host_server_info_file = ""
    if has_remote_server:
        host_server_info_file = Path(host_mount_path) / container_server_info_file.name

    return (
        container_dict,
        timeout,
        port,
        host_server_info_file,
        remove_server_info_file,
    )


def start_cfx_container(args: List[str], container_dict: Optional[dict] = None) -> tuple[int, str]:
    """Start a CFX container.

    Parameters
    ----------
    args : List[str]
        List of CFX launch arguments.
    container_dict : dict, default: None
        Dictionary with Docker container configuration.

    Returns
    -------
    tuple
        Either:

        - (str, str): For Unix domain socket server address.
        - (str, int, str): For TCP/IP server address.

    Raises
    ------
    TimeoutError
        If the CFX container launch reaches timeout.

    Notes
    -----
    Uses :func:`configure_container_dict` to parse the optional ``container_dict`` configuration.

    This function should usually not be called directly. It is automatically used by the
    :func:`~ansys.cfx.core.launcher.launcher.launch_cfx()` function.
    """

    if container_dict is None:
        container_dict = {}

    container_vars = configure_container_dict(args, **container_dict)

    (
        config_dict,
        timeout,
        port,
        host_server_info_file,
        remove_server_info_file,
    ) = container_vars

    if os.getenv("PYCFX_HIDE_LOG_SECRETS") != "1":
        logger.debug(f"container_vars: {container_vars}")
    else:
        config_dict_h = config_dict.copy()
        config_dict_h.pop("environment")
        container_vars_tmp = (
            config_dict_h,
            timeout,
            port,
            host_server_info_file,
            remove_server_info_file,
        )
        logger.debug(f"container_vars: {container_vars_tmp}")
        del container_vars_tmp

    try:
        if not host_server_info_file.exists():
            host_server_info_file.parents[0].mkdir(exist_ok=True)

        host_server_info_file.touch(exist_ok=True)
        last_mtime = host_server_info_file.stat().st_mtime

        docker_client = docker.from_env()

        mapped_volumes = copy.deepcopy(config_dict["volumes"])

        logger.debug("Starting CFX docker container...")

        docker_client.containers.run(config_dict.pop("cfx_image"), **config_dict)

        success = timeout_loop(lambda: host_server_info_file.stat().st_mtime > last_mtime, timeout)

        if not success:
            raise TimeoutError("CFX container launch has timed out. Stop container manually.")
        else:
            values = _parse_server_info_file(str(host_server_info_file))
            if len(values) == 2:
                # Server address is a Unix domain socket file
                volumes_string = mapped_volumes[0]
                host_mount_path, container_mount_path = _get_host_and_container_mount_paths(
                    volumes_string
                )
                # Replace container path with host path in the server address
                server_address, password = values
                server_address = server_address.replace(container_mount_path, host_mount_path)
                return server_address, password
            else:
                return values
    finally:
        if remove_server_info_file and host_server_info_file.exists():
            host_server_info_file.unlink()


def extract_mount_paths(container_dict: dict) -> dict:
    """
    Extract host and container mount paths from a container configuration dictionary.

    This function looks for a "volumes" key in the input dictionary. If present, it expects
    the value to be a list of volume specifications. It extracts mount paths for test home
    mounts and temp directory mounts from the first two volumes (if available).

    Returns a dictionary with the following keys:

    - ``host_mount_path``: Path on the host for the first volume (or ``None``).
    - ``container_mount_path``: Path in the container for the first volume (or ``None``).
    - ``host_temporary_directory_path``: Path on the host for the second volume (or ``None``).
    - ``container_temporary_directory_path``: Path in the container for the second volume
      (or ``None``).

    Parameters
    ----------
    container_dict : dict
        Container configuration dictionary.

    Returns
    -------
    dict
        Dictionary containing extracted mount paths.
    """
    paths = {
        "host_mount_path": None,
        "container_mount_path": None,
        "host_temporary_directory_path": None,
        "container_temporary_directory_path": None,
    }
    if "volumes" in container_dict:
        volumes = container_dict["volumes"]
        if len(volumes) > 0:
            paths["host_mount_path"], paths["container_mount_path"] = (
                _get_host_and_container_mount_paths(volumes[0])
            )
        if len(volumes) > 1:
            paths["host_temporary_directory_path"], paths["container_temporary_directory_path"] = (
                _get_host_and_container_mount_paths(volumes[1])
            )
    return paths


def replace_container_path_with_host_path(line: str, mount_paths: dict[str, str]) -> str:
    """
    Replace the first occurrence of a container path in the given line with its corresponding host
    path.

    Parameters
    ----------
    line : str
        Input string potentially containing a container path.
    mount_paths : dict[str, str]
        Dictionary with keys:

        - ``container_mount_path``
        - ``host_mount_path``
        - ``container_temporary_directory_path``
        - ``host_temporary_directory_path``

    Returns
    -------
    str
        Line with the container path replaced by the host path, if found.
    """
    if (
        mount_paths["container_mount_path"]
        and mount_paths["host_mount_path"]
        and mount_paths["container_mount_path"] in line
    ):
        line = line.replace(mount_paths["container_mount_path"], mount_paths["host_mount_path"], 1)
    elif (
        mount_paths["container_temporary_directory_path"]
        and mount_paths["host_temporary_directory_path"]
        and mount_paths["container_temporary_directory_path"] in line
    ):
        line = line.replace(
            mount_paths["container_temporary_directory_path"],
            mount_paths["host_temporary_directory_path"],
            1,
        )
    return line


def replace_host_path_with_container_path(line: str, mount_paths: dict[str, str]) -> str:
    """
    Replace the first occurrence of a host path in the given line with its corresponding container
    path.

    Parameters
    ----------
    line : str
        Input string potentially containing a host path.
    mount_paths : dict[str, str])
        Dictionary with keys:

        - ``container_mount_path``
        - ``host_mount_path``
        - ``container_temporary_directory_path``
        - ``host_temporary_directory_path``

    Returns
    -------
    str
        Line with the host path replaced by the container path, if found.
    """
    if (
        mount_paths["container_mount_path"]
        and mount_paths["host_mount_path"]
        and mount_paths["host_mount_path"] in line
    ):
        line = line.replace(mount_paths["host_mount_path"], mount_paths["container_mount_path"], 1)
    elif (
        mount_paths["container_temporary_directory_path"]
        and mount_paths["host_temporary_directory_path"]
        and mount_paths["host_temporary_directory_path"] in line
    ):
        line = line.replace(
            mount_paths["host_temporary_directory_path"],
            mount_paths["container_temporary_directory_path"],
            1,
        )
    return line
