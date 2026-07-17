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

import copy
import re

import pytest

from ansys.cfx.core.session_pre import PreProcessing
from ansys.cfx.core.utils.cfx_version import CFXVersion


def _round_mesh_stats(stats: dict, decimals: int = 2) -> dict:
    """Return a copy of a mesh statistics dictionary with floats rounded to *decimals* places.

    This allows comparison of mesh statistics without precision issues from floating point numbers.

    Handles three value types found in the dict:
    - ``int``  – returned unchanged.
    - ``float`` – rounded to *decimals* decimal places.
    - ``str`` with an embedded number (e.g. ``"99.624493 [m^3]"``) –
      the numeric part is rounded and the units suffix is preserved.
    """

    def _round_value(value):
        if isinstance(value, float):
            return round(value, decimals)
        if isinstance(value, str):
            match = re.fullmatch(r"(-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?)\s*(.*)", value)
            if match:
                number = round(float(match.group(1)), decimals)
                suffix = match.group(2)
                return f"{number} {suffix}".rstrip() if suffix else str(number)
        return value

    return {k: _round_value(v) for k, v in stats.items()}


def test_mesh_objects(pre_load_static_mixer_case: PreProcessing, pytestconfig):
    """Test for the handling of the mesh object."""

    pypre = pre_load_static_mixer_case

    if pypre.get_cfx_version() < CFXVersion.v271:
        pytest.skip("Mesh objects are not supported in Release 26.1 and earlier.")

    assert pypre.setup.mesh.get_object_names() == ["StaticMixerMesh"]

    pypre.file.import_mesh(
        file_name=f"{pytestconfig.test_data_directory_path}/data/StaticMixer.def"
    )
    assert pypre.setup.mesh.get_object_names() == ["StaticMixer", "StaticMixerMesh"]

    pypre.setup.mesh["StaticMixer"].rename("MeshFromDefFile")
    assert pypre.setup.mesh.get_object_names() == ["MeshFromDefFile", "StaticMixerMesh"]

    try:
        pypre.setup.mesh["MeshFromDefFile"].rename("StaticMixerMesh")
    except RuntimeError as e:
        assert str(e) == "A mesh object with the new name 'StaticMixerMesh' already exists."
    else:
        assert False, "Expected RuntimeError"

    try:
        pypre.setup.mesh["MeshFromDefFile"].rename("2ndMesh")
    except RuntimeError as e:
        assert str(e) == (
            "The name '2ndMesh' is not a valid mesh object name. Names must start "
            "with a letter and contain only letters, digits, and spaces."
        )
    else:
        assert False, "Expected RuntimeError"

    try:
        pypre.setup.mesh.create("NewMesh")
    except RuntimeError as e:
        assert str(e) == ("Creating mesh objects is not supported; use import_mesh() instead.")
    else:
        assert False, "Expected RuntimeError"

    attrs_list = [
        "active?",
        "webui-release-active?",
        "read-only?",
        "default",
        "min",
        "max",
        "user-creatable?",
        "allowed-values",
        "file-purpose",
        "sub-type",
    ]

    assert pypre.setup.mesh.get_attrs(attrs_list) == {
        "active?": True,
        "read-only?": True,
        "user-creatable?": False,
        "webui-release-active?": True,
    }
    assert pypre.setup.mesh["MeshFromDefFile"].get_attrs(attrs_list) == {
        "active?": True,
        "read-only?": True,
        "webui-release-active?": True,
    }
    assert pypre.setup.mesh["MeshFromDefFile"].file_path.get_attrs(attrs_list) == {
        "active?": True,
        "read-only?": True,
        "webui-release-active?": True,
    }

    all_mesh_state = pypre.setup.mesh.get_state()
    assert len(all_mesh_state) == 2
    assert all_mesh_state.keys() == {"MeshFromDefFile", "StaticMixerMesh"}

    mesh2_state = pypre.setup.mesh["MeshFromDefFile"].get_state()
    assert len(mesh2_state) == 1
    mesh2_file_path = mesh2_state["file_path"].replace("\\", "/")
    assert mesh2_file_path.endswith("data/StaticMixer.def")

    param_state = pypre.setup.mesh["MeshFromDefFile"].file_path.get_state()
    param_state_file_path = param_state.replace("\\", "/")
    assert param_state_file_path.endswith("data/StaticMixer.def")

    param_value = pypre.setup.mesh["MeshFromDefFile"].file_path()
    param_value_file_path = param_value.replace("\\", "/")
    assert param_value_file_path.endswith("data/StaticMixer.def")

    try:
        pypre.setup.mesh["MeshFromDefFile"].file_path = "new/path/to/StaticMixer.def"
    except RuntimeError as e:
        assert str(e) == "Parameter 'File Path' is read-only and cannot be set."
    else:
        assert False, "Expected RuntimeError"

    new_state = copy.deepcopy(all_mesh_state)
    new_state["MeshFromDefFile"]["file_path"] = "new/path/to/StaticMixer.def"
    try:
        pypre.setup.mesh = new_state
    except RuntimeError as e:
        assert str(e) == "Directly changing the state of mesh objects is not supported."
    else:
        assert False, "Expected RuntimeError"

    # There should be no error if the new state or parameter value is the same as the old one
    pypre.setup.mesh["MeshFromDefFile"].file_path = param_value
    pypre.setup.mesh = all_mesh_state

    try:
        del pypre.setup.mesh["BadMeshName"]
    except RuntimeError as e:
        assert str(e) == "Mesh object with name 'BadMeshName' not found for deletion."
    else:
        assert False, "Expected RuntimeError"

    del pypre.setup.mesh["MeshFromDefFile"]
    assert pypre.setup.mesh.get_object_names() == ["StaticMixerMesh"]


