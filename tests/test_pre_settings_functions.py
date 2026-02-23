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

import time
from pathlib import Path

from util.common import read_ccl_from_file, setup_write_dir

from ansys.cfx.core.launcher.cfx_container import timeout_loop
from ansys.cfx.core.session_pre import PreProcessing
from ansys.cfx.core.utils.cfx_version import CFXVersion


def test_save_picture(pre_load_static_mixer_case: PreProcessing, pytestconfig, capsys):
    """Test the save_picture function under PreProcessing."""

    generated_path_engine, generated_path_client = setup_write_dir(
        pytestconfig.test_data_directory_path, ["MyPicturePre.*", "hardcopy_pre.ccl"]
    )

    pypre = pre_load_static_mixer_case

    # Basic test
    client_picture_file = str(Path(generated_path_client) / "MyPicturePre.png")

    pypre.file.save_picture(file_name=f"{generated_path_engine}/MyPicturePre.png")
    assert timeout_loop(Path(client_picture_file).exists, timeout=10.0)
    assert Path(client_picture_file).stat().st_size > 0
    Path(client_picture_file).unlink()

    # Test format argument
    pypre.file.save_picture(file_name=f"{generated_path_engine}/MyPicturePre.jpg", format="jpg")
    jpg_file = Path(generated_path_client) / "MyPicturePre.jpg"
    assert timeout_loop(jpg_file.exists, timeout=10.0)
    assert jpg_file.stat().st_size > 0
    jpg_file.unlink()

    pypre.file.save_picture(file_name=f"{generated_path_engine}/MyPicturePre.ps", format="ps")
    ps_file = Path(generated_path_client) / "MyPicturePre.ps"
    assert timeout_loop(ps_file.exists, timeout=10.0)
    assert ps_file.stat().st_size > 0
    ps_file.unlink()

    # Test bad value for format argument
    try:
        pypre.file.save_picture(file_name=f"{generated_path_engine}/MyPicturePre.ps", format="none")
    except RuntimeError as e:
        if pypre.get_cfx_version() > CFXVersion.v261:
            msg = (
                "CCL validation failed with message:\n"
                "Error: Invalid Option parameter 'none' in /HARDCOPY\n"
            )
        else:
            msg = (
                "CCLAPI::validateCCLData::CCL validation failed with message:\n"
                "Error: Invalid Option parameter 'none' in /HARDCOPY\n"
            )
        assert str(e) == msg
    else:
        assert False, "Expected RuntimeError"

    # Test bad argument
    try:
        pypre.file.save_picture(file_name=f"{generated_path_engine}/MyPicturePre.ps", badarg="2")
    except AttributeError as e:
        assert str(e) == ("'super' object has no attribute 'badarg'")
    else:
        assert False, "Expected AttributeError"

    # Test other arguments. These are stored in the /hardcopy_pre.ccl.
    picture_file = f"{generated_path_engine}/MyPicturePre.jpg"
    pypre.file.save_picture(
        file_name=picture_file,
        format="jpg",
        use_white_background=True,
        use_transparent_background=True,
        use_enhanced_output=False,
        use_screen_size=False,
        image_size_option="4k",
        image_height=888,
        image_width=999,
        image_scale=200,
        image_quality=55,
        tolerance=0.03,
    )
    jpg_file = Path(generated_path_client) / "MyPicturePre.jpg"
    assert timeout_loop(jpg_file.exists, timeout=10.0)
    jpg_file.unlink()

    pypre.file.export_ccl(
        file_name=f"{generated_path_engine}/hardcopy_pre.ccl", objects="/HARDCOPY"
    )
    expected_ccl = [
        "HARDCOPY:",
        "  Antialiasing = False",
        f"  Hardcopy Filename = {generated_path_engine}/MyPicturePre.jpg",
        "  Hardcopy Format = jpg",
        "  Hardcopy Tolerance = 0.030000",
        "  Image Height = 888",
        "  Image Scale = 200",
        "  Image Size Option = 4k",
        "  Image Width = 999",
        "  JPEG Image Quality = 55",
        "  Use Screen Size = False",
        "  White Background = True",
        "END",
    ]

    ccl_file_path = f"{generated_path_client}/hardcopy_pre.ccl"
    reduced_lines = read_ccl_from_file(ccl_file_path)
    assert reduced_lines == expected_ccl

    picture_file = f"{generated_path_engine}/MyPicturePre.png"
    pypre.file.save_picture(
        file_name=picture_file,
        format="png",
        use_white_background=True,
        use_transparent_background=True,
        use_enhanced_output=False,
        use_screen_size=False,
        image_size_option="4k",
        image_height=888,
        image_width=999,
        image_scale=200,
        image_quality=55,
        tolerance=0.03,
    )
    png_file = Path(generated_path_client) / "MyPicturePre.png"
    assert timeout_loop(png_file.exists, timeout=10.0)
    png_file.unlink()

    pypre.file.export_ccl(
        file_name=f"{generated_path_engine}/hardcopy_pre.ccl", objects="/HARDCOPY"
    )
    expected_ccl = [
        "HARDCOPY:",
        "  Antialiasing = False",
        f"  Hardcopy Filename = {generated_path_engine}/MyPicturePre.png",
        "  Hardcopy Format = png",
        "  Hardcopy Tolerance = 0.030000",
        "  Image Height = 888",
        "  Image Scale = 200",
        "  Image Size Option = 4k",
        "  Image Width = 999",
        "  Transparent Background = True",
        "  Use Screen Size = False",
        "  White Background = True",
        "END",
    ]
    ccl_file_path = f"{generated_path_client}/hardcopy_pre.ccl"
    reduced_lines = read_ccl_from_file(ccl_file_path)
    assert reduced_lines == expected_ccl
    Path(ccl_file_path).unlink()


