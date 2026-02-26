.. _ref_session_guide:

Use PyCFX sessions
==================

PyCFX provides three types of session objects:

- **PreProcessing**: Connects to CFX-Pre to set up simulations.
- **Solver**: Controls the CFX-Solver.
- **PostProcessing**: Connects to CFD-Post to postprocess simulation results.

For an overview of these session objects, see the :ref:`User guide <ref_user_guide>`.

Each PyCFX session object exposes a hierarchy of Python *settings objects* that provide access to the
underlying CFX setup and tools. For example, both the PreProcessing and PostProcessing session
objects have a child ``setup`` object, which contains the CFX setup in a hierarchy that corresponds
to the CFX Command Language (CCL) structure of CFX-Pre or CFD-Post, respectively. They also have a
child ``file`` object, which provides actions that broadly correspond to the functions accessible
from the CFX-Pre or CFD-Post **File** menus.

Each settings object that is a child of the ``setup`` object represents a CCL object or parameter,
or a related function. For example, ``pypre.setup.flow['Flow Analysis 1'].analysis_type.option``
represents the following CCL parameter:

.. code-block::

  FLOW: Flow Analysis 1
    ANALYSIS TYPE:
      Option = Steady State
    END
  END

When Python settings objects are created, their names are derived from the related CCL object
types and parameter names by converting to lowercase and replacing spaces with underscores.
Named object names (such as ``Flow Analysis 1``) and parameter values (such as ``Steady State``)
remain unchanged from CCL.

All settings objects share a uniform interface with methods like ``get_state()``, ``set_state()``,
and ``is_active()``. Additional methods such as ``allowed_values()``, ``min()``, and ``max()``
are available for relevant objects.

All of the following examples assume that you have initialized a PreProcessing session object
named ``pypre`` with a suitable case (for example, the :ref:`Static mixer <ref_static_mixer>` example).

.. code-block:: python

  # Retrieve the parameter value
  >>> pypre.setup.flow['Flow Analysis 1'].analysis_type.option()
  'Steady State'

  # Find out the allowed values
  >>> pypre.setup.flow['Flow Analysis 1'].analysis_type.option.allowed_values()
  ['Steady State', 'Transient', 'Transient Blade Row']

  # Set the Analysis Type option
  >>> pypre.setup.flow['Flow Analysis 1'].analysis_type.option = "Transient"

  # get_state() can also be used to get the parameter value
  >>> pypre.setup.flow['Flow Analysis 1'].analysis_type.option.get_state()
  'Transient'

  # Invalid values cannot be set
  >>> pypre.setup.flow['Flow Analysis 1'].analysis_type.option.set_state("Invalid Value")
  Traceback (most recent call last):
    ...
  RuntimeError: Parameter value 'Option' for object '/FLOW:Flow Analysis 1/ANALYSIS TYPE' is not allowed.

Some items in the settings object hierarchy are methods that you call to request a particular
action in PyCFX:

.. code-block:: python

  >>> pypre.file.save_picture(file_name = "Image.png")

Settings object types
---------------------

.. vale Google.Spacing = NO

A settings object can be one of the primitive types such as:
:obj:`~ansys.cfx.core.solver.flobject.Integer`,
:obj:`~ansys.cfx.core.solver.flobject.Real`,
:obj:`~ansys.cfx.core.solver.flobject.String`, and
:obj:`~ansys.cfx.core.solver.flobject.Boolean`. A settings object can also be one of the two types
of container objects: :obj:`~ansys.cfx.core.solver.flobject.Group` and
:obj:`~ansys.cfx.core.solver.flobject.NamedObject`.

- The :obj:`~ansys.cfx.core.solver.flobject.Group` type is a static container with predefined
  child objects that you can access as attributes, for example,
  ``pypre.setup.flow['Flow Analysis 1'].analysis_type`` or ``pypre.setup.flow['Flow Analysis 1']``.
  The names of the child objects of a group can be accessed via ``<Group>.child_names``. Within
  the PyCFX session ``setup`` object, Group objects correspond directly to CCL objects.

- The :obj:`~ansys.cfx.core.solver.flobject.NamedObject` type is a container holding
  dynamically created named ``Group`` objects. For a given ``NamedObject`` container, each contained
  ``Group`` object is of the same specific CCL type. A given named ``Group`` object can be accessed using
  the index operator. For example, ``pypre.setup.flow['Flow Analysis 1']`` yields a ``flow`` object
  with the name ``Flow Analysis 1``, assuming it exists. The current list of named ``Group`` object
  children can be accessed using the ``<NamedObject>.get_object_names()`` method. Note that these
  ``NamedObject`` containers do not correspond to any CCL object but represent an intermediate layer.
  However, their contained named ``Group`` objects do correspond to CCL objects.

