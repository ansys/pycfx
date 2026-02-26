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

"""Provides a module to process launch string."""

import json
import os
from pathlib import Path

from ansys.cfx.core.launcher import launcher_utils
from ansys.cfx.core.launcher.pycfx_enums import CFXMode
from ansys.cfx.core.utils.cfx_version import CFXVersion

_THIS_DIR = Path(__file__).parent
_OPTIONS_FILE = _THIS_DIR / "cfx_launcher_options.json"


def _build_cfx_launch_args_string(**kwargs) -> str:
    """Build CFX's launch arguments string from keyword arguments.

    Returns
    -------
    str
        CFX's launch arguments string.
    """
    all_options = None
    with _OPTIONS_FILE.open(encoding="utf-8") as fp:
        all_options = json.load(fp)
    launch_args_string = ""
    for k, v in all_options.items():
        argval = kwargs.get(k)
        default = v.get("default")
        if argval is None and v.get("cfx_required") is True:
            argval = default
        if argval is not None:
            allowed_values = v.get("allowed_values")
            if allowed_values and argval not in allowed_values:
                if default is not None:
                    old_argval = argval
                    argval = default
                    launcher_utils.logger.warning(
                        f"Specified value '{old_argval}' for argument '{k}' is not an allowed value ({allowed_values})."
                        f" Default value '{argval}' is going to be used instead."
                    )
                else:
                    launcher_utils.logger.warning(
                        f"{k} = {argval} is discarded as it is not an allowed value. Allowed values: {allowed_values}"
                    )
                    continue
            cfx_map = v.get("cfx_map")
            if cfx_map:
                if isinstance(argval, str):
                    json_key = argval
                else:
                    json_key = json.dumps(argval)
                argval = cfx_map[json_key]
            launch_args_string += v["cfx_format"].replace("{}", str(argval))
    addArgs = kwargs.get("additional_arguments")
    ui_mode = kwargs.get("ui_mode")
    if ui_mode and ui_mode.value[0]:
        launch_args_string += f" -{ui_mode.value[0]}"
    return launch_args_string


def _generate_launch_string(
    argvals,
    mode: CFXMode,
    additional_arguments: str,
    server_info_file_name: str,
):
    """Generates the launch string to launch CFX."""
    if launcher_utils.is_windows():
        exe_path = str(get_cfx_exe_path(**argvals))
        if " " in exe_path:
            exe_path = '"' + exe_path + '"'
    else:
        exe_path = str(get_cfx_exe_path(**argvals))
    launch_string = exe_path

    # This is intentionally hidden from options as this is
    # for development only
    cfx_local_root = os.getenv("PYCFX_CFX_LOCAL_ROOT")
    if cfx_local_root:
        if launcher_utils.is_windows():
            if " " in cfx_local_root:
                cfx_local_root = '"' + cfx_local_root + '"'
        launch_string += " -local-root " + cfx_local_root

    launch_string += _build_cfx_launch_args_string(**argvals)
    if additional_arguments:
        launch_string += f" {additional_arguments}"
    if " " in server_info_file_name:
        server_info_file_name = '"' + server_info_file_name + '"'
    launch_string += f" -sifile {server_info_file_name}"
    return launch_string


def get_cfx_exe_path(**launch_argvals) -> Path:
    """Get the path for the CFX executable file.
    The search for the path is performed in this order:

    1. ``product_version`` parameter passed with the ``launch_cfx()`` method.
    2. The latest Ansys version from ``AWP_ROOTnnn`` environment variables.

    Returns
    -------
    Path
        CFX executable path.
    """

    def get_cfx_root(version: CFXVersion) -> Path:
        awp_root = os.environ[version.awp_var]
        return Path(awp_root) / "CFX"

    def get_exe_path(cfx_root: Path, cfx_mode: CFXMode) -> Path:
        cfx_exe = cfx_mode.value[0].get_cmd_name()
        if launcher_utils.is_windows():
            cfx_exe += ".exe"

        return cfx_root / "bin" / cfx_exe

    launch_mode = launch_argvals.get("mode")

    # (DEV) "PYCFX_CFX_ROOT" environment variable
    cfx_root = os.getenv("PYCFX_CFX_ROOT")
    if cfx_root:
        return get_exe_path(Path(cfx_root), launch_mode)

    # Look for CFX exe path in the following order:
    # 1. product_version parameter passed with launch_cfx
    product_version = launch_argvals.get("product_version")
    if product_version:
        return get_exe_path(get_cfx_root(CFXVersion(product_version)), launch_mode)

    # 2. the latest ANSYS version from AWP_ROOT environment variables
    return get_exe_path(get_cfx_root(CFXVersion.get_latest_installed()), launch_mode)
