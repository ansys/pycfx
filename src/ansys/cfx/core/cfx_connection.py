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

"""Module for CFX connection functionality."""

from ctypes import c_int, sizeof
from dataclasses import dataclass
import ipaddress
import itertools
import logging
import os
from pathlib import Path
import socket
import threading
import time
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
import warnings
import weakref

import docker
from docker.models.containers import Container
import grpc
import psutil

from ansys.cfx.core.services import service_creator
from ansys.cfx.core.services.engine_eval import EngineEvalService
from ansys.cfx.core.utils.execution import timeout_exec, timeout_loop
from ansys.platform.instancemanagement import Instance

logger = logging.getLogger("pycfx.general")


class InsecureGrpcWarning(Warning):
    """Raised when the gRPC connection is insecure."""

    pass


def _connect_to_server_with_retry(uds_address, options=None, max_retries=10, delay_seconds=1):
    """
    Attempts to connect to a gRPC server at a UDS address.

    If the connection fails because the server is not ready, it waits
    for a specified delay and retries, up to a maximum number of retries.

    Parameters
    ----------
    uds_address : str
        UDS address string. For example, ``'unix:/tmp/my_app.sock'``.
    options : Any, default: None
        Options for the gRPC connection.
    max_retries : int, default: 10
        Maximum number of connection attempts.
    delay_seconds : int, default: 1
        Time to wait in seconds between retries.

    Returns
    -------
    grpc.Channel or None
        gRPC channel object if successful, otherwise ``None``.
    """
    for attempt in range(max_retries):
        try:
            # This creates a channel, but doesn't connect immediately.
            channel = grpc.insecure_channel(uds_address, options=options)

            # Ask the channel to become ready with a timeout. If the server
            # is not listening, it will raise a grpc.FutureTimeoutError.
            grpc.channel_ready_future(channel).result(timeout=delay_seconds)

            return channel

        except grpc.FutureTimeoutError:
            print(
                f"Connection attempt {attempt + 1}/{max_retries} failed. "
                f"Server not ready. Retrying in {delay_seconds} seconds..."
            )
            # Wait before the next attempt
            time.sleep(delay_seconds)

    print(f"Could not connect to the server after {max_retries} attempts.")
    return None


class PortNotProvided(ValueError):
    """Raised when the port is not provided."""

    def __init__(self):
        super().__init__("Provide the port to connect to an existing CFX instance.")


class UnsupportedRemoteCFXInstance(ValueError):
    """Raised when the ``wait_process_finished`` method does not support a remote CFX session."""

    def __init__(self):
        super().__init__("Remote CFX instance is unsupported.")


class WaitTypeError(TypeError):
    """Raised when invalid ``wait`` type is provided."""

    def __init__(self):
        super().__init__("Invalid 'wait' type.")


def _get_max_c_int_limit() -> int:
    """Get the maximum limit of a C int.

    Returns
    -------
    int
        Maximum limit of a C int.
    """
    return 2 ** (sizeof(c_int) * 8 - 1) - 1


class MonitorThread(threading.Thread):
    """Monitors a CFX session.

    A daemon thread that ensures cleanup of session objects and shut down of
    non-daemon threads.

    Attributes
    ----------
    cbs : List[Callable]
        Cleanup and shutdown functions.
    """

    def __init__(self):
        """Initialize an instance of the ``MonitorThread`` class."""
        super().__init__(daemon=True)
        self.cbs: List[Callable] = []

    def run(self) -> None:
        """Run the monitor thread."""
        main_thread = threading.main_thread()
        main_thread.join()
        for cb in self.cbs:
            cb()


def get_container(container_id_or_name: str) -> Union[bool, Container, None]:
    """Get the Docker container object.

    Returns
    -------
    Union[bool, Container, None]
        If the system is not correctly set up to run Docker containers, returns ``None``.
        If the container was not found, returns ``False``.
        If the container is found, returns the associated Docker container object.

    Notes
    -----
    See `Docker container`_ for more information.

    .. _Docker container: https://docker-py.readthedocs.io/en/stable/containers.html#docker.models.containers.Container
    """

    if not isinstance(container_id_or_name, str):
        container_id_or_name = str(container_id_or_name)
    try:
        docker_client = docker.from_env()
        container = docker_client.containers.get(container_id_or_name)
    except docker.errors.NotFound:  # NotFound is a child from DockerException
        return False
    except docker.errors.DockerException as exc:
        logger.info(f"{type(exc).__name__}: {exc}")
        return None
    return container


