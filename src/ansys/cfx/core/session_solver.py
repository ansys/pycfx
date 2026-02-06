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

"""Module containing class encapsulating CFX connection."""

import logging
import os
import tempfile

from ansys.cfx.core.launcher.cfx_container import _get_host_and_container_mount_paths
from ansys.cfx.core.session import BaseSession
from ansys.cfx.core.session_pre import PreProcessing
from ansys.cfx.core.solver_controller import SolverController
from ansys.cfx.core.utils.cfx_version import CFXVersion

logger = logging.getLogger("pycfx.solver_control")


class Solver(BaseSession):
    """Encapsulates a CFX solver session.

    An object exposing the CFX-Solver in a Pythonic manner.
    """

    #: The 'solution' object is used to control the CFX-Solver. For example,
    #: <Solver>.solution.start_run()
    solution: SolverController

    def __init__(self, **argvals):
        self.solution = SolverController(solver_args=argvals)
        self._cfx_connection = None
        self._argvals = argvals
        self._host_temporary_directory_path = None
        self._container_temporary_directory_path = None
        self._temporary_directory = None

    def get_cfx_version(self) -> CFXVersion:
        """Gets and returns the CFX version."""
        return self.solution._get_cfx_version()

    def exit(self, **kwargs) -> None:
        """Exit session."""
        # This call is not necessary for this basic Solver object as it has no engine connection
        # to close. However, we should allow and encourage its use as it will be necessary when
        # the Solver object does have a connection (in the future).
        pass

    def __getattr__(self, attr):
        # This is necessary to override the base class function which relies on an engine
        # connection to function correctly.
        raise RuntimeError(f"Attribute {attr} does not exist.")

    def __dir__(self):
        # This is necessary to override the base class function which relies on an engine
        # connection to function correctly.
        dir_list = set(list(self.__dict__.keys()) + dir(type(self)))
        return sorted(dir_list)

    def _init_from_session(self, session: BaseSession):

        if isinstance(session, PreProcessing):
            self._init_from_preprocessing(session)
        else:
            raise TypeError(
                f"The session type '{type(self).__name__}' cannot be initialized from a session "
                f"of type '{type(session).__name__}'."
            )

    def _init_from_preprocessing(self, session: PreProcessing):

        case_name = self._argvals["case_file_name"]
        if case_name and case_name.endswith(".cfx"):
            case_name = case_name[:-4]
        if not case_name:
            if self.get_cfx_version() > CFXVersion.v252:
                case_name = session.engine_eval.info_query("Case Name")
        if not case_name or case_name.startswith("ERROR:"):
            raise RuntimeError(
                "The 'case_file_name' argument must be specified unless the PreProcessing "
                "session already has a saved case name. "
                "Note that the 'case_file_name' argument must always be specified for CFX "
                "releases earlier than Release 26.1."
            )

        # If a path is provided, only use the file name
        if case_name:
            case_name = os.path.basename(case_name)

        is_inside_container = (
            self.solution._is_inside_container and "volumes" in self.solution._container_dict
        )
        if is_inside_container:
            volumes_string = self.solution._container_dict["volumes"][1]
            (self._host_temporary_directory_path, self._container_temporary_directory_path) = (
                _get_host_and_container_mount_paths(volumes_string)
            )
        else:
            self._temporary_directory = tempfile.TemporaryDirectory()
            self._host_temporary_directory_path = self._temporary_directory.name

        temporary_case_path_host = os.path.join(self._host_temporary_directory_path, case_name)
        if is_inside_container:
            temporary_case_path_engine = os.path.join(
                self._container_temporary_directory_path, case_name
            )
        else:
            temporary_case_path_engine = temporary_case_path_host

        logger.debug(f"Solver temporary directory: {self._host_temporary_directory_path}")

        try:
            # CFX-Pre will take care of switching the extension to .mdef if necessary
            logger.debug(f"def_file_name: {temporary_case_path_engine}.def")
            session.file.write_solver_input_file(file_name=f"{temporary_case_path_engine}.def")
        except:
            raise RuntimeError(
                f"The temporary solver input file '{temporary_case_path_host}.def' or "
                f"'{temporary_case_path_host}.mdef' could not be written."
            )

        if os.path.exists(f"{temporary_case_path_host}.def"):
            temporary_solver_input_file = f"{temporary_case_path_engine}.def"
        elif os.path.exists(f"{temporary_case_path_host}.mdef"):
            temporary_solver_input_file = f"{temporary_case_path_engine}.mdef"
        logger.debug(f"Set solver input file: {temporary_solver_input_file}")
        self.solution._set_solver_input_file(temporary_solver_input_file)

    @classmethod
    def get_name(cls) -> str | None:
        """Return session name."""
        return "solver"

    @classmethod
    def get_cmd_name(cls) -> str | None:
        """Return the CFX command name related to the session."""
        return "cfx5solve"

    @classmethod
    def has_remote_server(cls) -> bool:
        """Return True if the session can connect to a remote server."""
        return False
