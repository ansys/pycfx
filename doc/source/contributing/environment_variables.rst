.. _ref_environment_variables:

=====================
Environment variables
=====================

This page lists selected environment variables that can be set to control various aspects of PyCFX.
The values of these variables are frozen at the time of importing the PyCFX package and
any later changes to these variables within the same Python process do not affect
the behavior of PyCFX. PyCFX also provides a set of configuration variables that can be used to
control the behavior of PyCFX within the same Python process.

.. vale off

.. list-table::
    :header-rows: 1

    * - Variable
      - Description
    * - ANSYSLMD_LICENSE_FILE
      - Specifies the license server for CFX.
    * - AWP_ROOT<NNN>
      - Specifies the CFX root directory for the version vNNN while launching CFX in
        :func:`from_install() <ansys.cfx.core.session_utilities.SessionBase.from_install>`.
    * - CFX_CONTAINER_IMAGE
      - Specifies the full Docker image name including its tag while starting a CFX container in
        :func:`from_container() <ansys.cfx.core.session_utilities.SessionBase.from_container>`.
    * - CFX_IMAGE_NAME
      - Specifies the Docker image name while starting a CFX container in
        :func:`from_container() <ansys.cfx.core.session_utilities.SessionBase.from_container>`.
    * - CFX_IMAGE_TAG
      - Specifies the Docker image tag while starting a CFX container in
        :func:`from_container() <ansys.cfx.core.session_utilities.SessionBase.from_container>`.
    * - PYCFX_CFX_IP
      - Specifies the IP address of the CFX server in
        :func:`from_connection() <ansys.cfx.core.session_utilities.SessionBase.from_connection>`.
    * - PYCFX_CFX_PORT
      - Specifies the port of the CFX server in
        :func:`from_connection() <ansys.cfx.core.session_utilities.SessionBase.from_connection>`.
    * - PYCFX_CFX_ROOT
      - Specifies the CFX root directory while launching CFX in
        :func:`from_install() <ansys.cfx.core.session_utilities.SessionBase.from_install>`.
    * - PYCFX_CODEGEN_OUTDIR
      - Specifies the directory where API files are written out during codegen.