class ErrorState:
    """Indicates the error state of the connected CFX client.

    Examples
    --------
    >>> import ansys.cfx.core as pycfx
    >>> session = pycfx.launch_cfx()
    >>> session._cfx_connection._error_state.set("test", "test details")
    >>> session._cfx_connection._error_state.name
    'test'
    >>> session._cfx_connection._error_state.details
    'test details'
    >>> session._cfx_connection._error_state.clear()
    >>> session._cfx_connection._error_state.name
    ''
    """

    @property
    def name(self):
        """Name of the error state."""
        return self._name

    @property
    def details(self):
        """Additional details of the error state."""
        return self._details

    def __init__(self, name: str = "", details: str = ""):
        """Initialize the error state object.

        Parameters
        ----------
        name : str
            Name of the error state, which is by default an empty string, indicating no errors.
        details : str
            Additional details of the error, which is by default an empty string.
        """
        self._name = name
        self._details = details

    def set(self, name: str, details: str):
        """Set the error state name and details to new values."""
        self._name = name
        self._details = details

    def clear(self):
        """Clear the current error state, emptying the error name and details
        properties."""
        self._name = ""
        self._details = ""


@dataclass(frozen=True)
class CFXConnectionProperties:
    """Stores CFX connection properties, including connection IP address, port, UDS address, and
    password; CFX Engine working directory, process ID, and hostname; and whether CFX was
    launched in a Docker container.

    Examples
    --------
    These properties are also available through the session object and can be accessed:

    >>> import ansys.cfx.core as pycfx
    >>> session = pycfx.launch_cfx()
    >>> session.connection_properties.list_names()
    ['ip', 'port', 'password', 'engine_pwd', 'engine_pid', 'engine_host', 'cfx_host_pid', 'inside_container']
    >>> session.connection_properties.ip
    'localhost'
    """

    ip: Optional[str] = None
    """The IP address of the connected CFX session."""
    port: Optional[int] = None
    """The port of the connected CFX session."""
    address: Optional[str] = None
    """The UDS address of the connected CFX session."""
    password: Optional[str] = None
    """The password used to connect to the CFX session."""
    engine_pwd: Optional[str] = None
    """The CFX engine working directory."""
    engine_pid: Optional[int] = None
    """The process ID of the CFX engine (same as `cfx_host_pid`)."""
    engine_host: Optional[str] = None
    """The hostname of the machine where the CFX engine is running."""
    cfx_host_pid: Optional[int] = None
    """The process ID of the CFX engine (same as `engine_pid`)."""
    inside_container: Optional[Union[bool, Container, None]] = None
    """Whether the connected CFX session is running inside a Docker container."""

    def list_names(self) -> list:
        """Get a list of all property names."""
        return [k for k, _ in vars(self).items()]

    def list_values(self) -> dict:
        """Get a dictionary with all property names and values."""
        return vars(self)


def _get_ip_and_port(ip: str | None = None, port: int | None = None) -> tuple[str, int]:
    if not ip:
        ip = os.getenv("PYCFX_CFX_IP", "127.0.0.1")
    if not port:
        port = os.getenv("PYCFX_CFX_PORT")
    if not port:
        raise PortNotProvided()
    return ip, port


def _get_tls_channel(
    address: str,
    certificates_folder: str | None,
    options: list[tuple[str, int]] | None = None,
):
    cert_file = f"{certificates_folder}/client.crt"
    key_file = f"{certificates_folder}/client.key"
    ca_file = f"{certificates_folder}/ca.crt"

    missing = [f for f in (cert_file, key_file, ca_file) if not Path(f).exists()]
    if missing:
        raise RuntimeError(f"Missing required TLS files for mutual TLS: {', '.join(missing)}")

    certificate_chain, private_key, root_certificates = (
        open(path, "rb").read() for path in (cert_file, key_file, ca_file)
    )

    creds = grpc.ssl_channel_credentials(
        root_certificates=root_certificates,
        private_key=private_key,
        certificate_chain=certificate_chain,
    )
    return grpc.secure_channel(target=address, credentials=creds, options=options)


def _is_localhost(address: str) -> bool:
    # Unix domain sockets
    if address.startswith("unix:/"):
        return True

    # Strip off port (if present) and brackets for IPv6
    host = address.split(":", 1)[0].strip("[]")

    try:
        return ipaddress.ip_address(host).is_loopback
    except ValueError:
        # Not an IP, fall back to hostname
        return host.lower() == "localhost"