def test_case_functions(pypre: PreProcessing, pytestconfig, capsys):
    """Test functions relating to case handling for PreProcessing."""

    # Test setup
    generated_path_engine, generated_path_client = setup_write_dir(
        pytestconfig.test_data_directory_path, ["*.cfx"]
    )

    # Utility function to test if a case is open
    def is_case_open():
        try:
            pypre.setup.library.cel.expressions.create("AA")
        except Exception as e:
            if str(e) == "A simulation must be opened before this action can be performed.":
                return False
            else:
                raise RuntimeError("Test for open simulation did not complete successfully.")
        else:
            return True

    # No case open initially
    assert not is_case_open()

    # New case, test by saving and closing without error
    pypre.file.new_case()
    assert is_case_open()
    # Can't open another case when one is already open
    try:
        pypre.file.new_case()
    except RuntimeError as e:
        if pypre.get_cfx_version() > CFXVersion.v261:
            msg = (
                "A simulation is already open! This must be closed before "
                "opening a new simulation."
            )
        else:
            msg = (
                "LoadExecutor::invoke::A simulation is already open! This must be closed before "
                "opening a new simulation."
            )
        assert str(e) == msg
    else:
        assert False, "Expected RuntimeError"

    # Save case
    empty_case_file_engine = f"{generated_path_engine}/EmptyCase.cfx"
    empty_case_file_client = f"{generated_path_client}/EmptyCase.cfx"
    pypre.file.save_case(file_name=empty_case_file_engine)
    # Test that case was successfully saved
    time.sleep(2)
    assert Path(empty_case_file_client).exists()
    assert Path(empty_case_file_client).stat().st_size > 0
    Path(empty_case_file_client).unlink()

    # Test close case. This is not available in 25.2.
    if pypre.get_cfx_version() > CFXVersion.v252:
        pypre.file.close_case()
        # Test that case was closed
        assert not is_case_open()

        # Basic testing of open_case is present for 25.2 in other tests. Just test arguments
        # in 26.1 and onwards, since we can't close the case in 25.2 without exiting PreProcessing
        # and we can't restart PreProcessing within a test.
        pypre.file.open_case(
            file_name=f"{pytestconfig.test_data_directory_path}/data/StaticMixer.def"
        )
        assert is_case_open()

        pypre.file.close_case()
        try:
            # This will fail as StaticMixer.cfx does not exist, which is necessary if
            # recover_case_file is True.
            pypre.file.open_case(
                file_name=f"{pytestconfig.test_data_directory_path}/data/StaticMixer.def",
                recover_case_file=True,
                replace_flow_data=True,
            )
        except RuntimeError as e:
            if pypre.get_cfx_version() > CFXVersion.v261:
                msg = "The file 'StaticMixer.cfx' could not be opened."
            else:
                msg = "LoadDefFile::openIIFile::The file 'StaticMixer.cfx' could not be opened."
            assert str(e) == msg
        else:
            assert False, "Expected RuntimeError"

    info1 = pypre.file.open_case.get_completer_info(prefix="re")
    assert len(info1) == 2
    assert len(info1[0]) == 3
    assert info1[0][0] == "recover_case_file"
    assert info1[0][1] == "Boolean"
    assert " ".join(info1[0][2].split()) == (
        "For CFX-Solver input files, locate and open the original case file (.cfx) instead."
    )
    assert info1[1][0] == "replace_flow_data"

    info2 = pypre.file.open_case.get_completer_info(prefix="re", excluded=["replace_flow_data"])
    assert len(info2) == 1
    assert info2[0][0] == "recover_case_file"