def test_mesh_statistics(pre_load_static_mixer_case: PreProcessing, pytestconfig):
    """Test for the get_mesh_statistics query."""

    pypre = pre_load_static_mixer_case

    if pypre.get_cfx_version() < CFXVersion.v271:
        pytest.skip("Mesh objects are not supported in Release 26.1 and earlier.")

    # Transform the mesh in order to make it easier to test for the other object types
    mesh_transformation_ccl = """
MESH TRANSFORMATION:
Delete Original = Off
Glue Copied = Off
Glue Reflected = Off
Number of Copies = 1
Option = Reflection
Reflection Method = Copy (Keep Original)
Reflection Option = XY Plane
Target Location = B1.P3
Use Multiple Copy = Off
Z Pos = 2.0
END
> update
> gtmTransform B1.P3
"""
    pypre.execute_ccl(mesh_transformation_ccl)

    pypre.setup.flow["Flow Analysis 1"].rigid_body["Rigid Body 1"] = {
        "location": "out 2",
        "mass": "1 [kg]",
        "rigid_body_coord_frame": "Coord 0",
        "dynamics": {
            "degrees_of_freedom": {
                "rotational_degrees_of_freedom": {"option": "None"},
                "translational_degrees_of_freedom": {"option": "None"},
            }
        },
        "mass_moment_of_inertia": {
            "xxvalue": "0.0001 [kg m^2]",
            "xyvalue": "0.0001 [kg m^2]",
            "xzvalue": "0.0001 [kg m^2]",
            "yyvalue": "0.0001 [kg m^2]",
            "yzvalue": "0.0001 [kg m^2]",
            "zzvalue": "0.0001 [kg m^2]",
        },
    }

    pypre.setup.flow["Flow Analysis 1"].domain_interface["Domain Interface 1"] = {
        "filter_domain_list1": "Default Domain",
        "filter_domain_list2": "Default Domain",
        "interface_region_list1": "F2.B1.P3",
        "interface_region_list2": "F2.B1.P3 2",
        "interface_type": "Fluid Fluid",
        "interface_models": {
            "option": "General Connection",
        },
        "mesh_connection": {"option": "Automatic"},
    }

    pypre.setup.flow["Flow Analysis 1"].domain["Default Domain"].subdomain["Subdomain 1"] = {
        "location": "B1.P3",
    }

    pypre.file.import_mesh(
        file_name=f"{pytestconfig.test_data_directory_path}/data/StaticMixer.def"
    )

    # All the mesh statistics are rounded to avoid precision issues with comparisons of floating
    # point numbers.
    all_mesh_stats = _round_mesh_stats(pypre.setup.mesh.get_mesh_statistics())
    assert all_mesh_stats == {
        "Elements": 41283,
        "Hexahedra": 0,
        "Maximum Edge Length Ratio": 4.95,
        "Maximum X": "2.0 [m]",
        "Maximum Y": "3.0 [m]",
        "Maximum Z": "6.0 [m]",
        "Minimum X": "-2.0 [m]",
        "Minimum Y": "-3.0 [m]",
        "Minimum Z": "-2.0 [m]",
        "Nodes": 8358,
        "Pyramids": 0,
        "Tetrahedra": 41283,
        "Volume": "99.62 [m^3]",
        "Wedges": 0,
    }

    mesh_stats = _round_mesh_stats(pypre.setup.mesh["StaticMixerMesh"].get_mesh_statistics())
    assert mesh_stats == {
        "Elements": 27522,
        "Hexahedra": 0,
        "Maximum Edge Length Ratio": 4.95,
        "Maximum X": "2.0 [m]",
        "Maximum Y": "3.0 [m]",
        "Maximum Z": "6.0 [m]",
        "Minimum X": "-2.0 [m]",
        "Minimum Y": "-3.0 [m]",
        "Minimum Z": "-2.0 [m]",
        "Nodes": 5572,
        "Pyramids": 0,
        "Tetrahedra": 27522,
        "Volume": "66.42 [m^3]",
        "Wedges": 0,
    }

    domain_stats = _round_mesh_stats(
        pypre.setup.flow["Flow Analysis 1"].domain["Default Domain"].get_mesh_statistics()
    )
    assert domain_stats == all_mesh_stats

    boundary_stats = _round_mesh_stats(
        pypre.setup.flow["Flow Analysis 1"]
        .domain["Default Domain"]
        .boundary["out"]
        .get_mesh_statistics()
    )
    assert boundary_stats == {
        "Area": "0.71 [m^2]",
        "Elements": 20,
        "Maximum Edge Length Ratio": 2.49,
        "Maximum X": "0.5 [m]",
        "Maximum Y": "0.5 [m]",
        "Maximum Z": "-2.0 [m]",
        "Minimum X": "-0.5 [m]",
        "Minimum Y": "-0.5 [m]",
        "Minimum Z": "-2.0 [m]",
        "Nodes": 15,
        "Quadrilaterals": 0,
        "Triangles": 20,
    }

    subdomain_stats = _round_mesh_stats(
        pypre.setup.flow["Flow Analysis 1"]
        .domain["Default Domain"]
        .subdomain["Subdomain 1"]
        .get_mesh_statistics()
    )
    assert subdomain_stats == {
        "Elements": 13761,
        "Hexahedra": 0,
        "Maximum Edge Length Ratio": 4.95,
        "Maximum X": "2.0 [m]",
        "Maximum Y": "3.0 [m]",
        "Maximum Z": "2.0 [m]",
        "Minimum X": "-2.0 [m]",
        "Minimum Y": "-3.0 [m]",
        "Minimum Z": "-2.0 [m]",
        "Nodes": 2786,
        "Pyramids": 0,
        "Tetrahedra": 13761,
        "Volume": "33.21 [m^3]",
        "Wedges": 0,
    }

    domain_interface_stats = _round_mesh_stats(
        pypre.setup.flow["Flow Analysis 1"]
        .domain_interface["Domain Interface 1"]
        .get_mesh_statistics()
    )
    assert domain_interface_stats == {
        "Area": "24.97 [m^2]",
        "Elements": 552,
        "Maximum Edge Length Ratio": 2.63,
        "Maximum X": "2.0 [m]",
        "Maximum Y": "2.0 [m]",
        "Maximum Z": "2.0 [m]",
        "Minimum X": "-2.0 [m]",
        "Minimum Y": "-2.0 [m]",
        "Minimum Z": "2.0 [m]",
        "Nodes": 310,
        "Quadrilaterals": 0,
        "Triangles": 552,
    }

    rigid_body_stats = _round_mesh_stats(
        pypre.setup.flow["Flow Analysis 1"].rigid_body["Rigid Body 1"].get_mesh_statistics()
    )
    assert rigid_body_stats == {
        "Area": "0.71 [m^2]",
        "Elements": 20,
        "Maximum Edge Length Ratio": 2.49,
        "Maximum X": "0.5 [m]",
        "Maximum Y": "0.5 [m]",
        "Maximum Z": "6.0 [m]",
        "Minimum X": "-0.5 [m]",
        "Minimum Y": "-0.5 [m]",
        "Minimum Z": "6.0 [m]",
        "Nodes": 15,
        "Quadrilaterals": 0,
        "Triangles": 20,
    }


