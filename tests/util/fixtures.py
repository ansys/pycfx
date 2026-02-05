# Copyright (C) 2023 - 2026 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
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

import tempfile

import pytest

import ansys.cfx.core as pycfx
from ansys.cfx.core.session_post import PostProcessing
from ansys.cfx.core.session_pre import PreProcessing
from ansys.cfx.core.session_solver import Solver
from ansys.cfx.core.utils.cfx_version import CFXVersion

from .common import (
    CONTAINER_TEMP_DIR,
    CONTAINER_WORKING_DIR,
    get_container_cfx_version,
    get_image_tag,
    is_containerized_mode,
)


# Fixtures are set-up methods. The method is passed as an argument to the test method and will be
# run before the method definition.
@pytest.fixture
def pypre(pytestconfig, request) -> PreProcessing:

    # Start CFX-Pre
    temp_dir = None
    if is_containerized_mode(pytestconfig):
        temp_dir = tempfile.TemporaryDirectory()
        image_tag = get_image_tag(pytestconfig)
        cfx_version = get_container_cfx_version(image_tag)
        config_dict = {
            "image_tag": f"{image_tag}",
            "volumes": [
                f"{pytestconfig.test_home_directory_path}:{CONTAINER_WORKING_DIR}",
                f"{temp_dir.name}:{CONTAINER_TEMP_DIR}",
            ],
            "working_dir": f"{CONTAINER_WORKING_DIR}",
        }
        pypre = pycfx.PreProcessing.from_container(
            product_version=cfx_version, container_dict=config_dict
        )
    else:
        pypre = pycfx.PreProcessing.from_install()

    yield pypre

    pypre.exit()
    if temp_dir:
        temp_dir.cleanup()


@pytest.fixture
def pypost(pytestconfig, request) -> PostProcessing:

    # Start CFX-Post
    temp_dir = None
    if is_containerized_mode(pytestconfig):
        temp_dir = tempfile.TemporaryDirectory()
        image_tag = get_image_tag(pytestconfig)
        cfx_version = get_container_cfx_version(image_tag)
        config_dict = {
            "image_tag": f"{image_tag}",
            "volumes": [
                f"{pytestconfig.test_home_directory_path}:{CONTAINER_WORKING_DIR}",
                f"{temp_dir.name}:{CONTAINER_TEMP_DIR}",
            ],
            "working_dir": f"{CONTAINER_WORKING_DIR}",
        }
        pypost = pycfx.PostProcessing.from_container(
            product_version=cfx_version, container_dict=config_dict
        )
    else:
        pypost = pycfx.PostProcessing.from_install()

    yield pypost

    pypost.exit()
    if temp_dir:
        temp_dir.cleanup()


@pytest.fixture
def pysolve(pytestconfig, request) -> callable:
    """
    Factory for creating a pycfx Solver instance, handling containerized and local modes.
    Registers cleanup for solver and temporary resources.
    """

    def _make(solver_input_file_name: str) -> Solver:
        temp_dir = None
        try:
            if is_containerized_mode(pytestconfig):
                temp_dir = tempfile.TemporaryDirectory()
                image_tag = get_image_tag(pytestconfig)
                cfx_version = get_container_cfx_version(image_tag)
                config_dict = {
                    "image_tag": f"{image_tag}",
                    "volumes": [
                        f"{pytestconfig.test_home_directory_path}:{CONTAINER_WORKING_DIR}",
                        f"{temp_dir.name}:{CONTAINER_TEMP_DIR}",
                    ],
                    "working_dir": f"{CONTAINER_WORKING_DIR}",
                }
                solver = pycfx.Solver.from_container(
                    product_version=cfx_version,
                    solver_input_file_name=solver_input_file_name,
                    container_dict=config_dict,
                )
            else:
                solver = pycfx.Solver.from_install(solver_input_file_name=solver_input_file_name)
        except Exception:
            if temp_dir:
                temp_dir.cleanup()
            raise

        request.addfinalizer(solver.exit)
        if temp_dir:
            request.addfinalizer(temp_dir.cleanup)
        return solver

    return _make


@pytest.fixture
def pre_load_static_mixer_case(pytestconfig, pypre) -> PreProcessing:
    pre_session = pypre
    pre_session.file.open_case(
        file_name=f"{pytestconfig.test_data_directory_path}/data/StaticMixer.def"
    )
    yield pre_session
    pre_session.exit()


class Helpers:
    """Can be reused to provide helper methods to tests."""

    def __init__(self, monkeypatch: pytest.MonkeyPatch):
        self.monkeypatch = monkeypatch

    def mock_awp_vars(self, version=None):
        """
        Activates environment variables for CFX versions up to the specified version,
        and deactivates environment variables for versions newer than the specified version.

        Parameters
        ----------
        version : None, str, or CFXVersion, optional
            The maximum CFX version for which to activate environment variables.
            If None, uses the current release.

        Returns
        -------
        None
        """
        if not version:
            version = CFXVersion.current_release()
        elif not isinstance(version, CFXVersion):
            version = CFXVersion(version)
        self.monkeypatch.delenv("PYCFX_CFX_ROOT", raising=False)
        for fv in CFXVersion:
            if fv <= version:
                self.monkeypatch.setenv(fv.awp_var, f"ansys_inc/{fv.name}")
            else:
                self.monkeypatch.delenv(fv.awp_var, raising=False)

    def delete_all_awp_vars(self):
        """Remove all CFX-related environment variables."""
        self.monkeypatch.delenv("PYCFX_CFX_ROOT", raising=False)
        for fv in CFXVersion:
            self.monkeypatch.delenv(fv.awp_var, raising=False)


@pytest.fixture
def helpers(monkeypatch):
    return Helpers(monkeypatch)
