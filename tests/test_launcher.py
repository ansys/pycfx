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


import pytest

import ansys.cfx.core as pycfx
from ansys.cfx.core.exceptions import DisallowedValuesError
from ansys.cfx.core.launcher.error_handler import UnexpectedKeywordArgument
from ansys.cfx.core.launcher.process_launch_string import get_cfx_exe_path
from ansys.cfx.core.utils.cfx_version import AnsysVersionNotFound, CFXVersion


def test_mode():
    with pytest.raises(DisallowedValuesError):
        pycfx.launch_cfx(
            mode="meshing",
            start_container=False,
        )


def test_get_cfx_exe_path_when_nothing_is_set(helpers):
    helpers.delete_all_awp_vars()
    with pytest.raises(AnsysVersionNotFound):
        get_cfx_exe_path(mode=pycfx.CFXMode.PRE_PROCESSING)
    with pytest.raises(AnsysVersionNotFound):
        CFXVersion.get_latest_installed()


def test_kwargs():
    with pytest.raises(UnexpectedKeywordArgument):
        pycfx.launch_cfx(abc=1, meshing_mode=True)
    with pytest.raises(UnexpectedKeywordArgument):
        pycfx.launch_cfx(abc=1, xyz=2)


def test_unsuccessful_pre_connection():
    # start-timeout is intentionally provided to be 1s for the connection to fail
    with pytest.raises(Exception):
        pycfx.PreProcessing.from_install(start_timeout=1)


def test_unsuccessful_post_connection():
    # start-timeout is intentionally provided to be 1s for the connection to fail
    with pytest.raises(Exception):
        pycfx.PostProcessing.from_install(start_timeout=1)
