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

import os
import tempfile

import pytest

from ansys.cfx.core import examples


def test_download_file(pytestconfig):
    """
    Test file download by pulling a mesh file and verifying its existence.
    """
    mesh_filename = "StaticMixerMesh.gtm"
    mesh_subdir = "pycfx/static_mixer"
    dest_dir = tempfile.gettempdir()
    mesh_file_path = os.path.join(dest_dir, mesh_filename)

    if os.path.exists(mesh_file_path):
        os.remove(mesh_file_path)

    # Download the mesh file
    mesh_file_path = examples.download_file(
        mesh_filename,
        mesh_subdir,
        dest_dir,
    )

    # Record modification time after first download
    mtime_before = os.path.getmtime(mesh_file_path)

    assert os.path.isfile(mesh_file_path), f"Mesh file not found at {mesh_file_path}"

    # Download the same file again. Local copy should be used.
    mesh_file_path_new = examples.download_file(
        mesh_filename,
        mesh_subdir,
        dest_dir,
    )

    # Record modification time after second download
    mtime_after = os.path.getmtime(mesh_file_path_new)

    assert mesh_file_path == mesh_file_path_new
    assert mtime_before == mtime_after, "File was overwritten during second download"

    os.remove(mesh_file_path)


def test_download_non_exist_file():
    with pytest.raises(examples.RemoteFileNotFoundError):
        examples.download_file(
            "foo.res",
            "pycfx/static_mixer",
        )