.. vale Google.Spacing = YES

Object state
------------

You can access the state of any object by "calling" it. This returns the state of the children
as a dictionary for ``Group`` and ``NamedObject`` types.

.. code-block:: python

  >>> pypre.setup.flow['Flow Analysis 1'].analysis_type.option()
  'Transient'
  >>> pypre.setup.flow['Flow Analysis 1'].analysis_type.get_state() == {
  ...   'option': 'Transient',
  ...   'external_solver_coupling': {'option': 'None'},
  ...   'time_duration': {'option': 'Total Time', 'total_time': '-- Undefined --'},
  ...   'initial_time': {'option': 'Automatic with Value', 'time': '0 [s]'},
  ...   'time_steps': {'option': 'Timesteps', 'timesteps': '-- Undefined --'}}
  True

To modify the state of any object, you can assign the corresponding attribute
in its parent object. This assignment can be done at any level. For ``Group``
and ``NamedObject`` types, the state value is a dictionary.

.. code-block:: python

  >>> pypre.setup.flow['Flow Analysis 1'].analysis_type.option = "Transient"

You can also access the state of an object with the ``get_state()`` method and
modify it with the ``set_state()`` method.

``Real``, ``RealTriplet``, and ``RealList`` settings objects incorporate units alongside values. If
the object has units (not dimensionless), you must set its value as a string including the
unit. Setting the value as a float is not supported. For example:

.. code-block:: python

  >>> pypre.setup.flow['Flow Analysis 1'].analysis_type.time_duration.total_time = "2.0 [s]"

You can print the current state in a simple text format with the ``print_state()`` method. For
example:

.. code-block:: python

  >>> pypre.setup.flow['Flow Analysis 1'].analysis_type.print_state()
  <BLANKLINE>
  option : Transient
  external_solver_coupling : 
    option : None
  time_duration : 
    option : Total Time
    total_time : 2.0 [s]
  initial_time : 
    option : Automatic with Value
    time : 0 [s]
  time_steps : 
    option : Timesteps
    timesteps : -- Undefined --

Expressions, expert parameters, and user data
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In CFX, expressions are CCL parameters:

.. code-block::

  LIBRARY:
    CEL:
      EXPRESSIONS:
        MyPressure = 2 * OpeningPressure
        OpeningPressure = 101325 [Pa]
      END
    END
  END

However, in PyCFX, each expression is a ``Group`` object within the ``expressions`` container. Expression values must be set with the ``definition`` attribute. Examples of creating and using expressions follow.

.. code-block:: python

  >>> pypre.setup.library.cel.expressions.create("MyPressure") # doctest: +ELLIPSIS
  <ansys.cfx.core... object at 0x...>
  >>> pypre.setup.library.cel.expressions['MyPressure'].definition = "2 * OpeningPressure"
  >>> pypre.setup.library.cel.expressions['OpeningPressure'] = {"definition": "101325 [Pa]"}
  >>> pypre.setup.library.cel.expressions.get_state()
  {'MyPressure': {'definition': '2 * OpeningPressure'}, 'OpeningPressure': {'definition': '101325 [Pa]'}}
  >>> print(pypre.setup.library.cel.expressions.list_properties())
  LIBRARY:
    CEL:
      EXPRESSIONS:
        MyPressure = 2 * OpeningPressure
        OpeningPressure = 101325 [Pa]
      END
    END
  END
  <BLANKLINE>

Other commands relating to expressions can be found by using the ``dir()`` function on the
``expressions`` container.

Similar behavior exists for other objects that have parameters that can be given a user-defined
name, for example, the ``EXPERT PARAMETERS`` and ``USER`` CCL objects in CFX-Pre.

Commands
--------

Commands are methods of settings objects that you use to modify the state of
the session, for example, the ``open_case()`` method of the ``pypre.file`` object.
The ``get_active_command_names()`` method of a settings object
provides the names of the object's currently available commands.

If keyword arguments are needed, you can use commands to pass them. To access a
list of valid arguments, use the ``argument_names`` attribute. If you do not specify
an argument, its default value is used. Arguments are also settings objects
and can be of either the primitive or container type.

Queries
-------

Queries are methods of settings objects that you use to query the state of
the session, for example, the ``get_physics_messages()`` method of many of the
PreProcessing settings objects. The ``query_names`` attribute of a settings object
provides the names of the object's currently available queries.

