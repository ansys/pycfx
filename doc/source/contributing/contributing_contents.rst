.. _ref_contributing:

========================
Contributing to PyCFX
========================

.. toctree::
   :maxdepth: 1
   :hidden:

   environment_variables

General guidance on contributing to a PyAnsys library appears in the
`Contributing <https://dev.docs.pyansys.com/how-to/contributing.html>`_ topic
in the *PyAnsys Developer's Guide*. Ensure that you are thoroughly familiar with
this guide, paying particular attention to the `Coding Style
<https://dev.docs.pyansys.com/coding-style/index.html#coding-style>`_ topic, before
attempting to contribute to PyCFX.

The following contribution information is specific to PyCFX.

Clone the repository
--------------------
Follow the steps in the Development Installation section of :ref:`ref_installation`
to set up PyCFX in development mode.

Run unit tests
--------------

To run the PyCFX unit tests, execute the following command in the root
(``pycfx``) directory of the repository:

.. code-block:: bash

    pip install -e .[tests]
    python -m pytest -n 4 --cfx-version=25.2

The 'cfx-version' argument, if specified, selects only tests compatible with this version
to run. (It does not select which version of CFX to run.)

Build documentation
-------------------
To build the PyCFX documentation locally, run the following commands in the root
(``pycfx``) directory of the repository:

.. code-block:: bash

    pip install -e .[doc]
    cd doc
    set BUILD_ALL_DOCS=1
    set CFX_IMAGE_TAG=v25.2.0
    make html

After the build completes, the HTML documentation is located in the
``_build/html`` directory. You can load the ``index.html`` file in
this directory into a web browser.

You can clear all HTML files from the ``_build/html`` directory with:

.. code-block:: bash

    make clean

Post issues
-----------
Use the `PyCFX Issues <https://github.com/ansys/pycfx/issues>`_ page to
submit questions, report bugs, and request new features.


Adhere to code style
--------------------
PyCFX is compliant with the `PyAnsys code style
<https://dev.docs.pyansys.com/coding-style/index.html>`_. It uses the tool
`pre-commit <https://pre-commit.com/>`_ to check the code style. You can
install and activate this tool with:

.. code-block:: bash

   python -m pip install pre-commit
   pre-commit install

You can then use the ``style`` rule defined in ``Makefile`` with:

.. code-block:: bash

   make style

Or, you can directly execute `pre-commit <https://pre-commit.com/>`_ with:

.. code-block:: bash

    pre-commit run --all-files --show-diff-on-failure

In order to generate a changelog automatically it is important to follow
the branch and commit names conventions as described in the *PyAnsys Developer's Guide*
`branch <https://dev.docs.pyansys.com/how-to/contributing.html#branch-naming-conventions>`_ and
`commit <https://dev.docs.pyansys.com/how-to/contributing.html#commit-naming-conventions>`_ naming
sections.
