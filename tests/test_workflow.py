# Copyright (C) 2023 - 2026 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from pathlib import Path

from util.common import setup_write_dir

import ansys.cfx.core as pycfx
from ansys.cfx.core import examples
from ansys.cfx.core.launcher.cfx_container import timeout_loop
from ansys.cfx.core.session_pre import PreProcessing
from ansys.cfx.core.utils.cfx_version import CFXVersion

# pycfx.logging.enable()


def test_workflow(pypre: PreProcessing, pytestconfig):
    """
    End-to-end test for the static mixer example workflow using pycfx.

    This test performs the following steps:
    1. Downloads a mesh file for a static mixer example.
    2. Creates a new case and imports the mesh.
    3. Sets up fluid properties, reference pressure, heat transfer, and turbulence models.
    4. Configures inlet and outlet boundary conditions, including copying state between inlets.
    5. Sets solver control options and parallel execution parameters.
    6. Saves the case file and runs the solver
    7. Waits for the solver to finish
    8. Loads results in postprocessing, checks case loading, and sets up a plane and contour plot.
    9. Saves a PNG image of the contour plot and verifies its existence.

    Args:
        pypre (PreProcessing): The preprocessing session object.
        pytestconfig: Pytest configuration object with test directory paths.

    Raises:
        RuntimeError: If loading results fails and no cases are defined.
        AssertionError: If the contour image file is not created.
    """

    mesh_file = "StaticMixerMesh.gtm"
    generated_path_engine, generated_path_client = setup_write_dir(
        pytestconfig.test_data_directory_path, [mesh_file]
    )

    mesh_file_path_client = examples.download_file(
        mesh_file,
        "pycfx/static_mixer",
        generated_path_client,
    )

    pypre.file.new_case()

    mesh_file_path_engine = Path(generated_path_engine) / Path(mesh_file_path_client).name
    pypre.file.import_mesh(file_name=str(mesh_file_path_engine))

    default_domain = pypre.setup.flow["Flow Analysis 1"].domain["Default Domain"]
    default_domain.fluid_definition["Fluid 1"].material = "Water"
    default_domain.domain_models.reference_pressure.reference_pressure = "1 [atm]"
    default_domain.fluid_models.heat_transfer_model.option = "Thermal Energy"
    default_domain.fluid_models.turbulence_model.option = "k epsilon"

    default_domain.boundary["in1"] = {}
    in1 = default_domain.boundary["in1"]
    in1.boundary_type = "INLET"
    in1.location = "in1"
    in1.boundary_conditions.mass_and_momentum.option = "Normal Speed"
    in1.boundary_conditions.mass_and_momentum.normal_speed = "2 [m s^-1]"
    in1.boundary_conditions.heat_transfer.static_temperature = "315 [K]"

    in1_state = default_domain.boundary["in1"].get_state()
    default_domain.boundary["in2"] = in1_state
    in2 = default_domain.boundary["in2"]
    in2.location = "in2"
    in2.boundary_conditions.heat_transfer.static_temperature = "285 [K]"

    pypre.setup.flow["Flow Analysis 1"].domain["Default Domain"].boundary["out"] = {}
    out = pypre.setup.flow["Flow Analysis 1"].domain["Default Domain"].boundary["out"]
    out.boundary_type = "OUTLET"
    out.location = "out"
    out.boundary_conditions.mass_and_momentum.option = "Average Static Pressure"
    out.boundary_conditions.mass_and_momentum.relative_pressure = "0 [Pa]"

    solver_control = pypre.setup.flow["Flow Analysis 1"].solver_control
    solver_control.advection_scheme.option = "Upwind"
    solver_control.convergence_control.timescale_control = "Physical Timescale"
    solver_control.convergence_control.physical_timescale = "2 [s]"

    exec_control = pypre.setup.simulation_control.execution_control
    exec_control.solver_step_control.parallel_environment.start_method = "Intel MPI Local Parallel"
    exec_control.solver_step_control.parallel_environment.maximum_number_of_processes = 2

    case_file_root = "static_mixer"

    if pypre.get_cfx_version() > CFXVersion.v252:
        pysolve = pycfx.Solver.from_session(pypre)
    else:
        pysolve = pycfx.Solver.from_session(pypre, case_file_name=case_file_root)

    pypre.exit()
    Path(mesh_file_path_client).unlink()

    pysolve.solution.start_run()

    pypost = pycfx.PostProcessing.from_session(pysolve)
    results_file = pysolve.solution.get_results_file_name()  # For tidying up later
    pysolve.exit()

    case_names = pypost.results.data_reader.case.get_object_names()
    if case_names:
        current_case = case_names[0]
    else:
        raise RuntimeError("Loading results failed; no cases defined.")

    current_case = pypost.results.data_reader.case[current_case]

    hardcopy = pypost.results.hardcopy
    hardcopy.hardcopy_format = "png"
    hardcopy.image_height = 1200
    hardcopy.image_width = 1200
    hardcopy.use_screen_size = False

    pypost.results.plane["Plane 1"] = {"option": "ZX Plane", "plane_type": "Slice"}

    pypost.results.contour["Contour 1"] = {
        "colour_variable": "Pressure",
        "location_list": "/PLANE:Plane 1",
        "number_of_contours": 11,
        "contour_range": "Local",
        "draw_contours": True,
        "fringe_fill": True,
    }
    contour = pypost.results.contour["Contour 1"]
    contour.show(view="/VIEW:View 1")

    contour_file_name = "static_mixer_contour.png"
    client_picture_file = Path(generated_path_client) / contour_file_name
    pypost.file.save_picture(file_name=f"{generated_path_engine}/{contour_file_name}")
    assert timeout_loop(client_picture_file.exists, timeout=10.0)
    assert client_picture_file.stat().st_size > 0
    client_picture_file.unlink()

    pypost.exit()

    output_file = results_file.replace(".res", ".out")
    assert Path(results_file).exists()
    assert Path(output_file).exists()
    Path(results_file).unlink()
    Path(output_file).unlink()
