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

import argparse
import os
from pathlib import Path
import pickle

import print_cfx_version
import settingsgen

from ansys.cfx.core import CODEGEN_OUTDIR, CFXMode, launch_cfx
from ansys.cfx.core.utils.cfx_version import CFXVersion, get_version_for_file_name
from ansys.cfx.core.utils.search import get_api_tree_file_name


def _update_first_level(d, u):
    for k in d:
        d[k].update(u.get(k, {}))


if __name__ == "__main__":
    api_tree = {
        "<pre_processing_session>": {},
        "<solver_session>": {},
        "<post_processing_session>": {},
    }
    parser = argparse.ArgumentParser(description="Generate python code from CFX APIs")
    parser.add_argument(
        "--pycfx-path",
        dest="pycfx_path",
        help="Specify the pycfx installation folder to patch, with a full path e.g. '/my-venv/Lib/site-packages'.",
    )
    if not os.getenv("PYCFX_LAUNCH_CONTAINER"):
        parser.add_argument(
            "--ansys-version",
            dest="ansys_version",
            help=f"Specify the ansys package version to use. The default is {CFXVersion.get_latest_installed().value}.",
        )
        parser.add_argument(
            "--cfx-path",
            dest="cfx_path",
            help="Specify the CFX folder to use, with a full path e.g. /apps/ansys_inc/v252/CFX.",
        )
        parser.add_argument(
            "--write-static-info",
            dest="static_info_file_path",
            help="Enabling the writing of the engine static info and specify the file path.",
            default=None,
        )

    args = parser.parse_args()
    if not os.getenv("PYCFX_LAUNCH_CONTAINER"):
        if args.ansys_version:
            awp_root = os.environ[CFXVersion(args.ansys_version).awp_var]
            os.environ["PYCFX_CFX_ROOT"] = str(Path(awp_root) / "CFX")
        if args.cfx_path:
            os.environ["PYCFX_CFX_ROOT"] = args.cfx_path

    CODEGEN_OUTDIR.mkdir(parents=True, exist_ok=True)
    cfx_app_list = [CFXMode.PRE_PROCESSING, CFXMode.POST_PROCESSING]
    for cfx_app in cfx_app_list:
        sessions = {cfx_app: launch_cfx(mode=cfx_app)}
        version = get_version_for_file_name(session=sessions[cfx_app])
        print_cfx_version.generate(args.pycfx_path, sessions)
        settingsgen.reset_globals()
        static_info_file_path = getattr(args, "static_info_file_path", None)
        if static_info_file_path:
            static_info_file_path += "." + cfx_app.value[1]
        _update_first_level(
            api_tree,
            settingsgen.generate(
                version, args.pycfx_path, sessions, cfx_app, static_info_file_path
            ),
        )
    api_tree_file = get_api_tree_file_name(version, args.pycfx_path)
    Path(api_tree_file).parent.mkdir(parents=True, exist_ok=True)
    with open(api_tree_file, "wb") as f:
        pickle.dump(api_tree, f)
