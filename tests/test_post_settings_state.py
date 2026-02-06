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

from ansys.cfx.core.session_post import PostProcessing
from ansys.cfx.core.utils.cfx_version import CFXVersion


def test_get_var(pypost: PostProcessing, pytestconfig, capsys):
    """Test for getting values from the CFD-Post engine.

    The test includes systematic coverage of all the parameter types used by CFD-Post,
    plus related tests for object state."""

    # Load the file twice so that we have multiple domains
    # PostProcessing doesn't support multifile=append, so do it via CCL submission
    pypost.file.load_results(
        file_name=f"{pytestconfig.test_data_directory_path}/data/StaticMixer.def"
    )
    pypost.execute_ccl(
        f">load filename={pytestconfig.test_data_directory_path}/data/StaticMixer.def, "
        "multifile=append"
    )
    case_names = pypost.results.data_reader.case.get_object_names()
    assert case_names == ["Case StaticMixer", "Case StaticMixer 1"]

    # Set up some new objects needed to expose parameters of each type
    pypost.results.plane["Plane 1"] = {}
    plane = pypost.results.plane["Plane 1"]
    plane.suspend()
    plane.option = "ZX Plane"
    plane.y = "0.5 [m]"
    plane.plane_type = "Slice"
    plane.colour_mode = "Variable"
    plane.colour_variable = "X"
    plane.draw_contours = True
    plane.unsuspend()

    # The following types are not used by CFD-Post, or not used by user-settable parameters in
    # CFD-Post: Integer Expression, Integer List, Logical List, Real Triplet

    # Integer param
    num_contours = plane.number_of_contours()
    assert type(num_contours) is int
    assert num_contours == 11

    # Logical param
    specular_lighting = plane.specular_lighting()
    assert type(specular_lighting) is bool
    assert specular_lighting == True

    # Real param
    y_val = plane.y()
    assert type(y_val) is str
    assert y_val == "0.5 [m]"

    # Real List param
    plane.option = "Point and Normal"
    plane.point = "1.0 [m], 2.0 [m], 3.0 [m]"
    plane_point = plane.point()
    assert type(plane_point) is list
    assert type(plane_point[0]) is str
    assert plane_point == ["1.0 [m]", "2.0 [m]", "3.0 [m]"]

    # String param
    # Deliberately uses get_state() to test the direct function call
    plane_type = plane.plane_type.get_state()
    assert type(plane_type) is str
    assert plane_type == "Slice"

    # String List param
    domain_list = plane.domain_list()
    assert type(domain_list) is list
    assert type(domain_list[0]) is str
    assert domain_list == ["All Domains"]
    plane.domain_list = "All StaticMixer Domains, All StaticMixer 1 Domains"
    domain_list = plane.domain_list()
    assert type(domain_list) is list
    assert type(domain_list[0]) is str
    assert domain_list == ["All StaticMixer Domains", "All StaticMixer 1 Domains"]

    # Simple object containing parameters of all types and nested object
    plane.object_view_transform.rotation_angle = "1 [rad]"
    plane.number_of_contours = 15

    plane_state = pypost.results.plane()
    assert type(plane_state) is dict
    if pypost.get_cfx_version() > CFXVersion.v252:
        assert plane_state == {
            "Plane 1": {
                "colour_mode": "Variable",
                "colour_variable": "X",
                "domain_list": ["All StaticMixer Domains", "All StaticMixer 1 Domains"],
                "draw_contours": True,
                "number_of_contours": 15,
                "option": "Point and Normal",
                "plane_type": "Slice",
                "point": [
                    "1.0 [m]",
                    "2.0 [m]",
                    "3.0 [m]",
                ],
                "y": "0.5 [m]",
                "object_view_transform": {"rotation_angle": "1 [rad]"},
            }
        }
    else:
        assert plane_state == {
            "Plane 1": {
                "colour_mode": "Variable",
                "colour_variable": "X",
                "domain_list": ["All StaticMixer Domains", "All StaticMixer 1 Domains"],
                "draw_contours": True,
                "number_of_contours": 15,
                "option": "Point and Normal",
                "plane_type": "Slice",
                "point": "1.0 [m], 2.0 [m], 3.0 [m]",
                "y": "0.5 [m]",
                "object_view_transform": {"rotation_angle": "1 [rad]"},
            }
        }

    plane.print_state()
    captured = capsys.readouterr()
    if pypost.get_cfx_version() > CFXVersion.v252:
        assert (
            "\n"
            "colour_mode : Variable\n"
            "colour_variable : X\n"
            "domain_list : \n"
            "  0 : All StaticMixer Domains\n"
            "  1 : All StaticMixer 1 Domains\n"
            "draw_contours : True\n"
            "number_of_contours : 15\n"
            "option : Point and Normal\n"
            "plane_type : Slice\n"
            "point : \n"
            "  0 : 1.0 [m]\n"
            "  1 : 2.0 [m]\n"
            "  2 : 3.0 [m]\n"
            "y : 0.5 [m]\n"
            "object_view_transform : \n"
            "  rotation_angle : 1 [rad]\n" == captured.out
        )
    else:
        assert (
            "\n"
            "colour_mode : Variable\n"
            "colour_variable : X\n"
            "domain_list : \n"
            "  0 : All StaticMixer Domains\n"
            "  1 : All StaticMixer 1 Domains\n"
            "draw_contours : True\n"
            "number_of_contours : 15\n"
            "option : Point and Normal\n"
            "plane_type : Slice\n"
            "point : 1.0 [m], 2.0 [m], 3.0 [m]\n"
            "y : 0.5 [m]\n"
            "object_view_transform : \n"
            "  rotation_angle : 1 [rad]\n" == captured.out
        )

    plane.option.print_state()
    captured = capsys.readouterr()
    assert "Point and Normal\n" == captured.out


