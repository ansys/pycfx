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


from pathlib import Path

from ansys.cfx.core import CODEGEN_OUTDIR, CFXMode, launch_cfx
from ansys.cfx.core.session import BaseSession
from ansys.cfx.core.utils.cfx_version import get_version_for_file_name

_THIS_DIR = Path(__file__).parent


def print_cfx_version(pycfx_path, sessions: dict[CFXMode, BaseSession]):
    if not sessions:
        mode = CFXMode.PRE_PROCESSING
        sessions[mode] = launch_cfx(mode=mode.value[1])
    session = list(sessions.values())[0]
    _cfx_version = session.get_cfx_version().value
    version = get_version_for_file_name(_cfx_version)
    eval = session.engine_eval
    version_file = (CODEGEN_OUTDIR / f"cfx_version_{version}.py").resolve()
    with open(version_file, "w", encoding="utf8") as f:
        f.write(f'CFX_VERSION = "{_cfx_version}"\n')
        f.write(f'CFX_BUILD_TIME = "{eval.info_query("Engine Build Time")}"\n')
        f.write(f'CFX_BUILD_ID = "{eval.info_query("Engine Build ID")}"\n')
        f.write(f'CFX_REVISION = "{eval.info_query("Engine Source Revision")}"\n')
        f.write(f'CFX_BRANCH = "{eval.info_query("Engine Source Branch")}"\n')


def generate(pycfx_path, sessions: dict):
    print_cfx_version(pycfx_path, sessions)


if __name__ == "__main__":
    generate(None, {})
