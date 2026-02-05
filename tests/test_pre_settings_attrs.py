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


from ansys.cfx.core.common import flobject
from ansys.cfx.core.session_pre import PreProcessing
from ansys.cfx.core.utils.cfx_version import CFXVersion


def test_pre_attributes(pre_load_static_mixer_case: PreProcessing, pytestconfig, capsys):
    """Test the handling of attributes when connected to the CFX-Pre Engine."""

    pypre = pre_load_static_mixer_case

    pypre.setup.library.additional_variable["Additional Variable 1"] = {}
    av1 = pypre.setup.library.additional_variable["Additional Variable 1"]
    pypre.setup.flow["Flow Analysis 1"].domain["Default Domain"].fluid_models.additional_variable[
        "Additional Variable 1"
    ] = {}

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
        pypre.get_attrs(attrs=attrs_list) == {
            "active?": True,
            "read-only?": False,
            "webui-release-active?": True,
        }
    except AttributeError as e:
        assert str(e) == "'SettingsRoot' object has no attribute 'get_attrs'"
    else:
        assert False, "Expected AttributeError"

    # Menu level
    assert pypre.setup.get_attrs(attrs=attrs_list) == {
        "active?": True,
        "read-only?": False,
        "webui-release-active?": True,
    }

    # Named object type, user-defined name
    # User-creatable has the wrong value for DOMAIN and some other high-level objects in 25.2.
    if pypre.get_cfx_version() > CFXVersion.v252:
        user_creatable_attr = True
    else:
        user_creatable_attr = False
    assert pypre.setup.flow["Flow Analysis 1"].domain.get_attrs(attrs=attrs_list) == {
        "active?": True,
        "read-only?": False,
        "user-creatable?": user_creatable_attr,
        "webui-release-active?": True,
    }

    # Named object, user-defined name
    assert pypre.setup.flow["Flow Analysis 1"].domain["Default Domain"].get_attrs(
        attrs=attrs_list
    ) == {
        "active?": True,
        "read-only?": False,
        "webui-release-active?": True,
    }

    # Named object type, user-defined name
    assert pypre.setup.flow["Flow Analysis 1"].domain["Default Domain"].boundary.get_attrs(
        attrs=attrs_list
    ) == {
        "active?": True,
        "read-only?": False,
        "user-creatable?": True,
        "webui-release-active?": True,
    }

    # Named object, user-defined name
    assert pypre.setup.flow["Flow Analysis 1"].domain["Default Domain"].boundary["in1"].get_attrs(
        attrs=attrs_list
    ) == {
        "active?": True,
        "read-only?": False,
        "webui-release-active?": True,
    }

    # Named object type, pre-defined name
    assert pypre.setup.flow["Flow Analysis 1"].domain[
        "Default Domain"
    ].fluid_models.additional_variable.get_attrs(attrs=attrs_list) == {
        "active?": True,
        "read-only?": False,
        "user-creatable?": False,
        "webui-release-active?": True,
    }

    # Named object, pre-defined name
    assert pypre.setup.flow["Flow Analysis 1"].domain[
        "Default Domain"
    ].fluid_models.additional_variable["Additional Variable 1"].get_attrs(attrs=attrs_list) == {
        "active?": True,
        "read-only?": False,
        "webui-release-active?": True,
    }

    # Parameter with allowed values
    assert pypre.setup.flow["Flow Analysis 1"].analysis_type.option.get_attrs(attrs=attrs_list) == {
        "active?": True,
        "allowed-values": ["Steady State", "Transient", "Transient Blade Row"],
        "default": "Steady State",
        "read-only?": False,
        "webui-release-active?": True,
    }

    # Numerical parameter with min/max
    assert pypre.setup.flow["Flow Analysis 1"].domain["Default Domain"].boundary[
        "out"
    ].boundary_conditions.mass_and_momentum.pressure_profile_blend.get_attrs(attrs=attrs_list) == {
        "active?": True,
        "default": "0.05",
        "max": "1",
        "min": "0",
        "read-only?": False,
        "webui-release-active?": True,
    }

    # "Enabled" parameter (context group)
    if pypre.get_cfx_version() > CFXVersion.v252:
        assert pypre.setup.flow["Flow Analysis 1"].domain["Default Domain"].boundary[
            "out"
        ].boundary_contour.enabled.get_attrs(attrs=attrs_list) == {
            "active?": True,
            "default": False,
            "read-only?": False,
            "webui-release-active?": True,
        }
    else:
        assert pypre.setup.flow["Flow Analysis 1"].domain["Default Domain"].boundary[
            "out"
        ].boundary_contour.enabled.get_attrs(attrs=attrs_list) == {
            "active?": True,
            "default": "False",
            "read-only?": False,
            "webui-release-active?": True,
        }

    # "Enabled" parameter parent (context group)
    assert pypre.setup.flow["Flow Analysis 1"].domain["Default Domain"].boundary[
        "out"
    ].boundary_contour.get_attrs(attrs=attrs_list) == {
        "active?": True,
        "read-only?": False,
        "sub-type": "context-group",
        "webui-release-active?": True,
    }

    # Inactive object
    assert pypre.setup.flow["Flow Analysis 1"].domain["Default Domain"].boundary[
        "out"
    ].boundary_conditions.turbulence.get_attrs(attrs=attrs_list) == {
        "active?": False,
        "read-only?": False,
        "webui-release-active?": True,
    }

    # Essential parameter of inactive object
    try:
        pypre.setup.flow["Flow Analysis 1"].domain["Default Domain"].boundary[
            "out"
        ].boundary_conditions.turbulence.option.get_attrs(attrs=attrs_list)
    except flobject.InactiveObjectError as e:
        assert str(e) == (
            '\'<session>.setup.flow["Flow Analysis 1"].domain["Default '
            'Domain"].boundary["out"].boundary_conditions.turbulence\' is currently inactive.'
        )
    else:
        assert False, "Expected InactiveObjectError"

    # Inactive parameter
    if pypre.get_cfx_version() > CFXVersion.v252:
        assert pypre.setup.flow["Flow Analysis 1"].domain["Default Domain"].boundary[
            "out"
        ].frame_type.get_attrs(attrs=attrs_list) == {
            "active?": False,
            "allowed-values": None,
            "default": None,
            "read-only?": False,
            "webui-release-active?": True,
        }
    else:
        assert pypre.setup.flow["Flow Analysis 1"].domain["Default Domain"].boundary[
            "out"
        ].frame_type.get_attrs(attrs=attrs_list) == {
            "active?": False,
            "allowed-values": [],
            "default": "",
            "read-only?": False,
            "webui-release-active?": True,
        }

    # Function outside of CCL
    assert pypre.file.new_case.get_attrs(attrs=attrs_list) == {
        "active?": True,
        "read-only?": False,
        "webui-release-active?": True,
    }

    # Function argument
    assert pypre.file.open_case.file_name.get_attrs(attrs=attrs_list) == None

    # Function within CCL
    assert pypre.setup.flow["Flow Analysis 1"].domain[
        "Default Domain"
    ].get_physics_messages.get_attrs(attrs=attrs_list) == {
        "active?": True,
        "read-only?": False,
        "webui-release-active?": True,
    }

    # Function argument
    assert (
        pypre.setup.flow["Flow Analysis 1"]
        .domain["Default Domain"]
        .get_physics_messages.severity.get_attrs(attrs=attrs_list)
        == None
    )

    # Recursive attributes
    # Future work should refine the attributes of the nested children of inactive parents.
    if pypre.get_cfx_version() > CFXVersion.v252:
        assert pypre.setup.flow["Flow Analysis 1"].analysis_type.get_attrs(
            attrs=attrs_list, recursive=True
        ) == {
            "attrs": {
                "active?": True,
                "read-only?": False,
                "sub-type": "context-group",
                "webui-release-active?": True,
            },
            "group_children": {
                "EXTERNAL SOLVER COUPLING": {
                    "attrs": {"active?": True, "read-only?": False, "webui-release-active?": True},
                    "group_children": {
                        "Option": {
                            "attrs": {
                                "active?": True,
                                "allowed-values": ["None"],
                                "default": "None",
                                "read-only?": False,
                                "webui-release-active?": True,
                            }
                        },
                        "get_physics_messages": {
                            "attrs": {
                                "active?": True,
                                "read-only?": False,
                                "webui-release-active?": True,
                            }
                        },
                    },
                },
                "Enabled": {
                    "attrs": {
                        "active?": True,
                        "default": False,
                        "read-only?": False,
                        "webui-release-active?": True,
                    }
                },
                "INITIAL TIME": {
                    "attrs": {"active?": False, "read-only?": False, "webui-release-active?": True},
                    "group_children": {
                        "Option": {
                            "attrs": {
                                "active?": False,
                                "allowed-values": None,
                                "default": None,
                                "read-only?": False,
                                "webui-release-active?": True,
                            }
                        },
                        "Time": {
                            "attrs": {
                                "active?": False,
                                "default": None,
                                "max": None,
                                "min": None,
                                "read-only?": False,
                                "webui-release-active?": True,
                            }
                        },
                        "get_physics_messages": {
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
                        "allowed-values": ["Steady State", "Transient", "Transient Blade " "Row"],
                        "default": "Steady State",
                        "read-only?": False,
                        "webui-release-active?": True,
                    }
                },
                "TIME DURATION": {
                    "attrs": {"active?": False, "read-only?": False, "webui-release-active?": True},
                    "group_children": {
                        "Maximum Number of Timesteps": {
                            "attrs": {
                                "active?": False,
                                "default": None,
                                "max": None,
                                "min": None,
                                "read-only?": False,
                                "webui-release-active?": True,
                            }
                        },
                        "Number of Timesteps per Run": {
                            "attrs": {
                                "active?": False,
                                "default": None,
                                "max": None,
                                "min": None,
                                "read-only?": False,
                                "webui-release-active?": True,
                            }
                        },
                        "Option": {
                            "attrs": {
                                "active?": False,
                                "allowed-values": None,
                                "default": None,
                                "read-only?": False,
                                "webui-release-active?": True,
                            }
                        },
                        "Time per Run": {
                            "attrs": {
                                "active?": False,
                                "default": None,
                                "max": None,
                                "min": None,
                                "read-only?": False,
                                "webui-release-active?": True,
                            }
                        },
                        "Total Time": {
                            "attrs": {
                                "active?": False,
                                "default": None,
                                "max": None,
                                "min": None,
                                "read-only?": False,
                                "webui-release-active?": True,
                            }
                        },
                        "get_physics_messages": {
                            "attrs": {
                                "active?": True,
                                "read-only?": False,
                                "webui-release-active?": True,
                            }
                        },
                    },
                },
                "TIME STEPS": {
                    "attrs": {"active?": False, "read-only?": False, "webui-release-active?": True},
                    "group_children": {
                        "First Update Time": {
                            "attrs": {
                                "active?": False,
                                "default": None,
                                "max": None,
                                "min": None,
                                "read-only?": False,
                                "webui-release-active?": True,
                            }
                        },
                        "Initial Timestep": {
                            "attrs": {
                                "active?": False,
                                "default": None,
                                "max": None,
                                "min": None,
                                "read-only?": False,
                                "webui-release-active?": True,
                            }
                        },
                        "Option": {
                            "attrs": {
                                "active?": False,
                                "allowed-values": None,
                                "default": None,
                                "read-only?": False,
                                "webui-release-active?": True,
                            }
                        },
                        "TIMESTEP ADAPTION": {
                            "attrs": {
                                "active?": False,
                                "read-only?": False,
                                "webui-release-active?": True,
                            },
                            "group_children": {
                                "Courant Number": {
                                    "attrs": {
                                        "active?": False,
                                        "default": None,
                                        "max": None,
                                        "min": None,
                                        "read-only?": False,
                                        "webui-release-active?": True,
                                    }
                                },
                                "Decreasing Relaxation Factor": {
                                    "attrs": {
                                        "active?": False,
                                        "default": None,
                                        "max": None,
                                        "min": None,
                                        "read-only?": False,
                                        "webui-release-active?": True,
                                    }
                                },
                                "Increasing Relaxation Factor": {
                                    "attrs": {
                                        "active?": False,
                                        "default": None,
                                        "max": None,
                                        "min": None,
                                        "read-only?": False,
                                        "webui-release-active?": True,
                                    }
                                },
                                "Maximum Timestep": {
                                    "attrs": {
                                        "active?": False,
                                        "default": None,
                                        "max": None,
                                        "min": None,
                                        "read-only?": False,
                                        "webui-release-active?": True,
                                    }
                                },
                                "Minimum Timestep": {
                                    "attrs": {
                                        "active?": False,
                                        "default": None,
                                        "max": None,
                                        "min": None,
                                        "read-only?": False,
                                        "webui-release-active?": True,
                                    }
                                },
                                "Option": {
                                    "attrs": {
                                        "active?": False,
                                        "allowed-values": None,
                                        "default": None,
                                        "read-only?": False,
                                        "webui-release-active?": True,
                                    }
                                },
                                "Target Maximum Coefficient Loops": {
                                    "attrs": {
                                        "active?": False,
                                        "default": None,
                                        "max": None,
                                        "min": None,
                                        "read-only?": False,
                                        "webui-release-active?": True,
                                    }
                                },
                                "Target Minimum Coefficient Loops": {
                                    "attrs": {
                                        "active?": False,
                                        "default": None,
                                        "max": None,
                                        "min": None,
                                        "read-only?": False,
                                        "webui-release-active?": True,
                                    }
                                },
                                "Timestep Decrease Factor": {
                                    "attrs": {
                                        "active?": False,
                                        "default": None,
                                        "max": None,
                                        "min": None,
                                        "read-only?": False,
                                        "webui-release-active?": True,
                                    }
                                },
                                "Timestep Increase Factor": {
                                    "attrs": {
                                        "active?": False,
                                        "default": None,
                                        "max": None,
                                        "min": None,
                                        "read-only?": False,
                                        "webui-release-active?": True,
                                    }
                                },
                                "get_physics_messages": {
                                    "attrs": {
                                        "active?": True,
                                        "read-only?": False,
                                        "webui-release-active?": True,
                                    }
                                },
                            },
                        },
                        "Timestep Update Frequency": {
                            "attrs": {
                                "active?": False,
                                "default": None,
                                "max": None,
                                "min": None,
                                "read-only?": False,
                                "webui-release-active?": True,
                            }
                        },
                        "Timesteps": {
                            "attrs": {
                                "active?": False,
                                "default": None,
                                "read-only?": False,
                                "webui-release-active?": True,
                            }
                        },
                        "Timesteps for the Run": {
                            "attrs": {
                                "active?": False,
                                "default": None,
                                "read-only?": False,
                                "webui-release-active?": True,
                            }
                        },
                        "get_physics_messages": {
                            "attrs": {
                                "active?": True,
                                "read-only?": False,
                                "webui-release-active?": True,
                            }
                        },
                    },
                },
                "get_physics_messages": {
                    "attrs": {"active?": True, "read-only?": False, "webui-release-active?": True}
                },
            },
        }

    # Tests for get_attr
    m_and_m = (
        pypre.setup.flow["Flow Analysis 1"]
        .domain["Default Domain"]
        .boundary["out"]
        .boundary_conditions.mass_and_momentum
    )

    assert m_and_m.option.get_attr("allowed-values") == [
        "Average Static Pressure",
        "Normal Speed",
        "Cartesian Velocity Components",
        "Cylindrical Velocity Components",
        "Mass Flow Rate",
        "Static Pressure",
        "Implicit",
    ]

    assert m_and_m.pressure_profile_blend.get_attr("default") == "0.05"
    assert m_and_m.pressure_profile_blend.get_attr("active?") is True

    try:
        value = m_and_m.get_attr("non-existent-attr")
    except RuntimeError as e:
        assert str(e) == "Invalid attribute: 'non-existent-attr'."
    else:
        assert False, "Expected RuntimeError"

    # Other related functions
    assert (
        pypre.setup.flow["Flow Analysis 1"].analysis_type.option.default_value() == "Steady State"
    )
    if pypre.get_cfx_version() > CFXVersion.v252:
        assert (
            pypre.setup.flow[
                "Flow Analysis 1"
            ].solver_control.convergence_control.maximum_number_of_iterations.default_value()
            == 100
        )
    else:
        assert (
            pypre.setup.flow[
                "Flow Analysis 1"
            ].solver_control.convergence_control.maximum_number_of_iterations.default_value()
            == "100"
        )
    assert (
        pypre.setup.flow["Flow Analysis 1"]
        .domain["Default Domain"]
        .boundary["out"]
        .boundary_conditions.mass_and_momentum.pressure_profile_blend.default_value()
        == "0.05"
    )
    if pypre.get_cfx_version() > CFXVersion.v252:
        assert (
            pypre.setup.flow[
                "Flow Analysis 1"
            ].solver_control.dynamic_model_control.global_dynamic_model_control.default_value()
            == True
        )
    else:
        assert (
            pypre.setup.flow[
                "Flow Analysis 1"
            ].solver_control.dynamic_model_control.global_dynamic_model_control.default_value()
            == "Yes"
        )
    pypre.setup.library.coordinate_frame_definitions.coordinate_frame["Coord 1"] = {}
    pypre.setup.library.coordinate_frame_definitions.coordinate_frame["Coord 1"].option = (
        "Axis Points"
    )

    if pypre.get_cfx_version() > CFXVersion.v252:
        assert pypre.setup.library.coordinate_frame_definitions.coordinate_frame[
            "Coord 1"
        ].origin_point.default_value() == ["0.0[m]", "0.0[m]", "0.0[m]"]
    else:
        assert (
            pypre.setup.library.coordinate_frame_definitions.coordinate_frame[
                "Coord 1"
            ].origin_point.default_value()
            == "0.0[m],0.0[m],0.0[m]"
        )

    assert (
        pypre.setup.flow["Flow Analysis 1"]
        .domain["Default Domain"]
        .boundary["out"]
        .boundary_conditions.mass_and_momentum.pressure_profile_blend.min()
        == "0"
    )

    assert (
        pypre.setup.flow["Flow Analysis 1"]
        .domain["Default Domain"]
        .boundary["out"]
        .boundary_conditions.mass_and_momentum.pressure_profile_blend.max()
        == "1"
    )

    if pypre.get_cfx_version() > CFXVersion.v252:
        assert (
            pypre.setup.flow[
                "Flow Analysis 1"
            ].solver_control.convergence_control.minimum_number_of_iterations.min()
            == 0
        )
    else:
        assert (
            pypre.setup.flow[
                "Flow Analysis 1"
            ].solver_control.convergence_control.minimum_number_of_iterations.min()
            == "0"
        )

    # Test getting attributes with particular type, including conversion to bool
    assert (
        pypre.setup.flow["Flow Analysis 1"].analysis_type.option.get_attr("default", str)
        == "Steady State"
    )
    assert (
        pypre.setup.flow["Flow Analysis 1"].analysis_type.option.get_attr("default", (bool, str))
        == "Steady State"
    )
    assert (
        pypre.setup.flow["Flow Analysis 1"].analysis_type.option.get_attr("default", bool) is True
    )
    assert pypre.setup.flow["Flow Analysis 1"].analysis_type.option.get_attr("default", int) is None

    # Tests using internal functions (hard to test via public functions)

    try:
        value = pypre.setup.flow["Flow Analysis 1"].analysis_type.option.__setattr__(
            "non-existent-attr", "1"
        )
    except AttributeError as e:
        assert str(e) == "non-existent-attr"
    else:
        assert False, "Expected AttributeError"

    try:
        value = m_and_m.__setattr__("non-existent-attr", "1")
    except AttributeError as e:
        assert str(e) == (
            "'mass_and_momentum' object has no attribute 'non-existent-attr'.\n"
            "The most similar names are: axis_definition..\n"
            "The most similar names are: axis_definition."
        )
    else:
        assert False, "Expected AttributeError"
