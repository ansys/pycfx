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

"""Provides a module for launching CFX in standalone mode.

Examples
--------

>>> from ansys.cfx.core.launcher.launcher import create_launcher
>>> from ansys.cfx.core.launcher.pycfx_enums import LaunchMode, UIMode

>>> standalone_pre_launcher = create_launcher(LaunchMode.STANDALONE,
...                                           ui_mode=UIMode.HIDDEN_GUI,
...                                           mode=CFXMode.PRE_PROCESSING)
>>> standalone_pre_session = standalone_pre_launcher()

>>> standalone_solver_launcher = create_launcher(LaunchMode.STANDALONE,
...                                              ui_mode=UIMode.HIDDEN_GUI,
...                                              mode=CFXMode.SOLVER)
>>> standalone_solver_session = standalone_solver_launcher()
"""

import logging
import os
from pathlib import Path
import shutil
import subprocess
from typing import Any, Dict, Optional, Union

from ansys.cfx.core.launcher.error_handler import (
    LaunchCFXError,
    _process_invalid_args,
    _raise_non_gui_mode_exception,
)
from ansys.cfx.core.launcher.launcher_utils import (
    _await_cfx_launch,
    _build_journal_argument,
    _confirm_watchdog_start,
    _get_subprocess_kwargs_for_cfx,
    is_windows,
)
from ansys.cfx.core.launcher.process_launch_string import _generate_launch_string
from ansys.cfx.core.launcher.pycfx_enums import (
    CFXMode,
    LaunchMode,
    UIMode,
    _get_standalone_launch_cfx_version,
)
from ansys.cfx.core.launcher.server_info import _get_server_info, _get_server_info_file_name
import ansys.cfx.core.launcher.watchdog as watchdog
from ansys.cfx.core.session_solver import Solver
from ansys.cfx.core.utils.cfx_version import CFXVersion

logger = logging.getLogger("pycfx.launcher")