def test_named_objects(pypost: PostProcessing, pytestconfig):
    """Test for the handling of named objects when connected to the CFD-Post engine."""

    pypost.file.load_results(
        file_name=f"{pytestconfig.test_data_directory_path}/data/StaticMixer.def"
    )

    # Create from default
    pypost.results.plane["Plane 1"] = {}
    plane1 = pypost.results.plane["Plane 1"]
    plane1.option = "ZX Plane"
    plane1.y = "1 [m]"
    plane1.object_view_transform.rotation_angle = "1 [rad]"

    # Create from state
    plane_state = plane1()
    plane_state["y"] = "2 [m]"
    plane_state["object_view_transform"]["rotation_angle"] = "2 [rad]"
    pypost.results.plane["Plane 2"] = plane_state

    assert pypost.results.plane["Plane 2"]() == plane_state
    assert pypost.results.plane.get_object_names() == ["Plane 1", "Plane 2"]

    # Create using the create function
    pypost.results.plane.create(name="Plane 3")
    assert pypost.results.plane.get_object_names() == [
        "Plane 1",
        "Plane 2",
        "Plane 3",
    ]
    try:
        pypost.results.plane.create(name="Plane 3")
    except RuntimeError as e:
        assert str(e) == "Object 'Plane 3' of type 'PLANE' already exists."
    else:
        assert False, "Expected RuntimeError"

    # Rename tests
    pypost.results.plane.rename(old="Plane 2", new="Plane New")
    assert pypost.results.plane.get_object_names() == [
        "Plane 1",
        "Plane 3",
        "Plane New",
    ]
    assert pypost.results.plane["Plane New"].y() == "2 [m]"

    try:
        pypost.results.plane.rename(old="Plane 2", new="Plane Bad")
    except RuntimeError as e:
        assert str(e) == "Object '/PLANE:Plane 2' does not exist."
    else:
        assert False, "Expected RuntimeError"

    try:
        pypost.results.plane.rename(old="Plane 1", new="Plane New")
    except RuntimeError as e:
        assert str(e) == "Object '/PLANE:Plane New' already exists."
    else:
        assert False, "Expected RuntimeError"

    # Delete tests
    del pypost.results.plane["Plane 3"]
    assert pypost.results.plane.get_object_names() == ["Plane 1", "Plane New"]
    if pypost.get_cfx_version() > CFXVersion.v252:
        try:
            del pypost.results.plane["Plane 3"]
        except RuntimeError as e:
            assert str(e) == "Object '/PLANE:Plane 3' does not exist."
        else:
            assert False, "Expected RuntimeError"

    # Create object invalid in RULES
    try:
        pypost.results.bad_plane["Plane 1"] = {}
    except AttributeError as e:
        msg = (
            "'results' object has no attribute 'bad_plane'.\n"
            "The most similar names are: plane, clip_plane."
        )
        assert str(e) == msg
    else:
        assert False, "Expected AttributeError"


