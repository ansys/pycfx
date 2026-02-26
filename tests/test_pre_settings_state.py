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

from ansys.cfx.core.session_pre import PreProcessing
from ansys.cfx.core.utils.cfx_version import CFXVersion
import ansys.units as ansys_units


def test_get_var(pre_load_static_mixer_case: PreProcessing, capsys):
    """Test for getting values from the CFX-Pre engine.

    The test includes systematic coverage of all the parameter types used by CFX-Pre,
    plus related tests for object state."""

    pypre = pre_load_static_mixer_case

    in1 = pypre.setup.flow["Flow Analysis 1"].domain["Default Domain"].boundary["in1"]
    oc = pypre.setup.flow["Flow Analysis 1"].output_control
    sc = pypre.setup.flow["Flow Analysis 1"].solver_control

    # Set up some new objects needed to expose parameters of each type
    oc.backup_results["Backup Results 1"] = {}
    backup1 = oc.backup_results["Backup Results 1"]
    backup1.output_frequency.option = "Iteration List"
    backup1.output_frequency.iteration_list = [4, 6, 8]
    pypre.setup.library.user_location_definitions.user_line["User Line 1"] = {}
    user_line1 = pypre.setup.library.user_location_definitions.user_line["User Line 1"]
    user_line1.option = "Two Points"

    # Integer param
    max_iterations = sc.convergence_control.maximum_number_of_iterations()
    assert type(max_iterations) is int
    assert max_iterations == 100
    assert sc.convergence_control.maximum_number_of_iterations.state_with_units() == 100

    # Integer Expression param
    num_points = user_line1.number_of_points()
    if pypre.get_cfx_version() > CFXVersion.v252:
        assert type(num_points) is int
        assert num_points == 11
    else:
        assert type(num_points) is str
        assert num_points == "11"
    user_line1.number_of_points = "NumPoints"
    num_points = user_line1.number_of_points()
    assert type(num_points) is str
    assert num_points == "NumPoints"
    user_line1.number_of_points = 11

    # Integer List param
    iteration_lst = backup1.output_frequency.iteration_list()
    assert type(iteration_lst) is list
    assert type(iteration_lst[0]) is int
    assert iteration_lst == [4, 6, 8]

    # Logical param
    visibility_state = user_line1.visibility()
    assert type(visibility_state) is bool
    assert visibility_state == False

    # Real param
    inlet_vel = in1.boundary_conditions.mass_and_momentum.normal_speed()
    assert type(inlet_vel) is str
    assert inlet_vel == "2 [m s^-1]"
    try:
        val = in1.boundary_conditions.mass_and_momentum.normal_speed.state_with_units()
    except NotImplementedError as e:
        assert str(e) == "This function is not fully implemented."
    else:
        assert False, "Expected NotImplementedError"

    try:
        val = in1.boundary_conditions.mass_and_momentum.normal_speed.as_quantity()
    except NotImplementedError as e:
        assert str(e) == "This function is not fully implemented."
    else:
        assert False, "Expected NotImplementedError"

    # Real Triplet param
    point1 = user_line1.point_definition.point_1()
    assert type(point1) is list
    assert type(point1[0]) is str
    assert point1 == ["0.0[m]", "0.0[m]", "0.0[m]"]

    # Real List param
    physical_timescale = sc.convergence_control.physical_timescale()
    assert type(physical_timescale) is list
    assert type(physical_timescale[0]) is str
    assert physical_timescale == ["2 [s]"]
    sc.convergence_control.physical_timescale = "2*1[s], 5*2 [s], 10[s]"
    physical_timescale = sc.convergence_control.physical_timescale()
    assert type(physical_timescale) is list
    assert type(physical_timescale[0]) is str
    assert physical_timescale == ["2*1[s]", "5*2 [s]", "10[s]"]

    # String param
    # Deliberately uses get_state() to test the direct function call
    boundary_type = in1.boundary_type.get_state()
    assert type(boundary_type) is str
    assert boundary_type == "INLET"

    # String List param
    water_group = pypre.setup.library.material["Water"].material_group()
    assert type(water_group) is list
    assert type(water_group[0]) is str
    assert water_group == ["Water Data", "Constant Property Liquids"]

    # Simple object containing String parameters and nested object
    analysis_state = pypre.setup.flow["Flow Analysis 1"].analysis_type()
    assert type(analysis_state) is dict
    assert analysis_state == {
        "external_solver_coupling": {"option": "None"},
        "option": "Steady State",
    }

    # Object containing Integer Expression, Real Triplet and Logical parameters
    user_line_state = user_line1()
    assert type(user_line_state) is dict
    expected_user_line_state = {
        "number_of_points": 11,
        "option": "Two Points",
        "point_definition": {
            "coord_frame": "Coord 0",
            "option": "Cartesian Coordinates",
            "point_1": ["0.0[m]", "0.0[m]", "0.0[m]"],
            "point_2": ["0.0[m]", "0.0[m]", "0.0[m]"],
        },
        "visibility": False,
    }
    if pypre.get_cfx_version() < CFXVersion.v261:
        expected_user_line_state["number_of_points"] = "11"
        expected_user_line_state["point_definition"]["point_1"] = "0.0[m],0.0[m],0.0[m]"
        expected_user_line_state["point_definition"]["point_2"] = "0.0[m],0.0[m],0.0[m]"
    assert expected_user_line_state == user_line_state
    user_line1.number_of_points = "NumPoints"
    user_line_state = user_line1()
    assert type(user_line_state) is dict
    expected_user_line_state["number_of_points"] = "NumPoints"
    assert expected_user_line_state == user_line_state
    assert expected_user_line_state == user_line1.state_with_units()

    # Object containing Integer, Real List, Real and Logical parameters
    sc_state = sc()
    assert type(sc_state) is dict
    expected_sc_state = {
        "advection_scheme": {"option": "Upwind"},
        "convergence_control": {
            "maximum_number_of_iterations": 100,
            "minimum_number_of_iterations": 1,
            "physical_timescale": ["2*1[s]", "5*2 [s]", "10[s]"],
            "timescale_control": "Physical Timescale",
        },
        "convergence_criteria": {"residual_target": "1.E-4", "residual_type": "RMS"},
        "dynamic_model_control": {"global_dynamic_model_control": True},
        "interrupt_control": {
            "option": "Any Interrupt",
            "convergence_conditions": {"option": "Default Conditions"},
        },
        "turbulence_numerics": "First Order",
    }
    if pypre.get_cfx_version() < CFXVersion.v261:
        expected_sc_state["convergence_control"]["physical_timescale"] = "2*1[s], 5*2 [s], 10[s]"
    assert expected_sc_state == sc_state

    try:
        sc_state_with_units = sc.state_with_units()
    except NotImplementedError as e:
        assert str(e) == "This function is not fully implemented."
    else:
        assert False, "Expected NotImplementedError"

    # Object containing String List parameter
    water_state = pypre.setup.library.material["Water"]()
    assert type(water_state) is dict
    assert water_state["material_group"] == ["Water Data", "Constant Property Liquids"]

    # Object containing Integer List parameter
    backup1_state = backup1()
    assert type(backup1_state) is dict
    assert backup1_state == {
        "file_compression_level": "Default",
        "option": "Standard",
        "output_frequency": {
            "iteration_list": [4, 6, 8],
            "option": "Iteration List",
        },
    }

    # Named object
    try:
        in1.state_with_units()
    except NotImplementedError as e:
        assert str(e) == "This function is not fully implemented."
    else:
        assert False, "Expected NotImplementedError"

    # Non-existent named object
    try:
        pypre.setup.flow["Flow Analysis 1"].domain["Default Domain"].boundary["in3"].get_state()
    except KeyError as e:
        assert str(e) == (
            "\"'boundary' has no attribute 'in3'.\\nThe most similar names are: in2, in1.\""
        )
    else:
        assert False, "Expected KeyError"

    backup1.print_state()
    captured = capsys.readouterr()
    assert (
        "\n"
        "option : Standard\n"
        "file_compression_level : Default\n"
        "output_frequency : \n"
        "  option : Iteration List\n"
        "  iteration_list : \n"
        "    0 : 4\n"
        "    1 : 6\n"
        "    2 : 8\n" == captured.out
    )

    backup1.option.print_state()
    captured = capsys.readouterr()
    assert "Standard\n" == captured.out


