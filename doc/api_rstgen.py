"""Provides a module for generating PyCFX API RST files."""

import os
from pathlib import Path
import shutil

from ansys.cfx.core.utils.cfx_version import CFXVersion

api_contents_path = Path(__file__).parents[0].resolve() / "source" / "api" / "api_contents.rst"
cfx_version = CFXVersion.current_release()


def _write_rst_file(output_path: str, version: str):
    content = f""".. _ref_api:

API reference
=============

This API reference corresponds to {version}.

This section provides the class and function reference for PyCFX. For comprehensive guidelines on using PyCFX, see the :ref:`ref_user_guide`.

All public APIs for PyCFX appear in the left pane. Descriptions of some key APIs follow.

PreProcessing mode
------------------
The PreProcessing :ref:`settings API <ref_pre_processing_root>` is the main interface for using the CFX preprocessor (CFX-Pre).

Solution mode
-------------
The :ref:`Solver session<ref_session_solver>` is the main interface for running and controlling the
CFX-Solver. This module offers very limited control in this first PyCFX release.


PostProcessing mode
-------------------
The PostProcessing :ref:`settings API <ref_post_processing_root>` is the main interface for using the CFX postprocessor (CFD-Post).


.. toctree::
    :maxdepth: 2
    :hidden:
    :caption: ansys.cfx.core

    common/common_contents
    launcher/launcher_contents
    services/services_contents
    streaming_services/streaming_services_contents
    utils/utils_contents

    cfx_connection
    exceptions
    get_build_details
    logging
    post_processing
    pre_processing
    session_post
    session_pre
    session_solver
    session_utilities
    session
    solver_controller
    warnings
"""

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)


def _get_folder_path(folder_name: str):
    """Get folder path.

    Parameters
    ----------
    folder_name: str
        Name of the folder.

    Returns
    -------
        Path of the folder.
    """
    return (Path(__file__) / ".." / "source" / "api" / folder_name).resolve()


def _get_file_path(folder_name: str, file_name: str):
    """Get file path.

    Parameters
    ----------
    folder_name: str
        Name of the folder.

    file_name: str
        Name of the file.

    Returns
    -------
        Path of the file.
    """
    return (Path(__file__) / ".." / "source" / "api" / folder_name / f"{file_name}.rst").resolve()


hierarchy = {
    "common": ["error_message", "flobject"],
    "launcher": [
        "cfx_container",
        "container_launcher",
        "error_handler",
        "launcher_utils",
        "launcher",
        "process_launch_string",
        "pycfx_enums",
        "standalone_launcher",
        "watchdog",
    ],
    "services": [
        "batch_ops",
        "engine_eval",
        "events",
        "health_check",
        "interceptors",
        "settings",
        "streaming",
    ],
    "streaming_services": [
        "events_streaming",
        "streaming",
    ],
    "utils": [
        "cfx_version",
        "dictionary_operations",
        "execution",
        "fix_doc",
        "fldoc",
        "generic",
        "networking",
        "search",
    ],
    "other": [
        "cfx_connection",
        "exceptions",
        "get_build_details",
        "logging",
        "post_processing",
        "pre_processing",
        "session_post",
        "session_pre",
        "session_solver",
        "session_utilities",
        "session",
        "solver_controller",
        "warnings",
    ],
}


def _write_common_rst_members(rst_file):
    rst_file.write("    :members:\n")
    rst_file.write("    :show-inheritance:\n")
    rst_file.write("    :undoc-members:\n")
    rst_file.write("    :exclude-members: __weakref__, __dict__\n")
    rst_file.write("    :special-members: __init__\n")
    rst_file.write("    :autosummary:\n")


def _generate_settings_root(module: str, rst):
    if module == "pre_processing":
        session_name = "PreProcessing"
    elif module == "post_processing":
        session_name = "PostProcessing"
    rst.write(f"{module}\n")
    rst.write(f'{"="*(len(module))}\n\n')
    rst.write(
        f"The {module} :ref:`ref_{module}_root` is the top-level {session_name} object. It contains all\n"
    )
    rst.write("other settings objects in a hierarchical structure.\n")


def _generate_api_source_rst_files(folder: str, files: list, duplicate_files: dict):
    for file in files:
        if file.endswith("_contents"):
            pass
        else:
            if folder:
                rst_file = _get_file_path(folder, file)
            else:
                rst_file = _get_file_path("", file)
            with open(rst_file, "w", encoding="utf8") as rst:
                ref = f"_ref_{file}"
                if file in duplicate_files:
                    if duplicate_files[file] > 0:
                        ref = ref + str(duplicate_files[file])
                    duplicate_files[file] += 1
                rst.write(f".. {ref}:\n\n")
                if file == "post_processing":
                    _generate_settings_root("post_processing", rst)
                elif file == "pre_processing":
                    _generate_settings_root("pre_processing", rst)
                else:
                    if folder:
                        rst.write(f"{file}\n")
                        rst.write(f'{"="*(len(f"{file}"))}\n\n')
                        rst.write(f".. automodule:: ansys.cfx.core.{folder}.{file}\n")
                    else:
                        rst.write(f"{file}\n")
                        rst.write(f'{"="*(len(f"{file}"))}\n\n')
                        rst.write(f".. automodule:: ansys.cfx.core.{file}\n")
                    _write_common_rst_members(rst_file=rst)


def _generate_api_index_rst_files():

    # Handle duplicate references
    duplicate_files = {"streaming": 0, "launcher": 0}

    for folder, files in hierarchy.items():
        if Path(_get_folder_path(folder)).is_dir():
            shutil.rmtree(_get_folder_path(folder))
        if folder == "other":
            _generate_api_source_rst_files(None, files, duplicate_files)
        else:
            Path(_get_folder_path(folder)).mkdir(parents=True, exist_ok=True)
            folder_index = _get_file_path(folder, f"{folder}_contents")
            with open(folder_index, "w", encoding="utf8") as index:
                ref = f"_ref_{folder}"
                if folder in duplicate_files:
                    if duplicate_files[folder] > 0:
                        ref = ref + str(duplicate_files[folder])
                    duplicate_files[folder] += 1
                index.write(f".. {ref}:\n\n")
                index.write(f"{folder}\n")
                index.write(f'{"="*(len(f"{folder}"))}\n\n')
                index.write(f".. automodule:: ansys.cfx.core.{folder}\n")
                _write_common_rst_members(rst_file=index)
                index.write(".. toctree::\n")
                index.write("    :maxdepth: 2\n")
                index.write("    :hidden:\n\n")
                for file in files:
                    index.write(f"    {file}\n")
                index.write("\n")
            _generate_api_source_rst_files(folder, files, duplicate_files)


if __name__ == "__main__":
    _write_rst_file(api_contents_path, cfx_version)
    _generate_api_index_rst_files()
