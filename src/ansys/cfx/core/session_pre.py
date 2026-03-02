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

"""Module containing the class encapsulating the CFX-Pre connection."""

from typing import Any, Optional

from ansys.cfx.core.cfx_connection import CFXConnection
from ansys.cfx.core.session import BaseSession


class PreProcessing(BaseSession):
    """Encapsulates a CFX pre-processing session.
    This object exposes the CFX-Pre CCL and scripting (Power Syntax)
    capabilities in a Pythonic manner.
    """

    def __init__(
        self,
        cfx_connection: CFXConnection,
        file_transfer_service: Optional[Any] = None,
    ):
        """Instantiate an instance of the ``PreProcessing`` class.

        Args:
            cfx_connection (:ref:`ref_cfx_connection`): Encapsulates a CFX connection.
            file_transfer_service: Supports file upload and download.
        """
        super(PreProcessing, self).__init__(
            cfx_connection=cfx_connection,
            file_transfer_service=file_transfer_service,
        )

    @classmethod
    def get_name(cls) -> str | None:
        """Get the session name."""
        return "pre-processing"

    @classmethod
    def get_cmd_name(cls) -> str | None:
        """Get the CFX command name related to the session."""
        return "cfx5pre"
