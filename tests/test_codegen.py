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

import importlib

import pytest

from ansys.cfx.core.common import flobject
from ansys.cfx.core.session_post import PostProcessing
from ansys.cfx.core.session_pre import PreProcessing
from ansys.cfx.core.utils.cfx_version import get_version_for_file_name


@pytest.mark.codegen_required
def test_allapigen_files_pre(pypre: PreProcessing):
    version = get_version_for_file_name(session=pypre)
    importlib.import_module(f"ansys.cfx.core.generated.cfx_version_{version}")
    importlib.import_module(
        f"ansys.cfx.core.generated.{flobject.to_python_name(pypre.get_name())}.settings_{version}"
    )


@pytest.mark.codegen_required
def test_allapigen_files_post(pypost: PostProcessing):
    version = get_version_for_file_name(session=pypost)
    importlib.import_module(f"ansys.cfx.core.generated.cfx_version_{version}")
    importlib.import_module(
        f"ansys.cfx.core.generated.{flobject.to_python_name(pypost.get_name())}.settings_{version}"
    )
