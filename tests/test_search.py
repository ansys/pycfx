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

import pytest

import ansys.cfx.core as pycfx
from ansys.cfx.core.session_post import PostProcessing
from ansys.cfx.core.session_pre import PreProcessing
from ansys.cfx.core.utils.cfx_version import get_version_for_file_name
from ansys.cfx.core.utils.search import _get_version_path_prefix_from_obj


@pytest.mark.codegen_required
def test_search(capsys):
    pycfx.search("save_")
    lines = capsys.readouterr().out.splitlines()
    assert "<pre_processing_session>.file.save_case (Command)" in lines
    assert "<pre_processing_session>.file.save_picture (Command)" in lines
    assert "<post_processing_session>.file.save_picture (Command)" in lines
    assert "<post_processing_session>.results.hardcopy.save_picture (Command)" in lines

    pycfx.search("Save_", match_case=True)
    lines = capsys.readouterr().out.splitlines()
    assert not lines, "Expected no results."

    pycfx.search("save_", match_case=True, match_whole_word=True)
    lines = capsys.readouterr().out.splitlines()
    assert not lines, "Expected no results."

    pycfx.search("axis_definition")
    lines = capsys.readouterr().out.splitlines()
    assert (
        '<pre_processing_session>.setup.flow["<name>"].domain_interface["<name>"].'
        "interface_models.pitch_change.axis_definition (Object)" in lines
    )
    assert (
        "<pre_processing_session>.setup.library.transformation_definitions."
        'transformation["<name>"].rotation_axis_definition (Object)' in lines
    )

    pycfx.search("axis_definition", match_whole_word=True)
    lines = capsys.readouterr().out.splitlines()
    assert (
        '<pre_processing_session>.setup.flow["<name>"].domain_interface["<name>"].'
        "interface_models.pitch_change.axis_definition (Object)" in lines
    )
    assert (
        "<pre_processing_session>.setup.library.transformation_definitions."
        'transformation["<name>"].rotation_axis_definition (Object)' not in lines
    )

    pycfx.search("rotation_axis")
    lines = capsys.readouterr().out.splitlines()
    assert (
        '<pre_processing_session>.setup.flow["<name>"].domain_interface["<name>"].'
        "interface_models.axis_definition.rotation_axis (Parameter)" in lines
    )
    assert (
        '<pre_processing_session>.setup.flow["<name>"].domain_interface["<name>"].'
        "interface_models.axis_definition.rotation_axis_from (Parameter)" in lines
    )
    assert (
        '<pre_processing_session>.setup.flow["<name>"].domain_interface["<name>"].'
        "interface_models.axis_definition.rotation_axis_to (Parameter)" in lines
    )
    assert (
        "<post_processing_session>.results.object_view_transform.rotation_axis_from (Parameter)"
        in lines
    )
    assert (
        "<post_processing_session>.results.object_view_transform.rotation_axis_to (Parameter)"
        in lines
    )
    assert (
        "<post_processing_session>.results.object_view_transform.rotation_axis_type (Parameter)"
        in lines
    )


@pytest.mark.codegen_required
def test_search_pre_case_tree(pre_load_static_mixer_case: PreProcessing, capsys):
    pypre = pre_load_static_mixer_case
    pycfx.search(
        "diffuse_fraction",
        search_root=pypre.setup.flow["Flow Analysis 1"].domain["Default Domain"].boundary["out"],
    )
    lines = capsys.readouterr().out.splitlines()
    assert (
        "<search_root>.boundary_conditions.thermal_radiation.diffuse_fraction (Parameter)" in lines
    )
    assert (
        '<search_root>.fluid["<name>"].boundary_conditions.thermal_radiation.diffuse_fraction '
        "(Parameter)" in lines
    )


@pytest.mark.codegen_required
def test_get_version_path_prefix_from_obj_pre(pypre: PreProcessing):
    version = get_version_for_file_name(pypre.get_cfx_version().value)
    assert _get_version_path_prefix_from_obj(pypre) == (
        version,
        ["<pre_processing_session>"],
        "<search_root>",
    )
    assert _get_version_path_prefix_from_obj(pypre.setup) == (
        version,
        ["<pre_processing_session>"],
        "<search_root>",
    )
    assert _get_version_path_prefix_from_obj(pypre.setup.flow) == (
        version,
        ["<pre_processing_session>"],
        '<search_root>["<name>"]',
    )
    assert _get_version_path_prefix_from_obj(pypre.file.import_mesh) == (
        None,
        None,
        None,
    )


@pytest.mark.codegen_required
def test_get_version_path_prefix_from_obj_post(pypost: PostProcessing):
    version = get_version_for_file_name(pypost.get_cfx_version().value)
    assert _get_version_path_prefix_from_obj(pypost) == (
        version,
        ["<post_processing_session>"],
        "<search_root>",
    )
    assert _get_version_path_prefix_from_obj(pypost.results) == (
        version,
        ["<post_processing_session>"],
        "<search_root>",
    )
    assert _get_version_path_prefix_from_obj(pypost.results.plane) == (
        version,
        ["<post_processing_session>"],
        '<search_root>["<name>"]',
    )
    assert _get_version_path_prefix_from_obj(pypost.file.load_results) == (
        None,
        None,
        None,
    )