def check_boundary_position(pypre, boundary, min_x, max_x, min_y, max_y, min_z, max_z, area=None):
    """
    Check the position of a boundary in the mesh. It is assumed that the boundary is based
    on "in1" or a copy of "in1", so that the stats on numbers of mesh elements match.

    Parameters
    ----------
    pypre : PreProcessing
        The pre-processing object.
    boundary : str
        The name of the boundary to check.
    min_x, max_x, min_y, max_y, min_z, max_z : str
        The expected minimum and maximum coordinates of the boundary.
    area : str | None
        Optional expected boundary area (e.g. "2.83 [m^2]"). If None, defaults to the original
        area of in1 ("0.71 [m^2]").
    """

    expected_stats = {
        "Area": "0.71 [m^2]",
        "Elements": 14,
        "Maximum Edge Length Ratio": 2.76,
        "Maximum X": max_x,
        "Maximum Y": max_y,
        "Maximum Z": max_z,
        "Minimum X": min_x,
        "Minimum Y": min_y,
        "Minimum Z": min_z,
        "Nodes": 12,
        "Quadrilaterals": 0,
        "Triangles": 14,
    }
    if area is not None:
        expected_stats["Area"] = area
    assert (
        _round_mesh_stats(
            pypre.setup.flow["Flow Analysis 1"]
            .domain["Default Domain"]
            .boundary[boundary]
            .get_mesh_statistics()
        )
        == expected_stats
    )


