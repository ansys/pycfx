.. _ref_release_notes:

Release notes
#############

This document contains the release notes for the project.

.. vale off

.. towncrier release notes start

`0.1.0 <https://github.com/ansys/pycfx/releases/tag/v0.1.0>`_ - April 09, 2026
==============================================================================

.. tab-set::


  .. tab-item:: Added

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Initial pycfx merge
          - `#1 <https://github.com/ansys/pycfx/pull/1>`_

        * - Test updates for improved error messages from engine
          - `#7 <https://github.com/ansys/pycfx/pull/7>`_

        * - Update tests and doc for physics validation updates in engine
          - `#12 <https://github.com/ansys/pycfx/pull/12>`_


  .. tab-item:: Fixed

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Minor fixes following review
          - `#6 <https://github.com/ansys/pycfx/pull/6>`_

        * - Move from using argparse to click instead (#2).
          - `#11 <https://github.com/ansys/pycfx/pull/11>`_

        * - Replace os path operations with pathlib (#3)
          - `#13 <https://github.com/ansys/pycfx/pull/13>`_

        * - Corrections to doc and type hints
          - `#25 <https://github.com/ansys/pycfx/pull/25>`_, `#29 <https://github.com/ansys/pycfx/pull/29>`_

        * - Make ansys.units required
          - `#26 <https://github.com/ansys/pycfx/pull/26>`_

        * - Update ansys-actions version
          - `#31 <https://github.com/ansys/pycfx/pull/31>`_


  .. tab-item:: Dependencies

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Actions: Bump ansys/actions from 10.2.4 to 10.2.5
          - `#9 <https://github.com/ansys/pycfx/pull/9>`_

        * - Pip: Bump sphinxcontrib-openapi from 0.8.4 to 0.9.0
          - `#10 <https://github.com/ansys/pycfx/pull/10>`_

        * - Actions: Bump actions/download-artifact from 7.0.0 to 8.0.0
          - `#19 <https://github.com/ansys/pycfx/pull/19>`_

        * - Actions: Bump actions/upload-artifact from 6.0.0 to 7.0.0
          - `#21 <https://github.com/ansys/pycfx/pull/21>`_

        * - Actions: Bump ansys/actions from 10.2.5 to 10.2.7
          - `#22 <https://github.com/ansys/pycfx/pull/22>`_

        * - Actions: Bump docker/login-action from 3.7.0 to 4.0.0
          - `#27 <https://github.com/ansys/pycfx/pull/27>`_

        * - Pip: Bump h5py from 3.15.1 to 3.16.0
          - `#30 <https://github.com/ansys/pycfx/pull/30>`_

        * - Actions: Bump actions/download-artifact from 8.0.0 to 8.0.1
          - `#32 <https://github.com/ansys/pycfx/pull/32>`_

        * - Actions: Bump softprops/action-gh-release from 2.5.0 to 2.6.1
          - `#33 <https://github.com/ansys/pycfx/pull/33>`_

        * - Actions: Bump actions/cache from 5.0.3 to 5.0.4
          - `#34 <https://github.com/ansys/pycfx/pull/34>`_

        * - Pip: Bump pytest-cov from 7.0.0 to 7.1.0
          - `#35 <https://github.com/ansys/pycfx/pull/35>`_

        * - Pip: Bump requests from 2.32.5 to 2.33.0
          - `#37 <https://github.com/ansys/pycfx/pull/37>`_

        * - Pip: Bump requests from 2.33.0 to 2.33.1
          - `#38 <https://github.com/ansys/pycfx/pull/38>`_

        * - Actions: Bump ansys/actions from 10.2.7 to 10.2.12
          - `#39 <https://github.com/ansys/pycfx/pull/39>`_

        * - Actions: Bump pypa/gh-action-pypi-publish from 1.13.0 to 1.14.0
          - `#40 <https://github.com/ansys/pycfx/pull/40>`_


  .. tab-item:: Documentation

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Overall documentation review
          - `#14 <https://github.com/ansys/pycfx/pull/14>`_

        * - Fixing grid issues when rendering docs
          - `#15 <https://github.com/ansys/pycfx/pull/15>`_

        * - Move environment variables section
          - `#16 <https://github.com/ansys/pycfx/pull/16>`_

        * - Improve examples headings
          - `#17 <https://github.com/ansys/pycfx/pull/17>`_

        * - Formatting changes and other minor corrections
          - `#18 <https://github.com/ansys/pycfx/pull/18>`_

        * - Fix docstring examples
          - `#20 <https://github.com/ansys/pycfx/pull/20>`_


  .. tab-item:: Maintenance

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Enable doc workflows
          - `#4 <https://github.com/ansys/pycfx/pull/4>`_

        * - Deploy dev doc on every commit to main
          - `#5 <https://github.com/ansys/pycfx/pull/5>`_

        * - Add CODEOWNERS file
          - `#8 <https://github.com/ansys/pycfx/pull/8>`_

        * - Fix long lines and re-enable long line check in pre-commit
          - `#23 <https://github.com/ansys/pycfx/pull/23>`_

        * - Add support for python314
          - `#24 <https://github.com/ansys/pycfx/pull/24>`_

        * - Update for the release of v261
          - `#28 <https://github.com/ansys/pycfx/pull/28>`_

        * - Add release environment to ci_cd.yml file
          - `#42 <https://github.com/ansys/pycfx/pull/42>`_


  .. tab-item:: Test

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Add tests for mesh object
          - `#36 <https://github.com/ansys/pycfx/pull/36>`_
