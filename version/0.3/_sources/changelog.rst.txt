.. _ref_release_notes:

Release notes
#############

This document contains the release notes for the project.

.. vale off

.. towncrier release notes start

`0.3.0 <https://github.com/ansys/pycfx/releases/tag/v0.3.0>`_ - July 21, 2026
=============================================================================

.. tab-set::


  .. tab-item:: Added

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Use create() method in examples instead of {}
          - `#70 <https://github.com/ansys/pycfx/pull/70>`_

        * - Add object-names and display-text attributes for Simba
          - `#121 <https://github.com/ansys/pycfx/pull/121>`_

        * - Auto detect engine ansys-api-cfx version.
          - `#136 <https://github.com/ansys/pycfx/pull/136>`_


  .. tab-item:: Fixed

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Fix broken link to documentation
          - `#59 <https://github.com/ansys/pycfx/pull/59>`_

        * - Decompress docs artifact on stable doc deployment
          - `#62 <https://github.com/ansys/pycfx/pull/62>`_

        * - Pinned requirements incompatible with the rest of the ecosystem
          - `#69 <https://github.com/ansys/pycfx/pull/69>`_

        * - Requirements for ansys-tools-filetransfer
          - `#72 <https://github.com/ansys/pycfx/pull/72>`_

        * - Remove some bandit skipped checks and add to pre-commit
          - `#97 <https://github.com/ansys/pycfx/pull/97>`_

        * - Update dependabot configuration
          - `#99 <https://github.com/ansys/pycfx/pull/99>`_

        * - Use ansys-tools for example file download
          - `#106 <https://github.com/ansys/pycfx/pull/106>`_

        * - Fix up various bandit security issues
          - `#119 <https://github.com/ansys/pycfx/pull/119>`_

        * - Minor test and doc fixes
          - `#131 <https://github.com/ansys/pycfx/pull/131>`_


  .. tab-item:: Documentation

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Update \`\`CONTRIBUTORS.md\`\` with the latest contributors
          - `#73 <https://github.com/ansys/pycfx/pull/73>`_, `#102 <https://github.com/ansys/pycfx/pull/102>`_


  .. tab-item:: Dependencies

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Actions: Bump docker/login-action from 4.0.0 to 4.1.0
          - `#51 <https://github.com/ansys/pycfx/pull/51>`_

        * - Pip: Bump pytest from 9.0.2 to 9.0.3
          - `#55 <https://github.com/ansys/pycfx/pull/55>`_

        * - Actions: Bump actions/upload-artifact from 7.0.0 to 7.0.1
          - `#56 <https://github.com/ansys/pycfx/pull/56>`_

        * - Actions: Bump softprops/action-gh-release from 2.6.1 to 3.0.0
          - `#57 <https://github.com/ansys/pycfx/pull/57>`_

        * - Actions: Bump actions/cache from 5.0.4 to 5.0.5
          - `#58 <https://github.com/ansys/pycfx/pull/58>`_

        * - Bump ansys/actions from 10.3.0 to 10.3.1
          - `#98 <https://github.com/ansys/pycfx/pull/98>`_

        * - Bump the pre-commit group with 4 updates
          - `#116 <https://github.com/ansys/pycfx/pull/116>`_

        * - Bump the actions group with 3 updates
          - `#117 <https://github.com/ansys/pycfx/pull/117>`_

        * - Bump the pre-commit group with 3 updates
          - `#122 <https://github.com/ansys/pycfx/pull/122>`_

        * - Bump the actions group with 2 updates
          - `#123 <https://github.com/ansys/pycfx/pull/123>`_, `#128 <https://github.com/ansys/pycfx/pull/128>`_, `#130 <https://github.com/ansys/pycfx/pull/130>`_

        * - Bump github.com/PyCQA/pylint from v4.0.5 to 4.0.6 in the pre-commit group
          - `#126 <https://github.com/ansys/pycfx/pull/126>`_

        * - Bump pytest from 9.0.3 to 9.1.1
          - `#127 <https://github.com/ansys/pycfx/pull/127>`_

        * - Bump the actions group with 11 updates
          - `#135 <https://github.com/ansys/pycfx/pull/135>`_, `#139 <https://github.com/ansys/pycfx/pull/139>`_

        * - Update grpcio-health-checking requirement from <1.82.0,>=1.30.0 to >=1.30.0,<1.83.0
          - `#138 <https://github.com/ansys/pycfx/pull/138>`_


  .. tab-item:: Maintenance

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Update CHANGELOG for v0.2.0
          - `#49 <https://github.com/ansys/pycfx/pull/49>`_

        * - Update version in \`pyproject.toml\`
          - `#52 <https://github.com/ansys/pycfx/pull/52>`_

        * - Add codecov action and update README
          - `#54 <https://github.com/ansys/pycfx/pull/54>`_

        * - Update CHANGELOG for v0.2.1
          - `#61 <https://github.com/ansys/pycfx/pull/61>`_

        * - Update CHANGELOG for v0.2.2
          - `#64 <https://github.com/ansys/pycfx/pull/64>`_

        * - Update ansys/actions version to 10.3.0
          - `#66 <https://github.com/ansys/pycfx/pull/66>`_

        * - Update CHANGELOG for v0.2.3
          - `#68 <https://github.com/ansys/pycfx/pull/68>`_

        * - Updating CHANGELOG for v0.2.4
          - `#95 <https://github.com/ansys/pycfx/pull/95>`_

        * - Make update-changelog a required stage for releasing
          - `#96 <https://github.com/ansys/pycfx/pull/96>`_

        * - Update CHANGELOG for v0.2.5
          - `#104 <https://github.com/ansys/pycfx/pull/104>`_

        * - Add pre-commit section
          - `#107 <https://github.com/ansys/pycfx/pull/107>`_

        * - Grouping dependabot prs for actions and pre-commit
          - `#115 <https://github.com/ansys/pycfx/pull/115>`_

        * - Update pre-commit configuration
          - `#118 <https://github.com/ansys/pycfx/pull/118>`_

        * - Update missing or outdated files
          - `#120 <https://github.com/ansys/pycfx/pull/120>`_, `#124 <https://github.com/ansys/pycfx/pull/124>`_

        * - Update license headers
          - `#125 <https://github.com/ansys/pycfx/pull/125>`_

        * - Update CHANGELOG for v0.2.6
          - `#134 <https://github.com/ansys/pycfx/pull/134>`_

        * - Update version for 0.3.0 release
          - `#140 <https://github.com/ansys/pycfx/pull/140>`_


  .. tab-item:: Test

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Add tests for mesh statistics query
          - `#41 <https://github.com/ansys/pycfx/pull/41>`_

        * - Add test for some Solver errors
          - `#71 <https://github.com/ansys/pycfx/pull/71>`_

        * - Add unit tests for transform_mesh
          - `#129 <https://github.com/ansys/pycfx/pull/129>`_

        * - Add tests for mesh region queries
          - `#137 <https://github.com/ansys/pycfx/pull/137>`_