def test_mesh_transformation(pre_load_static_mixer_case: PreProcessing, pytestconfig):
    """Test mesh transformations performed via transform_mesh()."""

    pypre = pre_load_static_mixer_case

    if pypre.get_cfx_version() < CFXVersion.v271:
        pytest.skip("Mesh objects are not supported in Release 26.1 and earlier.")

    original_volume_stats = _round_mesh_stats(
        pypre.setup.mesh["StaticMixerMesh"].get_mesh_statistics()
    )
    original_in1_stats = _round_mesh_stats(
        pypre.setup.flow["Flow Analysis 1"]
        .domain["Default Domain"]
        .boundary["in1"]
        .get_mesh_statistics()
    )

    # Default transform (no change)
    pypre.setup.mesh["StaticMixerMesh"].transform_mesh()
    assert (
        _round_mesh_stats(pypre.setup.mesh["StaticMixerMesh"].get_mesh_statistics())
        == original_volume_stats
    )
    assert (
        _round_mesh_stats(
            pypre.setup.flow["Flow Analysis 1"]
            .domain["Default Domain"]
            .boundary["in1"]
            .get_mesh_statistics()
        )
        == original_in1_stats
    )

    pypre.setup.mesh["StaticMixerMesh"].transform_mesh(
        option="Reflection",
        reflection_option="XY Plane",
    )
    check_boundary_position(
        pypre, "in1", "-1.5 [m]", "-0.5 [m]", "-3.0 [m]", "-3.0 [m]", "-1.5 [m]", "-0.5 [m]"
    )
    pypre.file.undo()

    # Check that the undo has worked
    assert (
        _round_mesh_stats(
            pypre.setup.flow["Flow Analysis 1"]
            .domain["Default Domain"]
            .boundary["in1"]
            .get_mesh_statistics()
        )
        == original_in1_stats
    )

    pypre.setup.mesh["StaticMixerMesh"].transform_mesh(
        option="Reflection",
        reflection_option="XY Plane",
        z="2.0 [m]",
        reflection_method="Copy (Keep Original)",
    )
    check_boundary_position(
        pypre, "in1", "-1.5 [m]", "-0.5 [m]", "-3.0 [m]", "-3.0 [m]", "0.5 [m]", "1.5 [m]"
    )
    # We can't yet check stats for individual regions, so create a boundary for "in1 2" in order
    # to check its stats.
    pypre.setup.flow["Flow Analysis 1"].domain["Default Domain"].boundary.create("in1 2")
    pypre.setup.flow["Flow Analysis 1"].domain["Default Domain"].boundary[
        "in1 2"
    ].location = "in1 2"
    check_boundary_position(
        pypre, "in1 2", "-1.5 [m]", "-0.5 [m]", "-3.0 [m]", "-3.0 [m]", "2.5 [m]", "3.5 [m]"
    )
    pypre.file.undo()  # create boundary
    pypre.file.undo()  # transform mesh

    pypre.setup.mesh["StaticMixerMesh"].transform_mesh(
        option="Reflection",
        reflection_option="YZ Plane",
        x="7000 [mm]",
        reflection_method="Original (No Copy)",
    )
    check_boundary_position(
        pypre, "in1", "14.5 [m]", "15.5 [m]", "-3.0 [m]", "-3.0 [m]", "0.5 [m]", "1.5 [m]"
    )
    pypre.file.undo()

    pypre.setup.mesh["StaticMixerMesh"].transform_mesh(
        option="Reflection",
        reflection_option="YZ Plane",
        x="7",
        reflection_method="Original (No Copy)",
    )
    check_boundary_position(
        pypre, "in1", "14.5 [m]", "15.5 [m]", "-3.0 [m]", "-3.0 [m]", "0.5 [m]", "1.5 [m]"
    )
    pypre.file.undo()

    pypre.setup.mesh["StaticMixerMesh"].transform_mesh(
        option="Scale",
        scale_option="Uniform",
        scale_origin="0 [m], 200 [cm], 0 [m]",
        uniform_scale="2.0",
    )
    check_boundary_position(
        pypre,
        "in1",
        "-3.0 [m]",
        "-1.0 [m]",
        "-8.0 [m]",
        "-8.0 [m]",
        "1.0 [m]",
        "3.0 [m]",
        area="2.83 [m^2]",
    )
    pypre.file.undo()

    pypre.setup.mesh["StaticMixerMesh"].transform_mesh(
        option="Translation",
        translation_option="Deltas",
        translation_deltas="3 [m], 400 [cm], 5",
        use_multiple_copy=True,
        number_of_copies=2,
    )
    check_boundary_position(
        pypre, "in1", "-1.5 [m]", "-0.5 [m]", "-3.0 [m]", "-3.0 [m]", "0.5 [m]", "1.5 [m]"
    )
    pypre.setup.flow["Flow Analysis 1"].domain["Default Domain"].boundary.create("in1 2")
    pypre.setup.flow["Flow Analysis 1"].domain["Default Domain"].boundary[
        "in1 2"
    ].location = "in1 2"
    check_boundary_position(
        pypre, "in1 2", "1.5 [m]", "2.5 [m]", "1.0 [m]", "1.0 [m]", "5.5 [m]", "6.5 [m]"
    )
    pypre.file.undo()  # create boundary
    pypre.file.undo()  # transform mesh

    pypre.setup.mesh["StaticMixerMesh"].transform_mesh(
        option="Rotation",
        rotation_option="Principal Axis",
        principal_axis="Y",
        rotation_angle_option="Specified",
        rotation_angle="45 [deg]",
        delete_original=True,
        use_multiple_copy=False,
    )
    check_boundary_position(
        pypre, "in1", "-0.5 [m]", "0.5 [m]", "-3.0 [m]", "-3.0 [m]", "0.91 [m]", "1.91 [m]"
    )
    pypre.file.undo()

    pypre.setup.mesh["StaticMixerMesh"].transform_mesh(
        option="Turbo Rotation",
        rotation_option="Rotation Axis",
        rotation_axis_begin="0, 0, 4",
        rotation_axis_end="0 [m], 1 [m], 4 [m]",
        passages_per_mesh=1,
        passages_to_model=2,
        passages_in_360=4,
        theta_offset="45 [deg]",
    )
    check_boundary_position(
        pypre, "in1", "-3.33 [m]", "-2.33 [m]", "-3.0 [m]", "-3.0 [m]", "2.09 [m]", "3.09 [m]"
    )
    pypre.setup.flow["Flow Analysis 1"].domain["Default Domain"].boundary.create("in1 2")
    pypre.setup.flow["Flow Analysis 1"].domain["Default Domain"].boundary[
        "in1 2"
    ].location = "in1 2"
    check_boundary_position(
        pypre, "in1 2", "-1.91 [m]", "-0.91 [m]", "-3.0 [m]", "-3.0 [m]", "6.33 [m]", "7.33 [m]"
    )
    pypre.file.undo()  # create boundary
    pypre.file.undo()  # transform mesh


