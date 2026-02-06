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

"""Provides a module to search a word through the CFX's object hierarchy."""

from collections.abc import Mapping
from pathlib import Path
import pickle
from typing import Any, Optional

from ansys.cfx.core.common import flobject
from ansys.cfx.core.session_post import PostProcessing
from ansys.cfx.core.session_pre import PreProcessing
from ansys.cfx.core.session_solver import Solver
from ansys.cfx.core.utils.cfx_version import CFXVersion, get_version_for_file_name


def get_api_tree_file_name(version: str, pycfx_path: str) -> Path:
    """Get API tree file name."""
    from ansys.cfx.core import CODEGEN_OUTDIR

    return (CODEGEN_OUTDIR / f"api_tree_{version}.pickle").resolve()


def _match(source: str, word: str, match_whole_word: bool, match_case: bool):
    if not match_case:
        source = source.lower()
        word = word.lower()
    if match_whole_word:
        return source == word
    else:
        return word in source


def _remove_suffix(input: str, suffix):
    if hasattr(input, "removesuffix"):
        return input.removesuffix(suffix)
    else:
        if suffix and input.endswith(suffix):
            return input[: -len(suffix)]
        return input


def _get_version_path_prefix_from_obj(obj: Any):
    path = None
    version = None
    prefix = None
    if isinstance(obj, PreProcessing):
        path = ["<pre_processing_session>"]
        version = get_version_for_file_name(obj.get_cfx_version().value)
        prefix = "<search_root>"
    elif isinstance(obj, Solver):
        path = ["<solver_session>"]
        version = get_version_for_file_name(obj.get_cfx_version().value)
        prefix = "<search_root>"
    elif isinstance(obj, PostProcessing):
        path = ["<post_processing_session>"]
        version = get_version_for_file_name(obj.get_cfx_version().value)
        prefix = "<search_root>"
    elif isinstance(obj, flobject.Group):
        module = obj.__class__.__module__
        path_comps = module.split(".")
        version = path_comps[-2].rsplit("_", 1)[-1]
        prefix = "<search_root>"
        path = ["<" + path_comps[-3] + "_session>"]
        # Cannot deduce the whole path without api_tree
    elif isinstance(obj, flobject.NamedObject):
        module = obj.__class__.__module__
        path_comps = module.split(".")
        version = path_comps[-2].rsplit("_", 1)[-1]
        prefix = '<search_root>["<name>"]'
        path = ["<" + path_comps[-3] + "_session>"]
        # Cannot deduce the whole path without api_tree
    return version, path, prefix


def search(
    word: str,
    match_whole_word: bool = False,
    match_case: bool = False,
    version: Optional[str] = None,
    search_root: Optional[Any] = None,
):
    """Search for a word through the CFX's object hierarchy.

    Parameters
    ----------
    word : str
        The word to search for.
    match_whole_word : bool, optional
        Whether to match whole word, by default False
    match_case : bool, optional
        Whether to match case, by default False
    version : str, optional
        CFX version to search in, by default None in which case
        it will search in the latest version for which codegen was run.
    search_root : Any, optional
        The root object within which the search will be performed,
        can be a session object or any API object within a session,
        by default None in which case it will search everything.

    Examples
    --------
    >>> import ansys.cfx.core as pycfx
    >>> pycfx.search("injection_region")
    <pre_processing_session>.setup.flow["<name>"].domain["<name>"].particle_injection_region["<name>"] (Object)
    <pre_processing_session>.setup.flow["<name>"].domain["<name>"].injection_region["<name>"] (Object)
    <pre_processing_session>.setup.flow["<name>"].domain["<name>"].injection_region["<name>"].injection_region_type (Parameter)
    <pre_processing_session>.setup.flow["<name>"].domain["<name>"].injection_region["<name>"].injection_region_contour (Object)
    <pre_processing_session>.setup.flow["<name>"].domain["<name>"].injection_region["<name>"].injection_region_vector (Object)
    <pre_processing_session>.setup.flow["<name>"].output_control.transient_particle_diagnostics["<name>"].penetration_origin_and_direction.particle_injection_region (Parameter)
    <post_processing_session>.results.internal_particle_injection_region["<name>"] (Object)
    <post_processing_session>.results.injection_region["<name>"] (Object)
    """
    if version:
        version = get_version_for_file_name(version)
    root_version, root_path, prefix = _get_version_path_prefix_from_obj(search_root)
    if search_root and not prefix:
        return
    if not version:
        version = root_version
    if not version:
        for cfx_version in CFXVersion:
            version = get_version_for_file_name(cfx_version.value)
            if get_api_tree_file_name(version, None).exists():
                break
    api_tree_file = get_api_tree_file_name(version, None)
    with open(api_tree_file, "rb") as f:
        api_tree = pickle.load(f)

    if isinstance(search_root, (flobject.Group, flobject.NamedObject)):
        path = root_path + [flobject.to_python_name(x) for x in search_root.path.split("/")]
        root_path = []
        tree = api_tree
        while path:
            p = path.pop(0)
            if p in tree:
                tree = tree[p]
                root_path.append(p)
            elif f"{p}:<name>" in tree:
                tree = tree[f"{p}:<name>"]
                root_path.append(f"{p}:<name>")
                if path:
                    path.pop(0)
            else:
                return

    def inner(tree, path, root_path):
        if root_path:
            path = prefix
        while root_path:
            p = root_path.pop(0)
            if p in tree:
                tree = tree[p]
            else:
                return

        for k, v in tree.items():
            if k in ("<pre_processing_session>", "<solver_session>", "<post_processing_session>"):
                next_path = k
            else:
                if k.endswith(":<name>"):
                    k = _remove_suffix(k, ":<name>")
                    next_path = f'{path}.{k}["<name>"]'
                else:
                    next_path = f"{path}.{k}"
                if _match(k, word, match_whole_word, match_case):
                    type_ = "Object" if isinstance(v, Mapping) else v
                    print(f"{next_path} ({type_})")
            if isinstance(v, Mapping):
                inner(v, next_path, root_path)

    inner(api_tree, "", root_path)
