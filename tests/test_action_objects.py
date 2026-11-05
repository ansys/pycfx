# Copyright (C) 2023 - 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
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

from ansys.cfx.core.session_pre import PreProcessing
from ansys.cfx.core.utils.cfx_version import CFXVersion

def test_action_object(pypre: PreProcessing, pytestconfig):

    if pypre.get_cfx_version() < CFXVersion.v272:
        try:
            pypre.file.open_case.create("OpenCaseObject")
        except RuntimeError as e:
            assert str(e) == ("Failed to create action object 'OpenCaseObject'.\n"
                              "Command and query objects are only supported in Release 2027 R2 "
                              "and later.")
        else:
            assert False, "Expected RuntimeError"
        return

    assert pypre.file.open_case.get_object_names() == []
    pypre.file.open_case.create("OpenCaseObject")
    assert pypre.file.open_case.get_object_names() == ["OpenCaseObject"]

    state = pypre.file.open_case["OpenCaseObject"].get_state()
    assert state == {'file_name': '', 'recover_case_file': False, 'replace_flow_data': False}

    pypre.file.open_case["OpenCaseObject"].file_name = "TurboCase.cfx"
    state = pypre.file.open_case["OpenCaseObject"].get_state()
    assert state == {
        'file_name': 'TurboCase.cfx',
        'recover_case_file': False,
        'replace_flow_data': False,
    }

    pypre.file.open_case["OpenCaseObject"].recover_case_file = True
    state = pypre.file.open_case["OpenCaseObject"].get_state()
    assert state == {
        'file_name': 'TurboCase.cfx',
        'recover_case_file': True,
        'replace_flow_data': False,
    }

    file_name = pypre.file.open_case["OpenCaseObject"].file_name()
    assert file_name == "TurboCase.cfx"
    recover_case_file = pypre.file.open_case["OpenCaseObject"].recover_case_file()
    assert recover_case_file == True

    assert list(pypre.file.open_case.keys()) == ["OpenCaseObject"]
    assert list(pypre.file.open_case.values()) == [pypre.file.open_case["OpenCaseObject"]]
    assert len(pypre.file.open_case.items()) == 1
    for key, obj in pypre.file.open_case.items() :
        assert key == obj.obj_name
        assert obj.path == f"file/open_case/{key}"

    pypre.file.open_case.create("OpenCaseObject2")
    assert pypre.file.open_case.get_object_names() == ["OpenCaseObject", "OpenCaseObject2"]

    pypre.file.open_case.delete("OpenCaseObject")
    assert pypre.file.open_case.get_object_names() == ["OpenCaseObject2"]

    # Open a new case to allow for the creation of a new action object for a query
    pypre.file.new_case()

    solver_control = pypre.setup.flow["Flow Analysis 1"].solver_control
    solver_control.get_physics_messages.create("GetMessagesObject")
    state = solver_control.get_physics_messages['GetMessagesObject'].get_state()
    assert state == {'severity': ''}

    solver_control.get_physics_messages['GetMessagesObject'].severity = "Warning"
    state = solver_control.get_physics_messages['GetMessagesObject'].get_state()
    assert state == {'severity': 'Warning'}

    severity = solver_control.get_physics_messages['GetMessagesObject'].severity()
    assert severity == "Warning"