If keyword arguments are needed, you can use queries to pass them. To access a
list of valid arguments, use the ``argument_names`` attribute. If you do not specify
an argument, its default value is used. Arguments are also settings objects
and can be of either the primitive or container type.

Additional metadata
-------------------

Settings object methods are provided to access some additional attributes (metadata). There are
a number of explicit methods and two generic methods: ``get_attr()`` and ``get_attrs()``.

The following example shows how to use the two generic methods ``get_attr()`` and
``get_attrs()`` to get the list of allowed values for a particular **Option** parameter
in PyCFX. Additionally, the example uses the explicit method for this attribute: ``allowed_values()``.
All string and string list objects have an ``allowed_values()`` method, which returns a list of
allowed string values if such a constraint currently applies for that object. Otherwise, it
returns ``None``.

.. code-block:: python

  >>> pypre.setup.flow['Flow Analysis 1'].analysis_type.option.get_attr('allowed-values')
  ['Steady State', 'Transient', 'Transient Blade Row']
  >>>
  >>> pypre.setup.flow['Flow Analysis 1'].analysis_type.option.get_attrs(['allowed-values'])
  {'allowed-values': ['Steady State', 'Transient', 'Transient Blade Row']}
  >>>
  >>> pypre.setup.flow['Flow Analysis 1'].analysis_type.option.allowed_values()
  ['Steady State', 'Transient', 'Transient Blade Row']

The following table contains attribute names, corresponding methods to access the attribute, whether
the method can return ``None``, applicable object types, and returned data types:

==================  ==================  =================  =====================  ====================
Attribute name      Method              Can return None    Type applicability     Metadata type
==================  ==================  =================  =====================  ====================
``is-active?``      ``is_active``       No                 All                    ``bool``
``is-read-only?``   ``is_read_only``    No                 All                    ``bool``
``default-value``   ``default``         Yes                All primitives         Type of primitive
``allowed-values``  ``allowed_values``  Yes                ``str``, ``str list``  ``str list``
``min``             ``min``             Yes                ``int``, ``float``     ``int`` or ``float``
``max``             ``max``             Yes                ``int``, ``float``     ``int`` or ``float``
==================  ==================  =================  =====================  ====================

Using the ``get_attr()`` method requires knowledge of attribute names, their applicability, and
the ability to interpret the raw values of the attribute. You can avoid all these requirements by
using the explicitly named methods. Note that the attribute values are dynamic, which means
values can change based on the session state. A ``None`` value signifies that no value
is currently designated for this attribute.

Active objects, commands, and queries
-------------------------------------

Objects, commands, and queries can be active or inactive based on the session state.
The ``is_active()`` method returns ``True`` if an object, command, or query is currently active.

For the PreProcessing session, objects become active or inactive depending on their physical
availability. So, a turbulence model setting on a boundary is inactive if the domain does not
include a turbulence model.

The ``get_active_child_names()`` method returns a list of active children, including both CCL
objects and parameters:

.. code-block:: python

  >>> pypre.setup.flow['Flow Analysis 1'].domain['Default Domain'].get_active_child_names()
  ['location', 'domain_type', 'coord_frame', 'number_of_passages_in_360', 'number_of_passages_in_component', 'fluid_definition', 'domain_models', 'fluid_models', 'boundary', 'initialisation', 'solver_control']

The ``get_active_command_names()`` or ``get_active_query_names`` method returns the list of active
commands or queries:

>>> pypre.file.get_active_command_names()
['close_case', 'export_ccl', 'import_mesh', 'new_case', 'open_case', 'save_case', 'save_picture', 'write_solver_input_file']
>>>
>>> pypre.setup.get_active_query_names()
['get_physics_messages']

.. vale Google.Headings = NO

PreProcessing session details
-----------------------------

.. vale Google.Headings = YES

The PreProcessing session object has some unique behaviors that are designed to make it easy
to set up complex CFD simulations.

Physics messages
~~~~~~~~~~~~~~~~

A complex simulation setup can be difficult to set up correctly because many parameters and 
objects are interdependent and any change could require other updates. At any time, you can check
whether your setup is physically valid by calling the ``get_physics_messages()`` method of any
PreProcessing settings object that is a child of the ``setup`` object. For example, to check the
entire setup: ``pypre.setup.get_physics_messages()``. Or, to check a specific domain:
``pypre.setup.flow['Flow Analysis 1'].domain['Default Domain'].get_physics_messages()``.
The messages returned can be filtered by severity level (All, Beta, Information, Warning,
and Error).

