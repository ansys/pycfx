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

"""Provides a module to create gRPC services."""

from ansys.cfx.core.services.batch_ops import BatchOpsService
from ansys.cfx.core.services.engine_eval import EngineEval
from ansys.cfx.core.services.events import EventsService
from ansys.cfx.core.services.health_check import HealthCheckService
from ansys.cfx.core.services.settings import SettingsService

_service_cls_by_name = {
    "batch_ops": BatchOpsService,
    "events": EventsService,
    "engine_eval": EngineEval,
    "health_check": HealthCheckService,
    "settings": SettingsService,
}


class service_creator:
    """A gRPC service creator."""

    def __init__(self, service_name: str):
        self._service_cls = _service_cls_by_name[service_name]

    def create(self, *args, **kwargs):
        """Create a gRPC service."""
        return self._service_cls(*args, **kwargs)