def test_dynamic_parameters(pypost: PostProcessing, pytestconfig, capsys):
    """Test for the handling of dynamic parameters when connected to the CFD-Post engine.

    The only object containing dynamic parameters in CFD-Post is the EXPRESSIONS object."""

    pypost.file.load_results(
        file_name=f"{pytestconfig.test_data_directory_path}/data/StaticMixer.def"
    )

    expr = pypost.results.library.cel.expressions

    expr.create("InletTemp")
    if pypost.get_cfx_version() > CFXVersion.v252:
        assert expr["InletTemp"]() == {"definition": "0"}

    ccl_string = (
        "LIBRARY:\n"
        "  CEL:\n"
        "    EXPRESSIONS:\n"
        "      Accumulated Time Step = -1\n"
        "      Current Phase Position = 0\n"
        "      Current Time Step = -1\n"
        "      InletTemp = 0\n"
        "      Phase = Current Phase Position\n"
        "      Reference Pressure = 1 [atm]\n"
        "      Sequence Step = -1\n"
        "      Time = 0 [s]\n"
        "      atstep = Accumulated Time Step\n"
        "      ctstep = Current Time Step\n"
        "      sstep = Sequence Step\n"
        "      t = Time\n"
        "    END\n"
        "  END\n"
        "END\n"
    )
    assert expr.list_properties() == ccl_string

    expr["InletTemp"].definition = "330 [K]"
    expr["OutletTemp"] = {"definition": "270 [K]"}
    expr["AverageTemp"] = {"definition": "(InletTemp + OutletTemp)/2"}
    assert expr["AverageTemp"].evaluate() == "300 [K]"

    assert expr.list() == [
        "Accumulated Time Step",
        "AverageTemp",
        "Current Phase Position",
        "Current Time Step",
        "InletTemp",
        "OutletTemp",
        "Phase",
        "Reference Pressure",
        "Sequence Step",
        "Time",
        "atstep",
        "ctstep",
        "sstep",
        "t",
    ]

    assert expr.get_object_names() == [
        "Accumulated Time Step",
        "AverageTemp",
        "Current Phase Position",
        "Current Time Step",
        "InletTemp",
        "OutletTemp",
        "Phase",
        "Reference Pressure",
        "Sequence Step",
        "Time",
        "atstep",
        "ctstep",
        "sstep",
        "t",
    ]

    state = {
        "Accumulated Time Step": {"definition": "-1"},
        "AverageTemp": {"definition": "(InletTemp + OutletTemp)/2"},
        "Current Phase Position": {"definition": "0"},
        "Current Time Step": {"definition": "-1"},
        "InletTemp": {"definition": "330 [K]"},
        "OutletTemp": {"definition": "270 [K]"},
        "Phase": {"definition": "Current Phase Position"},
        "Reference Pressure": {"definition": "1 [atm]"},
        "Sequence Step": {"definition": "-1"},
        "Time": {"definition": "0 [s]"},
        "atstep": {"definition": "Accumulated Time Step"},
        "ctstep": {"definition": "Current Time Step"},
        "sstep": {"definition": "Sequence Step"},
        "t": {"definition": "Time"},
    }
    assert expr() == state
    assert expr.get_state() == state

    expr.print_state()
    captured = capsys.readouterr()
    msg = (
        "\n"
        "Accumulated Time Step : \n"
        "  definition : -1\n"
        "AverageTemp : \n"
        "  definition : (InletTemp + OutletTemp)/2\n"
        "Current Phase Position : \n"
        "  definition : 0\n"
        "Current Time Step : \n"
        "  definition : -1\n"
        "InletTemp : \n"
        "  definition : 330 [K]\n"
        "OutletTemp : \n"
        "  definition : 270 [K]\n"
        "Phase : \n"
        "  definition : Current Phase Position\n"
        "Reference Pressure : \n"
        "  definition : 1 [atm]\n"
        "Sequence Step : \n"
        "  definition : -1\n"
        "Time : \n"
        "  definition : 0 [s]\n"
        "atstep : \n"
        "  definition : Accumulated Time Step\n"
        "ctstep : \n"
        "  definition : Current Time Step\n"
        "sstep : \n"
        "  definition : Sequence Step\n"
        "t : \n"
        "  definition : Time\n"
    )
    assert msg == captured.out

    if pypost.get_cfx_version() > CFXVersion.v252:
        try:
            expr.create(name="OutletTemp")
        except RuntimeError as e:
            assert str(e) == "Parameter 'OutletTemp' for object 'EXPRESSIONS' already exists."
        else:
            assert False, "Expected RuntimeError"

    # Rename tests
    expr.rename(old="AverageTemp", new="NewAverageTemp")
    assert expr.get_object_names() == [
        "Accumulated Time Step",
        "Current Phase Position",
        "Current Time Step",
        "InletTemp",
        "NewAverageTemp",
        "OutletTemp",
        "Phase",
        "Reference Pressure",
        "Sequence Step",
        "Time",
        "atstep",
        "ctstep",
        "sstep",
        "t",
    ]
    assert expr["NewAverageTemp"].definition() == "(InletTemp + OutletTemp)/2"
    try:
        expr.rename(old="AverageTemp", new="NewAverageTemp2")
    except RuntimeError as e:
        assert str(e) == "Parameter 'AverageTemp' for object 'EXPRESSIONS' does not exist."
    else:
        assert False, "Expected RuntimeError"
    try:
        expr.rename(old="NewAverageTemp", new="OutletTemp")
    except RuntimeError as e:
        if pypost.get_cfx_version() > CFXVersion.v252:
            assert str(e) == "Parameter 'OutletTemp' for object 'EXPRESSIONS' already exists."
        else:
            assert str(e) == "Parameter 'OutletTemp' for object 'EXPRESSIONS' already exist."
    else:
        assert False, "Expected RuntimeError"

    # Duplicate tests
    expr.duplicate(old="OutletTemp", new="OutletTempDup")
    assert expr.get_object_names() == [
        "Accumulated Time Step",
        "Current Phase Position",
        "Current Time Step",
        "InletTemp",
        "NewAverageTemp",
        "OutletTemp",
        "OutletTempDup",
        "Phase",
        "Reference Pressure",
        "Sequence Step",
        "Time",
        "atstep",
        "ctstep",
        "sstep",
        "t",
    ]
    assert expr["OutletTempDup"].definition() == "270 [K]"
    try:
        expr.duplicate(old="AverageTemp", new="NewAverageTemp2")
    except RuntimeError as e:
        assert str(e) == "Parameter 'AverageTemp' for object 'EXPRESSIONS' does not exist."
    else:
        assert False, "Expected RuntimeError"
    try:
        expr.duplicate(old="OutletTemp", new="OutletTempDup")
    except RuntimeError as e:
        if pypost.get_cfx_version() > CFXVersion.v252:
            assert str(e) == "Parameter 'OutletTempDup' for object 'EXPRESSIONS' already exists."
        else:
            assert str(e) == "Parameter 'OutletTempDup' for object 'EXPRESSIONS' already exist."
    else:
        assert False, "Expected RuntimeError"

    # Delete tests
    # "del" isn't working for dynamic parameters in 25.2
    if pypost.get_cfx_version() > CFXVersion.v252:
        del expr["OutletTemp"]
        assert expr.get_object_names() == [
            "Accumulated Time Step",
            "Current Phase Position",
            "Current Time Step",
            "InletTemp",
            "NewAverageTemp",
            "OutletTempDup",
            "Phase",
            "Reference Pressure",
            "Sequence Step",
            "Time",
            "atstep",
            "ctstep",
            "sstep",
            "t",
        ]
        try:
            del expr["OutletTemp"]
        except RuntimeError as e:
            assert str(e) == "Parameter 'OutletTemp' for object 'EXPRESSIONS' does not exist."
        else:
            assert False, "Expected RuntimeError"
        expr["OutletTempDup"].definition = " "
        assert expr.get_object_names() == [
            "Accumulated Time Step",
            "Current Phase Position",
            "Current Time Step",
            "InletTemp",
            "NewAverageTemp",
            "Phase",
            "Reference Pressure",
            "Sequence Step",
            "Time",
            "atstep",
            "ctstep",
            "sstep",
            "t",
        ]
        expr["NewAverageTemp"].definition = None
        assert expr.get_object_names() == [
            "Accumulated Time Step",
            "Current Phase Position",
            "Current Time Step",
            "InletTemp",
            "Phase",
            "Reference Pressure",
            "Sequence Step",
            "Time",
            "atstep",
            "ctstep",
            "sstep",
            "t",
        ]
    else:
        expr["OutletTemp"].definition = " "
        expr["OutletTempDup"].definition = " "
        expr["NewAverageTemp"].definition = " "

    # Tests for functions which are run on an individual expression
    expr["InletTemp"].duplicate(new="InletTempDup")
    assert expr.get_object_names() == [
        "Accumulated Time Step",
        "Current Phase Position",
        "Current Time Step",
        "InletTemp",
        "InletTempDup",
        "Phase",
        "Reference Pressure",
        "Sequence Step",
        "Time",
        "atstep",
        "ctstep",
        "sstep",
        "t",
    ]
    assert expr["InletTempDup"].definition() == "330 [K]"
    try:
        expr["InletTemp"].duplicate(new="InletTempDup")
    except RuntimeError as e:
        if pypost.get_cfx_version() > CFXVersion.v252:
            assert str(e) == "Parameter 'InletTempDup' for object 'EXPRESSIONS' already exists."
        else:
            assert str(e) == "Parameter 'InletTempDup' for object 'EXPRESSIONS' already exist."
    else:
        assert False, "Expected RuntimeError"

    if pypost.get_cfx_version() > CFXVersion.v252:
        assert expr["InletTemp"]() == {"definition": "330 [K]"}
    expr["InletTemp"].definition.print_state()
    captured = capsys.readouterr()
    assert "330 [K]\n" == captured.out
    expr["InletTemp"].duplicate(new="InletTempDup2")
    assert expr.get_object_names() == [
        "Accumulated Time Step",
        "Current Phase Position",
        "Current Time Step",
        "InletTemp",
        "InletTempDup",
        "InletTempDup2",
        "Phase",
        "Reference Pressure",
        "Sequence Step",
        "Time",
        "atstep",
        "ctstep",
        "sstep",
        "t",
    ]
    if pypost.get_cfx_version() > CFXVersion.v252:
        assert expr["InletTempDup2"]() == {"definition": "330 [K]"}
        expr["InletTempDup2"].rename("InletTemp2")
        assert expr.get_object_names() == [
            "Accumulated Time Step",
            "Current Phase Position",
            "Current Time Step",
            "InletTemp",
            "InletTemp2",
            "InletTempDup",
            "Phase",
            "Reference Pressure",
            "Sequence Step",
            "Time",
            "atstep",
            "ctstep",
            "sstep",
            "t",
        ]

        try:
            expr["InletTemp2"].rename("InletTempDup")
        except RuntimeError as e:
            assert str(e) == "Parameter 'InletTempDup' for object 'EXPRESSIONS' already exists."
        else:
            assert False, "Expected RuntimeError"
    else:
        # Rename doesn't work in release 25.2, but we need to do the equivalent for the rest of the
        # test to complete successfully
        expr["InletTemp2"] = {"definition": "440 [K]"}
        expr["InletTempDup2"].definition = " "

    try:
        expr["InletTemp2"].set_state("440 [K]")
    except RuntimeError as e:
        if pypost.get_cfx_version() > CFXVersion.v252:
            msg = (
                "Setting a value '440 [K]' for the object '/LIBRARY/CEL/EXPRESSIONS:InletTemp2' is "
                "not allowed. Set the 'definition' parameter within the object instead."
            )
        else:
            msg = "DataCCLObject::setValue::Parameter 'EXPRESSIONS' is not recognized on object 'CEL'."
        assert str(e) == msg
    else:
        assert False, "Expected RuntimeError"
    expr["InletTemp2"].definition.set_state("440 [K]")
    ccl_string = (
        "LIBRARY:\n"
        "  CEL:\n"
        "    EXPRESSIONS:\n"
        "      Accumulated Time Step = -1\n"
        "      Current Phase Position = 0\n"
        "      Current Time Step = -1\n"
        "      InletTemp = 330 [K]\n"
        "      InletTemp2 = 440 [K]\n"
        "      InletTempDup = 330 [K]\n"
        "      Phase = Current Phase Position\n"
        "      Reference Pressure = 1 [atm]\n"
        "      Sequence Step = -1\n"
        "      Time = 0 [s]\n"
        "      atstep = Accumulated Time Step\n"
        "      ctstep = Current Time Step\n"
        "      sstep = Sequence Step\n"
        "      t = Time\n"
        "    END\n"
        "  END\n"
        "END\n"
    )
    assert expr.list_properties() == ccl_string

    if pypost.get_cfx_version() > CFXVersion.v252:
        assert expr.get_object_names() == [
            "Accumulated Time Step",
            "Current Phase Position",
            "Current Time Step",
            "InletTemp",
            "InletTemp2",
            "InletTempDup",
            "Phase",
            "Reference Pressure",
            "Sequence Step",
            "Time",
            "atstep",
            "ctstep",
            "sstep",
            "t",
        ]
        expr.clear()
        assert expr.get_object_names() == []
        ccl_string = "LIBRARY:\n" "  CEL:\n" "    EXPRESSIONS:\n" "    END\n" "  END\n" "END\n"
        assert expr.list_properties() == ccl_string


