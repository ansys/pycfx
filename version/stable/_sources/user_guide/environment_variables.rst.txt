.. _ref_environment_variables:

=====================
Environment variables
=====================

This page lists selected environment variables that control various aspects of PyCFX.
The values of these variables are frozen when you import the PyCFX package. Any later changes to these variables within the same Python process do not affect the behavior of PyCFX. PyCFX also provides configuration variables that control its behavior within the same Python process.

.. vale off

.. list-table::
    :header-rows: 1

    * - Variable
      - Description
    * - ANSYSLMD_LICENSE_FILE
      - Specifies the license server for CFX.
    * - AWP_ROOT<NNN>
      - Specifies the CFX root directory for version vNNN when launching CFX using the
        :func:`from_install() <ansys.cfx.core.session_utilities.SessionBase.from_install>` function.
    * - CFX_CONTAINER_IMAGE
      - Specifies the full Docker image name, including its tag, when starting a CFX container using the
        :func:`from_container() <ansys.cfx.core.session_utilities.SessionBase.from_container>` function.
    * - CFX_IMAGE_NAME
      - Specifies the Docker image name when starting a CFX container using the
        :func:`from_container() <ansys.cfx.core.session_utilities.SessionBase.from_container>` function.
    * - CFX_IMAGE_TAG
      - Specifies the Docker image tag when starting a CFX container using the
        :func:`from_container() <ansys.cfx.core.session_utilities.SessionBase.from_container>` function.
    * - PYCFX_CFX_IP
      - Specifies the IP address of the CFX server using the
        :func:`from_connection() <ansys.cfx.core.session_utilities.SessionBase.from_connection>` function.
    * - PYCFX_CFX_PORT
      - Specifies the port of the CFX server in the
        :func:`from_connection() <ansys.cfx.core.session_utilities.SessionBase.from_connection>` function.
    * - PYCFX_CFX_ROOT
      - Specifies the CFX root directory when launching CFX using the
        :func:`from_install() <ansys.cfx.core.session_utilities.SessionBase.from_install>` function.
    * - PYCFX_CODEGEN_OUTDIR
      - Specifies the directory where API files are written during code generation.