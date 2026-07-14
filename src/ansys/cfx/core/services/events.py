# Copyright (C) 2023 - 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
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

"""Wrapper over the events gRPC service of CFX."""

from typing import List, Tuple

import grpc

from ansys.cfx.core.services.streaming import StreamingService
from ansys.cfx.core.utils.api_version import get_events_modules
from ansys.cfx.core.utils.cfx_version import CFXVersion


class EventsService(StreamingService):
    """Wraps the events gRPC service of CFX."""

    def __init__(
        self,
        channel: grpc.Channel,
        metadata: List[Tuple[str, str]],
        engine_version: CFXVersion,
    ):
        """Initialize an instance of the ``EventsService`` class."""
        _, EventsGrpcModule = get_events_modules(engine_version)
        super().__init__(
            stub=EventsGrpcModule.EventsStub(channel),
            metadata=metadata,
        )
