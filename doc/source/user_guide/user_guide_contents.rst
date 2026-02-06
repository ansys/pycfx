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


The PyCFX user guide helps you understand how to use PyCFX to
leverage the power of Ansys CFX for your CFD simulations.

Getting started
---------------

The installation of PyCFX is described in :ref:`ref_installation`. Examples of PyCFX usage can be
found in :ref:`ref_example_gallery`.


PyCFX sessions
--------------

PyCFX provides three types of session objects:

- PreProcessing: provides a connection to CFX-Pre for setting up a simulation.
- Solver: allows control of the CFX-Solver.
- PostProcessing: provides a connection to CFD-Post for post-processing the simulation results.

In order to work through setting up, solving, and post-processing a CFD simulation with PyCFX, you
need to create and modify instances of each of these session objects.


Launching PyCFX sessions
------------------------

Session objects can be initialized from scratch (for example, when starting a new case in a
PreProcessing session), initialized from one or more files (for example, when opening a results
file in a PostProcessing session), or initialized from an existing session (for example, when
initializing a Solver session from an existing PreProcessing session). The
:ref:`Static Mixer <ref_static_mixer>` example demonstrates initializing from scratch or from a
file, and the :ref:`Fourier Blade Flutter <ref_fourier_blade_flutter>` example demonstrates
initializing asession from another session.

A detailed description of how to start a PyCFX session can be found in
:ref:`Launching CFX <ref_launch_guide>`.


Working with session objects
----------------------------

Each PyCFX session object exposes a hierarchy of Python objects that provide access to the
underlying CFX setup and tools. For example, both the PreProcessing and PostProcessing session
objects have a child ``setup`` object which contains the CFX setup in a hierarchy of 'settings
objects' that corresponds to the CFX Command Language (CCL) structure of CFX-Pre or CFD-Post,
respectively. They also have a child ``file`` object which provides actions that broadly correspond
to the functions that can be accessed from the CFX-Pre or CFD-Post File menus.

You can see all the available children by executing (for example) ``dir(pypre.setup)`` and
``dir(pypre.file)`` in an interactive Python session, assuming that you have a current
PreProcessing session named ``pypre``. Similarly, you can discover the children of any other
settings object by executing ``dir()`` on that object, for example,
``dir(pypre.setup.flow["Flow Analysis 1"])``.

You can also call the Python ``help()`` function on any settings object to find out more about
it: ``help(pypre.setup.flow["Flow Analysis 1"])``.

Each PyCFX session object corresponds to a single instance of CFX-Pre, the CFX-Solver or CFD-Post.
Multiple sessions of each type can exist within a single Python session. Each one can be exited
separately by calling its ``exit()`` function, for example, ``pypre.exit()``. Ending a
PreProcessing or PostProcessing session closes the associated CFX-Pre or CFD-Post instance, but
ending a Solver session does not stop an associated CFX-Solver run.

Further details of how the session objects can be used can be found in
:ref:`Using PyCFX sessions <ref_session_guide>`.




