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

import sys
import traceback

from ansys.cfx.core.session_post import PostProcessing


def test_invalid_ccl_parameter(pypost: PostProcessing, capsys):
    hardcopy = pypost.results.hardcopy
    hardcopy.hardcopy_format = "png"
    hardcopy.use_screen_size = False
    hardcopy.image_width = 1200

    try:
        hardcopy.image_height = "abc"
    except Exception:
        traceback.print_exc(file=sys.stdout)

    captured = capsys.readouterr()
    # Error from CCL API
    assert (
        "RuntimeError: CCLAPI::validateCCLData::CCL validation failed with message:"
        in captured.out.strip()
    )
    # Error from CCL perl parser
    assert (
        "Error: Parameter /HARDCOPY/Image Height = abc must be type Integer" in captured.out.strip()
    )