def _get_channel(
    address: str,
    allow_remote_host: bool,
    certificates_folder: str | None,
    insecure_mode: bool,
    inside_container: bool,
):
    # Same maximum message length is used in the server
    max_message_length = _get_max_c_int_limit()
    options = [
        ("grpc.max_send_message_length", max_message_length),
        ("grpc.max_receive_message_length", max_message_length),
    ]
    if allow_remote_host:
        if insecure_mode:
            if _is_localhost(address) and not inside_container:
                raise RuntimeError(
                    "Insecure gRPC mode is not allowed when connecting to localhost."
                )
            warnings.warn(
                "The CFX session will be connected in insecure gRPC mode. "
                "This mode is not recommended. For more information on the implications "
                "and usage of insecure mode, see the CFX documentation.",
                InsecureGrpcWarning,
            )
            return grpc.insecure_channel(address, options=options)
        else:
            if certificates_folder is None:
                raise ValueError(
                    "Specify 'certificates_folder' containing TLS certificates to connect to remote host."
                )
            return _get_tls_channel(address, certificates_folder, options=options)
    else:
        insecure_mode_env = os.getenv("CFX_CONTAINER_INSECURE_MODE") == "1"
        if not (_is_localhost(address) or (inside_container and insecure_mode_env)):
            raise ValueError(
                "Connecting to remote CFX instances is not allowed. "
                "Set 'allow_remote_host=True' to connect to remote hosts."
            )
        if address.startswith("unix:/"):
            # If using UDS transport, set default authority to localhost
            # see https://github.com/grpc/grpc/issues/34305
            options.append(("grpc.default_authority", "localhost"))
            # Ensure that UDS is ready before connecting
            return _connect_to_server_with_retry(address, options=options)
        else:
            return grpc.insecure_channel(address, options=options)


