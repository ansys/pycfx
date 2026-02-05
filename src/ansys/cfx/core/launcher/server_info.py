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

"""Provides a module for server information."""

import os
from pathlib import Path
import tempfile

from ansys.cfx.core.cfx_connection import PortNotProvided
from ansys.cfx.core.launcher import launcher_utils
from ansys.cfx.core.launcher.error_handler import IpPortNotProvided
from ansys.cfx.core.session import _parse_server_info_file


def _get_server_info_file_name(use_tmpdir=True):
    server_info_dir = os.getenv("SERVER_INFO_DIR")
    dir_ = (
        Path(server_info_dir)
        if server_info_dir
        else tempfile.gettempdir() if use_tmpdir else Path.cwd()
    )
    fd, file_name = tempfile.mkstemp(suffix=".txt", prefix="serverinfo-", dir=str(dir_))
    os.close(fd)
    return file_name


def _check_ip_port(ip: str, port: int):
    """Check if a port is open on a given IP address."""

    if not (ip and port):
        raise IpPortNotProvided()

    if not port:
        raise PortNotProvided()

    import socket

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(2)
    try:
        result = sock.connect_ex((ip, port))
        if result != 0:
            raise InvalidIpPort()
    finally:
        sock.close()


def _get_server_info(
    server_info_file_name: str,
    ip: str | None = None,
    port: int | None = None,
    password: str | None = None,
):
    """Get server connection information of an already running session.
    Returns (ip, port, password) or (unix_socket, password)"""

    if not (ip and port) and not server_info_file_name:
        raise IpPortNotProvided()
    if (ip or port) and server_info_file_name:
        launcher_utils.logger.warning(
            "The IP address and port are extracted from the server-info file "
            "and their explicitly specified values are ignored."
        )
    else:
        if server_info_file_name:
            values = _parse_server_info_file(server_info_file_name)
            if len(values) == 2:
                return values
            else:
                ip, port, password = values
        ip = ip or os.getenv("PYCFX_CFX_IP", "127.0.0.1")
        port = port or os.getenv("PYCFX_CFX_PORT")

    _check_ip_port(ip=ip, port=port)

    return ip, port, password
