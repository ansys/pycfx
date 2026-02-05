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

from unittest.mock import patch

import ansys.cfx.core.get_build_details as build_version


@patch("ansys.cfx.core.get_build_details.subprocess.check_output")
@patch("ansys.cfx.core.get_build_details.pycfx")
def test_get_build_version_string(mock_pycfx, mock_check_output):
    # Mock git log output
    mock_check_output.side_effect = [
        b"Thu Oct 29 14:23:45 2025 +0530",  # git log
        b"abc1234",  # git rev-parse
        b"main",  # git branch
    ]
    mock_pycfx.__version__ = "1.2.3"

    result = build_version.get_build_version_string()

    assert "Build Time:" in result
    assert "Current Version: 1.2.3" in result
    assert "ShaID: abc1234" in result
    assert "Branch: main" in result
