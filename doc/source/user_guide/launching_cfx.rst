.. _ref_launch_guide:

Launching CFX
=============

This document provides a comprehensive guide for launching Ansys CFX sessions using PyCFX, the
Python interface for CFX.

The initial release of PyCFX with Ansys CFX 2025 R2 Service Pack 3 supports running CFX sessions
only on the local machine (the same machine on which the Python session is executing).


Launch from local installation
------------------------------

.. vale Google.Spacing = NO

The :meth:`from_install() <ansys.cfx.core.session_utilities.SessionBase.from_install>` method
launches CFX using a locally installed version of Ansys CFX.

Use this method when:

- You have CFX installed on your local machine and want to run CFX only on the local machine.

**Example function calls:**

.. code-block:: python

  import ansys.cfx.core as pycfx

  pypre = pycfx.PreProcessing.from_install()

  pysolve = pycfx.Solver.from_install(solver_input_file_name=solver_input_file_name)

Useful arguments to the :meth:`from_install() <ansys.cfx.core.session_utilities.SessionBase.from_container>`
method include:

.. vale Google.Spacing = YES

- ``product_version``: Specifies the CFX version to launch. If not specified, the latest
  supported version is launched.
- ``case_file_name``: Specifies the path to a case file (.cfx) on the local file system to
  initialize a PreProcessing session.
- ``solver_input_file_name``: Specifies the path to a CFX-Solver Input File (.def or .mdef) on the
  local file system to initialize a Solver session.
- ``run_directory``: Specifies the run directory (.dir) for an existing CFX-Solver run to initialize a
  Solver session.
- ``results_file_name``: Specifies the path to a results file (.res or .mres) on the local file
  system to initialize a Solver or PostProcessing session.
- ``additional_arguments``: Specifies a list of additional command-line arguments to pass to the
  ``cfx5pre``/``cfx5solve``/``cfdpost`` commands when launching the session or starting the
  CFX-Solver.


Launch from existing session
----------------------------

The Solver and PostProcessing sessions can be launched from existing PyCFX sessions.

- The Solver session can be launched from an existing PreProcessing session. At the point where
  the Solver session is launched, the existing model setup in CFX-Pre is captured and stored in the
  Solver session, ready for starting the run. You can continue to edit the setup in the
  PreProcessing session without affecting the Solver session previously launched.
- The PostProcessing session can be launched from an existing Solver session. If the CFX-Solver run
  is complete, the results file is opened. If the CFX-Solver run is not complete, the new
  PostProcessing session waits for it to complete before reading the results.

When starting a PyCFX session from another PyCFX session, the new session inherits settings
from the existing session. For example, if a PreProcessing session is started with the
``product_version`` argument, a new Solver session initialized from the PreProcessing session
also uses that argument.

**Example function calls:**

.. code-block:: python

  pysolve = pycfx.Solver.from_session(pypre)

  pypost = pycfx.PostProcessing.from_session(pysolve)


Logging support
---------------
PyCFX has an option to run with logging enabled.
This command enables logging:

.. code-block:: python

  >>> import ansys.cfx.core as pycfx
  >>> pycfx.logging.enable() # doctest: +ELLIPSIS
  PyCFX logging file ...
  Setting PyCFX global logging level to DEBUG.

For more details, see :ref:`ref_logging_guide`.

