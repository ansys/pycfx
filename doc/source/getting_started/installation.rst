.. _ref_installation:

============
Installation
============

Install PyCFX in user mode
--------------------------

PyCFX supports Python 3.10 through Python 3.13 on Windows and Linux.

Install PyCFX with all optional dependencies in user mode using this command:

.. code-block:: console

   pip install ansys-cfx-core

.. _dev_installation:

Install PyCFX in developer mode
-------------------------------

The PyCFX source repository is available on GitHub. Clone the repository and set it up for local development with these commands:

.. code-block:: console

   git clone https://github.com/ansys/pycfx
   cd pycfx
   pip install -e .[doc,tests,style]
   python codegen/allapigen.py  # Generate API files

Step-by-step instructions
~~~~~~~~~~~~~~~~~~~~~~~~~

Clone the repository
++++++++++++++++++++

These commands clone the PyCFX repository from GitHub to your local machine and navigate to the repository directory:

.. code-block:: console

   git clone https://github.com/ansys/pycfx
   cd pycfx


Install PyCFX and dependencies
++++++++++++++++++++++++++++++

This command installs PyCFX and all its dependencies:

.. code-block:: console

   pip install -e .[doc,tests,style]

The ``doc``, ``tests``, and ``style`` extras are necessary for building documentation, running unit tests, and checking code style before contributing.

Set up a virtual environment
++++++++++++++++++++++++++++

Activate a virtual environment for PyCFX development:

.. code-block:: console

   python -m venv .venv
   # On Windows
   .\.venv\Scripts\activate
   # On Linux
   source .venv/bin/activate



Generate API classes
++++++++++++++++++++

The full PyCFX package includes required API classes that are auto-generated instead of maintained under version control. This step requires an Ansys CFX installation.

Run this command to generate these files:

.. code-block:: console

   python codegen/allapigen.py     # Generate the API files silently

Use the ``-v`` or ``--verbose`` flag to display the paths of the generated API files:

.. code-block:: console

   python codegen/allapigen.py --verbose

Install pre-commit
^^^^^^^^^^^^^^^^^^

The style checks use the `pre-commit`_ tool. To contribute changes to the PyCFX project, install ``pre-commit`` with this command:

.. code-block:: console

    python -m pip install pre-commit && pre-commit install

Run ``pre-commit`` on all modified files to ensure your changes conform to repository requirements:

.. code-block:: console

    pre-commit run

Build documentation
-------------------

Build documentation using the rules provided in the `Sphinx`_ Makefile:

.. code:: bash

    make -C doc/ html && your_browser_name doc/html/index.html

The recommended way to check documentation integrity is with this command:

.. code:: bash

    tox -e doc && your_browser_name .tox/doc_out/index.html

Install Ansys CFX
-----------------

To use PyCFX, you must have a licensed copy of Ansys CFX installed. PyCFX supports CFX 2025 R2 Service Pack 3 and later.

PyCFX uses an environment variable to locate your Ansys installation.

On Windows, the Ansys installer sets the environment variable. For example, the Ansys 2025 R2 installer sets the ``AWP_ROOT252`` environment variable to point to ``C:\Program Files\ANSYS Inc\v252`` if you accept the default installation location.

On Linux, the environment variable is not set automatically. Set it for the current user in the current shell session as follows:

.. code-block:: console

    export AWP_ROOT252=/usr/ansys_inc/v252

To make this variable persist between shell sessions, add this same export command to the user's ``~/.profile`` file.

For other ways to specify the CFX location for PyCFX, see :ref:`faqs_cfxloc` in :ref:`faqs`.

.. LINKS AND REFERENCES
.. _pre-commit: https://pre-commit.com/
.. _Sphinx: https://www.sphinx-doc.org/en/master/