def test_misc_functions(pypre: PreProcessing, pytestconfig, capsys):
    """Test various other functions for PreProcessing."""

    # Test setup
    generated_path_engine, generated_path_client = setup_write_dir(
        pytestconfig.test_data_directory_path, ["Fluids1.ccl", "*.def"]
    )

    pypre.file.new_case()
    pypre.setup.physics_options_control.beta_physics_enabled = True

    # Test import mesh
    pypre.file.import_mesh(
        file_name=f"{pytestconfig.test_data_directory_path}/data/StaticMixer.def"
    )
    assert pypre.setup.flow["Flow Analysis 1"].domain["Default Domain"].location() == "B1.P3"

    # Set up some physics which will result in physics messages.
    # Undefined parameters
    pypre.setup.flow["Flow Analysis 1"].domain["Default Domain"].boundary["in1"] = {}
    # Beta feature
    pypre.setup.flow["Flow Analysis 1"].domain[
        "Default Domain"
    ].fluid_models.turbulent_wall_functions.blended_near_wall_treatment = "Laminar Turbulent Blend"

    if pypre.get_cfx_version() > CFXVersion.v252:
        error_message = {
            "message": "The parameter 'Normal Speed' in object '/FLOW:Flow Analysis "
            "1/DOMAIN:Default Domain/BOUNDARY:in1/BOUNDARY CONDITIONS/MASS AND "
            "MOMENTUM' needs to be set to a valid value.",
            "path": "/FLOW:Flow Analysis 1/DOMAIN:Default Domain/BOUNDARY:in1/BOUNDARY "
            "CONDITIONS/MASS AND MOMENTUM",
            "severity": "Error",
        }
    else:
        error_message = {
            "message": "Bad expression value '-- Undefined --' detected in parameter 'Normal "
            "Speed' in object '/FLOW:Flow Analysis 1/DOMAIN:Default "
            "Domain/BOUNDARY:in1/BOUNDARY CONDITIONS/MASS AND MOMENTUM'.|CEL "
            "error:|Syntax error detected in the expression assigned to 'Normal "
            "Speed'.|Error detected at beginning of expression:| -- Undefined "
            "--|Details - Syntax error: end of expression may not follow '-' "
            "character.|",
            "path": "/FLOW:Flow Analysis 1/DOMAIN:Default Domain/BOUNDARY:in1/BOUNDARY "
            "CONDITIONS/MASS AND MOMENTUM",
            "severity": "Error",
        }

    beta_message = {
        "message": "The 'Laminar Turbulent Blend' setting for the Blended Near Wall "
        "Treatment is enabled as a Beta feature.",
        "path": "/FLOW:Flow Analysis 1/DOMAIN:Default Domain/FLUID MODELS/TURBULENT "
        "WALL FUNCTIONS/Blended Near Wall Treatment",
        "severity": "Beta",
    }

    # Test physics messages
    assert pypre.setup.get_physics_messages() == [error_message, beta_message]
    assert pypre.setup.get_physics_messages(severity="Beta") == [beta_message]
    assert pypre.setup.get_physics_messages(severity="All") == [error_message, beta_message]
    assert pypre.setup.flow["Flow Analysis 1"].domain["Default Domain"].get_physics_messages() == [
        error_message,
        beta_message,
    ]
    assert pypre.setup.flow["Flow Analysis 1"].domain["Default Domain"].boundary[
        "in1"
    ].get_physics_messages() == [error_message]

    pypre.file.export_ccl(
        file_name=f"{generated_path_engine}/fluid1.ccl",
        objects="/FLOW:Flow Analysis 1/DOMAIN:Default Domain/FLUID DEFINITION:Fluid 1",
    )
    expected_ccl = [
        "FLOW: Flow Analysis 1",
        "  DOMAIN: Default Domain",
        "    FLUID DEFINITION: Fluid 1",
        "      Material = Air at 25 C",
        "      Option = Material Library",
        "      MORPHOLOGY:",
        "        Option = Continuous Fluid",
        "      END",
        "    END",
        "  END",
        "END",
    ]

    ccl_file_path = f"{generated_path_client}/fluid1.ccl"
    reduced_lines = read_ccl_from_file(ccl_file_path)
    assert reduced_lines == expected_ccl
    Path(ccl_file_path).unlink()

    # Test write_solver_file
    solver_file_engine = f"{generated_path_engine}/SmallCase.def"
    solver_file_client = f"{generated_path_client}/SmallCase.def"
    pypre.file.write_solver_input_file(file_name=solver_file_engine)
    time.sleep(2)
    assert Path(solver_file_client).exists()
    assert Path(solver_file_client).stat().st_size > 0
    Path(solver_file_client).unlink()


