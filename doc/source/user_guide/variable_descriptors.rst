.. _ref_variable_descriptors:

Use variable descriptors
========================

Settings that take a CFX variable name, such as a contour's colour variable or a monitor
point's output variables, also accept a variable descriptor from the
``ansys-variable-descriptors`` package. PyCFX converts each descriptor to the matching CFX
variable name before sending it to CFX. This lets you use the same variable definitions across
PyAnsys products without remembering product-specific names.

.. code-block:: python

   from ansys.variable_descriptor import VariableCatalog

The following variables are currently supported:

=====================================  =====================
Variable descriptor                    CFX variable name
=====================================  =====================
``VariableCatalog.PRESSURE``           ``Pressure``
``VariableCatalog.STATIC_PRESSURE``    ``Pressure``
``VariableCatalog.TOTAL_PRESSURE``     ``Total Pressure``
``VariableCatalog.VELOCITY``           ``Velocity``
``VariableCatalog.VELOCITY_X``         ``Velocity u``
``VariableCatalog.VELOCITY_Y``         ``Velocity v``
``VariableCatalog.VELOCITY_Z``         ``Velocity w``
``VariableCatalog.TEMPERATURE``        ``Temperature``
``VariableCatalog.TOTAL_TEMPERATURE``  ``Total Temperature``
``VariableCatalog.DENSITY``            ``Density``
=====================================  =====================

Assigning a variable descriptor that isn't in this table raises a ``ValueError``. You can
still use any CFX variable name as a string, and you can mix strings and descriptors in a
list setting. Reading a setting back always returns the CFX variable name as a string.

Color a contour in CFD-Post
---------------------------

.. code-block:: python

   import ansys.cfx.core as pycfx
   from ansys.variable_descriptor import VariableCatalog

   pypost = pycfx.PostProcessing.from_install(results_file_name="StaticMixer_001.res")

   pypost.results.plane.create("Plane 1")
   plane = pypost.results.plane["Plane 1"]
   plane.suspend()
   plane.option = "ZX Plane"
   plane.plane_type = "Slice"
   plane.unsuspend()

   pypost.results.contour["Contour 1"] = {
       "colour_variable": VariableCatalog.PRESSURE,
       "location_list": "/PLANE:Plane 1",
       "number_of_contours": 11,
   }

   contour = pypost.results.contour["Contour 1"]
   contour.colour_variable()  # Returns 'Pressure'.

   contour.colour_variable = VariableCatalog.TEMPERATURE

Monitor variables in CFX-Pre
----------------------------

.. code-block:: python

   import ansys.cfx.core as pycfx
   from ansys.variable_descriptor import VariableCatalog

   pypre = pycfx.PreProcessing.from_install()
   pypre.file.open_case(file_name="StaticMixer.cfx")

   monitors = pypre.setup.flow["Flow Analysis 1"].output_control.monitor_objects
   monitors.enabled = True
   monitors.monitor_point.create("Outlet Monitor")
   monitors.monitor_point["Outlet Monitor"].output_variables_list = [
       VariableCatalog.PRESSURE,
       VariableCatalog.TOTAL_TEMPERATURE,
       "Velocity in Stn Frame",  # A CFX variable name without a descriptor.
   ]
