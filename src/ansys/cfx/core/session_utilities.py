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

"""Session utilities."""

from typing import Any, Dict

from typing_extensions import Self

import ansys.cfx.core as pycfx
from ansys.cfx.core.launcher.container_launcher import DockerLauncher
from ansys.cfx.core.launcher.pycfx_enums import CFXMode, UIMode
from ansys.cfx.core.launcher.standalone_launcher import StandaloneLauncher
from ansys.cfx.core.utils.cfx_version import CFXVersion


class SessionBase:
    """Base class for CFX sessions.

    This class is not intended to be used directly. Instead, use one of the `from_install`,
    `from_session`, `from_connection` or `from_container` methods to create a session.
    """

    _session_mode = {
        "PreProcessing": CFXMode.PRE_PROCESSING,
        "Solver": CFXMode.SOLVER,
        "PostProcessing": CFXMode.POST_PROCESSING,
    }

    @classmethod
    def from_install(
        cls,
        ui_mode: UIMode | str | None = None,
        product_version: CFXVersion | str | float | int | None = None,
        journal_file_names: None | str | list[str] = None,
        start_timeout: int = 60,
        additional_arguments: str = "",
        env: Dict[str, Any] = {},  # noqa: B006
        cleanup_on_exit: bool = True,
        dry_run: bool = False,
        start_transcript: bool = True,
        case_file_name: str | None = None,
        run_directory: str | None = None,
        results_file_name: str | None = None,
        solver_input_file_name: str | None = None,
        cwd: str | None = None,
        topy: str | list | None = None,
        start_watchdog: bool | None = None,
        file_transfer_service: Any | None = None,
    ):
        """
        Launch a CFX session in standalone mode.

        Parameters
        ----------
        ui_mode : UIMode
            Defines the user interface mode for CFX. Options correspond to values in the ``UIMode`` enum.
        product_version : CFXVersion or str or float or int, optional
            Indicates the version of Ansys CFX to launch. For example, to use version 2025 R2, pass
            ``CFXVersion.v252``, ``"25.2.0"``, ``"25.2"``, ``25.2``, or ``252``. Defaults to ``None``,
            which uses the newest installed version.
        journal_file_names : str or list of str, optional
            Path(s) to a CFX journal file(s) that CFX will execute. Defaults to ``None``.
        start_timeout : int, optional
            Maximum time in seconds allowed for connecting to the CFX server. Defaults to 60 seconds.
        additional_arguments : str, optional
            Additional command-line arguments for CFX, formatted as they would be on the command line.
        env : dict[str, str], optional
            A mapping for modifying environment variables in CFX. Defaults to ``None``.
        cleanup_on_exit : bool, optional
            Determines whether to shut down the connected CFX session when exiting PyCFX or calling
            the session's `exit()` method. Defaults to True.
        dry_run : bool, optional
            If True, does not launch CFX but prints configuration information instead. The `call()` method
            returns a tuple containing the launch string and server info file name. Defaults to False.
        start_transcript : bool, optional
            Indicates whether to start streaming the CFX transcript in the client. Defaults to True;
            streaming can be controlled via `transcript.start()` and `transcript.stop()` methods on the session object.
        case_file_name : str, optional
            Name of the case file to read into a CFX-Pre session. Defaults to None.
        run_directory : str, optional
            Name of the run directory to monitor with a CFX-Solver or CFD-Post session. Defaults to None.
        results_file_name : str, optional
            Name of the results file to read into a CFD-Post session or start a CFX-Solver session.
            Defaults to None.
        solver_input_file_name : str, optional
            Name of the solver input file to start a CFX-Solver session. Defaults to None.
        cwd : str, optional
            Working directory for the CFX client.
        topy :  bool or str, optional
            A flag indicating whether to write equivalent Python journals from provided journal files; can also specify
            a filename for the new Python journal.
        start_watchdog : bool, optional
            When `cleanup_on_exit` is True, defaults to True; an independent watchdog process ensures that any local
            GUI-less CFX sessions started by PyCFX are properly closed when the current Python process ends.
        file_transfer_service : Any
            Service for uploading/downloading files to/from the server.

        Raises
        ------
        UnexpectedKeywordArgument
            If an unexpected keyword argument is provided.

        Notes
        -----
        In job scheduler environments (e.g., SLURM, LSF, PBS), resources and compute nodes are allocated,
        and core counts are queried from these environments before being passed to CFX.
        """
        mode = cls._session_mode[cls.__name__]
        argvals = locals().copy()
        argvals.pop("cls", None)  # Remove the class reference from the arguments
        launcher = StandaloneLauncher(**argvals)
        return launcher()

    @classmethod
    def from_container(
        cls,
        ui_mode: UIMode | str | None = None,
        product_version: CFXVersion | str | float | int | None = None,
        start_timeout: int = 60,
        additional_arguments: str = "",
        container_dict: dict | None = None,
        dry_run: bool = False,
        cleanup_on_exit: bool = True,
        start_transcript: bool = True,
        start_watchdog: bool | None = None,
        file_transfer_service: Any | None = None,
        solver_input_file_name: str | None = None,
    ):
        """
        Launch a CFX session in container mode.

        Parameters
        ----------
        ui_mode : UIMode
            Defines the user interface mode for CFX. Options correspond to values in the ``UIMode`` enum.
        product_version :  CFXVersion or str or float or int, optional
            Indicates the version of Ansys CFX to launch. For example, to use version 2025 R2, pass
            any of ``CFXVersion.v252``, ``"25.2.0"``, ``"25.2"``, ``25.2``, or ``252``. Defaults to ``None``,
            which uses the newest installed version.
        start_timeout : int, optional
            Maximum allowable time in seconds for connecting to the CFX server. Defaults to 60 seconds.
        additional_arguments : str, optional
            Additional command-line arguments for CFX, formatted as they would be on the command line.
        container_dict : dict, optional
            Configuration dictionary for launching CFX inside a Docker container. See also
            :mod:`~ansys.cfx.core.launcher.cfx_container`.
        dry_run : bool, optional
            If True, does not launch CFX but prints configuration information instead. If dry running a
            container start, this method will return the configured ``container_dict``. Defaults to False.
        cleanup_on_exit : bool
            Determines whether to shut down the connected CFX session upon exit or when calling
            the session's `exit()` method. Defaults to True.
        start_transcript : bool
            Indicates whether to start streaming the CFX transcript in the client. Defaults to True;
            streaming can be controlled via `transcript.start()` and `transcript.stop()` methods on the session object.
        start_watchdog : bool, optional
            If True and `cleanup_on_exit` is True, an independent watchdog process is run to ensure that any local
            GUI-less CFX sessions started by PyCFX are properly closed when the current Python process ends.
        file_transfer_service : Any, optional
            Service for uploading/downloading files to/from the server.
        solver_input_file_name : str, optional
            Name of the solver input file to start a CFX-Solver session. Defaults to None.
        Returns
        -------
        Meshing | PureMeshing | Solver | SolverIcing | dict
            Session object or configuration dictionary if ``dry_run`` is True.

        Raises
        ------
        UnexpectedKeywordArgument
            If an unexpected keyword argument is provided.

        Notes
        -----
        In job scheduler environments (e.g., SLURM, LSF, PBS), resources and compute nodes are allocated,
        and core counts are queried from these environments before being passed to CFX.
        """
        mode = cls._session_mode[cls.__name__]
        argvals = locals().copy()
        argvals.pop("cls", None)
        launcher = DockerLauncher(**argvals)
        return launcher()

    @classmethod
    def from_connection(
        cls,
        ip: str | None = None,
        port: int | None = None,
        address: str | None = None,
        server_info_file_name: str | None = None,
        password: str | None = None,
        allow_remote_host: bool = False,
        certificates_folder: str | None = None,
        insecure_mode: bool = False,
    ):
        """Connect to an existing CFX server instance.

        Parameters
        ----------
        ip : str, optional
            IP address for connecting to an existing CFX instance. The
            IP address defaults to ``"127.0.0.1"``. You can also use the environment
            variable ``PYCFX_CFX_IP=<ip>`` to set this parameter.
            The explicit value of ``ip`` takes precedence over ``PYCFX_CFX_IP=<ip>``.
        port : int, optional
            Port to listen on for an existing CFX instance. You can use the
            environment variable ``PYCFX_CFX_PORT=<port>`` to set a default
            value. The explicit value of ``port`` takes precedence over
            ``PYCFX_CFX_PORT=<port>``.
        address : str, optional
            Address to connect to existing CFX instance.
        server_info_file_name: str
            Path to server-info file written out by CFX server. The default is
            ``None``. PyCFX uses the connection information in the file to
            connect to a running CFX session.
        password : str, optional
            Password to connect to existing CFX instance.
        allow_remote_host : bool, optional
            Whether to allow connecting to a remote CFX instance.
        certificates_folder : str, optional
            Path to the folder containing TLS certificates for CFX's gRPC server.
        insecure_mode : bool, optional
            If True, CFX's gRPC server will be connected in insecure mode without TLS.
            This mode is not recommended. For more details on the implications
            and usage of insecure mode, refer to the CFX documentation.

        Raises
        ------
        TypeError
            If the session type does not match the expected session type.
        """
        argvals = locals().copy()
        argvals.pop("cls", None)
        session = pycfx.connect_to_cfx(
            **argvals,
        )

        expected = cls.__name__
        actual = session.__class__.__name__

        if actual != expected:
            raise TypeError(f"Session type mismatch: expected {expected}, got {actual}.")

        return session

    @classmethod
    def from_session(cls, session: Self, case_file_name: str = None):
        """Launch a CFX session from another CFX session.

        Supported combinations are:

        - Launch a Solver session from a PreProcessing session. The current state of the case is
          captured when the Solver session is initialized.
        - Launch a PostProcessing session from a Solver session. The current results (if any) are
          automatically loaded into the PostProcessing session. If the Solver is currently running,
          this method waits until the run is complete before returning the initialized
          PostProcessing session.

        Parameters
        ----------
        session : SessionBase
            Existing CFX session.

        case_file_name: str
            The case file name to use when starting a Solver session from a PreProcessing session.
            This is used to determine the run name for the CFX-Solver. It does not need to be
            supplied if a case file has already been saved by the PreProcessing session (for
            Release 26.1 and later). The ".cfx" extension is not required and will be ignored if
            present.

        Raises
        ------
        TypeError
            If the session type does not match a supported session type.
        """
        new_mode = cls._session_mode[cls.__name__]

        if not hasattr(new_mode.value[0], "_init_from_session"):
            raise TypeError(
                f"The session type '{cls.__name__}' cannot be initialized from a session of type "
                f"'{type(session).__name__}'."
            )

        if not session._cfx_connection:
            # Only a Solver session does not have a _cfx_connection
            argvals = dict(session.solution.argvals)
        else:
            argvals = dict(session._cfx_connection.launcher_args)
        argvals["mode"] = new_mode

        # Remove arguments that are not relevant for the new session.
        # 1. All potential arguments that were used to specify the initial state of
        #    the original session object.
        # 2. Arguments that are set by environment variables and should not be
        #    carried over to the new session.
        args_to_remove = {
            "case_file_name",
            "run_directory",
            "results_file_name",
            "solver_input_file_name",
            "cfx_debug",
        }
        for arg in args_to_remove:
            argvals.pop(arg, None)

        if case_file_name:
            argvals["case_file_name"] = case_file_name
        if "is_inside_container" in argvals and argvals["is_inside_container"]:
            # These are specific arguments for an app that needs to reset again.
            argvals.pop("is_inside_container", None)
            argvals.pop("has_remote_server", None)
            launcher = DockerLauncher(**argvals)
        else:
            launcher = StandaloneLauncher(**argvals)
        new_session = launcher()
        new_session._init_from_session(session)
        return new_session


class PreProcessing(SessionBase):
    """Encapsulates a CFX server for pre-processing session connection."""

    pass


class Solver(SessionBase):
    """Encapsulates a CFX server for solver session connection."""

    pass


class PostProcessing(SessionBase):
    """Encapsulates a CFX server for post-processing session connection."""

    pass
