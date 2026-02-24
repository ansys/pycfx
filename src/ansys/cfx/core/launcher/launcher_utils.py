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

"""Provides a module for launching utilities."""

import logging
import os
from pathlib import Path
import platform
import socket
import subprocess
import time
from typing import Any, Dict, Union

from beartype import BeartypeConf, beartype

from ansys.cfx.core.exceptions import InvalidArgument
from ansys.cfx.core.utils.networking import find_remoting_ip

logger = logging.getLogger("pycfx.launcher")


def is_linux():
    """Check if the current operating system is Linux."""
    return platform.system() == "Linux"


def is_windows():
    """Check if the current operating system is Windows."""
    return platform.system() == "Windows"


def check_docker_support():
    """Check whether Python Docker SDK is supported by the current system."""
    import docker

    try:
        _ = docker.from_env()
    except docker.errors.DockerException:
        return False
    return True


def _get_subprocess_kwargs_for_cfx(env: Dict[str, Any], argvals) -> Dict[str, Any]:
    scheduler_options = argvals.get("scheduler_options")
    is_slurm = scheduler_options and scheduler_options["scheduler"] == "slurm"
    kwargs: Dict[str, Any] = {}
    if is_slurm:
        kwargs.update(stdout=subprocess.PIPE)
    if is_windows():
        kwargs.update(shell=True, creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
    else:
        kwargs.update(shell=True, start_new_session=True)
    cfx_env = os.environ.copy()
    cfx_env.update({k: str(v) for k, v in env.items()})
    cfx_env["REMOTING_THROW_LAST_TUI_ERROR"] = "1"

    if not is_slurm:
        from ansys.cfx.core import INFER_REMOTING_IP

        if INFER_REMOTING_IP and not "REMOTING_SERVER_ADDRESS" in cfx_env:
            remoting_ip = find_remoting_ip()
            if remoting_ip:
                cfx_env["REMOTING_SERVER_ADDRESS"] = remoting_ip

    kwargs.update(env=cfx_env)
    return kwargs


def _await_cfx_launch(server_info_file_name: str, start_timeout: int, sifile_last_mtime: float):
    """Wait for successful CFX launch or raise an error."""
    while True:
        if Path(server_info_file_name).stat().st_mtime > sifile_last_mtime:
            time.sleep(1)
            logger.info("CFX has been successfully launched.")
            break
        if start_timeout == 0:
            raise TimeoutError("The launch process has timed out.")
        time.sleep(1)
        start_timeout -= 1
        logger.info("Waiting for CFX to launch...")
        if start_timeout >= 0:
            logger.info(f"...{start_timeout} seconds remaining")


def _confirm_watchdog_start(
    start_watchdog, cleanup_on_exit, cfx_connection
):  # pragma: no cover (watchdog not used)
    """Confirm whether CFX is running locally and whether the Watchdog should be
    started."""
    if start_watchdog is None and cleanup_on_exit:
        host = cfx_connection.connection_properties.engine_host
        if host == socket.gethostname():
            logger.debug(
                "CFX running on the host machine and 'cleanup_on_exit' activated. Will launch Watchdog."
            )
            start_watchdog = True
    return start_watchdog


@beartype(conf=BeartypeConf(violation_type=TypeError))
def _build_journal_argument(
    topy: Union[None, bool, str], journal_file_names: Union[None, str, list[str]]
) -> str:  # pragma: no cover (journalling functionality not used)
    """Build CFX commandline journal argument."""
    if topy and not journal_file_names:
        raise InvalidArgument("Use 'journal_file_names' to specify and convert journal files.")
    cfx_jou_arg = ""
    if isinstance(journal_file_names, str):
        journal_file_names = [journal_file_names]
    if journal_file_names:
        cfx_jou_arg += "".join([f' -i "{journal}"' for journal in journal_file_names])
    if topy:
        if isinstance(topy, str):
            cfx_jou_arg += f' -topy="{topy}"'
        else:
            cfx_jou_arg += " -topy"
    return cfx_jou_arg
