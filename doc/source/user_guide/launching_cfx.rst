.. _ref_launch_guide:

Launch CFX
==========

This page explains how to launch Ansys CFX sessions using PyCFX.

The initial release of PyCFX with Ansys CFX 2025 R2 Service Pack 3 supports running CFX sessions
only on the local machine (the same machine where the Python session runs).


Launch from local installation
------------------------------

.. vale Google.Spacing = NO

Use the :meth:`from_install() <ansys.cfx.core.session_utilities.SessionBase.from_install>` method
to launch CFX with a locally installed version of Ansys CFX.

Use this method when CFX is installed on your local machine and you want to run CFX only on the local machine.

**Example calls:**

.. code-block:: python

  import ansys.cfx.core as pycfx

  pypre = pycfx.PreProcessing.from_install()

  pysolve = pycfx.Solver.from_install(solver_input_file_name=solver_input_file_name)

Useful arguments for the :meth:`from_install() <ansys.cfx.core.session_utilities.SessionBase.from_container>`
method follow:

.. vale Google.Spacing = YES

- ``product_version``: CFX version to launch. If not specified, the method launches
  the latest supported version.
- ``case_file_name``: Path to a case file (.cfx) on the local file system to
  initialize a PreProcessing session.
- ``solver_input_file_name``: Path to a CFX-Solver input file (.def or .mdef) on the
  local file system to initialize a Solver session.
- ``run_directory``: Run directory (.dir) for an existing CFX-Solver run to initialize a
  Solver session.
- ``results_file_name``: Path to a results file (.res or .mres) on the local file
  system to initialize a Solver or PostProcessing session.
- ``additional_arguments``:List of additional command-line arguments to pass to the
  ``cfx5pre``, ``cfx5solve``, or ``cfdpost`` commands when launching the session or starting the
  CFX-Solver.

Launch from an existing session
-------------------------------

You can launch Solver and PostProcessing sessions from existing PyCFX sessions.

- Launch a Solver session from an existing PreProcessing session. At the point of launch, the
  Solver session captures and stores the existing model setup in CFX-Pre, ready to start the run.
  You can continue editing the setup in the PreProcessing session without affecting the previously
  launched Solver session.
- Launch a PostProcessing session from an existing Solver session. If the CFX-Solver run is
  complete, the results file opens. If the CFX-Solver run is not complete, the new PostProcessing
  session waits for it to finish before reading the results.

When you start a PyCFX session from another PyCFX session, the new session inherits settings
from the existing session. For example, if you start a PreProcessing session with the
``product_version`` argument, a new Solver session initialized from the PreProcessing session
also uses that argument.

**Example calls:**

.. code-block:: python

  pysolve = pycfx.Solver.from_session(pypre)

  pypost = pycfx.PostProcessing.from_session(pysolve)

Enable logging
--------------

PyCFX supports running with logging enabled. Use this code to enable logging:

.. code-block:: python

  >>> import ansys.cfx.core as pycfx
  >>> pycfx.logging.enable() # doctest: +ELLIPSIS
  PyCFX logging file ...
  Setting PyCFX global logging level to DEBUG.

For more information, see :ref:`ref_logging_guide`.

