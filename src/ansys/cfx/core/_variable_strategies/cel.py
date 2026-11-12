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

"""Provides a conversion strategy for mapping ``VariableDescriptor`` to CFX CEL variable names."""

from ansys.variable_descriptor import MappingConversionStrategy, VariableCatalog


class CFXCelNamingStrategy(MappingConversionStrategy):
    """Convert ``VariableCatalog`` entries to CFX CEL variable names."""

    _c = VariableCatalog

    # Where several descriptors share a CFX name, the last one wins for the reverse lookup.
    _mapping = {
        _c.STATIC_PRESSURE: "Pressure",
        _c.PRESSURE: "Pressure",
        _c.TOTAL_PRESSURE: "Total Pressure",
        _c.VELOCITY: "Velocity",
        _c.VELOCITY_X: "Velocity u",
        _c.VELOCITY_Y: "Velocity v",
        _c.VELOCITY_Z: "Velocity w",
        _c.TEMPERATURE: "Temperature",
        _c.TOTAL_TEMPERATURE: "Total Temperature",
        _c.DENSITY: "Density",
    }
