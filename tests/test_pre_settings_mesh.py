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
    assert len(param_state) == 1
    param_state_file_path = param_state[0].replace("\\", "/")
    assert param_state_file_path.endswith("data/StaticMixer.def")

    param_value = pypre.setup.mesh["MeshFromDefFile"].file_path()
    assert len(param_value) == 1
    param_value_file_path = param_value[0].replace("\\", "/")
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