def test_function_data(pypre: PreProcessing, pytestconfig, capsys):
    """Test functions relating to generic handling of Settings objects."""

    pypre.file.new_case()

    if pypre.get_cfx_version() > CFXVersion.v252:
        assert pypre.setup.library.get_active_child_names() == [
            "additional_variable",
            "cel",
            "gt_suite_model",
            "material",
            "reaction",
            "user_routine_definitions",
            "material_group",
            "coordinate_frame_definitions",
            "user_location_definitions",
            "transformation_definitions",
            "mode_shape_definitions",
        ]
    else:
        assert pypre.setup.library.get_active_child_names() == [
            "variable",
            "variable_operator",
            "equation_definitions",
            "additional_variable",
            "cel",
            "gt_suite_model",
            "material",
            "reaction",
            "user_routine_definitions",
            "material_group",
            "hybrid_order_option",
            "coordinate_frame_definitions",
            "user_location_definitions",
            "transformation_definitions",
            "mode_shape_definitions",
        ]

    assert pypre.file.get_active_command_names() == [
        "close_case",
        "export_ccl",
        "import_mesh",
        "new_case",
        "open_case",
        "save_case",
        "save_picture",
        "write_solver_input_file",
    ]

    assert pypre.setup.library.get_active_query_names() == ["get_physics_messages"]

    def simplify_completer_whitespace(value):
        for item in value:
            item[2] = " ".join(item[2].split())
        return value

    assert simplify_completer_whitespace(pypre.setup.library.get_completer_info(prefix="m")) == [
        ["material", "NamedObject", "A container for Material objects."],
        ["material_group", "NamedObject", "A container for Material Group objects."],
        ["mode_shape_definitions", "Group", "Container for Mode Shapes."],
    ]

    assert simplify_completer_whitespace(
        pypre.setup.library.get_completer_info(prefix="m", excluded=["material_group"])
    ) == [
        ["material", "NamedObject", "A container for Material objects."],
        ["mode_shape_definitions", "Group", "Container for Mode Shapes."],
    ]

    assert simplify_completer_whitespace(pypre.file.get_completer_info(prefix="n")) == [
        ["new_case", "Command", "Start a new case."]
    ]

    assert pypre.file.get_completer_info(prefix="n", excluded=["new_case"]) == []
