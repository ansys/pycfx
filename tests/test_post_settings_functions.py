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


from pathlib import Path

from util.common import read_ccl_from_file, setup_write_dir

from ansys.cfx.core.launcher.cfx_container import timeout_loop
from ansys.cfx.core.session_post import PostProcessing
from ansys.cfx.core.utils.cfx_version import CFXVersion


def test_save_picture(pypost: PostProcessing, pytestconfig, capsys):

    generated_path_engine, generated_path_client = setup_write_dir(
        pytestconfig.test_data_directory_path, ["MyPicturePost.*", "hardcopy_post.ccl"]
    )

    pypost.file.load_results(
        file_name=f"{pytestconfig.test_data_directory_path}/data/StaticMixer.def"
    )

    # Basic test
    client_picture_file = str(Path(generated_path_client) / "MyPicturePost.png")

    pypost.file.save_picture(file_name=f"{generated_path_engine}/MyPicturePost.png")

    assert timeout_loop(Path(client_picture_file).exists, timeout=10.0)
    assert Path(client_picture_file).stat().st_size > 0
    Path(client_picture_file).unlink()

    # Test format argument
    pypost.file.save_picture(file_name=f"{generated_path_engine}/MyPicturePost.jpg", format="jpg")
    jpg_file = Path(generated_path_client) / "MyPicturePost.jpg"
    assert timeout_loop(jpg_file.exists, timeout=10.0)
    assert jpg_file.stat().st_size > 0
    jpg_file.unlink()

    pypost.file.save_picture(file_name=f"{generated_path_engine}/MyPicturePost.ps", format="ps")
    ps_file = Path(generated_path_client) / "MyPicturePost.ps"
    assert timeout_loop(ps_file.exists, timeout=10.0)
    assert ps_file.stat().st_size > 0
    ps_file.unlink()

    # Test bad value for format argument
    try:
        pypost.file.save_picture(
            file_name=f"{generated_path_engine}/MyPicturePost.ps", format="none"
        )
    except RuntimeError as e:
        if pypost.get_cfx_version() > CFXVersion.v261:
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
        pypost.file.save_picture(file_name=f"{generated_path_engine}/MyPicturePost.ps", badarg="2")
    except AttributeError as e:
        assert str(e) == ("'super' object has no attribute 'badarg'")
    else:
        assert False, "Expected AttributeError"

    # Test other arguments. These are stored in the /HARDCOPY CCL.
    picture_file = f"{generated_path_engine}/MyPicturePost.jpg"
    pypost.file.save_picture(
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
    jpg_file = Path(generated_path_client) / "MyPicturePost.jpg"
    assert timeout_loop(jpg_file.exists, timeout=10.0)
    jpg_file.unlink()

    state_file_name = f"{generated_path_engine}/hardcopy_post.ccl"
    save_hardcopy_ccl = f"""
    STATE:
      State Filename = {state_file_name}
      Save State Mode = Overwrite
      Save State Objects = /HARDCOPY
    END
    >savestate
    """
    pypost.execute_ccl(save_hardcopy_ccl)
    expected_ccl = [
        "HARDCOPY:",
        "  Antialiasing = False",
        f"  Hardcopy Filename = {generated_path_engine}/MyPicturePost.jpg",
        "  Hardcopy Format = jpg",
        "  Hardcopy Tolerance = 0.030000",
        "  Image Height = 888",
        "  Image Scale = 200",
        "  Image Size Option = 4k",
        "  Image Width = 999",
        "  JPEG Image Quality = 55",
        "  Paper Orientation = Landscape",
        "  Paper Size = Letter",
        "  Print Line Width = 1",
        "  Print Quality = High",
        "  Transparent Background = True",
        "  Use Screen Size = False",
        "  White Background = True",
        "END",
    ]

    ccl_file_path = f"{generated_path_client}/hardcopy_post.ccl"
    reduced_lines = read_ccl_from_file(ccl_file_path)
    assert reduced_lines == expected_ccl

    picture_file = f"{generated_path_engine}/MyPicturePost.png"
    pypost.file.save_picture(
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
    png_file = Path(generated_path_client) / "MyPicturePost.png"
    assert timeout_loop(png_file.exists, timeout=10.0)
    png_file.unlink()

    pypost.execute_ccl(save_hardcopy_ccl)
    expected_ccl = [
        "HARDCOPY:",
        "  Antialiasing = False",
        f"  Hardcopy Filename = {generated_path_engine}/MyPicturePost.png",
        "  Hardcopy Format = png",
        "  Hardcopy Tolerance = 0.030000",
        "  Image Height = 888",
        "  Image Scale = 200",
        "  Image Size Option = 4k",
        "  Image Width = 999",
        "  JPEG Image Quality = 55",
        "  Paper Orientation = Landscape",
        "  Paper Size = Letter",
        "  Print Line Width = 1",
        "  Print Quality = High",
        "  Transparent Background = True",
        "  Use Screen Size = False",
        "  White Background = True",
        "END",
    ]
    ccl_file_path = f"{generated_path_client}/hardcopy_post.ccl"
    reduced_lines = read_ccl_from_file(ccl_file_path)
    assert reduced_lines == expected_ccl
    Path(ccl_file_path).unlink()


def test_case_functions(pypost: PostProcessing, pytestconfig, capsys):

    # Test setup
    generated_path_engine, generated_path_client = setup_write_dir(
        pytestconfig.test_data_directory_path, ["*.cfx"]
    )

    # Utility function to test if a case is open
    def is_case_open():
        case_names = pypost.results.data_reader.case.get_object_names()
        return len(case_names) > 0

    # No case open initially
    assert not is_case_open()

    # New case, test by saving and closing without error
    pypost.file.load_results(
        file_name=f"{pytestconfig.test_data_directory_path}/data/StaticMixer.def"
    )
    assert is_case_open()

    # Save state. There is no function to do this, so use CCL submission.
    state_file_client = f"{generated_path_client}/StaticMixer.cst"
    state_file_engine = f"{generated_path_engine}/StaticMixer.cst"
    save_state_ccl = f"""
    STATE:
      State Filename = {state_file_engine}
      Save State Mode = Overwrite
      Save State Objects =
    END
    >savestate
    """
    pypost.execute_ccl(save_state_ccl)
    assert timeout_loop(Path(state_file_client).exists, timeout=10.0)
    assert Path(state_file_client).stat().st_size > 0

    # Close case. There is no function to do this, so use CCL submission.
    pypost.execute_ccl(">close")
    assert not is_case_open()

    # Load state to check it was correctly written
    pypost.file.load_state(file_name=state_file_engine, mode="overwrite")
    assert is_case_open()
    try:  # Path.unlink sometimes can't remove the file. Make the test robust to this.
        Path(state_file_client).unlink()
    except FileNotFoundError:
        pass

    # Check arguments to load_state
    pypost.results.library.cel.expressions["InletTemp"] = {"definition": "330 [K]"}
    state_file_name = f"{pytestconfig.test_data_directory_path}/data/create_expression.cst"
    pypost.file.load_state(file_name=state_file_name, mode="append")
    assert pypost.results.library.cel.expressions["MyTime"].definition() == "7 [s]"
    assert pypost.results.library.cel.expressions["InletTemp"].definition() == "330 [K]"

    if pypost.get_cfx_version() > CFXVersion.v252:
        del pypost.results.library.cel.expressions["MyTime"]
    else:
        pypost.results.library.cel.expressions["MyTime"].definition = " "

    pypost.file.load_state(file_name=state_file_name, mode="overwrite")
    assert pypost.results.library.cel.expressions["MyTime"].definition() == "7 [s]"
    assert "InletTemp" not in pypost.results.library.cel.expressions.get_object_names()

    # Load session
    session_file_name = f"{pytestconfig.test_data_directory_path}/data/create_expression.cse"
    pypost.file.load_session(file_name=session_file_name)
    assert pypost.results.library.cel.expressions["MyTime"].definition() == "3 [s]"


def test_misc_functions(pypost: PostProcessing, pytestconfig):

    pypost.file.load_results(
        file_name=f"{pytestconfig.test_data_directory_path}/data/StaticMixer.def"
    )

    pypost.results.plane["Plane 1"] = {}
    plane1 = pypost.results.plane["Plane 1"]
    pypost.results.library.cel.expressions["NodeCount"] = {"definition": "count()@Plane 1"}

    node_count = pypost.results.library.cel.expressions["NodeCount"].evaluate()
    assert node_count == "0 []"
    plane1.option = "ZX Plane"
    plane1.plane_type = "Slice"
    node_count = pypost.results.library.cel.expressions["NodeCount"].evaluate()
    assert int(node_count.split(" ")[0]) > 0

    # Test suspend/unsuspend
    pypost.results.plane["Plane 2"] = {}
    plane2 = pypost.results.plane["Plane 2"]
    pypost.results.library.cel.expressions["NodeCount"].definition = "count()@Plane 2"

    node_count = pypost.results.library.cel.expressions["NodeCount"].evaluate()
    assert node_count == "0 []"
    plane2.suspend()
    plane2.option = "ZX Plane"
    plane2.plane_type = "Slice"
    node_count = pypost.results.library.cel.expressions["NodeCount"].evaluate()
    assert node_count == "0 []"
    plane2.unsuspend()
    node_count = pypost.results.library.cel.expressions["NodeCount"].evaluate()
    assert int(node_count.split(" ")[0]) > 0

    # Test show/hide
    view1vis = pypost.results.view["View 1"].object_visibility_list
    assert view1vis() == "/DEFAULT LEGEND:Default Legend View 1,/WIREFRAME:Wireframe"
    plane1.show()
    plane2.show(view="/VIEW:View 1")
    assert (
        view1vis()
        == "/DEFAULT LEGEND:Default Legend View 1,/PLANE:Plane 1,/PLANE:Plane 2,/WIREFRAME:Wireframe"
    )
    plane1.hide(view="/VIEW:View 3")
    assert (
        view1vis()
        == "/DEFAULT LEGEND:Default Legend View 1,/PLANE:Plane 1,/PLANE:Plane 2,/WIREFRAME:Wireframe"
    )
    plane1.hide(view="/VIEW:View 1")
    plane2.hide()
    assert view1vis() == "/DEFAULT LEGEND:Default Legend View 1,/WIREFRAME:Wireframe"
    plane1.show(view="/VIEW:View 3")
    assert view1vis() == "/DEFAULT LEGEND:Default Legend View 1,/WIREFRAME:Wireframe"
