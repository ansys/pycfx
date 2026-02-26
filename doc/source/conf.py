"""Sphinx documentation configuration file."""

from datetime import datetime
import os

from ansys_sphinx_theme import ansys_favicon, get_version_match
from ansys_sphinx_theme import pyansys_logo_black as logo
from sphinx_gallery.sorting import FileNameSortKey

from ansys.cfx.core import __version__

# Project information
project = "ansys-cfx-core"
copyright = f"(c) {datetime.now().year} ANSYS, Inc. All rights reserved"
author = "ANSYS, Inc."
release = version = __version__
cname = os.getenv("DOCUMENTATION_CNAME", "cfx.docs.pyansys.com")
switcher_version = get_version_match(version)

# Select desired logo, theme, and declare the html title
html_logo = logo
html_theme = "ansys_sphinx_theme"
html_short_title = html_title = "PyCFX"
html_favicon = ansys_favicon

# specify the location of your github repo
html_theme_options = {
    "github_url": "https://github.com/ansys/pycfx",
    "show_prev_next": False,
    "show_breadcrumbs": True,
    "additional_breadcrumbs": [
        ("PyAnsys", "https://docs.pyansys.com/"),
    ],
    "switcher": {
        "json_url": f"https://{cname}/versions.json",
        "version_match": get_version_match(__version__),
    },
    "check_switcher": False,
}

# Sphinx extensions
extensions = [
    "autodocsumm",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "numpydoc",
    "sphinx.ext.intersphinx",
    "sphinx_copybutton",
    "sphinx_jinja",
    "sphinx_gallery.gen_gallery",
    "sphinx_design",
]

sphinx_gallery_conf = {
    "examples_dirs": "../../examples",  # path to your example scripts
    "gallery_dirs": "examples",  # path where the gallery generated output will be saved
    "within_subsection_order": FileNameSortKey,
    "remove_config_comments": True,
    "plot_gallery": False,
    "write_computation_times": False,
}
# config.cache: sphinx_gallery_conf having FileNameSortKey as part of it makes a warning that
# a cache can't happen. This doesn't bother us because we don't rely on it.
# for huge projects, this can be the equivalent of clean building every time.
suppress_warnings = ["config.cache"]

# Intersphinx mapping
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    # kept here as an example
    # "scipy": ("https://docs.scipy.org/doc/scipy/reference", None),
    # "numpy": ("https://numpy.org/devdocs", None),
    # "matplotlib": ("https://matplotlib.org/stable", None),
    # "pandas": ("https://pandas.pydata.org/pandas-docs/stable", None),
    # "pyvista": ("https://docs.pyvista.org/", None),
    # "grpc": ("https://grpc.github.io/grpc/python/", None),
}

# numpydoc configuration
numpydoc_show_class_members = False
numpydoc_xref_param_type = True

# Consider enabling numpydoc validation. See:
# https://numpydoc.readthedocs.io/en/latest/validation.html#
numpydoc_validate = True
numpydoc_validation_checks = {
    "GL06",  # Found unknown section
    "GL07",  # Sections are in the wrong order.
    # "GL08",  # The object does not have a docstring
    "GL09",  # Deprecation warning should precede extended summary
    "GL10",  # reST directives {directives} must be followed by two colons
    "SS01",  # No summary found
    "SS02",  # Summary does not start with a capital letter
    # "SS03", # Summary does not end with a period
    "SS04",  # Summary contains heading whitespaces
    # "SS05", # Summary must start with infinitive verb, not third person
    "RT02",  # The first line of the Returns section should contain only the
    # type, unless multiple values are being returned"
}


# static path
html_static_path = ["_static"]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# The suffix(es) of source filenames.
source_suffix = ".rst"

# The master toctree document.
master_doc = "index"

# Ignore links that do not exist yet (to be revisited).
linkcheck_ignore = [
    "https://github.com/ansys/pycfx/*",
    "https://pypi.org/project/ansys-cfx-core/*",
    "https://opensource.org/license/MIT",
]

# If we are on a release, we have to ignore the "release" URLs, since it is not
# available until the release is published.
if switcher_version != "dev":
    linkcheck_ignore.append(f"https://github.com/ansys/pycfx/releases/tag/v{__version__}")