Physics updates
~~~~~~~~~~~~~~~

In a PreProcessing session, changing one value (for example, ``Boundary Type``) can require large
numbers of dependent objects and parameters to be updated. For the PreProcessing session
to be usable, the session incorporates *physics updates*, which update the necessary dependent
objects when any parameter value or other change is made.

.. vale Google.Quotes = NO

For example, a case with ``Turbulence Model`` set to ``k-Epsilon`` must have a
``Wall Function`` set to ``Scalable`` as this is the only valid ``Wall Function``
for the ``k-Epsilon`` model. If you later set ``Turbulence Model`` to ``Shear Stress
Transport``, the ``Wall Function`` must be updated to ``Automatic`` as this is
the only allowed ``Wall Function`` option for the ``Shear Stress Transport`` model.
The physics updates in the PreProcessing session automatically makes this
change.

If you are familiar with the CFX-Pre user interface, then the easiest way to understand the
physics updates is to imagine opening the editor for the object that you want to change and
making the same parameter or object change. For example, if you open the Domain editor
for a case with ``Turbulence Model`` set to ``k-Epsilon``, then the ``Wall Function`` must
be set to ``Scalable``. If you then change ``Turbulence Model`` to ``Shear Stress Transport``,
you can see that the ``Wall Function`` option, further down the panel, automatically updates
to ``Automatic``.

.. vale Google.Quotes = YES

Physics updates are limited to the *top-level* objects. For example, changing a parameter in a
domain does not update a boundary condition object, only other dependent objects within the domain.
Top-level objects are those that have their own editors in CFX-Pre, such as for the domain,
boundary, initial conditions, and execution control.

.. code-block:: python

  >>> pypre.setup.flow['Flow Analysis 1'].domain['Default Domain'].fluid_models.print_state()
  <BLANKLINE>
  heat_transfer_model : 
    option : Thermal Energy
  turbulence_model : 
    option : k epsilon
  turbulent_wall_functions : 
    option : Scalable
  thermal_radiation_model : 
    option : None
  combustion_model : 
    option : None

  >>> pypre.setup.flow['Flow Analysis 1'].domain['Default Domain'].fluid_models.turbulence_model.option = "SST"
  >>> pypre.setup.flow['Flow Analysis 1'].domain['Default Domain'].fluid_models.print_state()
  <BLANKLINE>
  heat_transfer_model : 
    option : Thermal Energy
  turbulence_model : 
    option : SST
  turbulent_wall_functions : 
    option : Automatic
  thermal_radiation_model : 
    option : None
  combustion_model : 
    option : None

The ``turbulent_wall_functions`` option was automatically updated from ``Scalable`` to ``Automatic``
by the physics update.

.. note::
  For CFX versions up to and including 2026 R1, if a state is supplied as a dictionary, 
  the physics updates are not applied and the state is applied as-is. The PreProcessing session 
  may be left in an invalid physical state following such an update. You should check for any 
  physics warnings or errors.

Optional objects and parameters
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The CCL structure in the PreProcessing session is more complex than those of the other session
types. Some parameters and objects are optional, and their existence (or lack thereof) affects
the setup.

To add an optional parameter, simply set its value to the desired value. To remove an optional
parameter, set the value to ``None``. For example, this code adds and then removes the ``Coord Frame``
parameter in a boundary object:

.. code-block:: python

  >>> in1 = pypre.setup.flow["Flow Analysis 1"].domain["Default Domain"].boundary["in1"]
  >>> in1.print_state() # doctest: +ELLIPSIS
  <BLANKLINE>
  boundary_type : INLET
  location : in1
  boundary_conditions : 
    ...
  >>> in1.coord_frame = "Coord 0"  # Add the optional Coord Frame parameter
  >>> in1.print_state() # doctest: +ELLIPSIS
  <BLANKLINE>
  interface_boundary : False
  boundary_type : INLET
  location : in1
  coord_frame : Coord 0
  boundary_conditions : 
    ...
  >>> in1.coord_frame = None  # Remove the optional Coord Frame parameter
  >>> in1.print_state() # doctest: +ELLIPSIS
  <BLANKLINE>
  interface_boundary : False
  boundary_type : INLET
  location : in1
  boundary_conditions : 
    ...

.. vale Google.WordList = NO

To add or remove an optional object, it must be explicitly enabled or disabled. For example,
this code enables and then disables the ``Boundary Contour`` object for a boundary:

.. vale Google.WordList = YES