class CFXConnection:
    """Encapsulates a CFX connection.

    Methods
    -------
    exit()
        Close the CFX connection and exit CFX.
    """

    _on_exit_cbs: List[Callable] = []
    _id_iter = itertools.count()
    _monitor_thread: Optional[MonitorThread] = None

    def __init__(
        self,
        ip: Optional[str] = None,
        port: Optional[int] = None,
        address: str | None = None,
        password: Optional[str] = None,
        channel: Optional[grpc.Channel] = None,
        allow_remote_host: bool = False,
        certificates_folder: str | None = None,
        insecure_mode: bool = False,
        cleanup_on_exit: bool = True,
        start_transcript: bool = False,
        remote_instance: Optional[Instance] = None,
        launcher_args: Optional[Dict[str, Any]] = None,
        inside_container: Optional[bool] = None,
    ):
        """Initialize a session.

        Parameters
        ----------
        ip : str, default: None
            IP address to connect to an existing CFX instance. This parameter is
            used only when ``channel`` is ``None``. When this parameter is ``None``,
            ``"127.0.0.1"`` is used. The IP address can also be set by the ``PYCFX_CFX_IP=<ip>``
            environment variable.
        port : int, default: None
            Port to connect to an existing CFX instance. This parameter is used only
            when ``channel`` is ``None``. The port can also be set by the ``PYCFX_CFX_PORT=<port>``
            environment variable.
        address : str, default: None
            Address to connect to an existing CFX instance.
        password : str, default: None
            Password to connect to an existing CFX instance.
        channel : grpc.Channel, default: None
            gRPC channel to use to connect to an existing CFX instance.
            The ``ip`` and ``port`` parameters are ignored when a gRPC channel is
            specified.
        allow_remote_host : bool, default: False
            Whether to allow connecting to a remote CFX instance.
        certificates_folder : str, default: None
            Path to the folder containing TLS certificates for CFX's gRPC server.
        insecure_mode : bool, default: False
            Whether to connect CFX's gRPC server in insecure mode without TLS.
            This mode is not recommended. For more information on the implications
            and usage of insecure mode, see the CFX documentation.
        cleanup_on_exit : bool, default: True
            Whether to shut down the connected CFX session when PyCFX is exited or
            the exit() function is called on the session instance.
        start_transcript : bool, default: False
            Whether to start the CFX transcript in the client. The CFX transcript
            can be started and stopped subsequently using method calls on the session
            object.
        remote_instance : ansys.platform.instancemanagement.Instance
            Corresponding remote instance when CFX is launched through
            PyPIM. This instance is deleted when calling the
            ``Session.exit()`` function.
        inside_container: bool, default: None
            Whether the CFX session that is being connected to
            is running inside a Docker container.

        Raises
        ------
        PortNotProvided
            If port is not provided.
        """
        self._error_state = ErrorState()
        self._data_valid = False
        self._server_address = None
        self.finalizer_cbs = []
        if channel is not None:
            self._channel = channel
        else:
            if address is not None:
                self._server_address = address
            else:
                ip, port = _get_ip_and_port(ip, port)
                self._server_address = f"{ip}:{port}"
            self._channel = _get_channel(
                self._server_address,
                allow_remote_host,
                certificates_folder,
                insecure_mode,
                inside_container,
            )
        self._metadata: List[Tuple[str, str]] = [("password", password)] if password else []

        self.health_check_service = service_creator("health_check").create(
            self._channel, self._metadata, self._error_state
        )
        # At this point, the server must be running. If the following check_health()
        # throws, we should not proceed.
        self.health_check_service.check_health()

        self._id = f"session-{next(CFXConnection._id_iter)}"

        if not CFXConnection._monitor_thread:
            CFXConnection._monitor_thread = MonitorThread()
            CFXConnection._monitor_thread.start()

        # Move this service later.
        # Currently, required by launcher to connect to a running session.
        self._engine_eval_service = self.create_grpc_service(EngineEvalService, self._error_state)
        self.engine_eval = service_creator("engine_eval").create(self._engine_eval_service)

        self._cleanup_on_exit = cleanup_on_exit
        self.start_transcript = start_transcript
        from grpc._channel import _InactiveRpcError

        try:
            logger.info(self.cfx_build_info)
            logger.debug("Obtaining Engine connection properties...")
            cfx_host_pid = self.engine_eval.info_query("Engine PID")
            engine_host = self.engine_eval.info_query("Engine Host")
            engine_pid = cfx_host_pid
            engine_pwd = self.engine_eval.info_query("Engine PWD")
            logger.debug("Engine connection properties successfully obtained.")
        except _InactiveRpcError:
            logger.warning(
                "CFX Engine properties unobtainable. Force exit and other"
                "methods are not going to work properly. Proceeding..."
            )
            engine_host = None
            engine_pid = None
            engine_pwd = None
            cfx_host_pid = None

        if (
            (inside_container is None or inside_container is True)
            and not remote_instance
            and engine_host is not None
        ):
            logger.info("Checking if CFX is running inside a container.")
            inside_container = get_container(engine_host)
            logger.debug(f"get_container({engine_host}): {inside_container}")
            if inside_container is False:
                logger.info("CFX is not running inside a container.")
            elif inside_container is None:
                logger.info(
                    "The current system does not support Docker containers. "
                    "Assuming CFX is not inside a container."
                )

        self.connection_properties = CFXConnectionProperties(
            ip,
            port,
            address,
            password,
            engine_pwd,
            engine_pid,
            engine_host,
            cfx_host_pid,
            inside_container,
        )

        self._remote_instance = remote_instance
        self.launcher_args = launcher_args

        self._exit_event = threading.Event()

        # session.exit() is handled in the daemon thread (MonitorThread), which ensures
        # shutdown of non-daemon threads. A daemon thread is terminated abruptly
        # during interpreter exit, after all non-daemon threads are exited.
        # self._waiting_thread is a long-running thread which is exited
        # at the end of session.exit() to ensure everything within session.exit()
        # gets executed during exit.
        self._waiting_thread = threading.Thread(target=self._exit_event.wait)
        self._waiting_thread.start()

        self._finalizer = weakref.finalize(
            self,
            CFXConnection._exit,
            self._channel,
            self._cleanup_on_exit,
            self.engine_eval,
            self.finalizer_cbs,
            self._remote_instance,
            self._exit_event,
        )
        CFXConnection._monitor_thread.cbs.append(self._finalizer)

    @property
    def cfx_build_info(self) -> str:
        """CFX build information."""
        build_time = self.engine_eval.info_query("Engine Build Time")
        build_id = self.engine_eval.info_query("Engine Build ID")
        rev = self.engine_eval.info_query("Engine Source Revision")
        branch = self.engine_eval.info_query("Engine Source Branch")
        return f"Build Time: {build_time}  Build Id: {build_id}  Revision: {rev}  Branch: {branch}"

    def force_exit(self):
        """Terminate the CFX client immediately, which results in losing unsaved progress and data.

        Notes
        -----
        If the CFX session is responsive, using the :func:`exit()` function is preferred.

        Examples
        --------
        >>> import ansys.cfx.core as pycfx
        >>> session = pycfx.launch_cfx()
        >>> session.force_exit()
        """
        if self.connection_properties.inside_container:
            self._force_exit_container()
        elif self._remote_instance is not None:
            logger.error("Cannot execute cleanup script, CFX running remotely.")
            return
        else:
            pwd = self.connection_properties.engine_pwd
            pid = self.connection_properties.cfx_host_pid
            host = self.connection_properties.engine_host
            if host != socket.gethostname():
                logger.error("CFX host is not the current host, cancelling forced exit...")
                return
            if os.name == "nt":
                cleanup_file_ext = "bat"
                cmd_list = []
            elif os.name == "posix":
                cleanup_file_ext = "sh"
                cmd_list = ["bash"]
            else:
                logger.error(
                    "Unrecognized or unsupported operating system. Cancelling CFX cleanup script execution."
                )
                return
            # TODO: Currently CFX does not generate a cleanup script. Needed by watchdog
            # cleanup_file_name = f"cleanup-cfx-{host}-{pid}.{cleanup_file_ext}"
            # logger.debug(f"Looking for {cleanup_file_name}...")
            # cleanup_file_name = Path(pwd, cleanup_file_name)
            # if cleanup_file_name.is_file():
            #     logger.info(f"Executing CFX cleanup script, file path: {cleanup_file_name}")
            #     cmd_list.append(cleanup_file_name)
            #     logger.debug(f"Cleanup command list = {cmd_list}")
            #     subprocess.Popen(
            #         cmd_list,
            #         stdout=subprocess.DEVNULL,
            #         stderr=subprocess.DEVNULL,
            #     )
            # else:
            #     logger.error("Could not find cleanup file.")

    def _force_exit_container(self):
        """Immediately terminate the CFX client running inside a container, losing
        unsaved progress and data."""
        container = self.connection_properties.inside_container
        container_id = self.connection_properties.engine_host
        pid = self.connection_properties.cfx_host_pid
        cleanup_file_name = f"cleanup-cfx-{container_id}-{pid}.sh"
        logger.debug(f"Executing CFX container cleanup script: {cleanup_file_name}")
        if get_container(container_id):
            try:
                container.exec_run(["bash", cleanup_file_name], detach=True)
            except docker.errors.APIError as e:
                logger.info(f"{type(e).__name__}: {e}")
                logger.debug(
                    "Caught Docker APIError. Docker container probably not running anymore."
                )
        else:
            logger.debug("Container not found, cancelling cleanup script execution.")

    def register_finalizer_cb(self, cb):
        """Register a callback to run with the finalizer."""
        self.finalizer_cbs.append(cb)

    def create_grpc_service(self, service, *args):
        """Create a gRPC service.

        Parameters
        ----------
        service : Any
            Service class.
        args : Any
            Additional arguments.

        Returns
        -------
        Any
            Service object.
        """
        return service(self._channel, self._metadata, *args)

    def wait_process_finished(self, wait: Union[float, int, bool] = 60):
        """Return ``True`` if local CFX processes have finished, ``False`` if they
        are still running when wait limit (default 60 seconds) is reached. Immediately
        cancels and returns ``None`` if ``wait`` is set to ``False``.

        Parameters
        ----------
        wait : float, int or bool, default: 60
            How long to wait for processes to finish before returning. The default is 60 seconds.
            This parameter can also be set to ``True``, which results in waiting indefinitely.

        Raises
        ------
        UnsupportedRemoteCFXInstance
            If current CFX instance is running remotely.
        WaitTypeError
            If ``wait`` is specified improperly.
        """
        if self._remote_instance:
            raise UnsupportedRemoteCFXInstance()
        if isinstance(wait, bool):
            if wait:
                wait = 60
            else:
                logger.debug("Wait limit set to 'False'. Cancelling process wait.")
                return
        if isinstance(wait, (float, int)):
            logger.info(f"Waiting {wait} seconds for CFX processes to finish...")
        else:
            raise WaitTypeError()
        if self.connection_properties.inside_container:
            _response = timeout_loop(
                get_container,
                wait,
                args=(self.connection_properties.engine_host,),
                idle_period=0.5,
                expected="falsy",
            )
        else:
            _response = timeout_loop(
                lambda connection: psutil.pid_exists(connection.cfx_host_pid)
                or psutil.pid_exists(connection.engine_pid),
                wait,
                args=(self.connection_properties,),
                idle_period=0.5,
                expected="falsy",
            )
        return not _response

    def exit(
        self,
        timeout: Optional[float] = None,
        timeout_force: bool = True,
        wait: Optional[Union[float, int, bool]] = False,
    ) -> None:
        """Close the CFX connection and exit CFX.

        Parameters
        ----------
        timeout : float, default: None
            Time in seconds before considering that the exit request has timed out.
            If omitted or specified as ``None``, the request does not time out and locks up the
            interpreter while waiting for a response. The request returns earlier if it succeeds
            earlier.
        timeout_force : bool, default: True
            Whether to attempt to terminate the CFX process if the exit request reached timeout.
            If no timeout is set, this option is ignored. Executes the :func:`force_exit()` or
            :func:`force_exit_container()` function to terminate the CFX process,
            depending on how CFX was launched.
        wait : float, int or bool, default: False
            Whether to wait for local CFX processes to finish completely before proceeding.
            If omitted or specified as ``False``, the request proceeds as usual without
            waiting for the CFX processes to finish. If this parameter is set
            to ``True`` the request waits for up to 60 seconds by default.
            The wait limit can be specified as a float or integer value.
            If the wait limit is reached, the request forcefully terminate the CFX process.
            If it is set to wait, it returns as soon as the processes completely finishes.
            It does not work for the remote CFX processes.

        Notes
        -----
        The ``PYCFX_TIMEOUT_FORCE_EXIT`` environment variable can also be used to specify the
        number of seconds and alter the default ``timeout`` value. Setting this environment
        variable to a non-number value, such as ``OFF``, returns this function to the default
        behavior. Note that the environment variable is ignored if a timeout is specified when
        calling this function.

        Examples
        --------

        >>> import ansys.cfx.core as pycfx
        >>> session = pycfx.launch_cfx()
        >>> session.exit()
        """

        if wait is not False and self._remote_instance:
            logger.warning(
                "Session exit 'wait' option is ignored when working with remote CFX sessions."
            )

        if timeout is None:
            env_timeout = os.getenv("PYCFX_TIMEOUT_FORCE_EXIT")

            if env_timeout:
                logger.debug("Found PYCFX_TIMEOUT_FORCE_EXIT environment variable.")
                try:
                    timeout = float(env_timeout)
                    logger.debug(f"Setting TIMEOUT_FORCE_EXIT to {timeout}.")
                except ValueError:
                    logger.debug(
                        "Off or unrecognized PYCFX_TIMEOUT_FORCE_EXIT value. Not enabling timeout force exit."
                    )

        if timeout is None:
            logger.info("Finalizing CFX connection...")
            self._finalizer()
            if wait is not False:
                self.wait_process_finished(wait=wait)
        else:
            if not self.health_check_service.is_serving:
                logger.debug("gRPC service not working. Cancelling soft exit call.")
            else:
                logger.info("Attempting to send exit request to CFX...")
                success = timeout_exec(self._finalizer, timeout)
                if success:
                    if wait is not False:
                        if self.wait_process_finished(wait=wait):
                            return
                    else:
                        return

            logger.debug("Continuing...")
            if (timeout is not None and timeout_force) or isinstance(wait, (float, int)):
                if self._remote_instance:
                    logger.warning("Cannot force exit from CFX remote instance.")
                    return
                elif self.connection_properties.inside_container:
                    logger.debug(
                        "CFX running inside container. Cleaning up CFX inside container..."
                    )
                    self.force_exit()
                else:
                    logger.debug("CFX running locally. Cleaning up CFX processes...")
                    self.force_exit()
                logger.debug("Done.")
            else:
                logger.debug("Timeout and wait force exit disabled. Returning...")

    @staticmethod
    def _exit(
        channel,
        cleanup_on_exit,
        engine_eval,
        finalizer_cbs,
        remote_instance,
        exit_event,
    ) -> None:
        logger.debug("CFXConnection exit method called.")
        if channel:
            for cb in finalizer_cbs:
                cb()
            if cleanup_on_exit:
                try:
                    engine_eval.process_ccl((">quit",), False)
                except Exception:
                    pass
            channel.close()
            channel = None

        if remote_instance:
            remote_instance.delete()

        exit_event.set()
