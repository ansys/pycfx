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

"""Provides a module for launching CFX in container mode.

Examples
--------

>>> from ansys.cfx.core.launcher.launcher import create_launcher
>>> from ansys.cfx.core.launcher.pycfx_enums import LaunchMode

>>> container_pre_launcher = create_launcher(LaunchMode.CONTAINER,
...                                          ui_mode=UIMode.HIDDEN_GUI,
...                                          mode=CFXMode.PRE_PROCESSING,
...                                          container_dict={...} )
>>> container_pre_session = container_pre_launcher()

>>> container_solver_launcher = create_launcher(LaunchMode.CONTAINER,
...                                             ui_mode=UIMode.HIDDEN_GUI,
...                                             mode=CFXMode.SOLVER,
...                                             container_dict={...})
>>> container_solver_session = container_solver_launcher()
"""

import logging
import os
from typing import Any, Dict, Optional, Union

from ansys.cfx.core.cfx_connection import CFXConnection
from ansys.cfx.core.launcher.cfx_container import configure_container_dict, start_cfx_container
from ansys.cfx.core.launcher.error_handler import _process_invalid_args
from ansys.cfx.core.launcher.process_launch_string import _build_cfx_launch_args_string
from ansys.cfx.core.launcher.pycfx_enums import CFXMode, LaunchMode, UIMode
import ansys.cfx.core.launcher.watchdog as watchdog
from ansys.cfx.core.session_solver import Solver
from ansys.cfx.core.utils.file_transfer_service import PimFileTransferService

_THIS_DIR = os.path.dirname(__file__)
_OPTIONS_FILE = os.path.join(_THIS_DIR, "cfx_launcher_options.json")
logger = logging.getLogger("pycfx.launcher")


