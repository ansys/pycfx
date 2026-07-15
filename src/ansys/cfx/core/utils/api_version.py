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
"""Resolve the CFX proto API version from the engine version."""

import importlib
import logging
import os

import grpc

from ansys.cfx.core.utils.cfx_version import CFXVersion

logger = logging.getLogger("pycfx.general")

API_V1_MIN_VERSION = CFXVersion.v271

# Statuses that mean "this proto version is not the right one" rather
# than a real server failure.
_PROBE_FALLBACK_STATUSES = {
    grpc.StatusCode.UNIMPLEMENTED,
    grpc.StatusCode.INTERNAL,  # protobuf parse failure on server
    grpc.StatusCode.INVALID_ARGUMENT,
}


def _probe_engine_version(channel, metadata, api_tag: str) -> CFXVersion | None:
    """Try ``InfoQuery('Engine Version')`` against the given proto version."""
    try:
        pb2 = importlib.import_module(f"ansys.api.cfx.{api_tag}.engine_eval_pb2")
        pb2_grpc = importlib.import_module(f"ansys.api.cfx.{api_tag}.engine_eval_pb2_grpc")
    except (ModuleNotFoundError, ImportError) as exc:
        logger.debug(f"Proto API modules for {api_tag} not available ({exc}).")
        return None
    stub = pb2_grpc.EngineEvalStub(channel)
    request = pb2.InfoQueryRequest(query="Engine Version")
    try:
        response = stub.InfoQuery(request, metadata=metadata, timeout=10)
    except grpc.RpcError as exc:
        if exc.code() in _PROBE_FALLBACK_STATUSES:
            logger.debug(f"API probe with {api_tag} failed ({exc.code().name}).")
            return None
        raise
    return CFXVersion(response.output)


def detect_engine_version(channel, metadata) -> CFXVersion:
    """Resolve the engine version by probing the CFX gRPC service.

    The ``CFX_API_VERSION_1`` environment variable, when set to any value,
    forces the v1 proto API and skips v0 probing. Otherwise, v1 is tried
    first and v0 is used as a fallback; the first proto version that yields
    a valid response wins.

    Callers should cache the returned version and reuse it via
    :func:`use_api_v1` for all subsequent service lookups.

    Raises
    ------
    RuntimeError
        If neither the v1 nor v0 protos produce a usable response.
    """
    if os.getenv("CFX_API_VERSION_1") is not None:
        candidates = ("v1",)
    else:
        candidates = ("v1", "v0")

    for tag in candidates:
        version = _probe_engine_version(channel, metadata, tag)
        if version is not None:
            logger.info(f"Detected engine {version} via proto API {tag}.")
            return version
    tried = ", ".join(candidates)
    raise RuntimeError(f"Could not detect CFX engine version with protos: {tried}.")


def get_batch_ops_modules(engine_version: CFXVersion):
    """Return ``(api_package, batch_ops_pb2, batch_ops_pb2_grpc)`` for the engine version."""
    if use_api_v1(engine_version):
        import ansys.api.cfx.v1 as api
        from ansys.api.cfx.v1 import batch_ops_pb2, batch_ops_pb2_grpc
    else:
        import ansys.api.cfx.v0 as api
        from ansys.api.cfx.v0 import batch_ops_pb2, batch_ops_pb2_grpc
    return api, batch_ops_pb2, batch_ops_pb2_grpc


def get_engine_eval_modules(engine_version: CFXVersion):
    """Return the ``engine_eval`` pb2 and pb2_grpc modules matching the engine version."""
    if use_api_v1(engine_version):
        from ansys.api.cfx.v1 import engine_eval_pb2, engine_eval_pb2_grpc
    else:
        from ansys.api.cfx.v0 import engine_eval_pb2, engine_eval_pb2_grpc
    return engine_eval_pb2, engine_eval_pb2_grpc


def get_events_modules(engine_version: CFXVersion):
    """Return the ``events`` pb2 and pb2_grpc modules matching the engine version."""
    if use_api_v1(engine_version):
        from ansys.api.cfx.v1 import events_pb2, events_pb2_grpc
    else:
        from ansys.api.cfx.v0 import events_pb2, events_pb2_grpc
    return events_pb2, events_pb2_grpc


def get_health_check_modules(engine_version: CFXVersion):
    """Return the health-check pb2 and pb2_grpc modules.

    Uses the CFX v1 health service for new engines, falling back to the
    standard ``grpc_health.v1`` modules for older engines.
    """
    if use_api_v1(engine_version):
        from ansys.api.cfx.v1 import health_pb2, health_pb2_grpc
    else:
        from grpc_health.v1 import health_pb2, health_pb2_grpc
    return health_pb2, health_pb2_grpc


def get_settings_modules(engine_version: CFXVersion):
    """Return the ``settings`` pb2 and pb2_grpc modules matching the engine version."""
    if use_api_v1(engine_version):
        from ansys.api.cfx.v1 import settings_pb2, settings_pb2_grpc
    else:
        from ansys.api.cfx.v0 import settings_pb2, settings_pb2_grpc
    return settings_pb2, settings_pb2_grpc


def use_api_v1(engine_version: CFXVersion) -> bool:
    """Return ``True`` if the engine speaks the new (v1) proto API."""
    if os.getenv("CFX_API_VERSION_1") is not None:
        return True
    result = engine_version >= API_V1_MIN_VERSION
    return result
