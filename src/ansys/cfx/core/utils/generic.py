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

"""Module providing generic functionality."""

from abc import ABCMeta
import asyncio
from functools import partial
import time

loop = asyncio.get_event_loop()


class SingletonMeta(type):
    """Meta class for singleton type."""

    _single_instance = None

    def __call__(cls, *args, **kwargs):
        if not cls._single_instance:
            cls._single_instance = super(SingletonMeta, cls).__call__(*args, **kwargs)
        return cls._single_instance


class AbstractSingletonMeta(ABCMeta, SingletonMeta):
    """Meta class for abstract singleton type."""

    pass


def execute_in_event_loop_threadsafe(f):
    """Decorator to execute function in an event loop from another thread."""

    def cb(*args, **kwargs):
        par = partial(f, *args, **kwargs)
        loop.call_soon_threadsafe(par)

    return cb


def execute_in_event_loop(f):
    """Decorator to execute function in an event loop."""

    def cb(*args, **kwargs):
        par = partial(f, *args, **kwargs)
        loop.call_soon(par)

    return cb


def in_notebook():
    """Function to check if application is running in notebook."""
    try:
        from IPython import get_ipython

        if "IPKernelApp" not in get_ipython().config:
            return False
    except (ImportError, AttributeError):
        return False
    return True


def timing(func):
    """Timing function decorator."""

    def wrapper(*args, **kwargs):
        t1 = time.time()
        res = func(*args, **kwargs)
        t2 = time.time()
        print(func.__name__, t2 - t1)
        return res

    return wrapper
