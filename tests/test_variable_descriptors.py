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

"""Tests for ``VariableDescriptor`` support."""

import re

import pytest

from ansys.cfx.core._variable_strategies import CFXCelNamingStrategy
from ansys.cfx.core.session_post import PostProcessing
from ansys.cfx.core.session_pre import PreProcessing
from ansys.variable_descriptor import VariableCatalog


@pytest.mark.parametrize(
    "variable, cfx_name",
    [
        (VariableCatalog.PRESSURE, "Pressure"),
        (VariableCatalog.STATIC_PRESSURE, "Pressure"),
        (VariableCatalog.TOTAL_PRESSURE, "Total Pressure"),
        (VariableCatalog.VELOCITY, "Velocity"),
        (VariableCatalog.VELOCITY_X, "Velocity u"),
        (VariableCatalog.VELOCITY_Y, "Velocity v"),
        (VariableCatalog.VELOCITY_Z, "Velocity w"),
        (VariableCatalog.TEMPERATURE, "Temperature"),
        (VariableCatalog.TOTAL_TEMPERATURE, "Total Temperature"),
        (VariableCatalog.DENSITY, "Density"),
    ],
)
def test_cel_naming_strategy_to_string(variable, cfx_name):
    assert CFXCelNamingStrategy().to_string(variable) == cfx_name


def test_cel_naming_strategy_passes_strings_through():
    assert CFXCelNamingStrategy().to_string("X") == "X"


def test_cel_naming_strategy_unsupported_variable():
    strategy = CFXCelNamingStrategy()
    unsupported = next(
        v
        for v in vars(VariableCatalog).values()
        if hasattr(v, "name") and v not in strategy._mapping
    )
    assert not strategy.supports(unsupported)
    with pytest.raises(ValueError):
        strategy.to_string(unsupported)


def test_cel_naming_strategy_to_variable_descriptor():
    strategy = CFXCelNamingStrategy()
    assert strategy.to_variable_descriptor("Temperature") == VariableCatalog.TEMPERATURE
    assert strategy.to_variable_descriptor("Pressure") == VariableCatalog.PRESSURE
    assert strategy.to_variable_descriptor("Unknown Variable") is None


def test_variable_descriptor_contour_in_post(pypost: PostProcessing, pytestconfig):
    pypost.file.load_results(
        file_name=f"{pytestconfig.test_data_directory_path}/data/StaticMixer.def"
    )
    pypost.results.plane.create("Plane 1")
    plane = pypost.results.plane["Plane 1"]
    plane.suspend()
    plane.option = "ZX Plane"
    plane.plane_type = "Slice"
    plane.unsuspend()

    pypost.results.contour["Contour 1"] = {
        "colour_variable": VariableCatalog.PRESSURE,
        "location_list": "/PLANE:Plane 1",
        "number_of_contours": 11,
    }
    contour = pypost.results.contour["Contour 1"]
    assert contour.colour_variable() == "Pressure"

    contour.colour_variable = VariableCatalog.TEMPERATURE
    assert contour.colour_variable() == "Temperature"


def test_variable_descriptor_monitor_point_in_pre(pre_load_static_mixer_case: PreProcessing):
    pypre = pre_load_static_mixer_case
    monitors = pypre.setup.flow["Flow Analysis 1"].output_control.monitor_objects
    monitors.enabled = True
    monitors.monitor_point.create("Outlet Monitor")
    monitor = monitors.monitor_point["Outlet Monitor"]
    monitor.output_variables_list = [
        VariableCatalog.PRESSURE,
        VariableCatalog.TOTAL_TEMPERATURE,
        "Static Entropy",
    ]
    assert monitor.output_variables_list() == [
        "Pressure",
        "Total Temperature",
        "Static Entropy",
    ]

    # Rotating-frame variables are not available in the static mixer case.
    with pytest.raises(ValueError, match=re.escape("['Pressure', 'Velocity in Stn Frame']")):
        monitor.output_variables_list = [VariableCatalog.PRESSURE, "Velocity in Stn Frame"]
