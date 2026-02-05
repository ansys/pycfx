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

from contextlib import suppress
import logging
import os

import ansys.cfx.core as pycfx


def test_set_logging_level(pytestconfig, caplog):

    generated_path = os.path.join(os.path.dirname(__file__), "generated")
    log_file_path = os.path.join(generated_path, "test.log")

    os.makedirs(generated_path, exist_ok=True)
    with suppress(FileNotFoundError):
        os.remove(log_file_path)

    assert pycfx.logging.is_active() == False

    config_dict = pycfx.logging.get_default_config()
    config_dict["handlers"]["pycfx_file"]["filename"] = log_file_path

    pycfx.logging.enable(custom_config=config_dict)
    settings_logger = logging.getLogger("pycfx.settings_api")
    settings_logger.setLevel("WARNING")
    settings_logger.warning("ABC")
    assert len(caplog.records) == 1

    assert pycfx.logging.is_active() == True

    # Tidy up
    settings_logger.disabled = True