def test_set_var(pypost: PostProcessing, pytestconfig, capsys):
    """Test for setting parameter values and state.

    The test includes systematic coverage of all the parameter types used by CFD-Post,
    plus related tests for object state."""

    # Load the file twice so that we have multiple domains
    # PostProcessing doesn't support multifile=append, so do it via CCL submission
    pypost.file.load_results(
        file_name=f"{pytestconfig.test_data_directory_path}/data/StaticMixer.def"
    )
    pypost.execute_ccl(
        f">load filename={pytestconfig.test_data_directory_path}/data/StaticMixer.def, "
        "multifile=append"
    )

    # Initial setup
    pypost.results.plane["Plane 1"] = {}
    plane = pypost.results.plane["Plane 1"]
    plane.suspend()
    plane.option = "ZX Plane"
    plane.y = "0.5 [m]"
    plane.plane_type = "Slice"
    plane.colour_mode = "Variable"
    plane.colour_variable = "X"
    plane.draw_contours = True
    plane.unsuspend()

    # Integer param
    plane.number_of_contours = 17
    assert plane.number_of_contours() == 17
    plane.number_of_contours = "27"
    assert plane.number_of_contours() == 27
    for invalid_value, err_str in [
        ("NotAnExpression", "NotAnExpression"),
        (False, "False"),
        (6.3, "6.300000"),
        ([6, 7, 8], "6,7,8"),
    ]:
        try:
            plane.number_of_contours = invalid_value
        except RuntimeError as e:
            assert str(e) == (
                "CCLAPI::validateCCLData::CCL validation failed with message:\n"
                f"Error: Parameter /PLANE:Plane 1/Number of Contours = {err_str} must be "
                "type Integer\n"
            )
        else:
            assert False, f"Expected RuntimeError for {invalid_value}"

    # Logical param
    assert plane.specular_lighting() == True
    for value, result in [(False, False), (77, True), (6.3, True)]:
        plane.specular_lighting = value
        assert plane.specular_lighting() == result
    for invalid_value, err_str in [("NotAnExpression", "NotAnExpression"), ([6, 7, 8], "6,7,8")]:
        try:
            plane.specular_lighting = invalid_value
        except RuntimeError as e:
            assert str(e) == (
                "CCLAPI::validateCCLData::CCL validation failed with message:\n"
                f"Error: Parameter '/PLANE:Plane 1/Specular Lighting = {err_str}' must be "
                "type Logical\n"
            )
        else:
            assert False, f"Expected RuntimeError for {invalid_value}"

    # Real param
    pypost.results.library.cel.expressions["MyExpr"] = {"definition": "3.3 [m]"}
    for value, result in [
        ("4.4 [m]", "4.4 [m]"),
        (5.9, "5.900000"),
        ("77", "77"),
        ("MyExpr", "MyExpr"),
    ]:
        plane.y = value
        assert plane.y() == result
    invalid_value = "4.4 [K]"
    try:
        plane.y = invalid_value
    except RuntimeError as e:
        assert str(e) == "Quantity::convertTo::Unable to convert units from 'K' to 'm'."
    else:
        assert False, f"Expected RuntimeError for {invalid_value}"
    for invalid_value, err_str in [("MyBadExpr", "MyBadExpr"), (False, "False")]:
        try:
            plane.y = invalid_value
        except RuntimeError as e:
            assert str(e) == (
                "ExpressionEvaluator::geniEvalSingle::The following unrecognised name was "
                f"referenced: {err_str}."
            )
        else:
            assert False, f"Expected RuntimeError for {invalid_value}"
    invalid_value = [6, 7, 8]
    try:
        plane.y = invalid_value
    except RuntimeError as e:
        assert str(e) == (
            "ExpressionEvaluator::geniEvalSingle::Syntax error detected in the expression "
            "assigned to 'Y'.\n"
            "Successfully read 1 characters:\n\t6\nthen error detected at:\n\t,7,8\n"
            "Details - Invalid text after valid expression.\n"
        )
    else:
        assert False, f"Expected RuntimeError for {invalid_value}"

    # Real List param
    plane.option = "Point and Normal"
    plane.point = "1.0 [m], 2.0 [m], 3.0 [m]"
    for value, result in [
        ("4.4 [m], 2*5.5 [m], 6.6 [m]", ["4.4 [m]", "2*5.5 [m]", "6.6 [m]"]),
        (
            "4.4 [m], 2*5.5 [m], 6.6 [m], 7.7 [m]",
            [
                "4.4 [m]",
                "2*5.5 [m]",
                "6.6 [m]",
                "7.7 [m]",
            ],
        ),
    ]:
        plane.point = value
        assert plane.point() == result
    invalid_value = "4.4 [s], 2*5.5 [K], 6.6 [s]"
    try:
        plane.point = invalid_value
    except RuntimeError as e:
        assert str(e) == "Quantity::convertTo::Unable to convert units from 's' to 'm'."
    else:
        assert False, f"Expected RuntimeError for {invalid_value}"
    for invalid_value, err_str in [("MyBadExpr", "MyBadExpr"), (False, "False")]:
        try:
            plane.point = invalid_value
        except RuntimeError as e:
            assert (
                str(e)
                == f"ExpressionEvaluator::geniEvalSingle::The following unrecognised name was referenced: {err_str}."
            )
        else:
            assert False, f"Expected RuntimeError for {invalid_value}"
    for invalid_value in [
        5.9,
        [77, 99],
        "MyExpr",
    ]:
        try:
            plane.point = invalid_value
        except RuntimeError as e:
            assert (
                str(e)
                == "PlaneCCLObject::processParameters::Parameter 'Point' must be defined by 3 float values."
            )
        else:
            assert False, f"Expected RuntimeError for {invalid_value}"

    # String param without allowed values
    plane.texture_file = "MyFile.jpg"
    for value, result in [
        ("A.txt", "A.txt"),
        ("A.txt # comment", "A.txt"),
        ("A.txt ! bad char", "A.txt ! bad char"),
        (5.9, "5.900000"),
        (False, "False"),
        ([77, 88], "77,88"),
    ]:
        plane.texture_file = value
        assert plane.texture_file() == result

    # String param with allowed values
    plane.option = "Point and Normal"
    # The error here is unexpected
    for invalid_value, err_str in [(5.9, "float"), (False, "bool")]:
        try:
            plane.option = invalid_value
        except TypeError as e:
            assert str(e) == f"'{err_str}' object is not iterable"
        else:
            assert False, f"Expected TypeError for {invalid_value}"
    for invalid_value in ["BAD TYPE", [77, 88]]:
        try:
            plane.option = invalid_value
        except ValueError as e:
            assert (
                str(e) == f"'option' has no attribute '{invalid_value}'.\n"
                "The allowed values are: ['Point and Normal', 'Three Points', 'XY Plane', 'YZ Plane', 'ZX Plane']."
            )
        else:
            assert False, f"Expected ValueError for {invalid_value}"

    # String List param without allowed values
    pypost.results.report.report_properties.keywords = "Word1, Word2"
    for value, result in [
        ("A, B", ["A", "B"]),
        ("A # comment", ["A"]),
        (["A # comment", "B # another comment"], ["A"]),
        ("A ! bad char", ["A ! bad char"]),
        (5.9, ["5.900000"]),
        (False, ["False"]),
        ([77, 88], ["77", "88"]),
    ]:
        pypost.results.report.report_properties.keywords = value
        assert pypost.results.report.report_properties.keywords() == result

    # String List param with allowed values
    pypost.results.export.export_type = "External Data"
    pypost.results.export.external_export_data = "Temperature, Heat Flow"
    assert pypost.results.export.external_export_data() == ["Temperature", "Heat Flow"]
    pypost.results.export.external_export_data = ["Heat Flow", "HTC and Wall Adjacent Temperature"]
    assert pypost.results.export.external_export_data() == [
        "Heat Flow",
        "HTC and Wall Adjacent Temperature",
    ]
    # The error here is unexpected
    for invalid_value, err_str in [(5.9, "float"), (False, "bool")]:
        try:
            pypost.results.export.external_export_data = invalid_value
        except TypeError as e:
            assert str(e) == f"'{err_str}' object is not iterable"
        else:
            assert False, f"Expected TypeError for {invalid_value}"
    for invalid_value in ["BAD TYPE", [77, 88]]:
        try:
            pypost.results.export.external_export_data = invalid_value
        except ValueError as e:
            assert (
                f"'external_export_data' has no attribute '{invalid_value}'.\n"
                "The allowed values are: ['HTC and Wall Adjacent Temperature', 'Heat Flow', "
                "'None', 'Temperature']."
            ) == str(e)
        else:
            assert False, f"Expected ValueError for {invalid_value}"

    # Set value for an object. This is an error.
    if pypost.get_cfx_version() > CFXVersion.v252:
        try:
            pypost.results.hardcopy = "MyExpr2"
        except RuntimeError as e:
            assert str(e) == ("Invalid parameter path '/HARDCOPY'.")
        else:
            assert False, f"Expected RuntimeError"

    # Tests for set_state

    plane_state = {
        "apply_instancing_transform": True,
        "colour_map": "Default Colour Map",
        "colour_mode": "Variable",
        "colour_scale": "Linear",
        "colour_variable": "Z",
        "domain_list": ["/DOMAIN GROUP:All Domains"],
        "draw_contours": True,
        "draw_faces": True,
        "draw_lines": False,
        "instancing_transform": "/DEFAULT INSTANCE TRANSFORM:Default Transform",
        "number_of_contours": 17,
        "option": "ZX Plane",
        "plane_bound": "None",
        "plane_type": "Slice",
        "range": "Global",
        "y": "1 [m]",
        "object_view_transform": {
            "apply_translation": True,
            "translation_vector": ["0 [m]", "-1 [m]", "0 [m]"],
        },
    }

    pypost.results.plane["Plane 2"] = {}
    plane2 = pypost.results.plane["Plane 2"]
    plane2.set_state(plane_state)
    if pypost.get_cfx_version() > CFXVersion.v252:
        assert plane_state == plane2.get_state()
        assert plane2.object_view_transform.translation_vector() == ["0 [m]", "-1 [m]", "0 [m]"]
    else:
        plane_state["object_view_transform"]["translation_vector"] = "0 [m],-1 [m],0 [m]"
        assert plane_state == plane2.get_state()

    plane_state["object_view_transform"]["translation_vector"] = "Bad Value"
    try:
        plane2.set_state(plane_state)
    except RuntimeError as e:
        assert str(e) == (
            "ExpressionEvaluator::geniEvalSingle::"
            "The following unrecognised name was referenced: Bad Value."
        )
    else:
        assert False, f"Expected RuntimeError"


