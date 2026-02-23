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

"""Provides a module for enums used in the PyCFX."""

from enum import Enum
from functools import total_ordering
import os
from pathlib import Path
from typing import Optional, Union

from ansys.cfx.core.cfx_connection import CFXConnection
from ansys.cfx.core.exceptions import DisallowedValuesError
import ansys.cfx.core.launcher.error_handler as exceptions
from ansys.cfx.core.launcher.launcher_utils import check_docker_support
from ansys.cfx.core.session_post import PostProcessing
from ansys.cfx.core.session_pre import PreProcessing
from ansys.cfx.core.session_solver import Solver
from ansys.cfx.core.utils.cfx_version import CFXVersion
import ansys.platform.instancemanagement as pypim


class LaunchMode(Enum):
    """Enumerates over supported CFX launch modes."""

    STANDALONE = 1
    PIM = 2
    CONTAINER = 3
    SLURM = 4


class CFXMode(Enum):
    """Enumerates over supported CFX modes."""

    PRE_PROCESSING = (PreProcessing, PreProcessing.get_name())
    SOLVER = (Solver, Solver.get_name())
    POST_PROCESSING = (PostProcessing, PostProcessing.get_name())

    @staticmethod
    def get_mode(mode: str) -> "CFXMode":
        """Get the CFXMode based on the provided mode string.

        Parameters
        ----------
        mode : str
            Mode

        Returns
        -------
        CFXMode
            CFX mode.

        Raises
        ------
        DisallowedValuesError
            If an unknown mode is passed.
        """
        allowed_modes = []
        for m in CFXMode:
            allowed_modes.append(m.value[1])
            if mode == m.value[1]:
                return m
        raise DisallowedValuesError("mode", mode, allowed_modes)

    @staticmethod
    def is_pre(mode: "CFXMode") -> bool:
        """Check if the current mode is pre-processing.

        Parameters
        ----------
        mode : CFXMode
            mode

        Returns
        -------
        bool
            ``True`` if the mode is ``CFXMode.PRE_PROCESSING``,
            ``False`` otherwise.
        """
        return mode == CFXMode.PRE_PROCESSING

    @staticmethod
    def is_solver(mode: "CFXMode") -> bool:
        """Check if the current mode is solver.

        Parameters
        ----------
        mode : CFXMode
            mode

        Returns
        -------
        bool
            ``True`` if the mode is ``CFXMode.SOLVER``,
            ``False`` otherwise.
        """
        return mode == CFXMode.SOLVER

    @staticmethod
    def is_post(mode: "CFXMode") -> bool:
        """Check if the current mode is post-processing.

        Parameters
        ----------
        mode : CFXMode
            mode

        Returns
        -------
        bool
            ``True`` if the mode is ``CFXMode.POST_PROCESSING``,
            ``False`` otherwise.
        """
        return mode == CFXMode.POST_PROCESSING


@total_ordering
class CFXEnum(Enum):
    """Provides the base class for CFX-related enums.

    Accepts lowercase member names as values and supports comparison operators.
    """

    @classmethod
    def _missing_(cls, value: str):
        if value is None:
            return cls._default(cls)
        for member in cls:
            if str(member) == value:
                return member
        raise ValueError(
            f"The specified value '{value}' is a supported value of {cls.__name__}."
            f""" The supported values are: '{", '".join(str(member) for member in cls)}'."""
        )

    def __str__(self):
        return self.name.lower()

    def __lt__(self, other):
        if not isinstance(other, type(self)):
            raise TypeError(
                f"Cannot compare between {type(self).__name__} and {type(other).__name__}"
            )
        if self == other:
            return False
        for member in type(self):
            if self == member:
                return True
            if other == member:
                return False


class UIMode(CFXEnum):
    """Provides supported user interface mode of CFX."""

    NO_GUI = ("batch",)
    HIDDEN_GUI = ("",)
    # TODO: Need to handle 'show gui' option in CFX engine
    GUI = ("",)

    def _default(self):
        return self.HIDDEN_GUI


def _get_mode(mode: Optional[Union[CFXMode, str, None]] = None):
    """Update the session information."""
    if mode is None:
        mode = CFXMode.PRE_PROCESSING

    if isinstance(mode, str):
        mode = CFXMode.get_mode(mode)

    return mode


def _get_running_session_mode(cfx_connection: CFXConnection, mode: Optional[CFXMode] = None):
    """Get the mode of the running session if the mode has not been explicitly given."""
    if mode:
        session_mode = mode
    else:
        try:
            session_mode = CFXMode.get_mode(cfx_connection.engine_eval.info_query("Engine Mode"))
        except Exception as ex:
            raise exceptions.InvalidPassword() from ex
    return session_mode.value[0]


def _get_cfx_launch_mode(start_container, container_dict, scheduler_options):
    """Get the CFX launch mode.

    Parameters
    ----------
    start_container: bool
        Whether to launch a CFX Docker container image.
    container_dict: dict
        Dictionary for CFX Docker container configuration.

    Returns
    -------
    cfx_launch_mode: LaunchMode
        CFX launch mode.
    """
    if pypim.is_configured():
        cfx_launch_mode = LaunchMode.PIM
    elif start_container is True or (
        start_container is None and (container_dict or os.getenv("PYCFX_LAUNCH_CONTAINER") == "1")
    ):
        if check_docker_support():
            cfx_launch_mode = LaunchMode.CONTAINER
        else:
            raise exceptions.DockerContainerLaunchNotSupported()
    elif scheduler_options and scheduler_options["scheduler"] == "slurm":
        cfx_launch_mode = LaunchMode.SLURM
    else:
        cfx_launch_mode = LaunchMode.STANDALONE
    return cfx_launch_mode


def _get_standalone_launch_cfx_version(
    product_version: Union[CFXVersion, str, None],
) -> Optional[CFXVersion]:
    """
    Determine the CFX version during the execution of the ``launch_cfx()``
    method in standalone mode.

    The search for the version is performed in this order:

    1. The ``product_version`` parameter passed with the ``launch_cfx`` method.
    2. The CFX version from the ``PYCFX_CFX_ROOT`` environment variable, if set.
    3. The latest Ansys version from ``AWP_ROOTnnn`` environment variables.

    Returns
    -------
    CFXVersion, optional
        CFX version or ``None``
    """

    # Look for CFX version in the following order:
    # 1. product_version parameter passed with launch_cfx
    if product_version:
        return CFXVersion(product_version)

    # 2. (DEV) Find CFX version from PYCFX_CFX_ROOT environment variable if set
    cfx_root = os.getenv("PYCFX_CFX_ROOT")
    if cfx_root:
        filename = Path(cfx_root) / "etc" / "BuildInfo.log"
        try:
            with open(filename, "r") as file:
                for line in file:
                    line = line.strip()
                    if line.startswith("CFX Internal Revision:"):
                        cfx_version = line.split(":")[1].strip().replace("'", "")
                        return CFXVersion(cfx_version)
        except (FileNotFoundError, PermissionError, OSError):
            return None
        return None

    # 3. the latest ANSYS version from AWP_ROOT environment variables
    return CFXVersion.get_latest_installed()
