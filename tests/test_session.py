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

import ansys.cfx.core as pycfx
from ansys.cfx.core.session_pre import PreProcessing


def test_launch_pre(pypre: PreProcessing, pytestconfig):
    assert pypre.health_check_service.check_health() == pypre.health_check_service.Status.SERVING
    assert pypre.is_server_healthy()

    props = pypre.connection_properties
    connection_kwargs = {
        "ip": props.ip,
        "port": props.port,
        "address": props.address,
        "password": props.password,
    }

    pypre_connected = pycfx.PreProcessing.from_connection(**connection_kwargs)

    assert (
        pypre_connected.health_check_service.check_health()
        == pypre_connected.health_check_service.Status.SERVING
    )
    assert pypre_connected.is_server_healthy()