class DockerLauncher:
    """Instantiates CFX session in container mode."""

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
        """Launch CFX session in container mode.

        Parameters
        ----------
        mode : CFXMode
            Launch mode of CFX to point to a specific session type.
        ui_mode : UIMode
            CFX user interface mode. Options are the values of the ``UIMode`` enum.
        product_version : str, optional
            Version of Ansys CFX to launch. The string must be in a format like
            ``"25.2.0"`` (for 2025 R2), matching the documented version format in the
            CFXVersion class. The default is ``None``, in which case the newest installed
            version is used.
        journal_file_names : str or list of str, optional
            The string path to a CFX journal file, or a list of such paths. CFX will execute the
            journal(s). The default is ``None``.
        start_timeout : int, optional
            Maximum allowable time in seconds for connecting to the CFX
            server. The default is ``60``.
        additional_arguments : str, optional
            Additional arguments to send to CFX as a string in the same
            format they are normally passed to CFX on the command line.
        env : dict[str, str], optional
            Mapping to modify environment variables in CFX. The default
            is ``None``.
        start_container : bool, optional
            Specifies whether to launch a CFX Docker container image. For more details about containers, see
            :mod:`~ansys.cfx.core.launcher.cfx_container`.
        container_dict : dict, optional
            Dictionary for CFX Docker container configuration. If specified,
            setting ``start_container = True`` as well is redundant.
            Will launch CFX inside a Docker container using the configuration changes specified.
            See also :mod:`~ansys.cfx.core.launcher.cfx_container`.
        dry_run : bool, optional
            Defaults to False. If True, will not launch CFX, and will instead print configuration information
            that would be used as if CFX was being launched. If dry running a container start,
            ``launch_cfx()`` will return the configured ``container_dict``.
        cleanup_on_exit : bool, optional
            Whether to shut down the connected CFX session when PyCFX is
            exited, or the ``exit()`` method is called on the session instance,
            or if the session instance becomes unreferenced. The default is ``True``.
        start_transcript : bool, optional
            Whether to start streaming the CFX transcript in the client. The
            default is ``True``. You can stop and start the streaming of the
            CFX transcript subsequently via the method calls, ``transcript.start()``
            and ``transcript.stop()`` on the session object.
        case_file_name : str, optional
            Name of the case file to read into a CFX-Pre session.
        run_directory : str, optional
            Name of the run directory to monitor with a CFX-Solver or CFD-Post session.
        results_file_name : str, optional
            Name of the results file to read into a CFD-Post session or start a CFX-Solver session.
        solver_input_file_name : str, optional
            Name of the solver input file to start a CFX-Solver session.
        cwd : str, Optional
            Working directory for the CFX client.
        topy : bool or str, optional
            A boolean flag to write the equivalent Python journal(s) from the journal(s) passed.
            Can optionally take the file name of the new python journal file.
        start_watchdog : bool, optional
            When ``cleanup_on_exit`` is True, ``start_watchdog`` defaults to True,
            which means an independent watchdog process is run to ensure
            that any local GUI-less CFX sessions started by PyCFX are properly closed (or killed if frozen)
            when the current Python process ends.
        file_transfer_service : optional
            File transfer service. Uploads/downloads files to/from the server.

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
        Job scheduler environments such as SLURM, LSF, PBS, etc. allocates resources / compute nodes.
        The allocated machines and core counts are queried from the scheduler environment and
        passed to CFX.
        """
        is_inside_container: bool = True
        del start_container
        argvals = locals().copy()
        del argvals["self"]
        _process_invalid_args(dry_run, LaunchMode.CONTAINER, argvals)
        if argvals["start_timeout"] is None:
            argvals["start_timeout"] = 60
        for arg_name, arg_values in argvals.items():
            setattr(self, arg_name, arg_values)
        self.argvals = argvals
        self.new_session = self.mode.value[0]
        self.file_transfer_service = (
            file_transfer_service if file_transfer_service else PimFileTransferService()
        )

    def __call__(self):
        has_remote_server: bool = self.mode.value[0].has_remote_server()
        if has_remote_server:
            args = _build_cfx_launch_args_string(**self.argvals).split()
        if self.container_dict is None:
            setattr(self, "container_dict", {})
        self.container_dict["cfx_cmd"] = self.mode.value[0].get_cmd_name()
        if self.product_version:
            self.container_dict["image_tag"] = f"v{self.product_version}"
        if self.dry_run:
            config_dict, *_ = configure_container_dict(args, **self.container_dict)
            from pprint import pprint

            print("\nDocker container run configuration:\n")
            print("config_dict = ")
            if os.getenv("PYCFX_HIDE_LOG_SECRETS") != "1":
                pprint(config_dict)
            else:
                config_dict_h = config_dict.copy()
                config_dict_h.pop("environment")
                pprint(config_dict_h)
                del config_dict_h
            return config_dict

        self.argvals["has_remote_server"] = has_remote_server
        if not has_remote_server:
            # For now, the Solver session is not using a gRPC connection to an
            # engine process. Instead, just create the local Solver object and
            # start solver container and run it in SolverController
            self.argvals["container_dict"] = self.container_dict
            if self.mode == CFXMode.SOLVER:
                return Solver(**self.argvals)
            else:
                raise NotImplementedError(
                    f"Launching {self.mode} in container mode without server is not supported."
                )

        ip, port, uds_address = None, None, None
        values = start_cfx_container(args, self.container_dict)
        if len(values) == 2:
            uds_address, password = values
        else:
            ip, port, password = values

        session = self.new_session(
            cfx_connection=CFXConnection(
                ip=ip,
                port=port,
                address=uds_address,
                password=password,
                cleanup_on_exit=self.cleanup_on_exit,
                start_transcript=self.start_transcript,
                launcher_args=self.argvals,
                inside_container=True,
            ),
            file_transfer_service=self.file_transfer_service,
        )

        if self.start_watchdog is None and self.cleanup_on_exit:
            setattr(self, "start_watchdog", True)
        if self.start_watchdog:
            logger.debug("Launching Watchdog for CFX container...")
            watchdog.launch(os.getpid(), port, password)

        return session
