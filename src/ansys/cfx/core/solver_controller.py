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

"""Module to control a CFX-Solver instance."""

from enum import Enum
import logging
import os
import subprocess
import time
from typing import Iterator, List, Optional

import docker

from ansys.cfx.core.launcher.cfx_container import (
    configure_container_dict,
    extract_mount_paths,
    replace_container_path_with_host_path,
    replace_host_path_with_container_path,
)
from ansys.cfx.core.utils.cfx_version import CFXVersion

logger = logging.getLogger("pycfx.solver_control")


class SolverController:
    """Provides basic operations for a local CFX-Solver session."""

    class RunState(Enum):
        """Enumerates over CFX-Solver run states."""

        NONE = 0
        DEFINED = 1
        IN_PROGRESS = 2
        FINISHED = 3
        ERROR = 4

    def __init__(self, **kwargs):
        """Sets up a CFX-Solver session.

        Parameters
        ----------
        processed_args : dict
            Contains arguments initially passed to a Solver.from_install() function.

        Raises
        ------
        RuntimeError
            If the provided arguments in process_args are not consistent or any necessary files do not exist.
        """
        self._solver_input_file = None
        self._run_directory = None
        self._run_prefix = None
        self._results_file = None
        self._state = self.RunState.NONE
        self._is_multiconfig_or_op = False

        self.argvals = kwargs["solver_args"]

        self._is_inside_container = self.argvals.get("is_inside_container", False)
        self._has_remote_server = self.argvals.get("has_remote_server", True)
        self._container_dict = self.argvals.get("container_dict", {})
        self._container_volume_paths = (
            extract_mount_paths(self._container_dict) if self._is_inside_container else {}
        )

        solver_input_file_name = self.argvals.get("solver_input_file_name")
        if solver_input_file_name is not None:
            self._set_solver_input_file(solver_input_file_name)

        run_directory = self.argvals.get("run_directory")
        if run_directory is not None:
            if solver_input_file_name:
                raise RuntimeError(
                    f"It is not valid to specify both the 'run_directory' and "
                    "'solver_input_file' arguments."
                )
            if not os.path.exists(run_directory):
                raise RuntimeError(f"Provided run_directory {run_directory} does not exist.")
            self._run_directory = run_directory
            self._state = self.RunState.IN_PROGRESS
            file_base_name, file_extension = os.path.splitext(run_directory)
            self._run_prefix = file_base_name
            if not file_extension:
                self._is_multiconfig_or_op = True

        results_file_name = self.argvals.get("results_file_name")
        if results_file_name is not None:
            if solver_input_file_name:
                raise RuntimeError(
                    f"It is not valid to specify both the 'results_file_name' and "
                    "'solver_input_file' arguments."
                )
            if run_directory:
                raise RuntimeError(
                    f"It is not valid to specify both the 'results_file_name' and "
                    "'run_directory' arguments."
                )
            if not os.path.exists(results_file_name):
                raise RuntimeError(f"Provided file_name {results_file_name} does not exist.")
            self._results_file = results_file_name
            self._state = self.RunState.FINISHED
            file_base_name, file_extension = os.path.splitext(results_file_name)
            self._run_prefix = file_base_name
            if file_extension == ".mdef" or file_extension == ".mres":
                self._is_multiconfig_or_op = True

    def start_run(self) -> None:
        """Command to start a CFX-Solver run.

        This can also be used to restart from an existing results file if the Solver session has
        previously completed a successful run or if the Solver session was started with a
        'results_file_name' argument.

        Execution control is read from the CFX-Solver input file.

        Raises
        ------
        RuntimeError
            If the run cannot be successfully started.
        """
        self._update_status()

        if self._state == self.RunState.NONE:
            raise RuntimeError(f"No run has been defined.")
        elif self._state == self.RunState.IN_PROGRESS:
            raise RuntimeError(f"A run is already in progress.")
        elif self._state == self.RunState.ERROR:
            raise RuntimeError(f"A run cannot be started as there was a previous error.")

        if self._state == self.RunState.DEFINED:
            input_file = self._solver_input_file
        else:
            # self.RunState.FINISHED
            input_file = self._results_file
        if input_file is None:
            raise RuntimeError(f"A run cannot be started as no solver input file is defined.")

        def_arg = "-mdef" if self._is_multiconfig_or_op else "-def"

        input_file_host = (
            replace_container_path_with_host_path(input_file, self._container_volume_paths)
            if self._is_inside_container
            else input_file
        )
        if not os.path.exists(input_file_host):
            logger.error(f"Solver input file {input_file_host} does not exist.")
            raise RuntimeError(f"Solver input file {input_file_host} does not exist.")
        solver_stream: Iterator[str] = iter([])
        if self._is_inside_container and not self._has_remote_server:
            args = ["-stdout-comms", "-batch", def_arg, input_file]
            solver_stream = self._start_cfx_container(args, self._container_dict)
        else:
            launch_cmd = [
                self._get_cfx_solve_exe(self.argvals),
                "-stdout-comms",
                "-batch",
                def_arg,
                input_file,
            ]
            logger.debug(f"Starting run with command {' '.join(launch_cmd)}")

            proc = subprocess.Popen(launch_cmd, stdout=subprocess.PIPE)
            solver_stream = self._iter_proc_stdout(proc)

        run_setup, messages, has_failed = self._parse_initial_run_setup(solver_stream)

        if has_failed:
            if messages:
                msg_list = "\n".join(messages)
                raise RuntimeError(f"Starting CFX run failed:\n{msg_list}")
            else:
                raise RuntimeError("Starting CFX run failed")

        logger.debug(f"Run setup is: {run_setup}")
        self._state = self.RunState.IN_PROGRESS
        self._run_directory = run_setup["Working Directory"]
        self._run_prefix = run_setup["Full Run Prefix"]
        self._results_file = None
        self._solver_input_file = input_file

    def stop_run(self, wait_for_run=True) -> None:
        """Command to stop a CFX-Solver run currently in progress.

        If the run is not currently in progress, then the command will do nothing.

        Parameters
        ----------
        wait_for_run : bool
            If True, the command does not return until the run has actually stopped. Depending on
            the problem setup, this could take a long time as the CFX-Solver will need to complete
            the iteration or timestep that is in progress and then write a results file.

        """
        self._update_status()
        if self._state == self.RunState.IN_PROGRESS and os.path.exists(self._run_directory):
            stop_exe = self._get_cfx_solve_exe(self.argvals).replace("cfx5solve", "cfx5stop")
            launch_cmd = [stop_exe, "-directory", self._run_directory]
            proc = subprocess.Popen(launch_cmd)
            logger.debug(f"Stopping run with command {' '.join(launch_cmd)}")
            if wait_for_run:
                self.wait_for_run()
        else:
            # Run might have finished just as the command was run, so don't interrupt the
            # session.
            logger.warning(f"Stop command not executed as run did not seem to be in progress.")

    def is_running(self) -> bool:
        """Returns True if a CFX-Solver run is in progress.

        Returns
        -------
        bool
            True if a CFX-Solver run is in progress.
        """
        self._update_status()
        return self._state == self.RunState.IN_PROGRESS

    def wait_for_run(self, interval=10, timeout=86400) -> None:
        """Waits for a CFX-Solver run in progress to complete.

        Note that run completion is indicated by the removal of the working directory and/or the
        presence of the results file or results error file. Some CFX-Solver failures may not
        trigger the "run complete" condition, and in this case, the wait_for_run function will
        raise an exception after the specified timeout.

        Parameters
        ----------
        interval : int
            Time interval in seconds between each check of the CFX-Solver status.
        timeout : int
            Maximum number of seconds to wait for the run to finish. If the run has not finished
            within this time limit, an exception is raised.

        Raises
        ------
        RuntimeError
            If the run has not stopped within the specified timeout.
        """
        logger.debug("Waiting for run")
        start_time = time.time()
        timeout_end = start_time + timeout
        while self.is_running() and time.time() < timeout_end:
            time.sleep(interval)
        if time.time() > timeout_end:
            raise RuntimeError("Timeout reached when waiting for run.")
        logger.debug("Waiting complete")

    def get_run_state(self) -> RunState:
        """Returns the CFX-Solver run state.

        Returns
        -------
        RunState
            The current CFX-Solver run state.
        """
        self._update_status()
        return self._state

    def get_results_file_name(self, use_engine_path: bool = False) -> str | None:
        """Returns the results file name associated with the current session.

        Returns
        -------
        str | None
            The current results file name, or None if no results file is associated with the
            current session.
        """
        self._update_status()
        if self._is_inside_container and use_engine_path:
            return replace_host_path_with_container_path(
                self._results_file, self._container_volume_paths
            )
        else:
            return self._results_file

    def _get_cfx_version(self):
        product_version = self.argvals.get("product_version")
        if product_version:
            return CFXVersion(product_version)
        return CFXVersion.get_latest_installed()

    def _update_status(self) -> None:

        if self._state == self.RunState.IN_PROGRESS:

            if self._is_multiconfig_or_op:
                results_file = self._run_prefix + ".mres"
                error_file = self._run_prefix + ".mres.err"
            else:
                results_file = self._run_prefix + ".res"
                error_file = self._run_prefix + ".res.err"

            if (
                not os.path.isdir(self._run_directory)
                or os.path.exists(results_file)
                or os.path.exists(error_file)
            ):
                # Wait in case the results file takes a few seconds to appear after the working
                # directory is removed.
                tries = 12
                while tries > 0 and self._state == self.RunState.IN_PROGRESS:
                    if os.path.exists(results_file):
                        self._run_directory = None
                        self._results_file = results_file
                        self._state = self.RunState.FINISHED
                    elif os.path.exists(error_file):
                        self._run_directory = None
                        self._results_file = results_file
                        self._state = self.RunState.ERROR
                    time.sleep(5)
                    tries -= 1

                if self._state == self.RunState.IN_PROGRESS:
                    self._state = self.RunState.ERROR

    def _get_cfx_solve_exe(self, argvals) -> str:
        from ansys.cfx.core.launcher.process_launch_string import get_cfx_exe_path

        return str(get_cfx_exe_path(**argvals))

    def _parse_initial_run_setup(self, solver_stream: Iterator[str]) -> tuple[dict, list, bool]:
        in_run_setup = False
        in_error = False
        run_setup = {}
        messages = []
        has_failed = False

        for line in solver_stream:
            if isinstance(line, bytes):
                line = line.decode("utf-8")  # decode bytes to str
            line = line.strip()
            if self._is_inside_container:
                line = replace_container_path_with_host_path(line, self._container_volume_paths)
            if line == "RUN SETUP INFORMATION:":
                in_run_setup = True
            elif "DISPLAY MESSAGE:" in line:
                in_error = True
            elif line == "END":
                if in_run_setup:
                    break
                in_error = False
                in_run_setup = False
            elif in_run_setup:
                l = line.split("=")
                if len(l) == 2:
                    run_setup[l[0].strip()] = l[1].strip()
            elif in_error:
                l = line.split("=")
                if len(l) == 2:
                    if l[0].strip() == "Level" and l[1].strip() == "ERROR":
                        has_failed = True
                    elif l[0].strip() == "Message":
                        # Long messages will have been broken up and need to be re-joined
                        msg = l[1].strip().replace('", "', " ")
                        msg = msg[1:-1]
                        messages.append(msg)
        return run_setup, messages, has_failed

    def _set_solver_input_file(self, solver_input_file_name):
        if self._state != self.RunState.NONE and self._state != self.RunState.DEFINED:
            raise RuntimeError(
                "The solver input file cannot be set if the run is already in progress, complete "
                "or in an error state."
            )
        solver_input_file_host_path = (
            replace_container_path_with_host_path(
                solver_input_file_name, self._container_volume_paths
            )
            if self._is_inside_container
            else solver_input_file_name
        )
        if not os.path.exists(solver_input_file_host_path):
            raise RuntimeError(
                f"Provided solver input file '{solver_input_file_host_path}' does not exist."
            )
        self._solver_input_file = solver_input_file_name
        self._state = self.RunState.DEFINED
        file_base_name, file_extension = os.path.splitext(solver_input_file_name)
        if file_extension == ".mdef" or file_extension == ".mres":
            self._is_multiconfig_or_op = True

    def _start_cfx_container(
        self, args: List[str], container_dict: Optional[dict] = None
    ) -> Iterator[str]:
        """Starts a CFX container with the specified arguments.

        Parameters
        ----------
        args : List[str]
            List of arguments to pass to the CFX-Solver executable inside the container.
        container_dict : Optional[dict]
            Dictionary containing container configuration options such as image name, volumes,
            environment variables, etc.

        Returns
        -------
        Iterator[str]
            A stream of output lines from the container.

        Raises
        ------
        RuntimeError
            If the container cannot be started.
        """

        config_dict, *_ = configure_container_dict(args, has_remote_server=False, **container_dict)

        client = docker.from_env()

        logger.debug("Starting CFX docker container...")

        try:
            image = config_dict.pop("cfx_image")
        except KeyError:
            raise ValueError("Missing 'cfx_image' in config_dict")
        detach = config_dict.pop("detach", True)

        try:
            container = client.containers.create(
                image,
                detach=detach,
                tty=False,
                stdin_open=False,
                **config_dict,
            )
            container.start()
            logger.debug(
                f"""Container '{container.id[:10]}' started with command: {config_dict["command"]}. Streaming output..."""
            )

            # Get the raw stream object
            # Use container.attach() with stream=True to get the real-time output.
            # The 'logs' flag includes the output generated since start.
            stream = container.attach(stream=True, logs=True, stdout=True, stderr=False)
            buffer = ""
            for chunk in stream:
                buffer += chunk.decode("utf-8")
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    yield line
            if buffer:
                yield buffer  # yield any remaining data

        except docker.errors.DockerException as e:
            raise RuntimeError(f"Failed to start CFX container: {e}") from e

    def _iter_proc_stdout(self, proc: subprocess.Popen) -> Iterator[str]:
        """
        Yield lines from the stdout of a subprocess as decoded UTF-8 strings.

        Args:
            proc (Popen): The subprocess whose stdout will be read.

        Yields:
            str: Each line from the subprocess's stdout, decoded and stripped.
        """
        while True:
            line = proc.stdout.readline()
            if not line:
                break
            yield line.decode("utf-8").strip()