def test_undefined_parameters(pypost: PostProcessing, pytestconfig):
    """Test for the handling of undefined parameters when connected to the CFD-Post engine."""

    pypost.file.load_results(
        file_name=f"{pytestconfig.test_data_directory_path}/data/StaticMixer.def"
    )

    # Initial setup
    pypost.results.plane["Plane 1"] = {}
    plane1 = pypost.results.plane["Plane 1"]
    plane1.option = "ZX Plane"
    plane1.plane_type = "Slice"

    # Try setting existing parameters to None
    try:
        plane1.option = None
    except TypeError as e:
        assert str(e) == "'NoneType' object is not iterable"
    try:
        plane1.z = None
    except TypeError as e:
        assert str(e) == "'NoneType' object is not iterable"

    # Undefined parameters due to creation of object where parameter has no default
    pypost.results.contour["Contour 1"] = {}
    contour1 = pypost.results.contour["Contour 1"]
    assert contour1.location_list() == None

    # Undefined parameters for "dynamic" parameters
    expr = pypost.results.library.cel.expressions
    expr.create("InletTemp")
    if pypost.get_cfx_version() > CFXVersion.v252:
        assert expr["InletTemp"]() == {"definition": "0"}
    ccl_string_zero = (
        "LIBRARY:\n"
        "  CEL:\n"
        "    EXPRESSIONS:\n"
        "      Accumulated Time Step = -1\n"
        "      Current Phase Position = 0\n"
        "      Current Time Step = -1\n"
        "      InletTemp = 0\n"
        "      Phase = Current Phase Position\n"
        "      Reference Pressure = 1 [atm]\n"
        "      Sequence Step = -1\n"
        "      Time = 0 [s]\n"
        "      atstep = Accumulated Time Step\n"
        "      ctstep = Current Time Step\n"
        "      sstep = Sequence Step\n"
        "      t = Time\n"
        "    END\n"
        "  END\n"
        "END\n"
    )
    assert expr.list_properties() == ccl_string_zero
    expr["InletTemp"].definition = "330 [K]"
    if pypost.get_cfx_version() > CFXVersion.v252:
        assert expr["InletTemp"]() == {"definition": "330 [K]"}
    ccl_string_330 = (
        "LIBRARY:\n"
        "  CEL:\n"
        "    EXPRESSIONS:\n"
        "      Accumulated Time Step = -1\n"
        "      Current Phase Position = 0\n"
        "      Current Time Step = -1\n"
        "      InletTemp = 330 [K]\n"
        "      Phase = Current Phase Position\n"
        "      Reference Pressure = 1 [atm]\n"
        "      Sequence Step = -1\n"
        "      Time = 0 [s]\n"
        "      atstep = Accumulated Time Step\n"
        "      ctstep = Current Time Step\n"
        "      sstep = Sequence Step\n"
        "      t = Time\n"
        "    END\n"
        "  END\n"
        "END\n"
    )
    assert expr.list_properties() == ccl_string_330
    expr["InletTemp"].definition = None
    if pypost.get_cfx_version() > CFXVersion.v252:
        try:
            val = expr["InletTemp"]
        except KeyError as e:
            assert (
                str(e) == "\"'expressions' has no attribute 'InletTemp'.\\n"
                'The most similar names are: sstep."'
            )
        else:
            assert False, "Expected KeyError"
        ccl_string = (
            "LIBRARY:\n"
            "  CEL:\n"
            "    EXPRESSIONS:\n"
            "      Accumulated Time Step = -1\n"
            "      Current Phase Position = 0\n"
            "      Current Time Step = -1\n"
            "      Phase = Current Phase Position\n"
            "      Reference Pressure = 1 [atm]\n"
            "      Sequence Step = -1\n"
            "      Time = 0 [s]\n"
            "      atstep = Accumulated Time Step\n"
            "      ctstep = Current Time Step\n"
            "      sstep = Sequence Step\n"
            "      t = Time\n"
            "    END\n"
            "  END\n"
            "END\n"
        )
        assert expr.list_properties() == ccl_string
    else:
        assert expr.list_properties() == ccl_string_330
