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

"""Module containing class encapsulating CFX connection and the Base Session."""

import logging
from typing import Any, Optional

from ansys.cfx.core.cfx_connection import CFXConnection
from ansys.cfx.core.common import flobject
from ansys.cfx.core.common.flobject import StateT
from ansys.cfx.core.journaling import Journal
from ansys.cfx.core.services import service_creator
from ansys.cfx.core.streaming_services.events_streaming import EventsManager
from ansys.cfx.core.utils.cfx_version import CFXVersion, get_version_for_file_name

logger = logging.getLogger("pycfx.general")


def _parse_server_info_file(file_name: str):
    """Parse server info file.
    Returns (ip, port, password) or (unix_socket, password)"""
    with open(file_name, encoding="utf-8") as f:
        lines = f.readlines()
    address = lines[0].strip()
    password = lines[1].strip()
    if address.startswith("unix:"):
        return address, password
    else:
        ip_and_port = address.split(":")
        ip = ip_and_port[0]
        port = int(ip_and_port[1])
        return ip, port, password


def _import_settings_root(root):
    _class_dict = {}
    api_keys = []
    if hasattr(root, "child_names"):
        api_keys = root.child_names

    for root_item in api_keys:
        _class_dict[root_item] = root.__dict__[root_item]

    settings_api_root = type("SettingsRoot", (object,), _class_dict)
    return settings_api_root()


