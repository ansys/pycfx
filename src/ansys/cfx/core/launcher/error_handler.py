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

"""Provides a module for customized error handling."""

from ansys.cfx.core.exceptions import InvalidArgument
from ansys.cfx.core.launcher import launcher_utils
from ansys.cfx.core.launcher.pycfx_enums import LaunchMode, UIMode
from ansys.cfx.core.utils.cfx_version import CFXVersion


class InvalidPassword(ValueError):
    """Raised when the password is invalid."""

    def __init__(self):
        super().__init__("Provide correct 'password'.")


class IpPortNotProvided(ValueError):
    """Raised when the IP address and port are not specified."""

    def __init__(self):
        super().__init__("Provide either 'ip' and 'port' or 'server_info_file_name'.")


class UnexpectedKeywordArgument(TypeError):
    """Raised when a valid keyword argument is not specified."""

    pass


class DockerContainerLaunchNotSupported(SystemError):
    """Raised when a Docker container launch is not supported."""

    def __init__(self):
        super().__init__("Python Docker SDK is unsupported on this system.")


class LaunchCFXError(Exception):
    """Raised when a CX launch error occurs."""

    def __init__(self, launch_string):
        """__init__ method of ``LaunchCFXError`` class."""
        details = "\n" + "CFX Launch string: " + launch_string
        super().__init__(details)


def _raise_non_gui_mode_exception(ui_mode: UIMode, product_version: CFXVersion) -> None:
    """Currently CFX user interface mode only supports ``UIMode.HIDDEN_GUI`` mode"""
    if UIMode(ui_mode) != UIMode.HIDDEN_GUI:
        raise InvalidArgument(f"'{ui_mode}' is not supported .")


def _process_kwargs(kwargs):
    """Verify whether keyword arguments are valid or not.

    Parameters
    ----------
    kwargs: Any
        Keyword arguments.

    Raises
    ------
    UnexpectedKeywordArgument
        If an unexpected keyword argument is provided.
    """
    if kwargs:
        raise UnexpectedKeywordArgument(
            f"launch_cfx() got an unexpected keyword argument {next(iter(kwargs))}"
        )


def _process_invalid_args(dry_run, cfx_launch_mode, argvals):
    """Get invalid arguments.

    Parameters
    ----------
    dry_run: bool
        Whether to dry run a container start.
         If ``True``, the ``launch_cfx()`` method returns the configured ``container_dict``.
    cfx_launch_mode: LaunchMode
        CFX launch mode.
    argvals: dict
        Local arguments.
    """
    if dry_run and cfx_launch_mode != LaunchMode.CONTAINER:
        launcher_utils.logger.warning(
            "'dry_run' argument for 'launch_cfx' method currently is only "
            "supported when starting containers."
        )
    if cfx_launch_mode != LaunchMode.STANDALONE:
        arg_names = [
            "env",
            "cwd",
            "topy",
            "run_directory",
            "results_file_name",
            "journal_file_names",
        ]
        invalid_arg_names = list(filter(lambda arg_name: argvals[arg_name] is not None, arg_names))
        if len(invalid_arg_names) != 0:
            invalid_str_names = ", ".join(invalid_arg_names)
            launcher_utils.logger.warning(
                f"These specified arguments are only supported when starting "
                f"local standalone CFX clients: {invalid_str_names}."
            )
