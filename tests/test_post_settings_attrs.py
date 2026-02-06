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


def test_post_attributes(pypost: PostProcessing, pytestconfig, capsys):

    pypost.file.load_results(
        file_name=f"{pytestconfig.test_data_directory_path}/data/StaticMixer.def"
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

    # Top level
    try:
        pypost.get_attrs(attrs=attrs_list) == {
            "active?": True,
            "read-only?": False,
            "webui-release-active?": True,
        }
    except AttributeError as e:
        assert str(e) == "'SettingsRoot' object has no attribute 'get_attrs'"
    else:
        assert False, "Expected AttributeError"

    # Menu level
    assert pypost.results.get_attrs(attrs=attrs_list) == {
        "active?": True,
        "read-only?": False,
        "webui-release-active?": True,
    }

    # Named object type, user-defined name
    assert pypost.results.plane.get_attrs(attrs=attrs_list) == {
        "active?": True,
        "read-only?": False,
        "user-creatable?": True,
        "webui-release-active?": True,
    }

    # Named object, user-defined name
    assert pypost.results.plane["Plane 1"].get_attrs(attrs=attrs_list) == {
        "active?": True,
        "read-only?": False,
        "webui-release-active?": True,
    }

    # Parameter with allowed values
    assert pypost.results.plane["Plane 1"].option.get_attrs(attrs=attrs_list) == {
        "active?": True,
        "allowed-values": ["Point and Normal", "Three Points", "XY Plane", "YZ Plane", "ZX Plane"],
        "default": "XY Plane",
        "read-only?": False,
        "webui-release-active?": True,
    }

    # Numerical parameter with min/max
    # The min/max are not part of the attributes for PostProcessing
    assert pypost.results.plane["Plane 1"].bound_radius.get_attrs(attrs=attrs_list) == {
        "active?": True,
        "default": "0.5 [m]",
        "read-only?": False,
        "webui-release-active?": True,
    }

    # Read-only object type
    assert pypost.results.case.get_attrs(attrs=attrs_list) == {
        "active?": True,
        "read-only?": True,
        "user-creatable?": True,
        "webui-release-active?": True,
    }

    # Read-only object
    assert pypost.results.data_reader.case["Case StaticMixer"].get_attrs(attrs=attrs_list) == {
        "active?": True,
        "read-only?": True,
        "webui-release-active?": True,
    }

    # Read-only parameter
    assert pypost.results.data_reader.case["Case StaticMixer"].file_length_units.get_attrs(
        attrs=attrs_list
    ) == {
        "active?": True,
        "default": "m",
        "read-only?": False,
        "webui-release-active?": True,
    }

    # Function outside of CCL
    assert pypost.file.load_results.get_attrs(attrs=attrs_list) == {
        "active?": True,
        "read-only?": False,
        "webui-release-active?": True,
    }

    # Function argument
    assert pypost.file.load_results.file_name.get_attrs(attrs=attrs_list) == None

    # Function within CCL
    assert pypost.results.library.cel.expressions["atstep"].evaluate.get_attrs(
        attrs=attrs_list
    ) == {
        "active?": True,
        "read-only?": False,
        "webui-release-active?": True,
    }

    # Recursive attributes
    if pypost.get_cfx_version() > CFXVersion.v252:
        assert pypost.results.plane["Plane 1"].get_attrs(attrs=attrs_list, recursive=True) == {
            "attrs": {"active?": True, "read-only?": False, "webui-release-active?": True},
            "group_children": {
                "Apply Instancing Transform": {
                    "attrs": {
                        "active?": True,
                        "default": True,
                        "read-only?": False,
                        "webui-release-active?": True,
                    }
                },
                "Apply Texture": {
                    "attrs": {
                        "active?": True,
                        "default": False,
                        "read-only?": False,
                        "webui-release-active?": True,
                    }
                },
                "Blend Texture": {
                    "attrs": {
                        "active?": True,
                        "default": True,
                        "read-only?": False,
                        "webui-release-active?": True,
                    }
                },
                "Bound Radius": {
                    "attrs": {
                        "active?": True,
                        "default": "0.5 [m]",
                        "read-only?": False,
                        "webui-release-active?": True,
                    }
                },
                "Colour": {
                    "attrs": {
                        "active?": True,
                        "default": ["0.75", "0.75", "0.75"],
                        "read-only?": False,
                        "webui-release-active?": True,
                    }
                },
                "Colour Map": {
                    "attrs": {
                        "active?": True,
                        "default": "Default Colour Map",
                        "read-only?": False,
                        "webui-release-active?": True,
                    }
                },
                "Colour Mode": {
                    "attrs": {
                        "active?": True,
                        "allowed-values": [
                            "Animated " "Time",
                            "Constant",
                            "Time",
                            "Unique",
                            "Use Plot " "Variable",
                            "Variable",
                        ],
                        "default": "Constant",
                        "read-only?": False,
                        "webui-release-active?": True,
                    }
                },
                "Colour Scale": {
                    "attrs": {
                        "active?": True,
                        "allowed-values": ["Linear", "Logarithmic"],
                        "default": "Linear",
                        "read-only?": False,
                        "webui-release-active?": True,
                    }
                },
                "Colour Variable": {
                    "attrs": {
                        "active?": True,
                        "default": "",
                        "read-only?": False,
                        "webui-release-active?": True,
                    }
                },
                "Colour Variable Boundary Values": {
                    "attrs": {
                        "active?": True,
                        "allowed-values": ["Conservative", "Hybrid"],
                        "default": "Hybrid",
                        "read-only?": False,
                        "webui-release-active?": True,
                    }
                },
                "Culling Mode": {
                    "attrs": {
                        "active?": True,
                        "allowed-values": ["Back Faces", "Front Faces", "No Culling"],
                        "default": "No Culling",
                        "read-only?": False,
                        "webui-release-active?": True,
                    }
                },
                "Direction 1 Bound": {
                    "attrs": {
                        "active?": True,
                        "default": "1.0 [m]",
                        "read-only?": False,
                        "webui-release-active?": True,
                    }
                },
                "Direction 1 Orientation": {
                    "attrs": {
                        "active?": True,
                        "default": "0 [degree]",
                        "read-only?": False,
                        "webui-release-active?": True,
                    }
                },
                "Direction 1 Points": {
                    "attrs": {
                        "active?": True,
                        "default": 10,
                        "read-only?": False,
                        "webui-release-active?": True,
                    }
                },
                "Direction 2 Bound": {
                    "attrs": {
                        "active?": True,
                        "default": "1.0 [m]",
                        "read-only?": False,
                        "webui-release-active?": True,
                    }
                },
                "Direction 2 Points": {
                    "attrs": {
                        "active?": True,
                        "default": 10,
                        "read-only?": False,
                        "webui-release-active?": True,
                    }
                },
                "Domain List": {
                    "attrs": {
                        "active?": True,
                        "default": ["All Domains"],
                        "read-only?": False,
                        "webui-release-active?": True,
                    }
                },
                "Draw Contours": {
                    "attrs": {
                        "active?": True,
                        "default": False,
                        "read-only?": False,
                        "webui-release-active?": True,
                    }
                },
                "Draw Faces": {
                    "attrs": {
                        "active?": True,
                        "default": True,
                        "read-only?": False,
                        "webui-release-active?": True,
                    }
                },
                "Draw Lines": {
                    "attrs": {
                        "active?": True,
                        "default": False,
                        "read-only?": False,
                        "webui-release-active?": True,
                    }
                },
                "Instancing Transform": {
                    "attrs": {
                        "active?": True,
                        "default": "Default Transform",
                        "read-only?": False,
                        "webui-release-active?": True,
                    }
                },
                "Invert Plane Bound": {
                    "attrs": {
                        "active?": True,
                        "default": False,
                        "read-only?": False,
                        "webui-release-active?": True,
                    }
                },
                "Lighting": {
                    "attrs": {
                        "active?": True,
                        "default": True,
                        "read-only?": False,
                        "webui-release-active?": True,
                    }
                },
                "Line Colour": {
                    "attrs": {
                        "active?": True,
                        "default": ["0", "0", "0"],
                        "read-only?": False,
                        "webui-release-active?": True,
                    }
                },
                "Line Colour Mode": {
                    "attrs": {
                        "active?": True,
                        "allowed-values": ["Default", "User " "Specified"],
                        "default": "Default",
                        "read-only?": False,
                        "webui-release-active?": True,
                    }
                },
                "Line Width": {
                    "attrs": {
                        "active?": True,
                        "default": 1,
                        "read-only?": False,
                        "webui-release-active?": True,
                    }
                },
                "Max": {
                    "attrs": {
                        "active?": True,
                        "default": None,
                        "read-only?": False,
                        "webui-release-active?": True,
                    }
                },
                "Min": {
                    "attrs": {
                        "active?": True,
                        "default": None,
                        "read-only?": False,
                        "webui-release-active?": True,
                    }
                },
                "Normal": {
                    "attrs": {
                        "active?": True,
                        "default": ["1.0", "0.0", "0.0"],
                        "read-only?": False,
                        "webui-release-active?": True,
                    }
                },
                "Number of Contours": {
                    "attrs": {
                        "active?": True,
                        "default": 11,
                        "read-only?": False,
                        "webui-release-active?": True,
                    }
                },
                "OBJECT VIEW TRANSFORM": {
                    "attrs": {"active?": True, "read-only?": False, "webui-release-active?": True},
                    "group_children": {
                        "Apply Reflection": {
                            "attrs": {
                                "active?": True,
                                "default": False,
                                "read-only?": False,
                                "webui-release-active?": True,
                            }
                        },
                        "Apply Rotation": {
                            "attrs": {
                                "active?": True,
                                "default": True,
                                "read-only?": False,
                                "webui-release-active?": True,
                            }
                        },
                        "Apply Scale": {
                            "attrs": {
                                "active?": True,
                                "default": True,
                                "read-only?": False,
                                "webui-release-active?": True,
                            }
                        },
                        "Apply Translation": {
                            "attrs": {
                                "active?": True,
                                "default": False,
                                "read-only?": False,
                                "webui-release-active?": True,
                            }
                        },
                        "Principal Axis": {
                            "attrs": {
                                "active?": True,
                                "allowed-values": ["X", "Y", "Z"],
                                "default": "Z",
                                "read-only?": False,
                                "webui-release-active?": True,
                            }
                        },
                        "Reflection Plane": {
                            "attrs": {
                                "active?": True,
                                "default": "",
                                "read-only?": False,
                                "webui-release-active?": True,
                            }
                        },
                        "Reflection Plane Option": {
                            "attrs": {
                                "active?": True,
                                "allowed-values": [
                                    "From " "Plane",
                                    "XY " "Plane",
                                    "YZ " "Plane",
                                    "ZX " "Plane",
                                ],
                                "default": "From " "Plane",
                                "read-only?": False,
                                "webui-release-active?": True,
                            }
                        },
                        "Rotation Angle": {
                            "attrs": {
                                "active?": True,
                                "default": "0 " "[degree]",
                                "read-only?": False,
                                "webui-release-active?": True,
                            }
                        },
                        "Rotation Axis From": {
                            "attrs": {
                                "active?": True,
                                "default": ["0.0", "0.0", "0.0"],
                                "read-only?": False,
                                "webui-release-active?": True,
                            }
                        },
                        "Rotation Axis To": {
                            "attrs": {
                                "active?": True,
                                "default": ["1.0", "0.0", "0.0"],
                                "read-only?": False,
                                "webui-release-active?": True,
                            }
                        },
                        "Rotation Axis Type": {
                            "attrs": {
                                "active?": True,
                                "allowed-values": ["Principal " "Axis", "Rotation " "Axis"],
                                "default": "Principal " "Axis",
                                "read-only?": False,
                                "webui-release-active?": True,
                            }
                        },
                        "Scale Vector": {
                            "attrs": {
                                "active?": True,
                                "default": ["1.0", "1.0", "1.0"],
                                "read-only?": False,
                                "webui-release-active?": True,
                            }
                        },
                        "Translation Vector": {
                            "attrs": {
                                "active?": True,
                                "default": ["0.0", "0.0", "0.0"],
                                "read-only?": False,
                                "webui-release-active?": True,
                            }
                        },
                        "X": {
                            "attrs": {
                                "active?": True,
                                "default": "0.0",
                                "read-only?": False,
                                "webui-release-active?": True,
                            }
                        },
                        "Y": {
                            "attrs": {
                                "active?": True,
                                "default": "0.0",
                                "read-only?": False,
                                "webui-release-active?": True,
                            }
                        },
                        "Z": {
                            "attrs": {
                                "active?": True,
                                "default": "0.0",
                                "read-only?": False,
                                "webui-release-active?": True,
                            }
                        },
                        "suspend": {
                            "attrs": {
                                "active?": True,
                                "read-only?": False,
                                "webui-release-active?": True,
                            }
                        },
                        "unsuspend": {
                            "attrs": {
                                "active?": True,
                                "read-only?": False,
                                "webui-release-active?": True,
                            }
                        },
                    },
                },
                "Option": {
                    "attrs": {
                        "active?": True,
                        "allowed-values": [
                            "Point and Normal",
                            "Three Points",
                            "XY Plane",
                            "YZ Plane",
                            "ZX Plane",
                        ],
                        "default": "XY Plane",
                        "read-only?": False,
                        "webui-release-active?": True,
                    }
                },
                "Plane Bound": {
                    "attrs": {
                        "active?": True,
                        "allowed-values": ["Circular", "None", "Rectangular"],
                        "default": "None",
                        "read-only?": False,
                        "webui-release-active?": True,
                    }
                },
                "Plane Type": {
                    "attrs": {
                        "active?": True,
                        "allowed-values": ["Sample", "Slice"],
                        "default": "Slice",
                        "read-only?": False,
                        "webui-release-active?": True,
                    }
                },
                "Point": {
                    "attrs": {
                        "active?": True,
                        "default": ["0.0", "0.0", "0.0"],
                        "read-only?": False,
                        "webui-release-active?": True,
                    }
                },
                "Point 1": {
                    "attrs": {
                        "active?": True,
                        "default": ["0.0", "0.0", "0.0"],
                        "read-only?": False,
                        "webui-release-active?": True,
                    }
                },
                "Point 2": {
                    "attrs": {
                        "active?": True,
                        "default": ["1.0", "0.0", "0.0"],
                        "read-only?": False,
                        "webui-release-active?": True,
                    }
                },
                "Point 3": {
                    "attrs": {
                        "active?": True,
                        "default": ["0.0", "1.0", "0.0"],
                        "read-only?": False,
                        "webui-release-active?": True,
                    }
                },
                "Range": {
                    "attrs": {
                        "active?": True,
                        "allowed-values": ["Global", "Local", "User Specified"],
                        "default": "Global",
                        "read-only?": False,
                        "webui-release-active?": True,
                    }
                },
                "Render Edge Angle": {
                    "attrs": {
                        "active?": True,
                        "default": "0 [degree]",
                        "read-only?": False,
                        "webui-release-active?": True,
                    }
                },
                "Specular Lighting": {
                    "attrs": {
                        "active?": True,
                        "default": True,
                        "read-only?": False,
                        "webui-release-active?": True,
                    }
                },
                "Surface Drawing": {
                    "attrs": {
                        "active?": True,
                        "allowed-values": [
                            "Draw As " "Lines",
                            "Draw As " "Points",
                            "Flat " "Shading",
                            "Smooth " "Shading",
                        ],
                        "default": "Smooth Shading",
                        "read-only?": False,
                        "webui-release-active?": True,
                    }
                },
                "Texture Angle": {
                    "attrs": {
                        "active?": True,
                        "default": "0",
                        "read-only?": False,
                        "webui-release-active?": True,
                    }
                },
                "Texture Direction": {
                    "attrs": {
                        "active?": True,
                        "default": ["0.0", "1.0", "0.0"],
                        "read-only?": False,
                        "webui-release-active?": True,
                    }
                },
                "Texture File": {
                    "attrs": {
                        "active?": True,
                        "default": "",
                        "read-only?": False,
                        "webui-release-active?": True,
                    }
                },
                "Texture Material": {
                    "attrs": {
                        "active?": True,
                        "allowed-values": [
                            "Blue " "Metal",
                            "Brick",
                            "Brushed " "Metal",
                            "Chrome",
                            "Gold",
                            "Metal",
                            "Red " "Metal",
                            "Rough " "Wall",
                            "White " "Metal",
                        ],
                        "default": "Metal",
                        "read-only?": False,
                        "webui-release-active?": True,
                    }
                },
                "Texture Position": {
                    "attrs": {
                        "active?": True,
                        "default": ["0.0", "0.0"],
                        "read-only?": False,
                        "webui-release-active?": True,
                    }
                },
                "Texture Scale": {
                    "attrs": {
                        "active?": True,
                        "default": "1.0",
                        "read-only?": False,
                        "webui-release-active?": True,
                    }
                },
                "Texture Type": {
                    "attrs": {
                        "active?": True,
                        "allowed-values": ["Custom", "Predefined"],
                        "default": "Predefined",
                        "read-only?": False,
                        "webui-release-active?": True,
                    }
                },
                "Tile Texture": {
                    "attrs": {
                        "active?": True,
                        "default": False,
                        "read-only?": False,
                        "webui-release-active?": True,
                    }
                },
                "Transform Texture": {
                    "attrs": {
                        "active?": True,
                        "default": False,
                        "read-only?": False,
                        "webui-release-active?": True,
                    }
                },
                "Transparency": {
                    "attrs": {
                        "active?": True,
                        "default": "0.0",
                        "read-only?": False,
                        "webui-release-active?": True,
                    }
                },
                "Visibility": {
                    "attrs": {
                        "active?": True,
                        "default": True,
                        "read-only?": False,
                        "webui-release-active?": True,
                    }
                },
                "X": {
                    "attrs": {
                        "active?": True,
                        "default": "0.0",
                        "read-only?": False,
                        "webui-release-active?": True,
                    }
                },
                "Y": {
                    "attrs": {
                        "active?": True,
                        "default": "0.0",
                        "read-only?": False,
                        "webui-release-active?": True,
                    }
                },
                "Z": {
                    "attrs": {
                        "active?": True,
                        "default": "0.0",
                        "read-only?": False,
                        "webui-release-active?": True,
                    }
                },
                "hide": {
                    "attrs": {"active?": True, "read-only?": False, "webui-release-active?": True}
                },
                "show": {
                    "attrs": {"active?": True, "read-only?": False, "webui-release-active?": True}
                },
                "suspend": {
                    "attrs": {"active?": True, "read-only?": False, "webui-release-active?": True}
                },
                "unsuspend": {
                    "attrs": {"active?": True, "read-only?": False, "webui-release-active?": True}
                },
            },
        }

    # Tests for get_attr
    assert pypost.results.plane["Plane 1"].option.get_attr("default") == "XY Plane"
    assert pypost.results.plane["Plane 1"].option.get_attr("allowed-values") == [
        "Point and Normal",
        "Three Points",
        "XY Plane",
        "YZ Plane",
        "ZX Plane",
    ]
    if pypost.get_cfx_version() > CFXVersion.v252:
        assert pypost.results.plane["Plane 1"].number_of_contours.get_attr("default") == 11
    else:
        assert pypost.results.plane["Plane 1"].number_of_contours.get_attr("default") == "11"
