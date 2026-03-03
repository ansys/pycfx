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

"""Module for controlling the writing of CFX Python journals."""


from ansys.cfx.core.services.engine_eval import EngineEval


class Journal:
    """Control the writing of CFX Python journals."""

    def __init__(self, engine_eval: EngineEval):
        """Initialize an instance of the ``Journal`` class."""
        self.engine_eval = engine_eval

    def start(self, file_name: str):
        """Start writing a CFX Python journal to the specified file."""
        # TODO: Implement Python Journaling in the Engine
        pass
        # self.engine_eval.process_ccl([f'(api-start-python-journal "{file_name}")'])

    def stop(self):
        """Stop writing the CFX Python journal."""
        # TODO: Implement Python Journaling in the Engine
        pass
        # self.engine_eval.process_ccl([f"(api-stop-python-journal)"])
