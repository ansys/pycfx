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

"""Provides a module for launching CFX.

This module supports both starting CFX locally and connecting to a remote instance
with gRPC.
"""

import logging
import os
from pathlib import Path
from typing import Any, Dict, Optional, Union

from ansys.cfx.core.cfx_connection import CFXConnection
from ansys.cfx.core.exceptions import DisallowedValuesError
from ansys.cfx.core.launcher.container_launcher import DockerLauncher
from ansys.cfx.core.launcher.error_handler import _process_invalid_args, _process_kwargs
from ansys.cfx.core.launcher.launcher_utils import _confirm_watchdog_start
from ansys.cfx.core.launcher.pycfx_enums import (
    CFXMode,
    LaunchMode,
    UIMode,
    _get_cfx_launch_mode,
    _get_mode,
    _get_running_session_mode,
)
from ansys.cfx.core.launcher.server_info import _get_server_info
from ansys.cfx.core.launcher.standalone_launcher import StandaloneLauncher
import ansys.cfx.core.launcher.watchdog as watchdog
from ansys.cfx.core.session_post import PostProcessing
from ansys.cfx.core.session_pre import PreProcessing
from ansys.cfx.core.session_solver import Solver

_THIS_DIR = Path(__file__).parent
_OPTIONS_FILE = _THIS_DIR / "cfx_launcher_options.json"
logger = logging.getLogger("pycfx.launcher")


def create_launcher(cfx_launch_mode: LaunchMode = None, **kwargs):
    """Use a factory function to create a launcher for supported launch modes.

    Parameters
    ----------
    cfx_launch_mode: LaunchMode
        Supported CFX launch modes. Options are ``"LaunchMode.CONTAINER"``
        and ``"LaunchMode.STANDALONE"``.
    kwargs : Any
        Keyword arguments.

    Returns
    -------
    launcher: Union[DockerLauncher, StandaloneLauncher]
        Session launcher.

    Raises
    ------
    DisallowedValuesError
        If an unknown CFX launch mode is passed.
    NotImplementedError
        If an unimplemented CFX launch mode is passed.
    """
    allowed_options = [mode for mode in LaunchMode]
    if not isinstance(cfx_launch_mode, LaunchMode) or cfx_launch_mode not in allowed_options:
        raise DisallowedValuesError(
            "cfx_launch_mode",
            cfx_launch_mode,
            allowed_values=allowed_options,
        )
    if cfx_launch_mode == LaunchMode.STANDALONE:
        return StandaloneLauncher(**kwargs)
    elif cfx_launch_mode == LaunchMode.CONTAINER:
        return DockerLauncher(**kwargs)
    elif cfx_launch_mode == LaunchMode.PIM:
        raise NotImplementedError("PIM launch mode is not yet implemented.")
        # return PIMLauncher(**kwargs)


