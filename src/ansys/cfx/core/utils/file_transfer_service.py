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

"""Module for file transfer service."""

import os
from pathlib import Path
from typing import Any, Callable, Optional, Union  # noqa: F401

import ansys.platform.instancemanagement as pypim


class PyPIMConfigurationError(ConnectionError):
    """Raised when `PyPIM <https://pypim.docs.pyansys.com/version/stable/>`_ is not configured."""

    def __init__(self):
        super().__init__("PyPIM is not configured.")


class PimFileTransferService:
    """Provides a file transfer service based on
    `PyPIM <https://pypim.docs.pyansys.com/version/stable/>`_ and the ``simple_upload_server()``
    function.

    Attributes
    ----------
    pim_instance: PIM instance
        Instance of PIM that supports upload server services.
    file_service: Client instance
        Instance of the client that supports upload and download methods.

    Methods
    -------
    upload(
        file_name, remote_file_name
        )
        Upload a file to the server.

    download(
        file_name, local_directory
        )
        Download a file from the server.
    """

    def __init__(self, pim_instance: Optional[Any] = None):
        self.pim_instance = pim_instance
        self.upload_server = None
        self.file_service = None
        try:
            if "http-simple-upload-server" in self.pim_instance.services:
                self.upload_server = self.pim_instance.services["http-simple-upload-server"]
            elif "grpc" in self.pim_instance.services:
                self.upload_server = self.pim_instance.services["grpc"]
        except (AttributeError, KeyError):
            pass
        else:
            try:
                from simple_upload_server.client import Client

                self.file_service = Client(
                    token="token",
                    url=self.upload_server.uri,
                    headers=self.upload_server.headers,
                )
            except ModuleNotFoundError:
                pass

    @property
    def pim_service(self):
        """PIM file transfer service."""
        return self.file_service

    def is_configured(self):
        """Check if PyPIM is configured."""
        return pypim.is_configured()

    def upload_file(self, file_name: str, remote_file_name: Optional[str] = None):
        """Upload a file to the server supported by
        `PyPIM <https://pypim.docs.pyansys.com/version/stable/>`_.

        Parameters
        ----------
        file_name : str
            File name.
        remote_file_name : str, default: None
            Remote file name.

        Raises
        ------
        FileNotFoundError
            If the file does not exist.
        PyPIMConfigurationError
            If PyPIM is not configured.
        """
        if not self.is_configured():
            raise PyPIMConfigurationError()
        elif self.file_service:
            file_path = Path(file_name)
            if file_path.is_file():
                expanded_file_path = os.path.expandvars(str(file_path))
                upload_file_name = remote_file_name or Path(expanded_file_path).name
                self.file_service.upload_file(expanded_file_path, upload_file_name)
            else:
                raise FileNotFoundError(f"{file_name} does not exist.")

    def upload(self, file_name: Union[list[str], str]):
        """Upload a file to the server.

        Parameters
        ----------
        file_name : str
            File name.

        Raises
        ------
        FileNotFoundError
            If a file does not exist.
        """
        files = [file_name] if isinstance(file_name, str) else file_name
        if self.is_configured():
            for file in files:
                file_path = Path(file)
                if file_path.is_file():
                    if not self.file_service.file_exist(file_path.name):
                        self.upload_file(file_name=file)
                elif not self.file_service.file_exist(file_path.name):
                    raise FileNotFoundError(f"{file} does not exist.")

    def download_file(self, file_name: str, local_directory: Optional[str] = None):
        """Download a file from the server supported by
        `PyPIM <https://pypim.docs.pyansys.com/version/stable/>`_.

        Parameters
        ----------
        file_name : str
            File name.
        local_directory : str, default: None
            Local directory.

        Raises
        ------
        FileNotFoundError
            If the remote file does not exist.
        PyPIMConfigurationError
            If PyPIM is not configured.
        """
        if not self.is_configured():
            raise PyPIMConfigurationError()
        elif self.file_service:
            if self.file_service.file_exist(file_name):
                self.file_service.download_file(file_name, local_directory)
            else:
                raise FileNotFoundError("Remote file does not exist.")

    def download(
        self,
        file_name: Union[list[str], str],
    ):
        """Download a file from the server.

        Parameters
        ----------
        file_name : str
            File name.
        """
        files = [file_name] if isinstance(file_name, str) else file_name
        if self.is_configured():
            for file in files:
                file_path = Path(file)
                if file_path.is_file():
                    print(f"\nFile already exists. File path:\n{file}\n")
                else:
                    self.download_file(file_name=file_path.name, local_directory=".")

    def __call__(self, pim_instance: Optional[Any] = None):
        self.pim_instance = pim_instance
