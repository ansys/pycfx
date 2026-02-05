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

from ansys.cfx.core.utils.cfx_version import AnsysVersionNotFound, CFXVersion


def test_examples():
    assert CFXVersion("25.2.0") == CFXVersion.v252
    assert CFXVersion.v252.number == 252
    assert CFXVersion.v252.awp_var == "AWP_ROOT252"
    assert CFXVersion.v252.name == "v252"
    assert CFXVersion.v252.value == "25.2.0"


def test_version_found():
    assert CFXVersion("25.2") == CFXVersion.v252
    assert CFXVersion(25.2) == CFXVersion.v252
    assert CFXVersion(252) == CFXVersion.v252


def test_version_not_found():
    with pytest.raises(AnsysVersionNotFound):
        CFXVersion("25.1.0")

    with pytest.raises(AnsysVersionNotFound):
        CFXVersion(22)


def test_get_latest_installed(helpers):
    helpers.mock_awp_vars()
    assert CFXVersion.get_latest_installed() == CFXVersion.current_release()


def test_gt():
    assert CFXVersion.v261 > CFXVersion.v252


def test_ge():
    assert CFXVersion.v261 >= CFXVersion.v252
    assert CFXVersion.v252 >= CFXVersion.v252


def test_lt():
    assert CFXVersion.v252 < CFXVersion.v261


def test_le():
    assert CFXVersion.v252 <= CFXVersion.v261
    assert CFXVersion.v252 <= CFXVersion.v252


def test_ne():
    assert CFXVersion.v252 != CFXVersion.v261


def test_eq():
    assert CFXVersion.v252 == CFXVersion.v252
    assert CFXVersion.v261 == CFXVersion.v261
