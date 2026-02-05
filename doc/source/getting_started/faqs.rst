.. _faqs:

Frequently asked questions
==========================

.. vale Google.FirstPerson = NO

What is PyAnsys?
----------------
PyAnsys is a set of open source technologies that allow you to interface with Ansys
CFX, Ansys Fluent, Mechanical APDL, System Coupling, and other Ansys products and
utilities, via Python. You can use PyAnsys libraries within a Python environment of
your choice in conjunction with external Python libraries.

What is PyCFX?
--------------
PyCFX provides Python access to Ansys CFX. Its features enable the seamless use of
CFX within the Python ecosystem and provide broad access to native CFX features for performing
actions such as these:

- Launch CFX using a local Ansys installation.
- Connect to a CFX instance running on a remote machine.

PyCFX has no graphical user interface. You interact with PyCFX through the Python
environment of your choice, interactively or via Python scripts.

Who should use PyCFX?
---------------------
PyCFX users can include engineers, product designers, consultants, and academia.

Which version of Python should I use?
-------------------------------------
PyCFX supports Python 3.10 through Python 3.13 on Windows and Linux.

You can use a suitable Python version from your Ansys installation. Python 3.10 is shipped with
Ansys Release 2023 R2 and later. For example, in a Release 2025 R2 Windows installation, the
executable file for Python 3.10 is typically located at:
``C:\Program Files\ANSYS Inc\v252\commonfiles\CPython\3_10\winx64\Release\python.exe``.
If you are using Python from an Ansys installation, make sure to install PyCFX
within a Python virtual environment to prevent any possible conflicts with
Ansys Python packages.

Alternatively, you can download any compatible version of Python directly from
the `Downloads page <https://www.python.org/downloads/>`_ of the Python web
site. Run the Python executable file as an administrator, selecting
the **Add Python [version] to PATH** checkbox on the first wizard page before
proceeding with the installation. On the last wizard page, which indicates that
Python is installed successfully, follow the instructions for disabling the path
length limit if you have long file paths.

Where do I find source code and documentation?
----------------------------------------------
All PyAnsys public libraries are available from the `PyAnsys GitHub account
<https://github.com/pyansys>`_. The **Repositories** page displays the number of
repositories, which are searchable by name. For example, to find all PyCFX
libraries, type ``pycfx`` in the search field.

The ``README.md`` file for the PyAnsys GitHub account lists the public PyAnsys
libraries. The links in this list are to the documentation for the respective
libraries. In addition to general usage information, the documentation for a
library includes some practical examples.

.. _faqs_cfxloc:

How does PyCFX infer the location to launch CFX?
------------------------------------------------
PyCFX locates installed Ansys versions based on environment variables of the form
``AWP_ROOT<version>``, where ``<version>`` is an Ansys release number such as ``252`` for
Release 2025 R2. The corresponding environment variable is automatically configured on Windows
systems when a new Ansys release is installed. On Linux systems, you must configure
``AWP_ROOT<version>`` to point to the absolute path of any Ansys installation that you want to use
with PyCFX. For example:

.. code-block:: console

    set AWP_ROOT252=/apps/ansys_inc/v252

When PyCFX launches CFX, it determines which versions are available using these environment
variables. The Ansys version selected (if more than one is installed) is based on the following, in
decreasing order of precedence:

.. vale Google.Spacing = NO

#. The value of the ``product_version`` parameter passed to the function that launches a PyCFX
   session, such as
   :func:`from_install() <ansys.cfx.core.session_utilities.SessionBase.from_install>`.

#. The latest supported installed version.

.. vale Google.Spacing = YES

How do I learn how to use PyCFX?
--------------------------------
Depending on how you prefer to learn, you can use any or all of these methods to
learn how to use PyCFX:

- Review the examples provided in the :ref:`ref_example_gallery`.

- Write scripts, using capabilities such as these:

  - IntelliSense to show available options for any given command. For example,
    in `JupyterLab <https://jupyter.org/>`_, press the tab key.
  - Standard Python or PyAnsys tooling to print options related to a specified
    object. For example, use ``dir (<object>)`` or ``help (<object>)``.


How do I set up JupyterLab to get better code completion for the API code in PyCFX?
-----------------------------------------------------------------------------------
By default, JupyterLab ignores the static typing information provided by PyCFX
and relies on dynamic lookup of the API for code completion. Because the dynamic lookup
generally involves gRPC calls to the CFX server, it can be slow and often times out.
To get a faster code completion experience based on the static typing information
provided by PyCFX, you can install the JupyterLab extension
`jupyterlab-lsp <https://jupyterlab-lsp.readthedocs.io/en/latest/>`_
along with a Python language server like
`python-lsp-server <https://github.com/python-lsp/python-lsp-server>`_
within your JupyterLab environment.


How do I get help for PyCFX?
----------------------------
Because PyCFX libraries are open source, support for issues, bugs, and
feature requests are available in their respective GitHub repositories.

- To log an issue for PyCFX, use the
  `PyCFX Issues page <https://github.com/ansys/pycfx/issues>`_.

For discussions about developer tools, engineering simulation, and physics for
Ansys software, visit the `Ansys Developer portal
<https://developer.ansys.com/>`_. The `Ansys Discuss
<https://discuss.ansys.com/>`_ page is where users, partners, students, and
Ansys subject matter experts connect, share ideas, discuss the latest
technologies, and ask questions to quickly obtain help and guidance. On this
page, you can filter discussions by category or apply the **CFX** tag to view
only CFX-related discussions.


.. vale Google.FirstPerson = YES