#   pylint: disable=unused-argument
def launch_cfx(
    product_version: Optional[str] = None,
    journal_file_names: Union[None, str, list[str]] = None,
    start_timeout: Optional[int] = None,
    additional_arguments: Optional[str] = "",
    env: Optional[Dict[str, Any]] = None,
    start_container: Optional[bool] = None,
    container_dict: Optional[dict] = None,
    dry_run: bool = False,
    cleanup_on_exit: bool = True,
    start_transcript: bool = False,
    ui_mode: Union[UIMode, str, None] = None,
    case_file_name: Optional[str] = None,
    run_directory: Optional[str] = None,
    results_file_name: Optional[str] = None,
    solver_input_file_name: Optional[str] = None,
    mode: Optional[Union[CFXMode, str, None]] = None,
    cwd: Optional[str] = None,
    topy: Optional[Union[str, list]] = None,
    start_watchdog: Optional[bool] = None,
    scheduler_options: Optional[dict] = None,
    file_transfer_service: Optional[Any] = None,
    **kwargs,
) -> Union[PreProcessing, Solver, PostProcessing, dict]:
    """Launch CFX locally in server mode or connect to a running CFX server
    instance.

    Parameters
    ----------
    product_version : str, default: None
        Version of Ansys CFX to launch. The string must be in a format like
        ``"25.2.0"`` (for 2025 R2), matching the documented version format in the
        CFXVersion class. The default is ``None``, in which case the newest installed
        version is used.
    journal_file_names : str | list[str], default: None
        String path to a CFX journal file or a list of such paths. CFX executes the
        journals.
    start_timeout : int, default: None
        Maximum allowable time in seconds for connecting to the CFX
        server. The default is ``None``, in which case 60 seconds is used if CFX is launched outside a Slurm environment. No timeout occurs if CFX is launched within a Slurm environment.
    additional_arguments : str, default: ""
        Additional arguments to send to CFX as a string in the same
        format they are normally passed to CFX on the command line.
    env : dict, default: None
        Mapping to modify environment variables in CFX.
    start_container : bool, default: None
        Whether to launch a CFX Docker container image. For more information about containers, see
        :mod:`~ansys.cfx.core.launcher.cfx_container`.
    container_dict : dict, default: None
        Dictionary for CFX Docker container configuration. If specified,
        setting ``start_container = True`` is redundant.
        CFX launches inside a Docker container using the configuration changes specified.
        See also :mod:`~ansys.cfx.core.launcher.cfx_container`.
    dry_run : bool, default: False
        Whether to dry run a container start. If ``True``, CFX is not launched but the
        configuration information that would be used is printed as if CFX is being launched.
        If dry running a container start, the ``launch_cfx()`` method returns the
        configured ``container_dict``.
    cleanup_on_exit : bool, default: True
        Whether to shut down the connected CFX session when PyCFX is
        exited, or the ``exit()`` method is called on the session instance,
        or if the session instance becomes unreferenced.
    start_transcript : bool, default: False
        Whether to start streaming the CFX transcript in the client. You can
        stop and start the streaming of the CFX transcript subsequently using the
        ``transcript.start()`` and ``transcript.stop()`` methods on the session object.
    ui_mode : UIMode or str, default: None
        CFX user interface mode. Options are either the values of the ``UIMode``
        enum or any of ``"no_gui"``, ``"hidden_gui"``, or ``"gui"``.
        When ``None``, ``UIMode.HIDDEN_GUI`` is used.
    case_file_name : str, default: None
        Name of the case file to read into a CFX-Pre session.
    run_directory : str, default: None
        Name of the run directory to monitor with a CFX-Solver or CFD-Post session.
    results_file_name : str, default: None
        Name of the results file to read into a CFD-Post session or start a CFX-Solver session.
    solver_input_file_name : str, default: None
        Name of the solver input file to start a CFX-Solver session.
    mode : str, default: None
        Launch mode of CFX to point to a specific session type.
        Options are ``"pre-processing"``, ``"solver"``, and ``"post-processing"``.
    cwd : str, default: None
        Working directory for the CFX client.
    topy : bool or str, default: None
        Boolean flag to write the equivalent Python journals from the journals passed.
        This parameter can optionally take the file name of a new Python journal file.
    start_watchdog : bool, default: None
        When ``cleanup_on_exit`` is ``True``, ``start_watchdog`` defaults to ``True``,
        which means an independent watchdog process is run to ensure
        that any local GUI-less CFX sessions started by PyCFX are properly closed (or
        killed if frozen) when the current Python process ends.
    scheduler_options : dict, default: None
        Dictionary containing scheduler (such as Slurm scheduler) options.
    file_transfer_service : default: None
        File transfer service. Uploads or downloads files to or from the server.
    kwargs : Any
        Keyword arguments.

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
    Job scheduler environments such as SLURM, LSF, and PBS allocate resources and compute nodes.
    The allocated machines and core counts are queried from the scheduler environment and
    passed to CFX.
    """
    _process_kwargs(kwargs)
    del kwargs
    if os.getenv("PYCFX_SHOW_SERVER_GUI") == "1":
        ui_mode = UIMode.GUI
    elif ui_mode is None or isinstance(ui_mode, str):
        ui_mode = UIMode(ui_mode)
    cfx_launch_mode = _get_cfx_launch_mode(
        start_container=start_container,
        container_dict=container_dict,
        scheduler_options=scheduler_options,
    )
    del start_container
    mode = _get_mode(mode)
    argvals = locals().copy()
    _process_invalid_args(dry_run, cfx_launch_mode, argvals)
    cfx_launch_mode = argvals.pop("cfx_launch_mode")
    launcher = create_launcher(cfx_launch_mode, **argvals)
    return launcher()