def test_named_objects(pre_load_static_mixer_case: PreProcessing, capsys):
    """Test for the handling of named objects when connected to the CFX-Pre engine."""

    pypre = pre_load_static_mixer_case

    dom = pypre.setup.flow["Flow Analysis 1"].domain["Default Domain"]
    oc = pypre.setup.flow["Flow Analysis 1"].output_control

    # Create from default
    oc.backup_results["Backup Results 1"] = {}
    backup1 = oc.backup_results["Backup Results 1"]
    backup1.output_frequency.option = "Iteration List"
    backup1.output_frequency.iteration_list = "4,6,8"

    # Create from state
    backup_state = backup1()
    backup_state["output_frequency"]["iteration_list"] = [1, 3, 5]
    oc.backup_results["Backup Results 2"] = backup_state

    assert oc.backup_results["Backup Results 2"]() == backup_state
    assert oc.backup_results.get_object_names() == ["Backup Results 1", "Backup Results 2"]

    # Create using the create function
    oc.backup_results.create(name="Backup Results 3")
    assert oc.backup_results.get_object_names() == [
        "Backup Results 1",
        "Backup Results 2",
        "Backup Results 3",
    ]
    try:
        oc.backup_results.create(name="Backup Results 3")
    except RuntimeError as e:
        assert (
            str(e) == "Object '/FLOW:Flow Analysis 1/OUTPUT CONTROL/"
            "BACKUP RESULTS:Backup Results 3' already exists."
        )
    else:
        assert False, "Expected RuntimeError"

    # Rename tests
    oc.backup_results.rename(old="Backup Results 2", new="Backup Results Odd")
    assert oc.backup_results.get_object_names() == [
        "Backup Results 1",
        "Backup Results 3",
        "Backup Results Odd",
    ]
    assert oc.backup_results["Backup Results Odd"].output_frequency.iteration_list() == [
        1,
        3,
        5,
    ]
    try:
        oc.backup_results.rename(old="Backup Results 2", new="Backup Results Bad")
    except RuntimeError as e:
        assert (
            str(e) == "Object '/FLOW:Flow Analysis 1/OUTPUT CONTROL/"
            "BACKUP RESULTS:Backup Results 2' does not exist."
        )
    else:
        assert False, "Expected RuntimeError"

    try:
        oc.backup_results.rename(old="Backup Results 1", new="Backup Results Odd")
    except RuntimeError as e:
        assert (
            str(e) == "Object '/FLOW:Flow Analysis 1/OUTPUT CONTROL/"
            "BACKUP RESULTS:Backup Results Odd' already exists."
        )
    else:
        assert False, "Expected RuntimeError"

    # Delete tests
    del oc.backup_results["Backup Results 3"]
    assert oc.backup_results.get_object_names() == ["Backup Results 1", "Backup Results Odd"]
    try:
        del oc.backup_results["Backup Results 3"]
    except RuntimeError as e:
        assert (
            str(e) == "Object '/FLOW:Flow Analysis 1/OUTPUT CONTROL/"
            "BACKUP RESULTS:Backup Results 3' does not exist."
        )
    else:
        assert False, "Expected RuntimeError"

    # Create object invalid in physics
    try:
        dom.fluid_models.additional_variable["MyAV"] = {}
    except RuntimeError as e:
        if pypre.get_cfx_version() > CFXVersion.v252:
            assert (
                str(e) == "Object '/FLOW:Flow Analysis 1/DOMAIN:Default Domain/FLUID MODELS/"
                "ADDITIONAL VARIABLE:MyAV' was not created as it is not physically valid."
            )
        else:
            assert (
                str(e) == "Object '/FLOW:Flow Analysis 1/DOMAIN:Default Domain/FLUID MODELS/"
                "ADDITIONAL VARIABLE:MyAV' was not created."
            )
    else:
        assert False, "Expected RuntimeError"

    assert (
        not pypre.setup.flow["Flow Analysis 1"]
        .domain["Default Domain"]
        .fluid_models.additional_variable.user_creatable()
    )

    try:
        dom.fluid_models.additional_variable["MyAV"] = {}
    except RuntimeError as e:
        if pypre.get_cfx_version() > CFXVersion.v252:
            assert str(e) == (
                "Object '/FLOW:Flow Analysis 1/DOMAIN:Default Domain/FLUID MODELS/"
                "ADDITIONAL VARIABLE:MyAV' was not created as it is not physically valid."
            )
        else:
            assert str(e) == (
                "Object '/FLOW:Flow Analysis 1/DOMAIN:Default Domain/FLUID MODELS/"
                "ADDITIONAL VARIABLE:MyAV' was not created."
            )
    else:
        assert False, "Expected RuntimeError"

    # For 25.2 and 26.1 this does not give an error (but the setup will have physics errors).
    try:
        dom.fluid_models.additional_variable["MyAV"] = {"option": "Transport Equation"}
    except RuntimeError as e:
        if pypre.get_cfx_version() > CFXVersion.v261:
            assert str(e) == (
                "Parameter value 'Transport Equation' for parameter 'Option' in object "
                "'/FLOW:Flow Analysis 1/DOMAIN:Default Domain/FLUID MODELS/ADDITIONAL "
                "VARIABLE:MyAV' was not set. This may not be physically valid."
            )

    pypre.setup.library.additional_variable["MyAV"] = {}
    dom.fluid_models.additional_variable["MyAV"] = {}
    dom.boundary["in1"].boundary_conditions.additional_variable["MyAV"] = {}
    assert dom.boundary["in1"].boundary_conditions.additional_variable.get_object_names() == [
        "MyAV"
    ]

    try:
        dom.boundary["in1"].boundary_conditions.additional_variable["BadAVName"] = {}
    except RuntimeError as e:
        if pypre.get_cfx_version() > CFXVersion.v252:
            assert str(e) == (
                "Object '/FLOW:Flow Analysis 1/DOMAIN:Default Domain/BOUNDARY:in1/"
                "BOUNDARY CONDITIONS/ADDITIONAL VARIABLE:BadAVName' was not created as it is not "
                "physically valid."
            )
        else:
            assert str(e) == (
                "Object '/FLOW:Flow Analysis 1/DOMAIN:Default Domain/BOUNDARY:in1/"
                "BOUNDARY CONDITIONS/ADDITIONAL VARIABLE:BadAVName' was not created."
            )
    else:
        assert False, "Expected RuntimeError"

    try:
        dom.fluid_models.additional_variable["BadAVName"] = {}
    except RuntimeError as e:
        if pypre.get_cfx_version() > CFXVersion.v252:
            assert str(e) == (
                "Object '/FLOW:Flow Analysis 1/DOMAIN:Default Domain/FLUID MODELS/"
                "ADDITIONAL VARIABLE:BadAVName' was not created as it is not physically valid."
            )
        else:
            assert (
                str(e) == "Object '/FLOW:Flow Analysis 1/DOMAIN:Default Domain/FLUID MODELS/"
                "ADDITIONAL VARIABLE:BadAVName' was not created."
            )
    else:
        assert False, "Expected RuntimeError"

    if pypre.get_cfx_version() > CFXVersion.v252:
        # These errors and exceptions were not implemented for release 25.2.
        # Rename object action invalid in physics
        try:
            dom.boundary["in1"].boundary_conditions.additional_variable.rename(
                old="MyAV", new="MyAV2"
            )
        except RuntimeError as e:
            assert (
                str(e) == "Object '/FLOW:Flow Analysis 1/DOMAIN:Default Domain/BOUNDARY:in1/"
                "BOUNDARY CONDITIONS/ADDITIONAL VARIABLE:MyAV' was not renamed as this is not "
                "physically valid."
            )
        else:
            assert False, "Expected RuntimeError"

        # Delete object action invalid in physics
        try:
            del dom.boundary["in1"].boundary_conditions.additional_variable["MyAV"]
        except RuntimeError as e:
            assert (
                str(e) == "Deletion of object '/FLOW:Flow Analysis 1/DOMAIN:Default Domain/"
                "BOUNDARY:in1/BOUNDARY CONDITIONS/ADDITIONAL VARIABLE:MyAV' is not permitted."
            )
        else:
            assert False, "Expected RuntimeError"

    # Create object invalid in RULES
    try:
        dom.additional_variable["MyAV"] = {}
    except AttributeError as e:
        msg = (
            "'domain_child' object has no attribute 'additional_variable'.\n"
            "The most similar names are: injection_region."
        )
        assert str(e) == msg
    else:
        assert False, "Expected AttributeError"
    captured = capsys.readouterr()
    if pypre.get_cfx_version() > CFXVersion.v252:
        assert (
            captured.out == "\n"
            " additional_variable can be accessed from the following paths: \n\n"
            '    <session>.setup.flow["Flow Analysis 1"].domain["Default Domain"].'
            "fluid_models.additional_variable\n"
        )
    else:
        assert (
            captured.out == "\n"
            " additional_variable can be accessed from the following paths: \n\n"
            '    <session>.setup.flow["Flow Analysis 1"].domain["Default Domain"].'
            "initialisation.initial_conditions.additional_variable\n\n"
            " additional_variable can be accessed from the following paths: \n\n"
            '    <session>.setup.flow["Flow Analysis 1"].domain["Default Domain"].'
            "fluid_models.additional_variable\n"
        )

    # Named object functions

    # get_completer_info only considers commands and queries, and there are currently none for
    # named objects.
    assert (
        pypre.setup.flow["Flow Analysis 1"]
        .domain["Default Domain"]
        .boundary.get_completer_info(prefix="", excluded=["no_object"])
        == []
    )

    assert list(pypre.setup.flow["Flow Analysis 1"].domain["Default Domain"].boundary.keys()) == [
        "in1",
        "Default Domain Default",
        "in2",
        "out",
    ]

    del pypre.setup.flow["Flow Analysis 1"].domain["Default Domain"].boundary["in2"]
    assert [
        obj.obj_name
        for obj in pypre.setup.flow["Flow Analysis 1"].domain["Default Domain"].boundary.values()
    ] == [
        "in1",
        "Default Domain Default",
        "out",
    ]

    # Deleting the boundary via CCL forces flobject to have to re-sync
    pypre.execute_ccl("> delete /FLOW:Flow Analysis 1/DOMAIN:Default Domain/BOUNDARY:out")

    assert list(pypre.setup.flow["Flow Analysis 1"].domain["Default Domain"].boundary.keys()) == [
        "in1",
        "Default Domain Default",
    ]

    for key, obj in pypre.setup.flow["Flow Analysis 1"].domain["Default Domain"].boundary.items():
        assert key == obj.obj_name
        assert obj.path == f"setup/FLOW/Flow Analysis 1/DOMAIN/Default Domain/BOUNDARY/{key}"

    assert "in1" in pypre.setup.flow["Flow Analysis 1"].domain["Default Domain"].boundary
    assert "in2" not in pypre.setup.flow["Flow Analysis 1"].domain["Default Domain"].boundary
    assert len(pypre.setup.flow["Flow Analysis 1"].domain["Default Domain"].boundary) == 2

    obj_iter = iter(pypre.setup.flow["Flow Analysis 1"].domain["Default Domain"].boundary)
    assert next(obj_iter) == "in1"
    assert next(obj_iter) == "Default Domain Default"

    assert pypre.setup.flow["Flow Analysis 1"].domain["Default Domain"].boundary.user_creatable()

    assert dom.boundary.to_engine_keys("value") == "value"


