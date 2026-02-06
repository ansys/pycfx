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

from ansys.cfx.core.utils.fldoc import docother


class MockSelf:
    def repr(self, obj):
        return repr(obj)

    def bold(self, text):
        return f"<b>{text}</b>"

    def indent(self, text):
        return "    " + text.replace("\n", "\n    ")


def test_docother_with_list():
    mock = MockSelf()
    obj = [1, 2, 3]
    name = "mylist"
    doc = "A simple list."
    result = docother(mock, obj, name=name, maxlen=40, doc=doc)
    assert "<b>mylist</b> =" in result
    assert "A simple list." in result
    assert "[1, 2, 3]" in result.replace("\n", "")


def test_docother_with_string():
    mock = MockSelf()
    obj = "hello"
    name = "greeting"
    doc = "A greeting string."
    result = docother(mock, obj, name=name, maxlen=20, doc=doc)
    assert "<b>greeting</b> =" in result
    assert "'hello'" in result
    assert "A greeting string." in result


def test_docother_with_long_repr():
    mock = MockSelf()
    obj = "x" * 100
    name = "longstr"
    result = docother(mock, obj, name=name, maxlen=20)
    assert result.endswith("...")
