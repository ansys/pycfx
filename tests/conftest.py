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

import functools
import operator
from pathlib import Path

from packaging.specifiers import SpecifierSet
from packaging.version import Version
import pytest
from util.common import CONTAINER_DEFAULT_IMAGE_TAG, CONTAINER_WORKING_DIR, is_containerized_mode

from ansys.cfx.core.utils.cfx_version import CFXVersion


def pytest_addoption(parser):
    parser.addoption(
        "--execution_mode",
        action="store",
        default="DIRECT",
        help="execution_mode can be either DIRECT or CONTAINERIZED",
        choices=("DIRECT", "CONTAINERIZED"),
    )
    parser.addoption(
        "--image_tag",
        action="store",
        default=CONTAINER_DEFAULT_IMAGE_TAG,
        help="The docker image tag to be used when --execution-mode==CONTAINERIZED",
    )
    parser.addoption(
        "--cfx-version",
        action="store",
        metavar="VERSION",
        help="only run tests supported by CFX version VERSION.",
    )


def pytest_runtest_setup(item: pytest.Item) -> None:
    if any(mark.name == "standalone" for mark in item.iter_markers()) and is_containerized_mode(
        item.config
    ):
        pytest.skip()

    version_specs = []
    cfx_release_version = CFXVersion.current_release().value
    for mark in item.iter_markers(name="cfx_version"):
        spec = mark.args[0]
        # if a test is marked as cfx_version("latest")
        # run with dev and release CFX versions in nightly
        # run with release CFX versions in PRs
        if spec == "latest":
            spec = f">={cfx_release_version}" if is_nightly else f"=={cfx_release_version}"
        version_specs.append(SpecifierSet(spec))
    if version_specs:
        combined_spec = functools.reduce(operator.and_, version_specs)
        version = item.config.getoption("--cfx-version")
        if version and Version(version) not in combined_spec:
            pytest.skip()


TEST_HOME_DIRECTORY_PATH = Path(__file__).resolve().parent


def pytest_configure(config):
    config.test_home_directory_path = TEST_HOME_DIRECTORY_PATH
    if is_containerized_mode(config):
        # In containerized mode, the test data directory is mounted to the container working directory.
        config.test_data_directory_path = CONTAINER_WORKING_DIR
    else:
        # In direct mode, the test data directory is the same as the test directory.
        config.test_data_directory_path = TEST_HOME_DIRECTORY_PATH


pytest_plugins = [
    "util.fixtures",
]