def test_dynamic_parameters(pre_load_static_mixer_case: PreProcessing, capsys):
    """Test for the handling of dynamic parameters when connected to the CFX-Pre engine.

    The objects containing dynamic parameters in CFX-Pre are EXPRESSIONS, EXPERT PARAMETERS
    and USER."""

    pypre = pre_load_static_mixer_case

    expr = pypre.setup.library.cel.expressions

    expr.create("InletTemp")
    if pypre.get_cfx_version() > CFXVersion.v252:
        assert expr["InletTemp"]() == {"definition": "0"}
    ccl_string = (
        "LIBRARY:\n"
        "  CEL:\n"
        "    EXPRESSIONS:\n"
        "      InletTemp = 0\n"
        "    END\n"
        "  END\n"
        "END\n"
    )
    assert expr.list_properties() == ccl_string
    expr["InletTemp"].definition = "330 [K]"

    expr["OutletTemp"] = {"definition": "270 [K]"}
    expr["AverageTemp"] = {"definition": "(InletTemp + OutletTemp)/2"}

    assert expr["AverageTemp"].evaluate() == "300 [K]"

    ccl_string = (
        "LIBRARY:\n"
        "  CEL:\n"
        "    EXPRESSIONS:\n"
        "      AverageTemp = (InletTemp + OutletTemp)/2\n"
        "      InletTemp = 330 [K]\n"
        "      OutletTemp = 270 [K]\n"
        "    END\n"
        "  END\n"
        "END\n"
    )
    assert expr.list_properties() == ccl_string
    assert expr.list() == ["AverageTemp", "InletTemp", "OutletTemp"]
    assert expr.get_object_names() == ["AverageTemp", "InletTemp", "OutletTemp"]

    state = {
        "AverageTemp": {"definition": "(InletTemp + OutletTemp)/2"},
        "InletTemp": {"definition": "330 [K]"},
        "OutletTemp": {"definition": "270 [K]"},
    }
    assert expr() == state

    expr.print_state()
    captured = capsys.readouterr()
    msg = (
        "\n"
        "AverageTemp : \n"
        "  definition : (InletTemp + OutletTemp)/2\n"
        "InletTemp : \n"
        "  definition : 330 [K]\n"
        "OutletTemp : \n"
        "  definition : 270 [K]\n"
    )
    assert msg == captured.out

    if pypre.get_cfx_version() > CFXVersion.v252:
        try:
            expr.create(name="OutletTemp")
        except RuntimeError as e:
            assert str(e) == "Parameter 'OutletTemp' for object 'EXPRESSIONS' already exists."
        else:
            assert False, "Expected RuntimeError"

    # Rename tests
    expr.rename(old="AverageTemp", new="NewAverageTemp")
    assert expr.get_object_names() == ["InletTemp", "NewAverageTemp", "OutletTemp"]
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
        if pypre.get_cfx_version() > CFXVersion.v252:
            assert str(e) == "Parameter 'OutletTemp' for object 'EXPRESSIONS' already exists."
        else:
            assert str(e) == "Parameter 'OutletTemp' for object 'EXPRESSIONS' already exist."
    else:
        assert False, "Expected RuntimeError"

    # Duplicate tests
    expr.duplicate(old="OutletTemp", new="OutletTempDup")
    assert expr.get_object_names() == ["InletTemp", "NewAverageTemp", "OutletTemp", "OutletTempDup"]
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
        if pypre.get_cfx_version() > CFXVersion.v252:
            assert str(e) == "Parameter 'OutletTempDup' for object 'EXPRESSIONS' already exists."
        else:
            assert str(e) == "Parameter 'OutletTempDup' for object 'EXPRESSIONS' already exist."
    else:
        assert False, "Expected RuntimeError"

    # Delete tests
    # "del" isn't working for dynamic parameters in 25.2
    if pypre.get_cfx_version() > CFXVersion.v252:
        del expr["OutletTemp"]
        assert expr.get_object_names() == ["InletTemp", "NewAverageTemp", "OutletTempDup"]
        try:
            del expr["OutletTemp"]
        except RuntimeError as e:
            assert str(e) == "Parameter 'OutletTemp' for object 'EXPRESSIONS' does not exist."
        else:
            assert False, "Expected RuntimeError"
        expr["OutletTempDup"].definition = " "
        assert expr.get_object_names() == ["InletTemp", "NewAverageTemp"]
        expr["NewAverageTemp"].definition = None
        assert expr.get_object_names() == ["InletTemp"]
    else:
        expr["OutletTemp"].definition = " "
        expr["OutletTempDup"].definition = " "
        expr["NewAverageTemp"].definition = " "

    # Tests for functions which are run on an individual expression
    expr["InletTemp"].duplicate(new="InletTempDup")
    assert expr.get_object_names() == ["InletTemp", "InletTempDup"]
    assert expr["InletTempDup"].definition() == "330 [K]"
    try:
        expr["InletTemp"].duplicate(new="InletTempDup")
    except RuntimeError as e:
        if pypre.get_cfx_version() > CFXVersion.v252:
            assert str(e) == "Parameter 'InletTempDup' for object 'EXPRESSIONS' already exists."
        else:
            assert str(e) == "Parameter 'InletTempDup' for object 'EXPRESSIONS' already exist."
    else:
        assert False, "Expected RuntimeError"

    if pypre.get_cfx_version() > CFXVersion.v252:
        assert expr["InletTemp"]() == {"definition": "330 [K]"}
    expr["InletTemp"].definition.print_state()
    captured = capsys.readouterr()
    assert "330 [K]\n" == captured.out
    expr["InletTemp"].duplicate(new="InletTempDup2")
    assert expr.get_object_names() == [
        "InletTemp",
        "InletTempDup",
        "InletTempDup2",
    ]
    if pypre.get_cfx_version() > CFXVersion.v252:
        assert expr["InletTempDup2"]() == {"definition": "330 [K]"}
        expr["InletTempDup2"].rename("InletTemp2")
        assert expr.get_object_names() == [
            "InletTemp",
            "InletTemp2",
            "InletTempDup",
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
        if pypre.get_cfx_version() > CFXVersion.v252:
            msg = (
                "Setting a value '440 [K]' for the object '/LIBRARY/CEL/EXPRESSIONS:InletTemp2' is "
                "not allowed. Set the 'definition' parameter within the object instead."
            )
        else:
            msg = "Parameter value 'EXPRESSIONS' for object '/LIBRARY/CEL' is not allowed."
        assert str(e) == msg
    else:
        assert False, "Expected RuntimeError"
    expr["InletTemp2"].definition.set_state("440 [K]")
    ccl_string = (
        "LIBRARY:\n"
        "  CEL:\n"
        "    EXPRESSIONS:\n"
        "      InletTemp = 330 [K]\n"
        "      InletTemp2 = 440 [K]\n"
        "      InletTempDup = 330 [K]\n"
        "    END\n"
        "  END\n"
        "END\n"
    )
    assert expr.list_properties() == ccl_string

    expr.set_state({"InletTemp2": {"definition": None}, "InletTemp": {"definition": "550 [K]"}})
    ccl_string = (
        "LIBRARY:\n"
        "  CEL:\n"
        "    EXPRESSIONS:\n"
        "      InletTemp = 550 [K]\n"
        "      InletTempDup = 330 [K]\n"
        "    END\n"
        "  END\n"
        "END\n"
    )
    assert expr.list_properties() == ccl_string

    if pypre.get_cfx_version() > CFXVersion.v252:
        assert expr.get_object_names() == ["InletTemp", "InletTempDup"]
        expr.clear()
        assert expr.get_object_names() == []
        ccl_string = "LIBRARY:\n" "  CEL:\n" "    EXPRESSIONS:\n" "    END\n" "  END\n" "END\n"
        assert expr.list_properties() == ccl_string

    # Test for dynamic parameters which are not part of the EXPRESSIONS object
    user = pypre.setup.user
    user.create("Inlet Temperature")
    user["Inlet Temperature"].definition = "77 [K]"
    user.duplicate(old="Inlet Temperature", new="New Inlet Temperature")
    ccl_string = (
        "USER:\n" "  Inlet Temperature = 77 [K]\n" "  New Inlet Temperature = 77 [K]\n" "END\n"
    )
    assert user.list_properties() == ccl_string
    user.delete("New Inlet Temperature")
    ccl_string = "USER:\n" "  Inlet Temperature = 77 [K]\n" "END\n"
    assert user.list_properties() == ccl_string

    # Mixture of keyword args and args
    user.rename("NewTemp2", old="Inlet Temperature")
    ccl_string = "USER:\n" "  NewTemp2 = 77 [K]\n" "END\n"
    assert user.list_properties() == ccl_string

    if pypre.get_cfx_version() > CFXVersion.v261:
        user.set_state(
            {
                "NewTemp3": {"definition": "99 [K]"},
                "NewTemp2": {"definition": None},
                "NewTemp4": {"definition": None},
            }
        )
        ccl_string = "USER:\n" "  NewTemp3 = 99 [K]\n" "END\n"
        assert user.list_properties() == ccl_string


def test_set_var(pre_load_static_mixer_case: PreProcessing, pytestconfig, capsys):
    """Test for setting parameter values and state.

    The test includes systematic coverage of all the parameter types used by CFX-Pre,
    plus related tests for object state."""

    pypre = pre_load_static_mixer_case

    in1 = pypre.setup.flow["Flow Analysis 1"].domain["Default Domain"].boundary["in1"]
    oc = pypre.setup.flow["Flow Analysis 1"].output_control
    sc = pypre.setup.flow["Flow Analysis 1"].solver_control
    mat_water = pypre.setup.library.material["Water"]
    lib_cel = pypre.setup.library.cel

    # Set up some new objects needed to expose parameters of each type
    oc.backup_results["Backup Results 1"] = {}
    backup1 = oc.backup_results["Backup Results 1"]
    backup1.output_frequency.option = "Iteration List"
    backup1.output_frequency.iteration_list = [4, 6, 8]
    pypre.setup.library.user_location_definitions.user_line["User Line 1"] = {}
    user_line1 = pypre.setup.library.user_location_definitions.user_line["User Line 1"]
    user_line1.option = "Two Points"

    pressure_in_pa = ansys_units.Quantity(value=1, units="Pa")

    # Integer param
    sc.convergence_control.maximum_number_of_iterations = 59
    assert sc.convergence_control.maximum_number_of_iterations() == 59
    sc.convergence_control.maximum_number_of_iterations = "77"
    assert sc.convergence_control.maximum_number_of_iterations() == 77
    for invalid_value, err_str in [
        ("NotAnExpression", "NotAnExpression"),
        (False, "False"),
        (6.3, "6.300000"),
        ([6, 7, 8], "6,7,8"),
        (pressure_in_pa, "1.0 Pa"),
    ]:
        try:
            sc.convergence_control.maximum_number_of_iterations = invalid_value
        except RuntimeError as e:
            if pypre.get_cfx_version() > CFXVersion.v261:
                msg = (
                    "CCL validation failed with message:\n"
                    "Error: Parameter /FLOW:Flow Analysis 1/SOLVER CONTROL/CONVERGENCE CONTROL/"
                    f"Maximum Number of Iterations = {err_str} must be type Integer\n"
                )
            else:
                msg = (
                    "CCLAPI::validateCCLData::CCL validation failed with message:\n"
                    "Error: Parameter /FLOW:Flow Analysis 1/SOLVER CONTROL/CONVERGENCE CONTROL/"
                    f"Maximum Number of Iterations = {err_str} must be type Integer\n"
                )
            assert str(e) == msg
        else:
            assert False, f"Expected RuntimeError for {invalid_value}"

    # Integer Expression param
    user_line1.number_of_points = 59
    if pypre.get_cfx_version() > CFXVersion.v252:
        assert user_line1.number_of_points() == 59
    else:
        assert user_line1.number_of_points() == "59"
    user_line1.number_of_points = "77"
    if pypre.get_cfx_version() > CFXVersion.v252:
        assert user_line1.number_of_points() == 77
    else:
        assert user_line1.number_of_points() == "77"
    # The 'False' behavior should not be allowed.
    for value, result in [
        ("MyExpr", "MyExpr"),
        (False, "False"),
        (6.3, "6.300000"),
        ([6, 7, 8], "6,7,8"),
    ]:
        user_line1.number_of_points = value
        assert user_line1.number_of_points() == result

    # Integer List param
    for value, result in [
        ([59, 65, 32], [59, 65, 32]),
        (["77, 65, 67"], [77, 65, 67]),
        (["34", "45", "12"], [34, 45, 12]),
        ((59, 65, 32), [59, 65, 32]),
        (("77, 65, 67"), [77, 65, 67]),
        (("34", "45", "12"), [34, 45, 12]),
        (59, [59]),
        ("77", [77]),
    ]:
        backup1.output_frequency.iteration_list = value
        assert backup1.output_frequency.iteration_list() == result
    # The behavior below is not ideal; the bad value should be caught when set.
    for invalid_value, err_str in [
        ("NotAnExpression", "NotAnExpression"),
        (False, "False"),
        (6.3, "6.300000"),
        ([6.300000, 7, 8], "6.300000,7,8"),
        ([6, 7, False], "6,7,False"),
        ([4, "NotAnExpression"], "4,NotAnExpression"),
    ]:
        backup1.output_frequency.iteration_list = invalid_value
        try:
            backup1.output_frequency.iteration_list()
        except RuntimeError as e:
            assert (
                str(e) == f"Invalid parameter value '{err_str}' for parameter "
                "'/FLOW:Flow Analysis 1/OUTPUT CONTROL/BACKUP RESULTS:Backup Results 1/OUTPUT "
                "FREQUENCY/Iteration List'"
            )
        else:
            assert False, f"Expected RuntimeError"

    # Logical param
    assert sc.dynamic_model_control.global_dynamic_model_control() == True
    for value, result in [(False, False), (77, True), (6.3, True)]:
        sc.dynamic_model_control.global_dynamic_model_control = value
        assert sc.dynamic_model_control.global_dynamic_model_control() == result
    for invalid_value, err_str in [("NotAnExpression", "NotAnExpression"), ([6, 7, 8], "6,7,8")]:
        try:
            sc.dynamic_model_control.global_dynamic_model_control = invalid_value
        except RuntimeError as e:
            if pypre.get_cfx_version() > CFXVersion.v261:
                msg = (
                    "CCL validation failed with message:\n"
                    "Error: Parameter '/FLOW:Flow Analysis 1/SOLVER CONTROL/DYNAMIC MODEL CONTROL/"
                    f"Global Dynamic Model Control = {err_str}' must be type Logical\n"
                )
            else:
                msg = (
                    "CCLAPI::validateCCLData::CCL validation failed with message:\n"
                    "Error: Parameter '/FLOW:Flow Analysis 1/SOLVER CONTROL/DYNAMIC MODEL CONTROL/"
                    f"Global Dynamic Model Control = {err_str}' must be type Logical\n"
                )
            assert str(e) == msg
        else:
            assert False, f"Expected RuntimeError for {invalid_value}"

    # Real param
    # Wrong units: this will be accepted here but give a physics error
    for value, result in [
        ("4.4 [m/s]", "4.4 [m/s]"),
        ("4.4 [K]", "4.4 [K]"),
        (5.9, "5.900000"),
        ("77", "77"),
        ("MyExpr", "MyExpr"),
        (False, "False"),
        ([6, 7, 8], "6,7,8"),
    ]:
        in1.boundary_conditions.mass_and_momentum.normal_speed = value
        assert in1.boundary_conditions.mass_and_momentum.normal_speed() == result

    # Real param with ansys.units
    pypre.setup.flow["Flow Analysis 1"].domain["Default Domain"].boundary[
        "out"
    ].boundary_conditions.mass_and_momentum.relative_pressure = pressure_in_pa
    assert (
        pypre.setup.flow["Flow Analysis 1"]
        .domain["Default Domain"]
        .boundary["out"]
        .boundary_conditions.mass_and_momentum.relative_pressure()
        == "1.0 [Pa]"
    )
    pressure_in_psf = pressure_in_pa.to("psf")
    pypre.setup.flow["Flow Analysis 1"].domain["Default Domain"].boundary[
        "out"
    ].boundary_conditions.mass_and_momentum.relative_pressure.set_state(pressure_in_psf)
    pressure_val = (
        pypre.setup.flow["Flow Analysis 1"]
        .domain["Default Domain"]
        .boundary["out"]
        .boundary_conditions.mass_and_momentum.relative_pressure()
    )
    assert pressure_val.startswith("0.0208")
    assert pressure_val.endswith(" [psf]")

    # Real Triplet param
    for value, result in [
        ("4.4 [m/s], 5.5 [m/s], 6.6 [m/s]", ["4.4 [m/s]", "5.5 [m/s]", "6.6 [m/s]"]),
        (
            "4.4 [m/s], 5.5 [m/s], 6.6 [m/s], 7.7 [m/s]",
            [
                "4.4 [m/s]",
                "5.5 [m/s]",
                "6.6 [m/s]",
                "7.7 [m/s]",
            ],
        ),
        ("4.4 [m/s], 5.5 [K], 6.6 [m/s]", ["4.4 [m/s]", "5.5 [K]", "6.6 [m/s]"]),
        (5.9, ["5.900000"]),
        ([77, 88], ["77", "88"]),
        ("MyExpr", ["MyExpr"]),
        (False, ["False"]),
    ]:
        user_line1.point_definition.point_1 = value
        assert user_line1.point_definition.point_1() == result

    # Real List param
    for value, result in [
        ("4.4 [m/s], 2*5.5 [m/s], 6.6 [m/s]", ["4.4 [m/s]", "2*5.5 [m/s]", "6.6 [m/s]"]),
        (
            "4.4 [m/s], 2*5.5 [m/s], 6.6 [m/s], 7.7 [m/s]",
            [
                "4.4 [m/s]",
                "2*5.5 [m/s]",
                "6.6 [m/s]",
                "7.7 [m/s]",
            ],
        ),
        ("4.4 [s], 2*5.5 [K], 6.6 [s]", ["4.4 [s]", "2*5.5 [K]", "6.6 [s]"]),
        (5.9, ["5.900000"]),
        ([77, 88], ["77", "88"]),
        ("MyExpr", ["MyExpr"]),
        (False, ["False"]),
    ]:
        sc.convergence_control.physical_timescale = value
        assert sc.convergence_control.physical_timescale() == result

    # String param without allowed values
    user_line1.option = "From File"
    for value, result in [
        ("A.txt", "A.txt"),
        ("A.txt # comment", "A.txt"),
        ("A.txt ! bad char", "A.txt ! bad char"),
        (5.9, "5.900000"),
        (False, "False"),
        ([77, 88], "77,88"),
    ]:
        user_line1.data_source.file_name = value
        assert user_line1.data_source.file_name() == result

    # String param with allowed values
    in1.boundary_type = "OUTLET"
    assert in1.boundary_type() == "OUTLET"
    # The error here is unexpected
    for invalid_value, err_str in [(5.9, "float"), (False, "bool")]:
        try:
            in1.boundary_type = invalid_value
        except TypeError as e:
            assert str(e) == f"'{err_str}' object is not iterable"
        else:
            assert False, f"Expected TypeError for {invalid_value}"
    for invalid_value in ["BAD TYPE", [77, 88]]:
        try:
            in1.boundary_type = invalid_value
        except ValueError as e:
            assert (
                str(e) == f"'boundary_type' has no attribute '{invalid_value}'.\n"
                "The allowed values are: ['INLET', 'OUTLET', 'OPENING', 'WALL', 'SYMMETRY']."
            )
        else:
            assert False, f"Expected ValueError for {invalid_value}"

    # String List param without allowed values
    for value, result in [
        ("A, B", ["A", "B"]),
        ("A # comment", ["A"]),
        (["A # comment", "B # another comment"], ["A"]),
        ("A ! bad char", ["A ! bad char"]),
        (5.9, ["5.900000"]),
        (False, ["False"]),
        ([77, 88], ["77", "88"]),
    ]:
        lib_cel.cel_function_order_list = value
        assert lib_cel.cel_function_order_list() == result

    # String List param with allowed values
    mat_water.material_group = ["Water Data", "User"]
    assert mat_water.material_group() == ["Water Data", "User"]
    # The error here is unexpected
    for invalid_value, err_str in [(5.9, "float"), (False, "bool")]:
        try:
            mat_water.material_group = invalid_value
        except TypeError as e:
            assert str(e) == f"'{err_str}' object is not iterable"
        else:
            assert False, f"Expected TypeError for {invalid_value}"
    for invalid_value in ["BAD TYPE", [77, 88]]:
        try:
            mat_water.material_group = invalid_value
        except ValueError as e:
            assert (
                f"'material_group' has no attribute '{invalid_value}'.\n"
                "The allowed values are: ['Air Data', " in str(e)
            )
        else:
            assert False, f"Expected ValueError for {invalid_value}"

    # Set value for an object. This is an error.
    try:
        pypre.setup.flow["Flow Analysis 1"].analysis_type = "MyExpr2"
    except RuntimeError as e:
        if pypre.get_cfx_version() > CFXVersion.v261:
            msg = (
                "Setting parameter value 'MyExpr2' for parameter 'ANALYSIS TYPE' in object "
                "'/FLOW:Flow Analysis 1' is not allowed."
            )
        else:
            msg = (
                "Parameter value 'ANALYSIS TYPE' for object '/FLOW:Flow Analysis 1' is not "
                "allowed."
            )
        assert str(e) == msg
    else:
        assert False, f"Expected RuntimeError"
    captured = capsys.readouterr()
    assert (
        captured.out == "\n"
        " allowed_values can be accessed from the following paths: \n\n"
        '    <session>.setup.flow["Flow Analysis 1"].analysis_type.external_solver_coupling."'
        '"option.allowed_values\n\n'
        " allowed_values can be accessed from the following paths: \n\n"
        '    <session>.setup.flow["Flow Analysis 1"].analysis_type.option.allowed_values\n'
    )

    # Tests for set_state
    in_bc_state = {
        "boundary_type": "INLET",
        "interface_boundary": False,
        "location": "F2.B1.P3",
        "boundary_conditions": {
            "flow_regime": {"option": "Subsonic"},
            "heat_transfer": {
                "option": "Static Temperature",
                "static_temperature": "777 [K]",
            },
            "mass_and_momentum": {
                "option": "Normal Speed",
                "normal_speed": "7 [m s^-1]",
            },
            "turbulence": {
                "option": "Low Intensity and Eddy Viscosity Ratio",
            },
        },
    }

    pypre.setup.flow["Flow Analysis 1"].domain["Default Domain"].boundary["in3"] = {}
    in3 = pypre.setup.flow["Flow Analysis 1"].domain["Default Domain"].boundary["in3"]
    in3.set_state(in_bc_state)
    assert in_bc_state == in3.get_state()
    assert in3.boundary_conditions.heat_transfer.static_temperature() == "777 [K]"

    in_bc_state["boundary_conditions"]["heat_transfer"]["option"] = "Bad Option"
    try:
        in3.set_state(in_bc_state)
    except RuntimeError as e:
        if pypre.get_cfx_version() > CFXVersion.v261:
            msg = (
                "CCL validation failed with message:\n"
                "Error: Invalid Option parameter 'Bad Option' in /FLOW:Flow Analysis 1/"
                "DOMAIN:Default Domain/BOUNDARY:in3/BOUNDARY CONDITIONS/HEAT TRANSFER\n"
                "\nParameter value 'Bad Option' for parameter 'Option' in object "
                "'/FLOW:Flow Analysis 1/DOMAIN:Default Domain/BOUNDARY:in3/BOUNDARY "
                "CONDITIONS/HEAT TRANSFER' was not set. This may not be physically valid."
            )
        else:
            msg = (
                "CCLAPI::validateCCLData::CCL validation failed with message:\n"
                "Error: Invalid Option parameter 'Bad Option' in /FLOW:Flow Analysis 1/"
                "DOMAIN:Default Domain/BOUNDARY:in3/BOUNDARY CONDITIONS/HEAT TRANSFER\n"
            )
        assert str(e) == msg
    else:
        assert False, f"Expected RuntimeError"

    user_line_state = {
        "number_of_points": 11,
        "option": "Two Points",
        "point_definition": {
            "coord_frame": "Coord 0",
            "option": "Cartesian Coordinates",
            "point_1": ["0.0[m]", "0.0[m]", "0.0[m]"],
            "point_2": ["0.0[m]", "0.0[m]", "0.0[m]"],
        },
        "visibility": "Bad Value",
    }

    pypre.setup.library.user_location_definitions.user_line["User Line 2"] = {}
    user_line2 = pypre.setup.library.user_location_definitions.user_line["User Line 2"]
    try:
        user_line2.set_state(user_line_state)
    except RuntimeError as e:
        if pypre.get_cfx_version() > CFXVersion.v261:
            msg = (
                "CCL validation failed with message:\n"
                "Error: Parameter '/LIBRARY/USER LOCATION DEFINITIONS/USER LINE:User Line 2/"
                "Visibility = Bad Value' must be type Logical\n\n"
                "Some or all of the state settings were not applied. The first two omissions "
                "are:\n"
                "  'Parameter value '11' for parameter 'Number of Points' in object "
                "'/LIBRARY/USER LOCATION DEFINITIONS/USER LINE:User Line 2' was not set. "
                "This may not be physically valid.'\n"
                "  'Parameter value 'Two Points' for parameter 'Option' in object "
                "'/LIBRARY/USER LOCATION DEFINITIONS/USER LINE:User Line 2' was not set. "
                "This may not be physically valid.'\n"
                "Note that CCL validation errors prevent any state from being applied."
            )
        else:
            msg = (
                "CCLAPI::validateCCLData::CCL validation failed with message:\n"
                "Error: Parameter '/LIBRARY/USER LOCATION DEFINITIONS/USER LINE:User Line 2/"
                "Visibility = Bad Value' must be type Logical\n"
            )
        assert str(e) == msg
    else:
        assert False, f"Expected RuntimeError"

    user_line_state["visibility"] = True
    user_line_state["bad parameter"] = "bad value"
    try:
        user_line2.set_state(user_line_state)
    except KeyError as e:
        assert str(e) == "'bad parameter'"
    else:
        assert False, "Expected KeyError"

    try:
        user_line2.to_engine_keys(user_line_state)
    except RuntimeError as e:
        assert str(e) == "Key 'bad parameter' is invalid"
    else:
        assert False, "Expected RuntimeError"

    assert user_line2.to_python_keys("Simple Value") == "Simple Value"
    assert (
        pypre.setup.library.user_location_definitions.user_line.to_python_keys("Simple Value")
        == "Simple Value"
    )


def test_optional_objs_and_params(pre_load_static_mixer_case: PreProcessing, pytestconfig, capsys):
    """Test for handling optional objects and parameters, including the "Enabled" parameter."""

    pypre = pre_load_static_mixer_case

    in1 = pypre.setup.flow["Flow Analysis 1"].domain["Default Domain"].boundary["in1"]
    in_bc_state = {
        "boundary_type": "INLET",
        "location": "in1",
        "interface_boundary": False,
        "boundary_conditions": {
            "flow_regime": {"option": "Subsonic"},
            "heat_transfer": {
                "option": "Static Temperature",
                "static_temperature": "315 [K]",
            },
            "mass_and_momentum": {
                "option": "Normal Speed",
                "normal_speed": "2 [m s^-1]",
            },
            "turbulence": {
                "option": "Medium Intensity and Eddy Viscosity Ratio",
            },
        },
    }
    in_bc_state_with_coord = in_bc_state.copy()
    in_bc_state_with_coord["coord_frame"] = "Coord 0"
    in_bc_state_with_contour = in_bc_state.copy()
    in_bc_state_with_contour["boundary_contour"] = {"profile_variable": "Static Temperature"}
    in1.set_state(in_bc_state)

    pypre.setup.library.additional_variable["Additional Variable 1"] = {}
    av1 = pypre.setup.library.additional_variable["Additional Variable 1"]

    # Test optional parameter
    # Start with the parameter disabled
    assert in1.coord_frame() == ""
    assert in1.coord_frame.is_active() == True
    assert in1.get_state() == in_bc_state
    # Enable just by setting the value
    in1.coord_frame = "Coord 0"
    assert (in1.coord_frame()) == "Coord 0"
    assert in1.coord_frame.is_active() == True
    assert in1.get_state() == in_bc_state_with_coord
    # Disable by setting to None
    in1.coord_frame = None
    assert (in1.coord_frame()) == ""
    assert in1.coord_frame.is_active() == True
    assert in1.get_state() == in_bc_state

    # Test optional singleton
    # Start with the singleton disabled
    assert in1.boundary_contour.enabled() == False
    assert in1.boundary_contour.is_active() == True
    assert in1.boundary_contour.get_state() == {}
    # Enable by just setting a parameter within the optional object
    in1.boundary_contour.profile_variable = "Static Temperature"
    assert in1.boundary_contour.enabled() == True
    assert in1.boundary_contour.is_active() == True
    assert in1.boundary_contour.get_state() == {"profile_variable": "Static Temperature"}
    assert in1.get_state() == in_bc_state_with_contour
    # Disable with the "enabled" parameter
    in1.boundary_contour.enabled = False
    assert in1.boundary_contour.is_active() == True
    assert in1.boundary_contour.get_state() == {}
    # Enable by using the "enabled" parameter; the default settings are picked up
    in1.boundary_contour.enabled = True
    assert in1.boundary_contour.is_active() == True
    assert in1.boundary_contour.get_state() == {"profile_variable": "Normal Speed"}
    in_bc_state_with_contour["boundary_contour"] = {"profile_variable": "Normal Speed"}
    assert in1.get_state() == in_bc_state_with_contour

    # Test optional named object
    fluid_models_obj = pypre.setup.flow["Flow Analysis 1"].domain["Default Domain"].fluid_models
    fluid_models_state = {
        "combustion_model": {"option": "None"},
        "heat_transfer_model": {"option": "Thermal Energy"},
        "thermal_radiation_model": {"option": "None"},
        "turbulence_model": {"option": "k epsilon"},
        "turbulent_wall_functions": {"option": "Scalable"},
    }
    fluid_models_state_with_av = fluid_models_state.copy()
    fluid_models_state_with_av["additional_variable"] = {
        "Additional Variable 1": {
            "option": "Transport Equation",
        }
    }
    assert fluid_models_obj.get_state() == fluid_models_state
    # Enable by creating object
    fluid_models_obj.additional_variable["Additional Variable 1"] = {}
    assert fluid_models_obj.get_state() == fluid_models_state_with_av
    assert fluid_models_obj.additional_variable.get_object_names() == ["Additional Variable 1"]
    # Disable by deleting object
    del fluid_models_obj.additional_variable["Additional Variable 1"]
    assert fluid_models_obj.get_state() == fluid_models_state
    assert fluid_models_obj.additional_variable.get_object_names() == []
    # Check that invalid name cannot be used
    try:
        fluid_models_obj.additional_variable["No such Additional Variable"] = {}
    except RuntimeError as e:
        if pypre.get_cfx_version() > CFXVersion.v252:
            assert str(e) == (
                "Object '/FLOW:Flow Analysis 1/DOMAIN:Default Domain/FLUID MODELS/"
                "ADDITIONAL VARIABLE:No such Additional Variable' was not created as it is "
                "not physically valid."
            )
        else:
            assert str(e) == (
                "Object '/FLOW:Flow Analysis 1/DOMAIN:Default Domain/FLUID MODELS/"
                "ADDITIONAL VARIABLE:No such Additional Variable' was not created."
            )
    else:
        assert False, f"Expected RuntimeError"
    try:
        del fluid_models_obj.additional_variable["No such Additional Variable"]
    except RuntimeError as e:
        assert str(e) == (
            "Object '/FLOW:Flow Analysis 1/DOMAIN:Default Domain/FLUID MODELS/"
            "ADDITIONAL VARIABLE:No such Additional Variable' does not exist."
        )
    else:
        assert False, f"Expected RuntimeError"


def test_undefined_parameters(pre_load_static_mixer_case: PreProcessing, pytestconfig, capsys):
    """Test for the handling of undefined parameters when connected to the CFX-Pre engine."""

    pypre = pre_load_static_mixer_case

    in1 = pypre.setup.flow["Flow Analysis 1"].domain["Default Domain"].boundary["in1"]

    # Try setting existing parameters to None
    try:
        in1.boundary_conditions.heat_transfer.option = None
    except TypeError as e:
        assert str(e) == "'NoneType' object is not iterable"
    try:
        in1.boundary_conditions.heat_transfer.static_temperature = None
    except TypeError as e:
        assert str(e) == "'NoneType' object is not iterable"

    # Undefined parameters due to creation of object where parameter has no default
    pypre.setup.flow["Flow Analysis 1"].domain["Default Domain"].boundary["in3"] = {}
    in3 = pypre.setup.flow["Flow Analysis 1"].domain["Default Domain"].boundary["in3"]
    if pypre.get_cfx_version() > CFXVersion.v252:
        assert in3.boundary_conditions.mass_and_momentum.normal_speed() == None
    else:
        assert in3.boundary_conditions.mass_and_momentum.normal_speed() == "-- Undefined --"

    # Undefined parameters for "dynamic" parameters
    expr = pypre.setup.library.cel.expressions
    expr.create("InletTemp")
    if pypre.get_cfx_version() > CFXVersion.v252:
        assert expr["InletTemp"]() == {"definition": "0"}
    ccl_string_zero = (
        "LIBRARY:\n"
        "  CEL:\n"
        "    EXPRESSIONS:\n"
        "      InletTemp = 0\n"
        "    END\n"
        "  END\n"
        "END\n"
    )
    assert expr.list_properties() == ccl_string_zero
    expr["InletTemp"].definition = "330 [K]"
    if pypre.get_cfx_version() > CFXVersion.v252:
        assert expr["InletTemp"]() == {"definition": "330 [K]"}
    ccl_string_330 = (
        "LIBRARY:\n"
        "  CEL:\n"
        "    EXPRESSIONS:\n"
        "      InletTemp = 330 [K]\n"
        "    END\n"
        "  END\n"
        "END\n"
    )
    assert expr.list_properties() == ccl_string_330
    expr["InletTemp"].definition = None
    if pypre.get_cfx_version() > CFXVersion.v252:
        try:
            val = expr["InletTemp"]
        except KeyError as e:
            assert str(e) == "\"'expressions' has no attribute 'InletTemp'.\\n\""
        else:
            assert False, "Expected KeyError"
        ccl_string = "LIBRARY:\n" "  CEL:\n" "    EXPRESSIONS:\n" "    END\n" "  END\n" "END\n"
        assert expr.list_properties() == ccl_string
    else:
        assert expr.list_properties() == ccl_string_330
