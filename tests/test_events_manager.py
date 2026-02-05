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


def test_events_manager(pypost: PostProcessing, pytestconfig):

    def on_error_event(session_id, event_info):
        on_error_event.received = True

    on_error_event.received = False
    cb_id = pypost.events_manager.register_callback("ErrorEvent", on_error_event)

    pypost.file.load_results(
        file_name=f"{pytestconfig.test_data_directory_path}/data/StaticMixer.def"
    )

    # Test warning for missing point locator definition
    pypost.results.point["Point 1"] = {}
    point = pypost.results.point["Point 1"]
    point.suspend()
    point.option = "Variable Maximum"
    point.variable = "X"
    point.unsuspend()

    assert on_error_event.received
    pypost.events_manager.unregister_callback(cb_id)
