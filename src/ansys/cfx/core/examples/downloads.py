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

"""Functions to download sample datasets from the Ansys example data repository."""

import logging
from pathlib import Path
import re
import zipfile

from ansys.cfx.core.utils.networking import check_url_exists, get_url_content

logger = logging.getLogger("pycfx.networking")


class RemoteFileNotFoundError(FileNotFoundError):
    """Raised on an attempt to download a non-existent remote file."""

    def __init__(self, url):
        """Initializes RemoteFileNotFoundError."""
        super().__init__(f"{url} does not exist.")


def _decompress(file_name: str, extract_path=None) -> None:
    """Decompress zipped file."""
    zip_ref = zipfile.ZipFile(file_name, "r")
    zip_ref.extractall(extract_path)
    return zip_ref.close()


def _get_file_url(file_name: str, directory: str | None = None) -> str:
    """Get file URL."""
    if directory:
        return "https://github.com/ansys/example-data/raw/main/" f"{directory}/{file_name}"
    return f"https://github.com/ansys/example-data/raw/main/{file_name}"


def _retrieve_file(
    url: str,
    file_name: str,
    save_path: str | None = None,
    return_without_path: bool = False,
) -> str:
    """Download specified file from specified URL."""
    file_name = Path(file_name).name
    if save_path is None:
        save_path_obj = Path.cwd()
    else:
        save_path_obj = Path(save_path).resolve()
    local_path = str(save_path_obj / file_name)
    local_path_no_zip = Path(re.sub(r"\.zip$", "", local_path))
    file_name_no_zip = re.sub(r"\.zip$", "", file_name)
    # First check if file has already been downloaded
    logger.info(f"Checking if {local_path_no_zip} already exists...")
    if local_path_no_zip.is_file() or local_path_no_zip.is_dir():
        logger.info("File already exists.")
        if return_without_path:
            return file_name_no_zip
        else:
            return str(local_path_no_zip)

    logger.info("File does not exist. Downloading specified file...")

    # Check if save path exists
    save_path_obj.mkdir(parents=True, exist_ok=True)

    # Download file
    logger.info(f'Downloading URL: "{url}"')
    content = get_url_content(url)
    with open(local_path, "wb") as f:
        f.write(content)

    if local_path.endswith(".zip"):
        _decompress(local_path, str(save_path_obj))
        local_path = str(local_path_no_zip)
        file_name = file_name_no_zip
    logger.info("Download successful.")
    if return_without_path:
        return file_name
    else:
        return local_path


def download_file(
    file_name: str,
    directory: str | None = None,
    save_path: str | None = None,
    return_without_path: bool = False,
) -> str:
    """Download specified example file from the Ansys example data repository.

    Parameters
    ----------
    file_name : str
        File to download.
    directory : str, default: None
        Ansys example data repository directory where the specified file is located. If not
        specified, looks for the file in the root directory of the repository.
    save_path : str, default: None
        Path to download the specified file to.
    return_without_path : bool, default: False
        Whether to return the full path to the file. If ``True``, only the file name is returned.

    Raises
    ------
    RemoteFileNotFoundError
        If remote file does not exist.

    Returns
    -------
    str
        File path of the downloaded or already existing file, or only the file name if
        ``return_without_path=True``.

    Examples
    --------
    >>> from ansys.cfx.core import examples
    >>> file_path = examples.download_file("StaticMixerMesh.gtm", "pycfx/static_mixer")
    """

    url = _get_file_url(file_name, directory)
    if not check_url_exists(url):
        raise RemoteFileNotFoundError(url)
    return _retrieve_file(url, file_name, save_path, return_without_path)
