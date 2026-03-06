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

"""Batch RPC service."""

import inspect
import logging
from types import ModuleType
from typing import TypeVar
import weakref

from google.protobuf.message import Message
import grpc

import ansys.api.cfx.v0 as api
from ansys.api.cfx.v0 import batch_ops_pb2, batch_ops_pb2_grpc

_TBatchOps = TypeVar("_TBatchOps", bound="BatchOps")

network_logger: logging.Logger = logging.getLogger("pycfx.networking")


class BatchOpsService:
    """Provides class wrapping methods in the batch RPC service."""

    def __init__(self, channel: grpc.Channel, metadata: list[tuple[str, str]]) -> None:
        """Initialize an instance of the ``BatchOpsService`` class."""

        from ansys.cfx.core.services.interceptors import GrpcErrorInterceptor

        intercept_channel = grpc.intercept_channel(
            channel,
            GrpcErrorInterceptor(),
        )
        self._stub = batch_ops_pb2_grpc.BatchOpsStub(intercept_channel)
        self._metadata = metadata

    def execute(self, request: batch_ops_pb2.ExecuteRequest) -> batch_ops_pb2.ExecuteResponse:
        """Execute RPC of the ``BatchOps`` service."""
        return self._stub.Execute(request, metadata=self._metadata)


class BatchOps:
    """Provides for executing operations in batch in CFX.

    Examples
    --------

    >>> import ansys.cfx.core as pycfx
    >>> pypost = pycfx.PostProcessing.from_install()
    >>> with pycfx.BatchOps(pypost):
    ...     pypost.file.load_results(file_name=<results_name>)
    ...     pypost.results.plane["Plane 1"] = {}

    The preceding code executes both operations through a single gRPC call upon exiting the
    ``with`` block.

    Operations that perform queries in CFX are executed immediately, while others are
    queued for batch execution. Some queries are executed behind the scenes while
    queuing an operation for batch execution. Developers must ensure that they do not
    depend on previously queued operations.


    For example, the following code throws a ``KeyError`` as ``pypost.results.plane["Plane 1"]``
    attempts to access the ``Plane 1`` named object which has not been created yet.

    >>> pypost = pycfx.PostProcessing.from_install()
    >>> with pycfx.BatchOps(pypost):
    ...     pypost.file.load_results(file_name="StaticMixer_001.res")
    ...     pypost.results.plane["Plane 1"] = {}
    ...     pypost.results.plane["Plane 1"].option = "ZX Plane"
    Traceback (most recent call last):
      ...
    KeyError: "'plane' has no attribute 'Plane 1'.\\n"
    """

    _proto_files: list[ModuleType] | None = None

    def _instance():
        return None

    @classmethod
    def instance(cls) -> _TBatchOps | None:
        """Get the ``BatchOps`` instance.

        Returns
        -------
        BatchOps
            BatchOps instance.
        """
        return cls._instance()

    class Op:
        """Provides for creating a single batch operation."""

        def __init__(self, package: str, service: str, method: str, request_body: bytes) -> None:
            """Initialize an instance of the ``Op`` class."""
            self._request = batch_ops_pb2.ExecuteRequest(
                package=package,
                service=service,
                method=method,
                request_body=request_body,
            )
            if not BatchOps._proto_files:
                BatchOps._proto_files = [
                    x[1]
                    for x in inspect.getmembers(api, inspect.ismodule)
                    if hasattr(x[1], "DESCRIPTOR")
                ]
            self._supported = False
            self.response_cls = None
            for file in BatchOps._proto_files:
                file_desc = file.DESCRIPTOR
                if file_desc.package == package:
                    service_desc = file_desc.services_by_name.get(service)
                    if service_desc:
                        # TODO Add custom option in .proto files to identify getters
                        if not method.startswith("Get") and not method.startswith("get"):
                            method_desc = service_desc.methods_by_name.get(method)
                            if (
                                method_desc
                                and not method_desc.client_streaming
                                and not method_desc.server_streaming
                            ):
                                self._supported = True
                                response_cls_name = method_desc.output_type.name
                                # TODO Get the response_cls from message_factory
                                try:
                                    self.response_cls = getattr(file, response_cls_name)
                                    break
                                except AttributeError:
                                    pass
            if self._supported:
                self._request = batch_ops_pb2.ExecuteRequest(
                    package=package,
                    service=service,
                    method=method,
                    request_body=request_body,
                )
                self._status = None
                self._result = None
            self.queued = False

        def update_result(self, status: batch_ops_pb2.ExecuteStatus, data: str) -> None:
            """Update results after the batch operation is executed."""
            obj = self.response_cls()
            try:
                obj.ParseFromString(data)
            except Exception:
                pass
            self._status = status
            self._result = obj

    def __new__(cls, session) -> _TBatchOps:
        if cls.instance() is None:
            instance = super(BatchOps, cls).__new__(cls)
            instance._service = session._batch_ops_service
            instance._ops = []
            instance.batching = False
            cls._instance = weakref.ref(instance)
        return cls.instance()

    def __enter__(self) -> _TBatchOps:
        """Entering the with block."""
        self.clear_ops()
        self.batching = True
        return self

    def __exit__(self, exc_type, exc_value, exc_tb) -> None:
        """Exiting from the with block."""
        network_logger.debug("Executing batch operations")
        self.batching = False
        if not exc_type:
            requests = (x._request for x in self._ops)
            responses = self._service.execute(requests)
            for i, response in enumerate(responses):
                self._ops[i].update_result(response.status, response.response_body)

    def add_op(self, package: str, service: str, method: str, request: Message) -> Op:
        """Queue a single batch operation. Only the non-getter operations are queued.

        Parameters
        ----------
        package : str
            gRPC package name.
        service : str
            gRPC service name.
        method : str
            gRPC method name.
        request : Any
            gRPC request message.

        Returns
        -------
        BatchOps.Op
            BatchOps.Op object with a queued attribute that is ``True`` if the operation
            has been queued.
        """
        op = BatchOps.Op(package, service, method, request.SerializeToString())
        if op._supported:
            network_logger.debug(
                f"Adding batch operation with package {package}, service {service}, and method "
                f"{method}."
            )
            self._ops.append(op)
            op.queued = True
        return op

    def clear_ops(self) -> None:
        """Clear all queued batch operations."""
        self._ops.clear()
