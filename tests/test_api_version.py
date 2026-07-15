# Copyright (C) 2023 - 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
# SPDX-License-Identifier: MIT

from unittest import mock

import grpc
import pytest

from ansys.cfx.core.utils import api_version
from ansys.cfx.core.utils.api_version import (
    API_V1_MIN_VERSION,
    detect_engine_version,
    get_batch_ops_modules,
    get_engine_eval_modules,
    get_events_modules,
    get_health_check_modules,
    get_settings_modules,
    use_api_v1,
)
from ansys.cfx.core.utils.cfx_version import CFXVersion

# ---------- use_api_v1 ----------


def test_use_api_v1_true_for_new_engine(monkeypatch):
    monkeypatch.delenv("CFX_API_VERSION_1", raising=False)
    assert use_api_v1(API_V1_MIN_VERSION) is True


def test_use_api_v1_false_for_old_engine(monkeypatch):
    monkeypatch.delenv("CFX_API_VERSION_1", raising=False)
    assert use_api_v1(CFXVersion.v252) is False


def test_use_api_v1_env_override(monkeypatch):
    monkeypatch.setenv("CFX_API_VERSION_1", "1")
    assert use_api_v1(CFXVersion.v252) is True


# ---------- module getters ----------


@pytest.mark.parametrize(
    "getter, expected_v1_suffix",
    [
        (get_batch_ops_modules, "v1"),
        (get_engine_eval_modules, "v1"),
        (get_events_modules, "v1"),
        (get_settings_modules, "v1"),
    ],
)
def test_getters_return_v1_for_new_engine(monkeypatch, getter, expected_v1_suffix):
    monkeypatch.delenv("CFX_API_VERSION_1", raising=False)
    result = getter(API_V1_MIN_VERSION)
    for mod in result if isinstance(result, tuple) else (result,):
        assert f".cfx.{expected_v1_suffix}" in mod.__name__


@pytest.mark.parametrize(
    "getter",
    [get_batch_ops_modules, get_engine_eval_modules, get_events_modules, get_settings_modules],
)
def test_getters_return_v0_for_old_engine(monkeypatch, getter):
    monkeypatch.delenv("CFX_API_VERSION_1", raising=False)
    result = getter(CFXVersion.v252)
    for mod in result if isinstance(result, tuple) else (result,):
        assert ".cfx.v0" in mod.__name__


def test_get_health_check_modules_new(monkeypatch):
    monkeypatch.delenv("CFX_API_VERSION_1", raising=False)
    pb2, pb2_grpc = get_health_check_modules(API_V1_MIN_VERSION)
    assert ".cfx.v1" in pb2.__name__


def test_get_health_check_modules_old(monkeypatch):
    monkeypatch.delenv("CFX_API_VERSION_1", raising=False)
    pb2, pb2_grpc = get_health_check_modules(CFXVersion.v252)
    assert "grpc_health.v1" in pb2.__name__


# ---------- detect_engine_version ----------


class _FakeRpcError(grpc.RpcError):
    def __init__(self, code):
        self._code = code

    def code(self):
        return self._code


def test_detect_engine_version_v1_success(monkeypatch):
    monkeypatch.delenv("CFX_API_VERSION_1", raising=False)

    def fake_probe(channel, metadata, tag):
        assert tag == "v1"
        return CFXVersion.v271

    monkeypatch.setattr(api_version, "_probe_engine_version", fake_probe)
    assert detect_engine_version(mock.Mock(), []) == CFXVersion.v271


def test_detect_engine_version_falls_back_to_v0(monkeypatch):
    monkeypatch.delenv("CFX_API_VERSION_1", raising=False)
    calls = []

    def fake_probe(channel, metadata, tag):
        calls.append(tag)
        return None if tag == "v1" else CFXVersion.v252

    monkeypatch.setattr(api_version, "_probe_engine_version", fake_probe)
    assert detect_engine_version(mock.Mock(), []) == CFXVersion.v252
    assert calls == ["v1", "v0"]


def test_detect_engine_version_env_forces_v1_only(monkeypatch):
    monkeypatch.setenv("CFX_API_VERSION_1", "1")
    calls = []

    def fake_probe(channel, metadata, tag):
        calls.append(tag)
        return CFXVersion.v271

    monkeypatch.setattr(api_version, "_probe_engine_version", fake_probe)
    detect_engine_version(mock.Mock(), [])
    assert calls == ["v1"]


def test_detect_engine_version_raises_when_all_fail(monkeypatch):
    monkeypatch.delenv("CFX_API_VERSION_1", raising=False)
    monkeypatch.setattr(api_version, "_probe_engine_version", lambda *a, **k: None)
    with pytest.raises(RuntimeError, match="Could not detect CFX engine version"):
        detect_engine_version(mock.Mock(), [])


def test_probe_engine_version_returns_none_on_fallback_status(monkeypatch):
    stub = mock.Mock()
    stub.InfoQuery.side_effect = _FakeRpcError(grpc.StatusCode.UNIMPLEMENTED)
    fake_pb2 = mock.Mock()
    fake_pb2_grpc = mock.Mock(EngineEvalStub=mock.Mock(return_value=stub))

    def fake_import(name):
        return fake_pb2_grpc if name.endswith("_grpc") else fake_pb2

    monkeypatch.setattr(api_version.importlib, "import_module", fake_import)
    assert api_version._probe_engine_version(mock.Mock(), [], "v1") is None


def test_probe_engine_version_reraises_unexpected_rpc_error(monkeypatch):
    stub = mock.Mock()
    stub.InfoQuery.side_effect = _FakeRpcError(grpc.StatusCode.UNAVAILABLE)
    fake_pb2 = mock.Mock()
    fake_pb2_grpc = mock.Mock(EngineEvalStub=mock.Mock(return_value=stub))

    def fake_import(name):
        return fake_pb2_grpc if name.endswith("_grpc") else fake_pb2

    monkeypatch.setattr(api_version.importlib, "import_module", fake_import)
    with pytest.raises(grpc.RpcError):
        api_version._probe_engine_version(mock.Mock(), [], "v1")
