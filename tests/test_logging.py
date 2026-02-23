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

import logging
from pathlib import Path

import ansys.cfx.core as pycfx


def test_set_logging_level(pytestconfig, caplog):

    generated_path = Path(__file__).parent / "generated"
    log_file_path = generated_path / "test.log"

    generated_path.mkdir(parents=True, exist_ok=True)
    log_file_path.unlink(missing_ok=True)

    assert not pycfx.logging.is_active()

    config_dict = pycfx.logging.get_default_config()
    config_dict["handlers"]["pycfx_file"]["filename"] = log_file_path

    pycfx.logging.enable(custom_config=config_dict)
    settings_logger = logging.getLogger("pycfx.settings_api")
    settings_logger.setLevel("WARNING")
    settings_logger.warning("ABC")
    assert len(caplog.records) == 1

    assert pycfx.logging.is_active()

    # Tidy up
    settings_logger.disabled = True