def connect_to_cfx(
    ip: Optional[str] = None,
    port: Optional[int] = None,
    address: Optional[str] = None,
    cleanup_on_exit: bool = False,
    start_transcript: bool = False,  # TODO: For now, "transcript" service is not used.
    server_info_file_name: Optional[str] = None,
    password: Optional[str] = None,
    allow_remote_host: bool = False,
    certificates_folder: str | None = None,
    insecure_mode: bool = False,
    start_watchdog: Optional[bool] = None,
) -> Union[PreProcessing, Solver, PostProcessing]:
    """Connect to an existing CFX server instance.

    Parameters
    ----------
    ip : str, default: None
        IP address for connecting to an existing CFX instance. When ``None``, the
        IP address defaults to ``"127.0.0.1"``. You can also use the ``PYCFX_CFX_IP=<ip>``
        environment variable to set this parameter. The explicit value of the ``ip``
        parameter  takes precedence over the ``PYCFX_CFX_IP=<ip>`` environment variable.
    port : int, default: None
        Port to listen on for an existing CFX instance. You can also use the
        ``PYCFX_CFX_PORT=<port>`` environment variable  to set a default
        value. The explicit value of the ``port`` parameter takes precedence over
        the ``PYCFX_CFX_PORT=<port>`` environment variable.
    address : str, default: None
        Address to connect to an existing CFX instance.
    cleanup_on_exit : bool, default: False
        Whether to shut down the connected CFX session when PyCFX is
        exited, or if the ``exit()`` method is called on the session instance,
        or if the session instance becomes unreferenced.
    start_transcript : bool, default: False
        Whether to start streaming the CFX transcript in the client. You can
        stop and start the streaming of the CFX transcript subsequently using
        the ``transcript.start()`` and ``transcript.stop()`` methods on the session object.
    server_info_file_name: str, default: None
        Path to the server information file written out by CFX server. PyCFX uses
        the connection information in the file to connect to a running CFX session.
    password : str, default: None
        Password to connect to an existing CFX instance.
    allow_remote_host : bool, default: False
        Whether to allow connecting to a remote CFX instance.
    certificates_folder : str, default: None
        Path to the folder containing TLS certificates for CFX's gRPC server.
    insecure_mode : bool, default: False
        Whether to connect CFX's gRPC server in insecure mode without TLS.
        This mode is not recommended. For more information on the implications
        and usage of insecure mode, see the CFX documentation.
    start_watchdog: bool, default: None
        When ``cleanup_on_exit`` is ``True``, ``start_watchdog`` defaults to ``True``,
        which means an independent watchdog process is run to ensure
        that any local CFX connections are properly closed (or terminated if frozen) when
        the Python process ends.

    Returns
    -------
    :obj:`~typing.Union` [:class:`~ansys.cfx.core.session_pre.PreProcessing`, \
    :class:`~ansys.cfx.core.session_solver.Solver`, \
    :class:`~ansys.cfx.core.session_post.PostProcessing`]
        Session object.

    Raises
    ------
    ValueError
        Raised when neither ``certificates_folder`` nor ``insecure_mode`` are set while ``allow_remote_host`` is ``True``.
        Raised when both ``certificates_folder`` and ``insecure_mode`` are set simultaneously.
        Raised when ``certificates_folder`` is set but ``allow_remote_host`` is ``False``.
        Raised when ``insecure_mode`` is set but ``allow_remote_host`` is ``False``.
    """
    if allow_remote_host:
        if certificates_folder is None and not insecure_mode:
            raise ValueError("To connect to a remote host, set `certificates_folder`.")
        if certificates_folder is not None and insecure_mode:
            raise ValueError(
                "`certificates_folder` and `insecure_mode` cannot be set at the same time."
            )
    else:
        if certificates_folder is not None:
            raise ValueError("To set `certificates_folder`, `allow_remote_host` must be `True`.")
        if insecure_mode:
            raise ValueError("To set `insecure_mode`, `allow_remote_host` must be `True`.")

    if address is None and (ip is None or port is None):
        values = _get_server_info(server_info_file_name, ip, port, password)
        if len(values) == 2:
            address, password = values
            ip, port = None, None
        else:
            ip, port, password = values

    cfx_connection = CFXConnection(
        ip=ip,
        port=port,
        address=address,
        password=password,
        allow_remote_host=allow_remote_host,
        certificates_folder=certificates_folder,
        insecure_mode=insecure_mode,
        cleanup_on_exit=cleanup_on_exit,
        start_transcript=start_transcript,
    )
    new_session = _get_running_session_mode(cfx_connection)

    start_watchdog = _confirm_watchdog_start(start_watchdog, cleanup_on_exit, cfx_connection)

    if start_watchdog:
        logger.info("Launching Watchdog for existing CFX session...")
        watchdog.launch(os.getpid(), port, password, ip)

    return new_session(
        cfx_connection=cfx_connection,
    )