class StandaloneLauncher:
    """Instantiates a CFX session in standalone mode."""

    def __init__(
        self,
        mode: CFXMode,
        ui_mode: UIMode,
        product_version: Optional[str] = None,
        journal_file_names: Union[None, str, list[str]] = None,
        start_timeout: int = 60,
        additional_arguments: Optional[str] = "",
        env: Optional[Dict[str, Any]] = None,
        start_container: Optional[bool] = None,
        container_dict: Optional[dict] = None,
        dry_run: bool = False,
        cleanup_on_exit: bool = True,
        start_transcript: bool = False,
        case_file_name: Optional[str] = None,
        run_directory: Optional[str] = None,
        results_file_name: Optional[str] = None,
        solver_input_file_name: Optional[str] = None,
        cwd: Optional[str] = None,
        topy: Optional[Union[str, list]] = None,
        start_watchdog: Optional[bool] = None,
        scheduler_options: Optional[dict] = None,
        file_transfer_service: Optional[Any] = None,
    ):
        """Launches a CFX session in standalone mode.

        Parameters
        ----------
        mode : CFXMode
            Launch mode of CFX to point to a specific session type.
        ui_mode : UIMode
            CFX user interface mode. Options are the values of the ``UIMode`` enum.
        product_version : str, default: None
            Version of Ansys CFX to launch. The string must be in a format like
            ``"25.2.0"`` (for 2025 R2), matching the documented version format in the
            CFXVersion class. The default is ``None``, in which case the newest installed
            version is used.
        journal_file_names : str or list of str, default: None
            String path to a CFX journal file or a list of such paths. CFX executes the
            journals.
        start_timeout : int, default: 60
            Maximum allowable time in seconds for connecting to the CFX
            server.
        additional_arguments : str, default: ""
            Additional arguments to send to CFX as a string in the same
            format they are normally passed to CFX on the command line.
        env : dict[str, str], default: None
            Mapping to modify environment variables in CFX.
        start_container : bool, default: None
            Whether to launch a CFX Docker container image. For more information about containers, see
            the :mod:`~ansys.cfx.core.launcher.cfx_container` module.
        container_dict : dict, default: None
            Dictionary for CFX Docker container configuration. If specified,
            setting ``start_container = True`` is redundant.
            CFX launches inside a Docker container using the configuration changes specified.
            See also the :mod:`~ansys.cfx.core.launcher.cfx_container` module.
        dry_run : bool, default: False
            Whether to dry run a container start. If ``True``, CFX is not launched but the configuration
            information that would be used is printed as if CFX is being launched. If dry running a
            container start, the ``launch_cfx()`` method returns the configured ``container_dict``.
        cleanup_on_exit : bool, default: True
            Whether to shut down the connected CFX session when PyCFX is
            exited, or the ``exit()`` method is called on the session instance,
            or if the session instance becomes unreferenced.
        case_file_name : str, default: None
            Name of the case file to read into a CFX-Pre session.
        run_directory : str, default: None
            Name of the run directory to monitor with a CFX-Solver or CFD-Post session.
        results_file_name : str, default: None
            Name of the results file to read into a CFD-Post session or start a CFX-Solver session,
        solver_input_file_name : str, default: None
            Name of the solver input file to start a CFX-Solver session.
        cwd : str, default: None
            Working directory for the CFX client.
        topy : bool or str, default: None
            A Boolean flag to write the equivalent Python journals from the journals passed.
            This parameter can optionally take the file name of a new Python journal file.
        start_watchdog : bool, default: None
            When ``cleanup_on_exit`` is ``True``, ``start_watchdog`` defaults to ``True``,
            which means an independent watchdog process is run to ensure
            that any local GUI-less CFX sessions started by PyCFX are properly closed (or killed if frozen) when the current Python process ends.
        file_transfer_service : default: None
            File transfer service. Uploads or downloads files to or from the server.

        Returns
        -------
        :obj:`~typing.Union` [:class:`~ansys.cfx.core.session_pre.PreProcessing`, \
        :class:`~ansys.cfx.core.session_solver.Solver`, \
        :class:`~ansys.cfx.core.session_post.PostProcessing`, dict]
            Session object or configuration dictionary if ``dry_run = True``.

        Raises
        ------
        UnexpectedKeywordArgument
            If an unexpected keyword argument is provided.
        DockerContainerLaunchNotSupported
            If a CFX Docker container launch is not supported.

        Notes
        -----
        Job scheduler environments such as SLURM, LSF, PBS, etc. allocate resources / compute nodes.
        The allocated machines and core counts are queried from the scheduler environment and
        passed to CFX.
        """
        del start_container
        argvals = locals().copy()
        del argvals["self"]
        _process_invalid_args(dry_run, LaunchMode.STANDALONE, argvals)
        if argvals["start_timeout"] is None:
            argvals["start_timeout"] = 60
        for arg_name, arg_values in argvals.items():
            setattr(self, arg_name, arg_values)
        self.argvals = argvals
        self.new_session = self.mode.value[0]
        self.file_transfer_service = file_transfer_service

    def __call__(
        self,
    ):  # pragma: no cover (can't cover the standalone_launch process under GitHub CI)
        self._cfx_version = _get_standalone_launch_cfx_version(self.product_version)
        if self._cfx_version:
            _raise_non_gui_mode_exception(self.ui_mode, self._cfx_version)

        cfx_debug_mode = os.getenv("PYCFX_CFX_DEBUG", "off").upper()
        if cfx_debug_mode in ("1", "ON"):
            self.argvals["cfx_debug"] = True

        # For now, the Solver session is not using a gRPC connection to an engine process.
        # Instead, just create the local Solver object.
        if self.mode == CFXMode.SOLVER:
            return Solver(**self.argvals)

        server_info_file_name = _get_server_info_file_name()
        launch_string = _generate_launch_string(
            self.argvals,
            self.mode,
            self.additional_arguments,
            server_info_file_name,
        )

        sifile_last_mtime = Path(server_info_file_name).stat().st_mtime
        if self.env is None:
            setattr(self, "env", {})
        kwargs = _get_subprocess_kwargs_for_cfx(self.env, self.argvals)
        if self.cwd:
            kwargs.update(cwd=self.cwd)
        launch_string += _build_journal_argument(self.topy, self.journal_file_names)

        filter_wnua = (
            is_windows() and self._cfx_version and CFXVersion(self._cfx_version) < CFXVersion.v261
        ) and os.getenv("PYCFX_SHOW_ALL_WNUA_MESSAGES", "unset") != "1"

        if filter_wnua:
            # On Windows with CFX version < 261, filter out specific WNUA access denied
            # messages that are generated during CUE server exit. The message does not
            # impact server functionality and the underlying issue has been addressed in v261.
            findstr_path = shutil.which("findstr.exe")
            if findstr_path:
                launch_cmd = f'{launch_string} 2>&1 | "{findstr_path}" /V "WNUA: Client is NOT same Windows user - ACCESS DENIED"'
            else:
                launch_cmd = launch_string
        else:
            launch_cmd = launch_string

        try:
            logger.debug(f"Launching CFX with command: {launch_cmd}")

            subprocess.Popen(launch_cmd, **kwargs)

            try:
                _await_cfx_launch(server_info_file_name, self.start_timeout, sifile_last_mtime)
            except TimeoutError as ex:
                if is_windows():
                    logger.warning(f"Exception caught - {type(ex).__name__}: {ex}")
                    launch_cmd = launch_string.replace('"', "", 2)
                    kwargs.update(shell=False)
                    logger.warning(f"Retrying CFX launch with less robust command: {launch_cmd}")
                    subprocess.Popen(launch_cmd, **kwargs)
                    _await_cfx_launch(server_info_file_name, self.start_timeout, sifile_last_mtime)
                else:
                    raise ex

            session = self.new_session._create_from_server_info_file(
                server_info_file_name=server_info_file_name,
                file_transfer_service=self.file_transfer_service,
                cleanup_on_exit=self.cleanup_on_exit,
                start_transcript=self.start_transcript,
                launcher_args=self.argvals,
                inside_container=False,
            )
            # TODO: Watchdog is not working. Turn off by default for now.
            env_enable_watchdog = os.getenv("PYCFX_ENABLE_WATCHDOG", "off").upper()
            start_watchdog = True if env_enable_watchdog in ("1", "ON") else False
            if start_watchdog:
                start_watchdog = _confirm_watchdog_start(
                    self.start_watchdog, self.cleanup_on_exit, session._cfx_connection
                )
            if start_watchdog:
                logger.info("Launching Watchdog for local CFX client...")
                values = _get_server_info(self._server_info_file_name)
                if len(values) == 3:
                    ip, port, password = values
                    watchdog.launch(os.getpid(), port, password, ip)
                elif len(values) == 2:
                    # When using a Unix domain socket connection, only the socket path and
                    # password are available (no TCP/IP host/port). The current watchdog
                    # implementation expects a TCP/IP endpoint, so it is not started in
                    # this case by design.
                    uds_path, password = values
                    logger.debug(
                        "Watchdog not started: Unix domain socket connection (%s) "
                        "is not currently supported by the watchdog.",
                        uds_path,
                    )

            if self.argvals["case_file_name"]:
                if self.mode == CFXMode.PRE_PROCESSING:
                    session.file.open_case(file_name=self.argvals["case_file_name"])
                else:
                    logger.warning(
                        f"The 'case_file_name' argument is only used for a CFX-Pre session."
                    )

            if self.argvals["run_directory"]:
                if self.mode == CFXMode.SOLVER:
                    # To implement when the SOLVER mode uses the full session base
                    pass
                elif self.mode == CFXMode.POST_PROCESSING:
                    logger.warning(
                        f"The 'run_directory' argument is not yet implemented for a "
                        "CFD-Post session."
                    )
                else:
                    logger.warning(
                        f"The 'run_directory' argument is only used for a CFX-Solver or "
                        "CFD-Post session."
                    )

            if self.argvals["results_file_name"]:
                if self.mode == CFXMode.SOLVER:
                    # To implement when the SOLVER mode uses the full session base
                    pass
                elif self.mode == CFXMode.POST_PROCESSING:
                    session.file.load_results(file_name=self.argvals["results_file_name"])
                else:
                    logger.warning(
                        f"The 'results_file_name' argument is only used for a CFX-Solver or "
                        "CFD-Post session."
                    )

            if self.argvals["solver_input_file_name"]:
                if self.mode == CFXMode.SOLVER:
                    # To implement when the SOLVER mode uses the full session base
                    pass
                else:
                    logger.warning(
                        f"The 'solver_input_file_name' argument is only used for a CFX-Solver session."
                    )

            return session
        except Exception as ex:
            logger.error(f"Exception caught - {type(ex).__name__}: {ex}")
            raise LaunchCFXError(launch_cmd) from ex
        finally:
            server_info_file = Path(server_info_file_name)
            if server_info_file.exists():
                server_info_file.unlink()
