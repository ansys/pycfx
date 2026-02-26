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

"""Wrapper over the health check gRPC service of CFX."""

from enum import Enum
import logging
import sys

import grpc
from grpc_health.v1 import health_pb2 as HealthCheckModule
from grpc_health.v1 import health_pb2_grpc as HealthCheckGrpcModule

from ansys.cfx.core.services.interceptors import (
    BatchInterceptor,
    ErrorStateInterceptor,
    GrpcErrorInterceptor,
    TracingInterceptor,
)

logger: logging.Logger = logging.getLogger("pycfx.general")


class HealthCheckService:
    """Wraps the health check gRPC service of CFX.

    Methods
    -------
    check_health()
        Check the health of the CFX connection.
    """

    class Status(Enum):
        """Health check status."""

        UNKNOWN: int = 0
        SERVING: int = 1
        NOT_SERVING: int = 2
        SERVICE_UNKNOWN: int = 3

    def __init__(
        self, channel: grpc.Channel, metadata: list[tuple[str, str]], cfx_error_state
    ) -> None:
        """Initialize an instance of the ``HealthCheckService`` class."""
        intercept_channel = grpc.intercept_channel(
            channel,
            GrpcErrorInterceptor(),
            ErrorStateInterceptor(cfx_error_state),
            TracingInterceptor(),
            BatchInterceptor(),
        )
        self._stub = HealthCheckGrpcModule.HealthStub(intercept_channel)
        self._metadata = metadata
        self._channel = channel

    def check_health(self) -> Status:
        """Check the health of the CFX connection.

        Returns
        -------
        Status
        """
        request = HealthCheckModule.HealthCheckRequest()
        response = self._stub.Check(request, metadata=self._metadata)
        return HealthCheckService.Status(response.status)

    def wait_for_server(self, timeout: int) -> None:
        """Keep a watch on the health of the CFX connection.

        Response changes only when the service's serving status changes.

        Parameters
        ----------
        timeout : int
            Timeout in seconds.

        Raises
        ------
        TimeoutError
            If the connection to the CFX server could not be established within the timeout.
        """
        request = HealthCheckModule.HealthCheckRequest()
        responses = self._stub.Watch(request, metadata=self._metadata, timeout=timeout)

        while True:
            try:
                response = next(responses)
                if response.status == 1:
                    responses.cancel()
            except StopIteration:
                break
            except grpc.RpcError as e:
                if e.code() == grpc.StatusCode.CANCELLED:
                    break
                if e.code() == grpc.StatusCode.DEADLINE_EXCEEDED:
                    raise TimeoutError(
                        f"The connection to the CFX server could not be established within the configurable {timeout} second time limit."
                    )
                raise

    def status(self) -> Status:
        """Get the health status of the CFX connection."""
        if self._channel:
            try:
                return self.check_health()
            except Exception:
                ex_type, ex_value, _ = sys.exc_info()
                logger.info(f"HealthCheckService.status() caught {ex_type.__name__}: {ex_value}")
                return self.Status.NOT_SERVING
        else:
            return self.Status.NOT_SERVING

    @property
    def is_serving(self) -> bool:
        """Flag indicating if CFX is serving."""
        return self.status() == self.Status.SERVING
