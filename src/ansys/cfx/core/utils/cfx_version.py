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

"""Provides a module to get CFX version."""

from enum import Enum
from functools import total_ordering
import os
import re
from typing import Optional

import ansys.cfx.core as pycfx


class AnsysVersionNotFound(RuntimeError):
    """Raised when Ansys version is not found."""

    pass


class ComparisonError(RuntimeError):
    """Raised when a comparison can't be completed."""

    def __init__(self):
        super().__init__(
            f"Comparison operations are only supported between two members of 'CFXVersion'."
        )


def get_version(session=None):
    """Get CFX version."""
    if session is None:
        # for CI runs, get the version statically from env var set within CI
        image_tag = os.getenv("CFX_IMAGE_TAG")
        if image_tag is not None:
            return image_tag.lstrip("v")
        session = pycfx.launch_cfx(mode=pycfx.CFXMode.PRE_PROCESSING)

    return session.get_cfx_version().value


def get_version_for_file_name(version: Optional[str] = None, session=None):
    """Get CFX version for file name."""
    if version is None:
        version = get_version(session)

    return "".join(version.split(".")[0:2])


@total_ordering
class CFXVersion(Enum):
    """An enumeration over supported CFX versions.

    Examples
    --------
    CFXVersion("25.2.0") == CFXVersion.v252

    CFXVersion.v252.number == 252

    CFXVersion.v252.awp_var == 'AWP_ROOT252'
    """

    v261 = "26.1.0"
    v252 = "25.2.0"

    @classmethod
    def _missing_(cls, version):
        if isinstance(version, (int, float, str)):
            version = str(version)

            # Remove the last digit if there are more than two dots for
            # patch version conventions like 25.2.3
            if version.count(".") > 1:
                version = re.sub(r"\.\d+$", "", version)

            if len(version) == 3:
                version = version[:2] + "." + version[2:]
            version += ".0"
            for member in cls:
                if version == member.value:
                    return member
        raise AnsysVersionNotFound(
            f"The specified version '{version[:-2]}' is not supported."
            + " Supported versions are: "
            + ", ".join([member.value for member in cls][::-1])
        )

    @classmethod
    def get_latest_installed(cls):
        """Return the version member corresponding to the most recent, available Ansys
        installation.

        Returns
        -------
        CFXVersion
            CFXVersion member corresponding to the newest CFX version.

        Raises
        ------
        AnsysVersionNotFound
            If an Ansys version cannot be found.
        """
        for member in cls:
            if member.awp_var in os.environ:
                return member

        raise AnsysVersionNotFound("Verify the value of the 'AWP_ROOT' environment variable.")

    @classmethod
    def current_release(cls):
        """Return the version member of the current release.

        Returns
        -------
        CFXVersion
            CFXVersion member corresponding to the latest release.
        """
        return cls(pycfx.CFX_RELEASE_VERSION)

    @classmethod
    def current_dev(cls):
        """Return the version member of the current development version.

        Returns
        -------
        CFXVersion
            CFXVersion member corresponding to the latest development version.
        """
        return cls(pycfx.CFX_DEV_VERSION)

    @property
    def awp_var(self):
        """Get the CFX version in AWP environment variable format."""
        return f"AWP_ROOT{self.number}"

    @property
    def number(self):
        """Get the CFX version as a plain integer."""
        return int(self.value.replace(".", "")[:-1])

    def __lt__(self, other):
        if isinstance(other, CFXVersion):
            return self.value < other.value
        raise ComparisonError()

    def __repr__(self) -> str:
        return self.value

    def __str__(self) -> str:
        """Return a string representation for the CFX version."""
        return f"Ansys CFX 20{self.value.split('.')[0]} R{self.value.split('.')[1]}"
