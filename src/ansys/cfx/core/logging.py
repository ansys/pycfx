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

"""Module controlling PyCFX's logging functionality."""

import logging.config
import os
from pathlib import Path
from typing import Optional, Union

import yaml

_logging_file_enabled = False


def root_config():
    """Sets up the root PyCFX logger that outputs messages to stdout, but not to
    files."""
    logger = logging.getLogger("pycfx")
    logger.setLevel("WARNING")
    formatter = logging.Formatter("%(name)s %(levelname)s: %(message)s")
    if not logger.handlers:
        ch = logging.StreamHandler()
        ch.setLevel("WARNING")
        ch.setFormatter(formatter)
        logger.addHandler(ch)


def is_active() -> bool:
    """Returns whether PyCFX logging to file is active."""
    return _logging_file_enabled


def get_default_config() -> dict:
    """Returns the default configuration dictionary obtained from parsing from the
    PyCFX ``logging_config.yaml`` file.

    Examples
    --------
    >>> import ansys.cfx.core as pycfx
    >>> import pprint
    >>> pprint.pprint(pycfx.logging.get_default_config())
    {'disable_existing_loggers': False,
     'formatters': {'logfile_fmt': {'format': '%(asctime)s %(name)-21s '
                                              '%(levelname)-8s %(message)s'}},
     'handlers': {'pycfx_file': {'backupCount': 9,
                                 'class': 'logging.handlers.RotatingFileHandler',
                                 'filename': 'pycfx.log',
                                 'formatter': 'logfile_fmt',
                                 'level': 'NOTSET',
                                 'maxBytes': 10485760}},
     'loggers': {'pycfx.general': {'handlers': ['pycfx_file'], 'level': 'DEBUG'},
                 'pycfx.launcher': {'handlers': ['pycfx_file'], 'level': 'DEBUG'},
                 'pycfx.networking': {'handlers': ['pycfx_file'], 'level': 'DEBUG'},
                 'pycfx.server_events': {'handlers': ['pycfx_file'],
                                         'level': 'DEBUG'},
                 'pycfx.settings_api': {'handlers': ['pycfx_file'],
                                        'level': 'DEBUG'},
                 'pycfx.solver_control': {'handlers': ['pycfx_file'],
                                          'level': 'DEBUG'}},
     'version': 1}
    """
    file_path = Path(__file__).resolve()
    file_dir = file_path.parent
    yaml_path = file_dir / "logging_config.yaml"
    with open(yaml_path, "rt") as f:
        config = yaml.safe_load(f)
    return config


def enable(level: Union[str, int] = "DEBUG", custom_config: Optional[dict] = None):
    """Enables PyCFX logging to file.

    Parameters
    ----------
    level : str or int, optional
        Specified logging level to set PyCFX loggers to. If omitted, level is set to DEBUG.
    custom_config : dict, optional
        Used to provide a customized logging configuration file that will be used instead
        of the ``logging_config.yaml`` file (see also :func:`get_default_config`).

    Notes
    -----
    See logging levels in https://docs.python.org/3/library/logging.html#logging-levels

    Examples
    --------
    Using the default logging setup:

    >>> import ansys.cfx.core as pycfx
    >>> pycfx.logging.enable() #doctest: +ELLIPSIS
    PyCFX logging file ...
    Setting PyCFX global logging level to DEBUG.

    Customizing logging configuration (see also :func:`get_default_config`):

    >>> import ansys.cfx.core as pycfx
    >>> config_dict = pycfx.logging.get_default_config()
    >>> config_dict['handlers']['pycfx_file']['filename'] = 'test.log'
    >>> pycfx.logging.enable(custom_config=config_dict) # doctest: +ELLIPSIS
    PyCFX logging file ...
    Setting PyCFX global logging level to DEBUG.

    """
    global _logging_file_enabled

    if _logging_file_enabled:
        print("PyCFX logging to file is already active, overwriting previous configuration...")

    _logging_file_enabled = True

    # Configure the logging system
    if custom_config is not None:
        config = custom_config
    else:
        config = get_default_config()

    logging.config.dictConfig(config)
    file_name = config["handlers"]["pycfx_file"]["filename"]

    print(f"PyCFX logging file {Path.cwd() / file_name}")

    set_global_level(level)