class BaseSession:
    """Instantiates a CFX connection.

    Attributes
    ----------
    engine_eval: EngineEval
        Instance of EngineEval on which CFX's ccl code can be
        executed.

    Methods
    -------
    create_from_server_info_file(
        server_info_file_name, cleanup_on_exit, start_transcript
        )
        Create a Session instance from server-info file

    exit()
        Close the CFX connection and exit CFX.
    """

    def __init__(
        self,
        cfx_connection: CFXConnection,
        file_transfer_service: Optional[Any] = None,
    ):
        """BaseSession.

        Args:
            cfx_connection (:ref:`ref_cfx_connection`): Encapsulates a CFX connection.
            file_transfer_service: Supports file upload and download.
        """
        self._cfx_version = None
        self._settings_root = None
        self._settings_api_root = None

        BaseSession.build_from_cfx_connection(self, cfx_connection, file_transfer_service)

    def build_from_cfx_connection(
        self,
        cfx_connection: CFXConnection,
        file_transfer_service: Optional[Any] = None,
    ):
        """Build a BaseSession object from cfx_connection object."""
        self._cfx_connection = cfx_connection
        self._file_transfer_service = file_transfer_service
        self._error_state = cfx_connection._error_state
        self.engine_eval = cfx_connection.engine_eval
        self._preferences = None
        self.journal = Journal(self.engine_eval)

        self._batch_ops_service = service_creator("batch_ops").create(
            cfx_connection._channel, cfx_connection._metadata
        )

        self._events_service = service_creator("events").create(
            cfx_connection._channel, cfx_connection._metadata
        )
        self.events_manager = EventsManager(
            self._events_service, self._error_state, cfx_connection._id
        )

        self.events_manager.start()

        self._settings_service = service_creator("settings").create(
            cfx_connection._channel,
            cfx_connection._metadata,
            self.engine_eval,
            self._error_state,
        )

        self.health_check_service = cfx_connection.health_check_service
        self.connection_properties = cfx_connection.connection_properties

        for obj in (self.events_manager,):
            self._cfx_connection.register_finalizer_cb(obj.stop)

    def is_server_healthy(self) -> bool:
        """Whether the current session is healthy (i.e. The server is 'SERVING')."""
        return self.health_check_service.is_serving

    @property
    def id(self) -> str:
        """Return the session ID."""
        return self._cfx_connection._id

    @classmethod
    def _create_from_server_info_file(
        cls,
        server_info_file_name: str,
        file_transfer_service: Optional[Any] = None,
        **connection_kwargs,
    ):
        """Create a Session instance from server-info file.

        Parameters
        ----------
        server_info_file_name : str
            Path to server-info file written out by CFX server
        file_transfer_service : Optional
            Support file upload and download.
        **connection_kwargs : dict, optional
            Additional keyword arguments may be specified, and they will be passed to the `CFXConnection`
            being initialized. For example, ``cleanup_on_exit = True``, or ``start_transcript = True``.
            See :func:`CFXConnection initialization <ansys.cfx.core.cfx_connection.CFXConnection.__init__>`
            for more details and possible arguments.

        Returns
        -------
        Session
            Session instance
        """
        values = _parse_server_info_file(server_info_file_name)
        if len(values) == 2:
            address, password = values
            ip, port = None, None
        else:
            ip, port, password = values
            address = None
        session = cls(
            cfx_connection=CFXConnection(
                ip=ip, port=port, address=address, password=password, **connection_kwargs
            ),
            file_transfer_service=file_transfer_service,
        )
        return session

    @classmethod
    def get_name(cls) -> str | None:
        """Return session name."""
        return None

    @classmethod
    def has_remote_server(cls) -> bool:
        """Return True if the session can connect to a remote server."""
        return True

    @property
    def _version(self):
        """CFX's product version."""
        if self._cfx_version is None:
            self._cfx_version = get_version_for_file_name(session=self)
        return self._cfx_version

    @property
    def settings(self):
        """Root settings object."""
        if self._settings_root is None:
            self._settings_root = flobject.get_root(
                flproxy=self._settings_service,
                session_name=self.get_name(),
                version=self._version,
                file_transfer_service=self._file_transfer_service,
                info_query=self._cfx_connection.engine_eval.info_query,
            )
        return self._settings_root

    def get_state(self) -> StateT:
        """Get the state of the object."""
        return self.settings.get_state()

    def set_state(self, state: Optional[StateT] = None, **kwargs):
        """Set the state of the object."""
        self.settings.set_state(state, **kwargs)

    def __call__(self):
        return self.get_state()

    def _populate_settings_api_root(self):
        if not self._settings_api_root:
            self._settings_api_root = _import_settings_root(self.settings)

    def __getattr__(self, attr):
        self._populate_settings_api_root()
        return getattr(self._settings_api_root, attr)

    def __dir__(self):
        self._populate_settings_api_root()
        dir_list = set(list(self.__dict__.keys()) + dir(type(self)) + dir(self._settings_api_root))
        return sorted(dir_list)

    def execute_ccl(self, command: str, wait: bool = True) -> None:
        """Executes a ccl command."""
        self.engine_eval.process_ccl([command], wait)

    def get_cfx_version(self) -> CFXVersion:
        """Gets and returns the CFX version."""
        return CFXVersion(self.engine_eval.version)

    def exit(self, **kwargs) -> None:
        """Exit session."""
        logger.debug("session.exit() called")
        self._cfx_connection.exit(**kwargs)

    def force_exit(self) -> None:
        """Immediately terminates the CFX session, losing unsaved progress and
        data."""
        self._cfx_connection.force_exit()

    def upload(self, file_name: str):
        """Upload a file to the server.

        Parameters
        ----------
        file_name : str
            Name of the local file to upload to the server.
        """
        if self._file_transfer_service:
            return self._file_transfer_service.upload_file(file_name)

    def download(self, file_name: str, local_directory: Optional[str] = "."):
        """Download a file from the server.

        Parameters
        ----------
        file_name : str
            Name of the file to download from the server.
        local_directory : str, optional
            Local destination directory. The default is the current working directory.
        """
        if self._file_transfer_service:
            return self._file_transfer_service.download_file(file_name, local_directory)

    def __enter__(self):
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any):
        """Close the CFX connection and exit CFX."""
        logger.debug("session.__exit__() called")
        self.exit()
