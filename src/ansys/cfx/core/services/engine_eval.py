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

"""Wrappers over EngineEval gRPC service of CFX.
"""

from typing import Sequence

import grpc

from ansys.api.cfx.v0 import engine_eval_pb2 as EngineEvalProtoModule
from ansys.api.cfx.v0 import engine_eval_pb2_grpc as EngineEvalGrpcModule
from ansys.cfx.core.services.interceptors import (
    BatchInterceptor,
    ErrorStateInterceptor,
    TracingInterceptor,
)
from ansys.cfx.core.utils.cfx_version import CFXVersion


class EngineEvalService:
    """Class wrapping the EngineEval gRPC service of CFX.

    Using the methods from the EngineEval class is recommended.
    """

    def __init__(
        self, channel: grpc.Channel, metadata: list[tuple[str, str]], cfx_error_state
    ) -> None:
        """__init__ method of EngineEvalService class."""
        intercept_channel = grpc.intercept_channel(
            channel,
            ErrorStateInterceptor(cfx_error_state),
            TracingInterceptor(),
            BatchInterceptor(),
        )
        self.__stub = EngineEvalGrpcModule.EngineEvalStub(intercept_channel)
        self.__metadata = metadata

    def process_ccl(
        self, request: EngineEvalProtoModule.ProcessCCLRequest
    ) -> EngineEvalProtoModule.ProcessCCLResponse:
        """Exec RPC of EngineEval service."""
        return self.__stub.ProcessCCL(request, metadata=self.__metadata)

    def info_query(
        self, request: EngineEvalProtoModule.InfoQueryRequest
    ) -> EngineEvalProtoModule.InfoQueryResponse:
        """InfoQuery RPC of EngineEval service."""
        return self.__stub.InfoQuery(request, metadata=self.__metadata)

    def eval_expression(
        self, request: EngineEvalProtoModule.ExpressionEvalRequest
    ) -> EngineEvalProtoModule.ExpressionEvalResponse:
        """EngineEval RPC of EngineEval service."""
        return self.__stub.ExpressionEval(request, metadata=self.__metadata)


class Symbol:
    """Class representing the symbol datatype in CFX.

    Attributes
    ----------
    str : str
        Underlying string representation
    """

    def __init__(self, str: str) -> None:
        """__init__ method of Symbol class."""
        self.str = str

    def __repr__(self) -> str:
        return self.str


class EngineEval:
    """Class on which CFX's CCL code can be executed.

    Methods
    -------
    process_ccl(ccl, wait, silent)
        Send CCL commands and settings to execute in the engine. Return output if any.
    info_query(query, args)
        Evaluates a query in string format, returns string
    eval_expression(input)
        Evaluates a CCL expression in string format, returns Python
        value
    """

    def __init__(self, service: EngineEvalService) -> None:
        """__init__ method of EngineEval class."""
        self.service = service
        self.version = self.info_query("Engine Version")

    def get_engine_version(self) -> str:
        """Return engine version number."""
        return self.version

    def eval_expression(self, input: str) -> str:
        """Evaluates a CFX expression.

        This function is not available in CFX versions earlier than Release 26.1.

        Parameters
        ----------
        input : str
            Input CFX expression represented as str

        Returns
        -------
        str
            Output value in string format

        Raises
        ------
        RuntimeError
            If a CFX version earlier than Release 26.1 is being used.
        """
        if CFXVersion(self.version) < CFXVersion.v261:
            raise RuntimeError(
                "eval_expression is not supported before Release 26.1. "
                "Expressions can be created and evaluated from the 'expressions' object."
            )

        request = EngineEvalProtoModule.ExpressionEvalRequest()
        request.input = input
        response = self.service.eval_expression(request)
        return response.output

    def process_ccl(self, ccl: Sequence[str], wait: bool = True, silent: bool = True) -> str:
        """Executes CCL commands and settings. The CCL is in the form of a sequence of strings.

        Parameters
        ----------
        ccl : Sequence[str]
            Sequence of CCL
        wait : bool, optional
            Specifies whether to wait until execution completes, by
            default True
        silent : bool, optional
            Specifies whether to execute silently, by default True

        Returns
        -------
        str
           Output as string
        """
        request = EngineEvalProtoModule.ProcessCCLRequest()
        request.ccl.extend(ccl)
        request.wait = wait
        request.silent = silent
        response = self.service.process_ccl(request)
        return response.output

    def info_query(self, query: str, args: str = None) -> str:
        """Query engine info in string format.

        Parameters
        ----------
        query : str
            Input query in string format

        args : str
            Input query arguments in string format

        Returns
        -------
        str
            Output query value in string format
        """
        request = EngineEvalProtoModule.InfoQueryRequest()
        request.query = query
        if args is not None:
            request.args = args
        response = self.service.info_query(request)
        return response.output