def get_logger(*args, **kwargs):
    """Retrieves logger.

    Convenience wrapper for Python's :func:`logging.getLogger` function.
    """
    return logging.getLogger(*args, **kwargs)


def set_global_level(level: Union[str, int]):
    """Changes the levels of all PyCFX loggers that write to log file.

    Parameters
    ----------
    level : str or int
        Specified logging level to set PyCFX loggers to.

    Notes
    -----
    See logging levels in https://docs.python.org/3/library/logging.html#logging-levels

    Examples
    --------
    >>> import ansys.cfx.core as pycfx
    >>> pycfx.logging.set_global_level(10)
    Setting PyCFX global logging level to 10.

    >>> pycfx.logging.set_global_level('DEBUG')
    Setting PyCFX global logging level to DEBUG.

    """
    if not is_active():
        print("Logging is not active, enable it first.")
        return
    if isinstance(level, str):
        if level.isdigit():
            level = int(level)
        else:
            level = level.upper()
    print(f"Setting PyCFX global logging level to {level}.")
    pycfx_loggers = list_loggers()
    for name in pycfx_loggers:
        if name != "pycfx":  # do not change the console root PyCFX logger
            logging.getLogger(name).setLevel(level)


def list_loggers():
    """List all PyCFX loggers.

    Returns
    -------
    list of str
        Each list element is a PyCFX logger name that can be individually controlled
        through :func:`ansys.cfx.core.logging.get_logger`.

    Notes
    -----
    PyCFX loggers use the standard Python logging library, for more details
    see https://docs.python.org/3/library/logging.html#logger-objects

    Examples
    --------
    >>> import ansys.cfx.core as pycfx
    >>> pycfx.logging.enable() #doctest: +ELLIPSIS
    PyCFX logging file ...
    Setting PyCFX global logging level to DEBUG.

    >>> all_loggers = pycfx.logging.list_loggers()
    >>> all_loggers.sort()
    >>> all_loggers #doctest: +ELLIPSIS
    ['pycfx', 'pycfx.general', 'pycfx.launcher', 'pycfx.networking', ...

    >>> logger = pycfx.logging.get_logger('pycfx.networking')
    >>> logger
    <Logger pycfx.networking (DEBUG)>
    >>> logger.setLevel('ERROR')
    >>> logger
    <Logger pycfx.networking (ERROR)>
    """
    logger_dict = logging.root.manager.loggerDict
    pycfx_loggers = []
    for name in logger_dict:
        if name.startswith("pycfx"):
            pycfx_loggers.append(name)
    return pycfx_loggers


def configure_env_var() -> None:
    """Verifies whether ``PYCFX_LOGGING`` environment variable was defined in the
    system. Executed once automatically on PyCFX initialization.

    Notes
    -----
    The usual way to enable PyCFX logging to file is through :func:`enable()`.
    ``PYCFX_LOGGING`` set to ``0`` or ``OFF`` is the same as if no environment variable was set.
    If logging debug output to file by default is desired, without having to use :func:`enable()` every time,
    set environment variable ``PYCFX_LOGGING`` to ``DEBUG``.
    """
    env_logging_level = os.getenv("PYCFX_LOGGING")
    if env_logging_level:
        if env_logging_level.isdigit():
            env_logging_level = int(env_logging_level)
        else:
            env_logging_level = env_logging_level.upper()
        if not is_active() and env_logging_level not in [0, "OFF"]:
            print("PYCFX_LOGGING environment variable specified, enabling logging...")
            enable(env_logging_level)
