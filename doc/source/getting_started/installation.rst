.. _ref_installation:

============
Installation
============


PyCFX Installation
---------------------

PyCFX supports Python 3.10 through Python 3.13 on Windows and Linux.

You can install PyCFX, along with all its optional dependencies, using:

.. code-block:: console

   pip install ansys-cfx-core


Development Installation
------------------------
The PyCFX source repository is available on GitHub. You can clone the repository and set up for local
development with the following commands:

.. code-block:: console

   git clone https://github.com/ansys/pycfx
   cd pycfx
   pip install -e .[doc,tests,style]
   python codegen/allapigen.py  # Generates the API files

Step-by-step explanation
~~~~~~~~~~~~~~~~~~~~~~~~

Clone the repository
++++++++++++++++++++

.. code-block:: console

   git clone https://github.com/ansys/pycfx
   cd pycfx

These commands clone the PyCFX repository from GitHub to your local machine and navigate into
the repository directory.

Install PyCFX and dependencies
++++++++++++++++++++++++++++++

.. code-block:: console

   pip install -e .[doc,tests,style]

These commands install pycfx and all of its dependencies. The 'doc', 'tests' and 'style' extras
are necessary if you plan to build the documentation, run the unit tests, or check that the code
style conforms to the style guide prior to contributing to the repository.

Set up a virtual environment
++++++++++++++++++++++++++++

.. code-block:: console

   python -m venv .venv
   # On Windows
   .\.venv\Scripts\activate
   # On Linux
   source .venv/bin/activate

This command activates a virtual environment for PyCFX development.

Generate required API classes
+++++++++++++++++++++++++++++

.. code-block:: console

   python codegen/allapigen.py     # Generate the API files silently

The full PyCFX package includes some required API classes that are auto-generated rather
than maintained under version control. The ``python codegen/allapigen.py`` command runs the
auto-generation script included in the repository. Note that this step requires an Ansys CFX
installation.

Pass ``-v`` or ``--verbose`` to display the paths of the generated API files:

.. code-block:: console

   python codegen/allapigen.py --verbose

A note on pre-commit
^^^^^^^^^^^^^^^^^^^^

The style checks take advantage of the `pre-commit`_ tool. If you want to contribute changes to the
PyCFX project, you should install this tool using:

.. code-block:: console

    python -m pip install pre-commit && pre-commit install

Run the tool on all modified files to check that your changes conform to the repository requirements:

.. code-block:: console

    pre-commit run


Documentation
-------------

For building documentation, you can run the usual rules provided in the
`Sphinx`_ Makefile, such as:

.. code:: bash

    make -C doc/ html && your_browser_name doc/html/index.html

However, the recommended way of checking documentation integrity is using:

.. code:: bash

    tox -e doc && your_browser_name .tox/doc_out/index.html


CFX Installation
----------------

To benefit from using PyCFX, you must have a licensed copy of Ansys CFX installed.
All versions of PyCFX support CFX 2025 R2 Service Pack 3 and later.

PyCFX uses an environment variable to locate your Ansys installation.

On Windows, the Ansys installer sets the environment variable. For instance, the Ansys 2025 R2
installer sets the ``AWP_ROOT252`` environment variable to point to
``C:\Program Files\ANSYS Inc\v252`` if you accept the default installation location.

**On Linux, the environment variable is not set automatically.** It can be set for the
current user in the current shell session as follows:

.. code-block:: console

    export AWP_ROOT252=/usr/ansys_inc/v252

For this variable to persist between different shell sessions for the current user, the same
export command can instead be added to the user's ``~/.profile`` file.

For information on other ways of specifying the CFX location for PyCFX, see :ref:`faqs_cfxloc`
in :ref:`faqs`.


.. LINKS AND REFERENCES
.. _pre-commit: https://pre-commit.com/
.. _Sphinx: https://www.sphinx-doc.org/en/master/