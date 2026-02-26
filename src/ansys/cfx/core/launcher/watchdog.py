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

"""Module for launching the PyCFX Watchdog to monitor the PyCFX and the CFX server.

This module should not be used manually. PyCFX automatically manages it.
For more information, see the ``start_watchdog`` argument for the :func:`~ansys.cfx.core.launcher.launcher.launch_cfx()` function.
"""

import os
from pathlib import Path
import random
import string
import subprocess
import sys
import time
from typing import Optional

import ansys.cfx.core as pycfx
from ansys.cfx.core.utils.execution import timeout_loop

logger = pycfx.logging.get_logger("pycfx.launcher")

IDLE_PERIOD = 2  # seconds
WATCHDOG_INIT_FILE = "watchdog_{}_init"


class UnsuccessfulWatchdogLaunch(RuntimeError):
    """Raised when Watchdog launch is unsuccessful."""

    pass


def launch(main_pid: int, sv_port: int, sv_password: str, sv_ip: Optional[str] = None) -> None:
    """Function to launch the Watchdog. This function is automatically used and managed by PyCFX.

    Parameters
    ----------
    main_pid : int
        Process ID of the Python interpreter used to launch PyCFX and the Watchdog.
    sv_port : int
        CFX server port number.
    sv_password : str
        CFX server password.
    sv_ip : str, optional
        CFX server IP address.

    Raises
    ------
    UnsuccessfulWatchdogLaunch
        If Watchdog fails to launch.
    """
    watchdog_id = "".join(
        random.choices(string.ascii_uppercase + string.ascii_lowercase + string.digits, k=6)
    )

    env_watchdog_debug = os.getenv("PYCFX_WATCHDOG_DEBUG", "off").upper()
    if env_watchdog_debug in ("1", "ON"):
        logger.debug(
            f"PYCFX_WATCHDOG_DEBUG environment variable found. "
            f"Enabling debugging for watchdog ID {watchdog_id}..."
        )

    watchdog_env = os.environ.copy()

    # No auto PyCFX logging to file on the watchdog
    if "PYCFX_LOGGING" in watchdog_env:
        watchdog_env.pop("PYCFX_LOGGING")

    # disable additional services/addons?

    # Path to the Python interpreter executable
    python_executable = sys.executable

    if not python_executable:
        logger.warning(
            "Python executable not found. Verify Python environment. "
            "Cancelling PyCFX Watchdog monitoring."
        )
        return

    logger.debug(f"Python sys.executable: {python_executable}")

    python_executable = Path(python_executable)

    watchdog_exec = Path(__file__).parents[0] / "watchdog_exec"

    if os.name == "nt":
        pythonw_executable = python_executable.parent / "pythonw.exe"
        if pythonw_executable.exists():
            python_executable = pythonw_executable
        else:
            logger.debug("Could not find Windows 'pythonw.exe' executable.")
        python_executable = str(python_executable)
        watchdog_exec = str(watchdog_exec)
        if " " in python_executable:
            python_executable = '"' + str(python_executable) + '"'
        if " " in watchdog_exec:
            watchdog_exec = '"' + str(watchdog_exec) + '"'

    # Command to be executed by the new process
    command_list = [
        python_executable,
        watchdog_exec,
        str(main_pid),
        str(sv_ip),
        str(sv_port),
        sv_password,
        watchdog_id,
    ]

    if env_watchdog_debug in ("1", "ON"):
        logger.debug(f"Starting Watchdog logging to directory {os.getcwd()}.")

    kwargs = {"env": watchdog_env, "stdin": subprocess.DEVNULL, "close_fds": True}

    if os.name == "nt":
        kwargs.update(shell=True)
        # https://learn.microsoft.com/en-us/windows/win32/procthread/process-creation-flags
        # https://docs.python.org/3/library/subprocess.html#windows-constants
        flags = 0
        flags |= subprocess.CREATE_NO_WINDOW
        flags |= subprocess.CREATE_NEW_PROCESS_GROUP
        flags |= subprocess.DETACHED_PROCESS
        flags |= subprocess.CREATE_BREAKAWAY_FROM_JOB
        flags |= subprocess.SW_HIDE
        kwargs.update(creationflags=flags)

    if os.name == "posix":
        kwargs.update(start_new_session=True)

    if env_watchdog_debug in ("1", "ON") and os.name != "nt":
        kwargs.update(
            stdout=open(f"pycfx_watchdog_out_{watchdog_id}.log", mode="w"),
            stderr=open(f"pycfx_watchdog_err_{watchdog_id}.log", mode="w"),
            bufsize=1,
        )
    else:
        kwargs.update(stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    if os.name == "nt":
        # https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/start
        cmd_send = 'start "" ' + " ".join(command_list)
    else:
        cmd_send = command_list

    logger.info(f"Watchdog command: {cmd_send}")

    init_file = Path(WATCHDOG_INIT_FILE.format(watchdog_id))
    watchdog_err = Path("pycfx_watchdog.err")

    if init_file.is_file():
        init_file.unlink()

    if watchdog_err.is_file():
        watchdog_err.unlink(missing_ok=True)

    subprocess.Popen(cmd_send, **kwargs)

    logger.info(f"Waiting for Watchdog to initialize, and then proceeding...")
    file_exists = timeout_loop(lambda: init_file.is_file() or watchdog_err.is_file(), 30.0)

    if file_exists and init_file.is_file():
        time.sleep(0.1)
        init_file.unlink()
        logger.info("Watchdog initialized.")
    else:
        if watchdog_err.is_file() and watchdog_err.exists():
            with open(watchdog_err) as f:
                err_content = "Watchdog - %s" % f.read().replace("\n", "")
            watchdog_err.unlink(missing_ok=True)
            logger.error(err_content)
            if os.getenv("PYCFX_WATCHDOG_EXCEPTION_ON_ERROR"):
                raise UnsuccessfulWatchdogLaunch(err_content)

        logger.warning("PyCFX Watchdog did not initialize correctly. Proceeding without it...")
        if os.getenv("PYCFX_WATCHDOG_EXCEPTION_ON_ERROR"):
            raise UnsuccessfulWatchdogLaunch("PyCFX Watchdog did not initialize correctly.")
