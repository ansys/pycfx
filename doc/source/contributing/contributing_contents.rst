.. _ref_contributing:

==========
Contribute
==========

.. toctree::
   :maxdepth: 1
   :hidden:

   environment_variables

General guidance on contributing to a PyAnsys library appears in the
`Contributing <https://dev.docs.pyansys.com/how-to/contributing.html>`_ topic
in the *PyAnsys developer's guide*. Ensure that you are thoroughly familiar with
this guide, paying particular attention to the `Coding style
<https://dev.docs.pyansys.com/coding-style/index.html#coding-style>`_ topic, before
attempting to contribute to PyCFX.

The following contribution information is specific to PyCFX.

Clone the repository
--------------------
Follow the steps in :ref:`dev_installation`.

Run unit tests
--------------

To run the PyCFX unit tests, run the following command in the root
(``pycfx``) directory of the repository:

.. code-block:: bash

    pip install -e .[tests]
    python -m pytest -n 4 --cfx-version=25.2

To run only tests compatible with a given version, use the ``cfx-version`` argument.
This argument does not select which version of CFX to run.

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

After the build completes, the HTML documentation is in the
``_build/html`` directory. Open the ``index.html`` file in this directory in
a web browser.

You can clear all HTML files from the ``_build/html`` directory with this command:

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
install and activate this tool with these commands:

.. code-block:: bash

   python -m pip install pre-commit
   pre-commit install

You can then use the ``style`` rule defined in ``Makefile`` with this command:

.. code-block:: bash

   make style

Alternatively, run ``pre-commit`` directly:

.. code-block:: bash

    pre-commit run --all-files --show-diff-on-failure

To generate a changelog automatically, follow the branch and commit naming conventions described in the *PyAnsys developer's guide*
`branch <https://dev.docs.pyansys.com/how-to/contributing.html#branch-naming-conventions>`_ and
`commit <https://dev.docs.pyansys.com/how-to/contributing.html#commit-naming-conventions>`_ naming sections.
