.. _ref_user_guide:

==========
User guide
==========

.. toctree::
   :maxdepth: 1
   :hidden:

   launching_cfx
   session
   log
   usability

This section explains how to use PyCFX to leverage Ansys CFX for CFD simulations.

- For installation instructions, see :ref:`ref_installation`.
- For usage examples, see :ref:`ref_example_gallery`.

PyCFX sessions
--------------

PyCFX provides three types of session objects:

- **PreProcessing**: Connects to CFX-Pre to set up simulations.
- **Solver**: Controls the CFX-Solver.
- **PostProcessing**: Connects to CFD-Post to postprocess simulation results.

To set up, solve, and postprocess a CFD simulation with PyCFX, you create and modify instances of these session objects.

Launch PyCFX sessions
---------------------

You can initialize session objects in three ways:

- From scratch, such as starting a new case in a PreProcessing session.
- From files, such as opening a results file in a PostProcessing session.
- From an existing session, such as starting a Solver session from a PreProcessing session.

The :ref:`Static mixer <ref_static_mixer>` example shows initialization from scratch or files. The :ref:`Fourier Blade Flutter <ref_fourier_blade_flutter>` example shows initialization from another session.

For more information on starting a PyCFX session, see :ref:`Launch CFX <ref_launch_guide>`.

Work with session objects
-------------------------

PyCFX session objects expose a hierarchy of Python objects for accessing the CFX setup and tools. For example:

- The ``setup`` object contains the CFX setup as *settings objects* that mirror the CFX Command Language (CCL) structure.
- The ``file`` object provides actions similar to the CFX-Pre or CFD-Post **File** menus.

To explore available children, run the ``dir()`` function on objects, such as ``dir(pypre.setup)`` or ``dir(pypre.file)``, assuming ``pypre`` is a PreProcessing session. For deeper exploration, run the ``dir()`` function on child objects, such as ``dir(pypre.setup.flow["Flow Analysis 1"])``.

Use the Python ``help()`` function to learn more about objects, for example, ``help(pypre.setup.flow["Flow Analysis 1"])``.

Each session object corresponds to one instance of CFX-Pre, the CFX-Solver, or CFD-Post. Multiple sessions can exist in a Python session. Exit sessions individually using the ``exit()`` function, for example, ``pypre.exit()``. Exiting a PreProcessing or PostProcessing session closes the associated instance, but exiting a Solver session does not stop the solver run.

For more information on using session objects, see :ref:`Use PyCFX sessions <ref_session_guide>`.




