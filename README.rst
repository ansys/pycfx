PyCFX
=====
|pyansys| |python| |pypi| |GH-CI| |codecov-internal| |MIT| |black| |pre-commit|

.. |pyansys| image:: https://img.shields.io/badge/Py-Ansys-ffc107.svg?logo=data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAIAAACQkWg2AAABDklEQVQ4jWNgoDfg5mD8vE7q/3bpVyskbW0sMRUwofHD7Dh5OBkZGBgW7/3W2tZpa2tLQEOyOzeEsfumlK2tbVpaGj4N6jIs1lpsDAwMJ278sveMY2BgCA0NFRISwqkhyQ1q/Nyd3zg4OBgYGNjZ2ePi4rB5loGBhZnhxTLJ/9ulv26Q4uVk1NXV/f///////69du4Zdg78lx//t0v+3S88rFISInD59GqIH2esIJ8G9O2/XVwhjzpw5EAam1xkkBJn/bJX+v1365hxxuCAfH9+3b9/+////48cPuNehNsS7cDEzMTAwMMzb+Q2u4dOnT2vWrMHu9ZtzxP9vl/69RVpCkBlZ3N7enoDXBwEAAA+YYitOilMVAAAAAElFTkSuQmCC
   :target: https://docs.pyansys.com/
   :alt: PyAnsys

.. |python| image:: https://img.shields.io/pypi/pyversions/ansys-cfx-core?logo=pypi
   :target: https://pypi.org/project/ansys-cfx-core/
   :alt: Python

.. |pypi| image:: https://img.shields.io/pypi/v/ansys-cfx-core.svg?logo=python&logoColor=white
   :target: https://pypi.org/project/ansys-cfx-core
   :alt: PyPI

.. |GH-CI| image:: https://github.com/ansys/pycfx/actions/workflows/ci_cd.yml/badge.svg
   :target: https://github.com/ansys/pycfx/actions/workflows/ci_cd.yml
   :alt: GH-CI

.. |codecov| image:: https://codecov.io/gh/ansys/pycfx/branch/main/graph/badge.svg
   :target: https://codecov.io/gh/ansys/pycfx
   :alt: Codecov

.. |codecov-internal| image:: https://github.com/ansys/pycfx/blob/main/coverage.svg
   :target: https://github.com/ansys/pycfx
   :alt: Codecov - internal

.. |MIT| image:: https://img.shields.io/badge/License-MIT-yellow.svg
   :target: https://opensource.org/license/MIT
   :alt: MIT

.. |black| image:: https://img.shields.io/badge/code%20style-black-000000.svg?style=flat
   :target: https://github.com/psf/black
   :alt: Black

.. |pre-commit| image:: https://results.pre-commit.ci/badge/github/ansys/pycfx/main.svg
   :target: https://results.pre-commit.ci/latest/github/ansys/pycfx/main
   :alt: pre-commit.ci status

Overview
--------
PyCFX is a Python wrapper for Ansys CFX, the industry-leading CFD software for turbomachinery
applications. You can use it to perform these tasks:

- Launch CFX from a local Ansys installation.
- Create, modify, and run CFX simulations in a Python environment.
- Postprocess simulation results.

Documentation and issues
------------------------
Documentation for the latest stable release of PyCFX is hosted at
`PyCFX documentation`_.

In the upper right corner of the documentation's title bar, there is an option for switching from
viewing the documentation for the latest stable release to viewing the documentation for the
development version or previously released versions.

On the `PyCFX Issues`_ page, you can create issues to report bugs and request new features.

For general PyAnsys support, email `pyansys.core@ansys.com <pyansys.core@ansys.com>`_.

Installation
------------
PyCFX supports Python 3.10 through 3.14 on Windows and Linux.

You can install it from `PyPI`_ with this command:

.. code:: console

   pip install ansys-cfx-core

For developers
^^^^^^^^^^^^^^
If you plan on doing local *development* of PyCFX with Git, install
the latest release with these commands:

.. code:: console

   git clone https://github.com/ansys/pycfx

   python -m pip install -U pip tox

   cd pycfx
   pip install -e .[doc,tests,style]
   python codegen/allapigen.py  # Generates the API files

Dependencies
------------
You must have a licensed copy of Ansys CFX installed locally. PyCFX supports CFX 2025 R2 Service Pack 3 and later.

On Windows, the Ansys CFX installer automatically sets the required environment variables. For example, using CFX 2025 R2 installed in the default directory, the installer sets the ``AWP_ROOT252`` environment variable to ``C:\Program Files\ANSYS Inc\v252``.

On Linux, you must set the required environment variable manually. For example, using CFX 2025 R2 in the default directory, run this command:

.. code:: console

    export AWP_ROOT252=/usr/ansys_inc/v252

To make this setting persistent for the current user, add this same export command to the ``~/.profile`` file or equivalent.

Getting started
---------------

Launch CFX
^^^^^^^^^^
To launch CFX from Python using a local installation, run these commands:

.. code:: python

  import ansys.cfx.core as pycfx
  pypre = pycfx.PreProcessing.from_install()   # Start CFX-Pre
  pysolve = pycfx.Solver.from_install()        # Start a Solver session
  pypost = pycfx.PostProcessing.from_install() # Start CFD-Post

Find examples in the `examples/` folder of the repository.


License and acknowledgments
---------------------------
PyCFX is licensed under the MIT license.

PyCFX makes no commercial claim over Ansys whatsoever. This library
extends the functionality of Ansys CFX by adding a Python interface
to CFX without changing the core behavior or license of the original
software. The use of PyCFX to run the CFX software requires a
legally licensed copy of CFX.

For more information on CFX, see the `Ansys CFX`_ page on the Ansys website.

.. LINKS AND REFERENCES
.. _Ansys CFX: https://www.ansys.com/products/fluids/ansys-cfx
.. _PyCFX documentation: https://glowing-telegram-gqq3j3l.pages.github.io/
.. _PyCFX Issues: https://github.com/ansys/pycfx/issues
.. _PyPI: https://pypi.org/project/ansys-cfx-core/