def test_mesh_region_queries(pre_load_static_mixer_case: PreProcessing, pytestconfig):
    """Test mesh region queries."""

    pypre = pre_load_static_mixer_case

    if pypre.get_cfx_version() < CFXVersion.v271:
        pytest.skip("Mesh objects are not supported in Release 26.1 and earlier.")

    assert pypre.setup.mesh["StaticMixerMesh"].get_assemblies() == ["Assembly"]
    assert pypre.setup.mesh["StaticMixerMesh"].get_composite_3d_regions() == []
    assert pypre.setup.mesh["StaticMixerMesh"].get_primitive_3d_regions() == ["B1.P3"]
    assert pypre.setup.mesh["StaticMixerMesh"].get_all_3d_regions() == ["B1.P3"]
    assert pypre.setup.mesh["StaticMixerMesh"].get_composite_bounding_2d_regions_for_3d_region(
        region="Assembly"
    ) == ["Default 2D Region", "in1", "in2", "out"]
    assert pypre.setup.mesh["StaticMixerMesh"].get_primitive_bounding_2d_regions_for_3d_region(
        region="Assembly"
    ) == [
        "F1.B1.P3",
        "F2.B1.P3",
        "F3.B1.P3",
        "F4.B1.P3",
        "F5.B1.P3",
        "F6.B1.P3",
        "F7.B1.P3",
        "F8.B1.P3",
        "F9.B1.P3",
    ]
    assert pypre.setup.mesh["StaticMixerMesh"].get_all_bounding_2d_regions_for_3d_region(
        region="Assembly"
    ) == [
        "Default 2D Region",
        "F1.B1.P3",
        "F2.B1.P3",
        "F3.B1.P3",
        "F4.B1.P3",
        "F5.B1.P3",
        "F6.B1.P3",
        "F7.B1.P3",
        "F8.B1.P3",
        "F9.B1.P3",
        "in1",
        "in2",
        "out",
    ]

    assert pypre.setup.mesh["StaticMixerMesh"].get_composite_bounding_2d_regions_for_3d_region(
        region="B1.P3"
    ) == ["Default 2D Region", "in1", "in2", "out"]
    assert pypre.setup.mesh["StaticMixerMesh"].get_primitive_bounding_2d_regions_for_3d_region(
        region="B1.P3"
    ) == [
        "F1.B1.P3",
        "F2.B1.P3",
        "F3.B1.P3",
        "F4.B1.P3",
        "F5.B1.P3",
        "F6.B1.P3",
        "F7.B1.P3",
        "F8.B1.P3",
        "F9.B1.P3",
    ]
    assert pypre.setup.mesh["StaticMixerMesh"].get_all_bounding_2d_regions_for_3d_region(
        region="B1.P3"
    ) == [
        "Default 2D Region",
        "F1.B1.P3",
        "F2.B1.P3",
        "F3.B1.P3",
        "F4.B1.P3",
        "F5.B1.P3",
        "F6.B1.P3",
        "F7.B1.P3",
        "F8.B1.P3",
        "F9.B1.P3",
        "in1",
        "in2",
        "out",
    ]

    assert pypre.setup.mesh["StaticMixerMesh"].get_composite_3d_regions_for_3d_region(
        region="B1.P3"
    ) == []
    assert pypre.setup.mesh["StaticMixerMesh"].get_composite_3d_regions_for_3d_region(
        region="Assembly"
    ) == []
    assert pypre.setup.mesh["StaticMixerMesh"].get_primitive_3d_regions_for_3d_region(
        region="B1.P3"
    ) == ["B1.P3"]
    assert pypre.setup.mesh["StaticMixerMesh"].get_primitive_3d_regions_for_3d_region(
        region="Assembly"
    ) == ["B1.P3"]

    # Transform the mesh to create a second 3D region
    pypre.setup.mesh["StaticMixerMesh"].transform_mesh(
        option="Turbo Rotation",
        rotation_option="Rotation Axis",
        rotation_axis_begin="0, 0, 4",
        rotation_axis_end="0 [m], 1 [m], 4 [m]",
        passages_per_mesh=1,
        passages_to_model=2,
        passages_in_360=4,
        theta_offset="45 [deg]",
    )

    assert pypre.setup.mesh["StaticMixerMesh"].get_assemblies() == ["Assembly", "Assembly 2"]
    assert pypre.setup.mesh["StaticMixerMesh"].get_composite_3d_regions() == []
    assert pypre.setup.mesh["StaticMixerMesh"].get_primitive_3d_regions() == ["B1.P3", "B1.P3 2"]
    assert pypre.setup.mesh["StaticMixerMesh"].get_all_3d_regions() == ["B1.P3", "B1.P3 2"]
    assert pypre.setup.mesh["StaticMixerMesh"].get_composite_bounding_2d_regions_for_3d_region(
        region="Assembly"
    ) == ["Default 2D Region", "in1", "in2", "out"]
    assert pypre.setup.mesh["StaticMixerMesh"].get_primitive_bounding_2d_regions_for_3d_region(
        region="Assembly"
    ) == [
        "F1.B1.P3",
        "F2.B1.P3",
        "F3.B1.P3",
        "F4.B1.P3",
        "F5.B1.P3",
        "F6.B1.P3",
        "F7.B1.P3",
        "F8.B1.P3",
        "F9.B1.P3",
    ]
    assert pypre.setup.mesh["StaticMixerMesh"].get_all_bounding_2d_regions_for_3d_region(
        region="Assembly 2"
    ) == [
        "Default 2D Region 2",
        "F1.B1.P3 2",
        "F2.B1.P3 2",
        "F3.B1.P3 2",
        "F4.B1.P3 2",
        "F5.B1.P3 2",
        "F6.B1.P3 2",
        "F7.B1.P3 2",
        "F8.B1.P3 2",
        "F9.B1.P3 2",
        "in1 2",
        "in2 2",
        "out 2",
    ]
    assert pypre.setup.mesh["StaticMixerMesh"].get_composite_bounding_2d_regions_for_3d_region(
        region="B1.P3 2"
    ) == ["Default 2D Region 2", "in1 2", "in2 2", "out 2"]
    assert pypre.setup.mesh["StaticMixerMesh"].get_primitive_bounding_2d_regions_for_3d_region(
        region="B1.P3"
    ) == [
        "F1.B1.P3",
        "F2.B1.P3",
        "F3.B1.P3",
        "F4.B1.P3",
        "F5.B1.P3",
        "F6.B1.P3",
        "F7.B1.P3",
        "F8.B1.P3",
        "F9.B1.P3",
    ]

    assert (
        pypre.setup.mesh["StaticMixerMesh"].get_bounded_3d_region_for_2d_primitive(
            region="F1.B1.P3"
        )
        == "B1.P3"
    )
    assert (
        pypre.setup.mesh["StaticMixerMesh"].get_bounded_3d_region_for_2d_primitive(
            region="F8.B1.P3 2"
        )
        == "B1.P3 2"
    )

    # Undo the mesh transformation to restore the original mesh state
    pypre.file.undo()

    pypre.file.import_mesh(
        file_name=f"{pytestconfig.test_data_directory_path}/data/StaticMixer.def"
    )

    # Create some regions across the two meshes
    pypre.execute_ccl(
        ">gtmAction op=createComposite,TwoDomains,Union,B1.P3,B1.P3 2\n"
        ">gtmAction op=createComposite,TwoRegions,Union,F3.B1.P3,F6.B1.P3 2\n"
    )

    assert pypre.setup.mesh.get_assemblies() == ["Assembly", "Assembly 2"]
    assert pypre.setup.mesh.get_composite_3d_regions() == ["TwoDomains"]
    assert pypre.setup.mesh.get_primitive_3d_regions() == ["B1.P3", "B1.P3 2"]
    assert pypre.setup.mesh.get_all_3d_regions() == ["B1.P3", "B1.P3 2", "TwoDomains"]
    assert pypre.setup.mesh.get_composite_bounding_2d_regions_for_3d_region(
        region="TwoDomains"
    ) == [
        "Default 2D Region",
        "Default 2D Region 2",
        "TwoRegions",
        "in1",
        "in1 2",
        "in2",
        "in2 2",
        "out",
        "out 2",
    ]
    assert pypre.setup.mesh.get_primitive_bounding_2d_regions_for_3d_region(
        region="TwoDomains"
    ) == [
        "F1.B1.P3",
        "F1.B1.P3 2",
        "F2.B1.P3",
        "F2.B1.P3 2",
        "F3.B1.P3",
        "F3.B1.P3 2",
        "F4.B1.P3",
        "F4.B1.P3 2",
        "F5.B1.P3",
        "F5.B1.P3 2",
        "F6.B1.P3",
        "F6.B1.P3 2",
        "F7.B1.P3",
        "F7.B1.P3 2",
        "F8.B1.P3",
        "F8.B1.P3 2",
        "F9.B1.P3",
        "F9.B1.P3 2",
    ]
    assert pypre.setup.mesh.get_all_bounding_2d_regions_for_3d_region(region="TwoDomains") == [
        "Default 2D Region",
        "Default 2D Region 2",
        "F1.B1.P3",
        "F1.B1.P3 2",
        "F2.B1.P3",
        "F2.B1.P3 2",
        "F3.B1.P3",
        "F3.B1.P3 2",
        "F4.B1.P3",
        "F4.B1.P3 2",
        "F5.B1.P3",
        "F5.B1.P3 2",
        "F6.B1.P3",
        "F6.B1.P3 2",
        "F7.B1.P3",
        "F7.B1.P3 2",
        "F8.B1.P3",
        "F8.B1.P3 2",
        "F9.B1.P3",
        "F9.B1.P3 2",
        "TwoRegions",
        "in1",
        "in1 2",
        "in2",
        "in2 2",
        "out",
        "out 2",
    ]

    assert (
        pypre.setup.mesh["StaticMixerMesh"].get_bounded_3d_region_for_2d_primitive(
            region="F1.B1.P3"
        )
        == "B1.P3"
    )
    assert (
        pypre.setup.mesh["StaticMixerMesh"].get_bounded_3d_region_for_2d_primitive(
            region="F8.B1.P3 2"
        )
        == "B1.P3 2"
    )

    try:
        pypre.setup.mesh["StaticMixerMesh"].get_bounded_3d_region_for_2d_primitive(
            region="TwoRegions"
        )
    except RuntimeError as e:
        assert str(e) == '"TwoRegions" is not a primitive region.\n'
    else:
        assert False, "Expected RuntimeError"

    assert pypre.setup.mesh.get_composite_3d_regions_for_3d_region(
        region="B1.P3"
    ) == []
    assert pypre.setup.mesh.get_composite_3d_regions_for_3d_region(
        region="TwoDomains"
    ) == ["TwoDomains"]

    assert pypre.setup.mesh.get_primitive_3d_regions_for_3d_region(
        region="TwoDomains"
    ) == ["B1.P3", "B1.P3 2"]
    assert pypre.setup.mesh.get_primitive_3d_regions_for_3d_region(
        region="B1.P3 2"
    ) == ["B1.P3 2"]
