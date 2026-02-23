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

import ansys.cfx.core as pycfx
from ansys.cfx.core.session_post import PostProcessing


def test_batch_ops_create_plane(pypost: PostProcessing, pytestconfig):
    # Setup hardcopy options
    hardcopy = pypost.results.hardcopy
    hardcopy.hardcopy_format = "png"
    hardcopy.image_height = 1200
    hardcopy.image_width = 1200
    hardcopy.use_screen_size = False

    # Assume the .def file is in the same directory as this test
    data_file_name = "StaticMixer.def"
    data_file_engine_path = f"{pytestconfig.test_data_directory_path}/data/{data_file_name}"
    data_file_client_path = f"{pytestconfig.test_home_directory_path}/data/{data_file_name}"
    assert Path(data_file_client_path).exists(), "Data file missing for test"

    with pycfx.BatchOps(pypost):
        pypost.file.load_results(file_name=data_file_engine_path)
        pypost.results.plane["Plane 1"] = {}

    # Plane setup
    plane = pypost.results.plane["Plane 1"]
    plane.suspend()
    plane.option = "ZX Plane"
    plane.plane_type = "Slice"
    plane.unsuspend()

    # Contour setup
    pypost.results.contour["Contour 1"] = {
        "colour_variable": "X",
        "location_list": "/PLANE:Plane 1",
        "number_of_contours": 11,
        "contour_range": "Local",
        "draw_contours": True,
        "fringe_fill": True,
        "object_view_transform": {"scale_vector": (1, 1, 2)},
    }
    contour = pypost.results.contour["Contour 1"]
    contour.show(view="/VIEW:View 1")
    image_file_name = "static_mixer_contour.png"
    image_file_engine_path = f"{pytestconfig.test_data_directory_path}/{image_file_name}"
    image_file_client_path = f"{pytestconfig.test_home_directory_path}/{image_file_name}"
    image_file = Path(image_file_client_path)
    if image_file.exists():
        image_file.unlink()
    pypost.file.save_picture(file_name=image_file_engine_path)
    assert image_file.exists()
    image_file.unlink()