.. code-block:: python

  >>> in1 = pypre.setup.flow["Flow Analysis 1"].domain["Default Domain"].boundary["in1"]
  >>> in1.print_state() # doctest: +ELLIPSIS
  <BLANKLINE>
  interface_boundary : False
  boundary_type : INLET
  location : in1
  boundary_conditions : 
    ...
  >>> in1.boundary_contour.enabled = True # Enable the optional Boundary Contour object
  >>> in1.print_state() # doctest: +ELLIPSIS
  <BLANKLINE>
  interface_boundary : False
  boundary_type : INLET
  location : in1
  boundary_conditions : 
    ...
  boundary_contour : 
    profile_variable : Normal Speed
  >>> in1.boundary_contour.enabled = False # Disables the optional Boundary Contour object
  >>> in1.print_state() # doctest: +ELLIPSIS
  <BLANKLINE>
  interface_boundary : False
  boundary_type : INLET
  location : in1
  boundary_conditions : 
    ...

Optional named objects are named objects that you can explicitly create but only with specific
names. They are uncommon in the PreProcessing session. You can create these named objects
in the same way as other named objects, for example, by using the ``create()`` method of the parent
``NamedObject`` container. To remove an optional named object, use the Python ``del`` keyword.

.. code-block:: python

  >>> pypre.setup.library.additional_variable.create('Additional Variable 1') # doctest: +ELLIPSIS
  <ansys.cfx.core... object at 0x...>
  >>> fluid_models_obj = pypre.setup.flow["Flow Analysis 1"].domain["Default Domain"].fluid_models
  >>> fluid_models_obj.additional_variable["Additional Variable 1"] = {}
  >>> del fluid_models_obj.additional_variable["Additional Variable 1"]

Note that if you use the ``set_state()`` method to apply the state as a dictionary, 
optional objects or parameters omitted from the dictionary are not removed from the PreProcessing
state. You must explicitly remove them.

Solver session details
----------------------

For the initial release of PyCFX with Ansys CFX 2025 R2, the Solver object is very
limited and does not implement a hierarchy of settings objects.

Solver-specific settings, such as parallel settings, precision settings, and initial conditions,
must be set up as **Execution Control** in the PreProcessing session.

The only available settings object is ``solution``, which provides access to a minimal set of
solver controls.

.. code-block:: python

  >>> pysolve = pycfx.Solver.from_install(solver_input_file_name=solver_input_file_name)
  >>> pysolve.solution.start_run()
  ...
  >>> pysolve.solution.is_running()
  True
  >>> pysolve.solution.wait_for_run() # To wait for the solver run to complete.

Other available methods can be found in the :ref:`Solver Controller <ref_solver_controller>`
module.

.. vale Google.Headings = NO

PostProcessing session details
------------------------------

.. vale Google.Headings = YES

Long calculations
~~~~~~~~~~~~~~~~~

Some operations in a PostProcessing session can take a significant amount of time to complete if a
large or complex case is loaded. A example is the generation (calculation) of a plane or contour.
For maximum efficiency, you need to avoid unnecessary recalculations such as calculating updates to
an object before you have finished setting it up.

Suppose you create a plane with this code:

.. code-block:: python

  >>> pypost.setup.plane["Plane 1"] = {}
  >>> plane1 = pypost.setup.plane["Plane 1"]
  >>> plane1.option = "ZX Plane"
  >>> plane1.plane_type = "Slice"

The plane update calculation is performed three times: once when the plane is created,
again with the default settings, and then finally when the ``option`` and ``plane_type``
are modified.

These unnecessary calculations can be reduced or avoided in two ways. One way is to *suspend*
the plane object until it is complete:

.. code-block:: python

  >>> pypost.setup.plane["Plane 1"] = {}
  >>> plane1 = pypost.setup.plane["Plane 1"]
  >>> plane1.suspend()  # Suspend update calculations for the plane
  >>> plane1.option = "ZX Plane"
  >>> plane1.plane_type = "Slice"
  >>> plane1.unsuspend()  # The plane is recalculated when it is unsuspended

The other way to avoid unneeded calculations is to set up the plane with all the desired
parameters in a single dictionary when it is created:

.. code-block:: python

  >>> pypost.setup.plane["Plane 1"] = {
  ...   "option": "ZX Plane",
  ...   "plane_type": "Slice"
  ... }


Active objects, commands, and queries
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For the initial release of PyCFX with Ansys CFX 2025 R2, all objects and parameters of the
PostProcessing session are always active. For example, you can set the ``X`` parameter for a plane
with the option set to ``XY``, even though the ``Z`` parameter is the only relevant parameter for this option. Parameters and objects that are not relevant are ignored by CFD-Post.