`0.2.6 <https://github.com/ansys/pycfx/releases/tag/v0.2.6>`_ - July 09, 2026
=============================================================================

.. tab-set::


  .. tab-item:: Fixed

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Minor test and doc fixes, plus version update
          - `#133 <https://github.com/ansys/pycfx/pull/133>`_


`0.2.5 <https://github.com/ansys/pycfx/releases/tag/v0.2.5>`_ - May 26, 2026
============================================================================

.. tab-set::


  .. tab-item:: Added

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Support API version 1 with env var
          - `#101 <https://github.com/ansys/pycfx/pull/101>`_


  .. tab-item:: Maintenance

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Update version for release 0.2.5
          - `#103 <https://github.com/ansys/pycfx/pull/103>`_


`0.2.4 <https://github.com/ansys/pycfx/releases/tag/v0.2.4>`_ - May 13, 2026
============================================================================

.. tab-set::


  .. tab-item:: Fixed

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Streamline dependencies
          - `#94 <https://github.com/ansys/pycfx/pull/94>`_


`0.2.3 <https://github.com/ansys/pycfx/releases/tag/v0.2.3>`_ - April 29, 2026
==============================================================================

.. tab-set::


  .. tab-item:: Dependencies

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Merge changes for release 0.2.3
          - `#67 <https://github.com/ansys/pycfx/pull/67>`_


`0.2.2 <https://github.com/ansys/pycfx/releases/tag/v0.2.2>`_ - April 28, 2026
==============================================================================

.. tab-set::


  .. tab-item:: Dependencies

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Merge changes for release 0.2.2
          - `#63 <https://github.com/ansys/pycfx/pull/63>`_


`0.2.1 <https://github.com/ansys/pycfx/releases/tag/v0.2.1>`_ - April 27, 2026
==============================================================================

.. tab-set::


  .. tab-item:: Dependencies

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Merge changes for release 0.2.1
          - `#60 <https://github.com/ansys/pycfx/pull/60>`_


`0.2.0 <https://github.com/ansys/pycfx/releases/tag/v0.2.0>`_ - April 09, 2026
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

        * - Remove release-from-main true option
          - `#43 <https://github.com/ansys/pycfx/pull/43>`_

        * - License metadata format
          - `#45 <https://github.com/ansys/pycfx/pull/45>`_

        * - Remove if always condition for unit tests
          - `#46 <https://github.com/ansys/pycfx/pull/46>`_


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

        * - Remove matrix strategy for build step
          - `#48 <https://github.com/ansys/pycfx/pull/48>`_


  .. tab-item:: Test

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Add tests for mesh object
          - `#36 <https://github.com/ansys/pycfx/pull/36>`_
