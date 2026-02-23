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

"""A package providing CFX solutions in Python."""

import os
from pathlib import Path
import pydoc

import platformdirs

try:
    import importlib.metadata as importlib_metadata
except ModuleNotFoundError:
    import importlib_metadata

__version__ = importlib_metadata.version(__name__.replace(".", "-"))

# Logging has to be set up before importing other PyCFX modules
import ansys.cfx.core.logging as logging

logging.root_config()
logging.configure_env_var()

from ansys.cfx.core.get_build_details import (  # noqa: F401
    get_build_version,
    get_build_version_string,
)
from ansys.cfx.core.launcher.launcher import connect_to_cfx, launch_cfx  # noqa: F401
from ansys.cfx.core.launcher.pycfx_enums import CFXMode, UIMode  # noqa: F401
from ansys.cfx.core.services.batch_ops import BatchOps  # noqa: F401
from ansys.cfx.core.session import BaseSession as CFX  # noqa: F401
from ansys.cfx.core.session_utilities import PostProcessing, PreProcessing, Solver  # noqa: F401
from ansys.cfx.core.utils import fldoc
from ansys.cfx.core.utils.cfx_version import CFXVersion  # noqa: F401
from ansys.cfx.core.utils.search import search  # noqa: F401
from ansys.cfx.core.warnings import PyCFXDeprecationWarning  # noqa: F401

_VERSION_INFO = None
"""Global variable indicating the version of the PyCFX package - Empty by default"""

_THIS_DIRNAME = Path(__file__).parent
_README_FILE = (_THIS_DIRNAME / "docs" / "README.rst").resolve()

if _README_FILE.exists():
    with open(_README_FILE, encoding="utf8") as f:
        __doc__ = f.read()


def version_info() -> str:
    """Method returning the version of PyCFX being used.

    Returns
    -------
    str
        The PyCFX version being used.

    Notes
    -------
    Only available in packaged versions. Otherwise it will return __version__.
    """
    return _VERSION_INFO if _VERSION_INFO is not None else __version__


def _set_container_image_env_vars():
    cfx_image = os.getenv("CFX_CONTAINER_IMAGE")
    if cfx_image and ":" in cfx_image:
        name, tag = cfx_image.rsplit(":", 1)
        os.environ["CFX_IMAGE_NAME"] = name
        os.environ["CFX_IMAGE_TAG"] = tag


_set_container_image_env_vars()

# Latest released CFX version
CFX_RELEASE_VERSION = "25.2.0"

# Current dev CFX version
CFX_DEV_VERSION = "26.1.0"

# Setup data directory
USER_DATA_PATH = platformdirs.user_data_dir(appname="ansys_cfx_core", appauthor="Ansys")
EXAMPLES_PATH = str(Path(USER_DATA_PATH) / "examples")

# Set this to False to stop automatically inferring and setting REMOTING_SERVER_ADDRESS
INFER_REMOTING_IP = True

# Time in second to wait for response for each ip while inferring remoting ip
INFER_REMOTING_IP_TIMEOUT_PER_IP = 2

pydoc.text.docother = fldoc.docother.__get__(pydoc.text, pydoc.TextDoc)

# Directory where API files are written out during codegen
CODEGEN_OUTDIR = Path(
    os.getenv("PYCFX_CODEGEN_OUTDIR", str((Path(__file__).parent / "generated").resolve()))
)
