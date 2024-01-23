"""
Solve the structural vibration problem and the aeroelastic stability problem as 
eigenvalue problems.

Look at the main() function to understand the data flow. 

The script assumes that Calculix (ccx) was already exectuted to output the FEM mass 
and stiffness matrices, which are read-in at the start of the main() function. 

The aerodynamic stiffness and damping matrices are calculated using simple 
modified strip theory equations, which include tip effects on the lift distribution 
and assume a constant Mtheta_dot term (-1.2).   

Execute this module to run simple test cases for a composite plate model and for 
a higher order box model. Note: CCX input files are included in the git folder, 
but you may need to run CCX to generate the required .mas and .sti output files, 
before exeturing this moodule. Step by step instruction are in the test case functions:
simple_plate_tests()
parametric_box_tests():

"""

from typing import Counter
from scipy.sparse import csr_matrix, csc_matrix, bmat, eye
from scipy.sparse.linalg import eigsh, eigs, inv
from scipy.interpolate import LinearNDInterpolator, interp2d
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
from pathlib import Path
import csv
from io import StringIO

from femtools import membertools
from Rocket.fem.FemStripTheoryAerodynamics import AeroModel
from Rocket.fem.CcxTools import CcxTools

# For interactive session debugging:
# np.set_printoptions(precision=3, linewidth=200)

# PLATE_AERO = {
#     "planform": {
#         "A": np.array([0.0, 0.0, 0.0], dtype=float),  # LE fixed root
#         "B": np.array([0.0, 0.3048, 0.0], dtype=float),  # LE tip
#         "CA": 0.0762,  # chord at root
#         "CB": 0.0762,  # chord at tip
#     },
#     "strips": 10,  # number of aero strips along the span >=1
#     "root_alpha": 10,  # AoA at the wing root in degrees
#     "rho": 1.225,  # air density in Pa
#     "V": {
#         "start": 1.0,
#         "end": 45.0,
#         "inc0": 2.0,
#         "inc_min": 0.01,
#     },  # air velocity range in m/s
#     "mode_tracking_threshold": 0.60,
#     "CL_alpha": 2 * np.pi,  # ideal lift curve slope
# }

BOX_AERO = {
    "planform": None,  # from box model - or {"A":[0,0,0], "B":[0,2.0,0], "CA":0.2, "CB":0.2}
    "strips": 10,  # number of aero strips along the span >=1
    "root_alpha": 0,  # AoA at the wing root in degrees
    "rho": 1.225,  # air density in Pa
    "V": {
        "start": 1.0,
        "end": 150.0,
        "inc0": 5.0,
        "inc_min": 0.01,
    },  # air velocity range in m/s
    "mode_tracking_threshold": 0.60,
    "CL_alpha": 2 * np.pi,  # ideal lift curve slope
}

DEBUG_MODE_TRACKING_FLAG = False


def modal_aeroelastic(analysis, aero_inputs=None, box_inputs=None, k_modes=10):

    ccx = CcxTools()
    ccx.analysis = analysis
    ccx.find_solver()

    if analysis.getObject("ccx_sti_file") is None:
        print("No stiffness matrix found")

    for o in analysis.getSubObjects():
        print(o)
        dir(o)

    # dofs that are constrained
    tools = membertools.AnalysisMember(analysis)
    for n in tools.cons_fixed:
        print(n)
    solver = ccx.solver
    print("Solver\n")
    print(solver)
    # mesh = membertools.get_mesh_to_solve(analysis) #analysis.getObject("Fin_Mesh")
    mesh = analysis.getObject("Fin_Mesh")
    print("Mesh\n")
    print(mesh)
    from femmesh import meshsetsgetter
    meshdatagetter = meshsetsgetter.MeshSetsGetter(
        analysis,
        solver,
        mesh,
        tools
    )
    meshdatagetter.get_mesh_sets()
    print("fixed nodes:\n")
    # print(meshdatagetter.member.cons_fixed)
    # fixed_dofs = np.array(tools.cons_fixed)
    data = []
    for node in meshdatagetter.member.cons_fixed[0]["Nodes"]:
        for i in range(1,7):
            row = [node, i * 1.0]
            data.append(row)
    fixed_dofs = np.array(data)
    print(fixed_dofs)

    # csv_file = Path(folder, "SPC_123456.bou")
    # fixed_dofs = _read_matrix_csv(csv_file, delimiter=",", skip_lines_with="**")

    # load row_dof lookup matrix, where each row matches K, M matrix rows and corresponds
    # to node.dir combination
    csv_file = analysis.getObject("ccx_dof_file")
    contents = csv_file.Text
    # print(contents)
    lookup = _read_matrix_csv_string(contents, delimiter=".")
    print(lookup)

    # # read shell node locations from input file
    # csv_file = Path(folder, "all.msh")
    # nodes_xyz = _read_matrix_csv(
    #     csv_file, delimiter=",", skip_lines_with="*", read_only="*NODE"
    # )
    # # filter nodes for aero shape interpolation (e.g. only upper surface on box)
    # nodes_xyz = nodes_xyz[nodes_xyz[:, 3] >= 0.0]
    print("Node locations\n")
    # print(dir(mesh.FemMesh))
    data = []
    for node, vector in mesh.FemMesh.Nodes.items():
        print(node)
        print(vector)
        data.append([node, vector.x, vector.y, vector.z])
    nodes_xyz = np.array(data)
    # print(nodes_xyz)
    # filter nodes for aero shape interpolation (e.g. only upper surface on box)
    # nodes_xyz = nodes_xyz[nodes_xyz[:, 2] >= 0.0]
    nodes_xyz = nodes_xyz[nodes_xyz[:, 2] > 0.0]
    # print(nodes_xyz)

    problem = {}
    csv_file = analysis.getObject("ccx_mas_file")
    contents = csv_file.Text
    data = _read_matrix_csv_string(contents)
    problem['mas'] = _get_matrix(data)  # , filter_out_rows=fixed_dofs_rows)

    csv_file = analysis.getObject("ccx_sti_file")
    contents = csv_file.Text
    data = _read_matrix_csv_string(contents)
    problem['sti'] = _get_matrix(data)  # , filter_out_rows=fixed_dofs_rows)

    # check that the stiffness matrix is positive definite
    if not all(eigsh(problem["sti"])[0] > 0):
        print("Warning: Stiffness matrix is not positive definite.")
    if not all(eigsh(problem["mas"])[0] > 0):
        print("Warning: Mass matrix is not positive definite.")

    # normal modes analysis
    omega, _, evecs = get_normal_modes(problem, k=k_modes)

    assert (
        k_modes % 2 == 0.0
    ), "Define even number of k_modes for the aeroelastic analysis."

    # get modal mass and stiffness matrices
    problem["M"] = csc_matrix(evecs.T @ problem["mas"] @ evecs)
    problem["K"] = csc_matrix(evecs.T @ problem["sti"] @ evecs)

    # instantiate aero model
    aeromodel = AeroModel(aero_inputs, box_inputs)

    # define the corner nodes of the aerodynamic planform
    aeromodel.get_planform()

    # calculate the internal aero node positions at the leading and trailing edges
    aeromodel.get_all_nodes()
    aeronodes = np.vstack([aeromodel.le_nodes, aeromodel.te_nodes])

    # filter normal mode eigenvector DOFs and reduce from 3D element nodes to shell nodes
    aero_evecs = _get_aero_evects(
        evecs,
        lookup,
        nodes_xyz,
        aeronodes,
        fixed=fixed_dofs,
        dirs=[3],
        plot_flag=False,
    )

    # get aero damping and stiffness matrices B and C
    problem["B"] = _get_aero_damping(aeromodel, aero_evecs, Mxi_dot=-1.2, e=0.25)
    problem["C"] = _get_aero_stiffness(aeromodel, aero_evecs, e=0.25)

    # flutter / divergence analysis
    V, V_omega, V_damping, _, _, flutter, divergence = get_complex_aero_modes(
        problem,
        rho=aero_inputs["rho"],
        Vdict=aero_inputs["V"],
        k=k_modes,
        plot_flag=True,
        folder=None,
        threshold=aero_inputs[
            "mode_tracking_threshold"
        ],  # used of macxp mode sorting
    )
    return omega, V, V_omega, V_damping, flutter, divergence


def simple_plate_tests():
    """Fast tests using a simple cantelevered flat plate model.
    NOTE: Requires mesh and CCX analysis output. Steps to generate these:
    1) cd "folder"
    2) cgx_2.19 -bg cgx_infile.fdb
    3) open all.msh file in editor and change element type from S8 to S8R
    4) ccx_2.19 ccx_normal_modes*
    5) ccx_2.19 ccx_normal_modes_matout

    *4) is not stricly required, but provides ccx normal mode eigenvalues for comparison.
    """

    # SIMPLE PLATE normal modes checks
    freq_scipy = main(
        file="ccx_normal_modes_matout",
        folder="test_data/test_eigenvalue_analysis/composite_plate_0_-45_45",
        k_modes=15,
    )
    freq_ccx = np.array(
        [
            0.9844066e01,
            0.4930842e02,
            0.6179677e02,
            0.1572807e03,
            0.1738530e03,
            0.2941666e03,
            0.3399870e03,
            0.4720929e03,
            0.5622821e03,
            0.6990578e03,
            0.6997033e03,
            0.8424458e03,
            0.9799083e03,
            0.1183415e04,
            0.1318173e04,
        ]
    )
    assert np.allclose(freq_scipy, freq_ccx, rtol=1e-3)

    # SIMPLE PLATE flutter analysis check
    freq_scipy, V, V_omega, V_damping, flutter, divergence = modal_analysis(
        file="ccx_normal_modes_matout",
        folder="test_data/test_eigenvalue_analysis/composite_plate_0_-45_45",
        aero_inputs=PLATE_AERO,
        k_modes=16,
    )
    assert flutter == [{"mode": 2, "V": 33.0}]
    assert divergence == []
    flutter_index = np.argwhere(np.isclose(V, flutter[0]["V"]))
    assert (
        V_damping[flutter_index[0] - 1, flutter[0]["mode"] - 1] > 0.0
        and V_damping[flutter_index[0], flutter[0]["mode"] - 1] <= 0.0
    )

    freq_scipy, V, V_omega, V_damping, flutter, divergence = modal_analysis(
        file="ccx_normal_modes_matout",
        folder="test_data/test_eigenvalue_analysis/composite_plate_0_0_90",
        aero_inputs=PLATE_AERO,
        k_modes=16,
    )
    assert flutter == [{"mode": 2, "V": 26.5}]
    assert divergence == [{"mode": 1, "V": 32.5}]
    divergence_index = np.argwhere(np.isclose(V, divergence[0]["V"]))
    assert (
        V_damping[divergence_index[0] - 1, divergence[0]["mode"] - 1] > 0.0
        and V_damping[divergence_index[0], divergence[0]["mode"] - 1] <= 0.0
    )


def parametric_box_tests():
    """Slower tests using a composite parametric box wing model.
    NOTE: Requires mesh and CCX analysis output. Steps to generate these:
    1) cd "folder"
    2) ccx_2.19 ccx_normal_modes*
    3) ccx_2.19 ccx_normal_modes_matout

    *2) is not stricly required, but provides ccx normal mode eigenvalues for comparison.
    """
    from parametric_box import INPUTS

    # box model aerelastic analysis
    freq_scipy, V, V_omega, V_damping, flutter, divergence = modal_analysis(
        file="ccx_normal_modes_matout",
        folder="test_data/test_eigenvalue_analysis/composite_wing",
        aero_inputs=BOX_AERO,
        box_inputs=INPUTS[1],
        k_modes=10,
    )
    freq_ccx = np.array(
        [
            0.6925236e01,
            0.3730376e02,
            0.4572749e02,
            0.5929500e02,
            0.8697576e02,
            0.1345654e03,
            0.1624646e03,
            0.1728907e03,
            0.1969553e03,
            0.2176435e03,
        ]
    )
    assert np.allclose(freq_scipy, freq_ccx, rtol=1e-3)
    assert flutter == [
        {"mode": 3, "V": 71.0},
        {"mode": 4, "V": 76.0},
        {"mode": 2, "V": 141.62},
        {"mode": 4, "V": 141.74},
    ]
    assert divergence == []


def get_normal_modes(problem, k=10):
    """Solve an real eigenvalue problem to obtain the k lowest eigenvalues and
    eigenvectors."""

    evals_small, evecs_small = eigsh(
        problem["sti"], k=k, M=problem["mas"], sigma=0.0, which="LM"
    )
    # print frequencies in Hz
    omega = np.sqrt(evals_small) / (2 * np.pi)
    print("Normal modes frequencies (Hz): ", omega)

    return omega, evals_small, evecs_small


def get_complex_aero_modes(
    problem, rho, Vdict, k=10, plot_flag=False, folder=None, threshold=0.55
):
    """Solve the aeroelastic stability equations at incrementally increasing
    velocity values to identify flutter and divergence speeds."""

    print("Starting aeroelastic stability analysis.")

    V_omega = np.zeros([0, k])
    V_damping = np.zeros([0, k])
    V_eig = np.empty([0, k], dtype=np.complex128)
    V_mode_id = np.zeros([0, k])
    V_flutter = np.zeros([0, k], dtype=np.bool8)
    V_divergence = np.zeros([0, k], dtype=np.bool8)
    V_eigv_memory = np.empty([k, k], dtype=np.complex128)
    flutter = []
    divergence = []
    vinc = Vdict["inc0"]  # starting velocity increment
    velocity = Vdict["start"]
    index = 0
    V = []
    incV_flag = True
    while incV_flag:

        tracked = False
        iteration_counter = 0
        while tracked is False:

            # solve complex eigenvalue problem
            Q = _get_system_matrix(problem, rho, velocity)
            evals_small, evecs_small = eigs(Q, k=k, sigma=0.0, which="LM")

            # mode tracking
            if index == 0:
                e_model1 = evals_small
                e_model2 = e_model1
                mu_model1 = evecs_small[k:, :]
                mu_model2 = mu_model1
            else:
                e_model1 = V_eig[index - 1, :]
                e_model2 = evals_small
                mu_model1 = V_eigv_memory
                mu_model2 = evecs_small[k:, :]
            macxp = _get_macpx(
                e_model1,
                e_model2,
                mu_model1=mu_model1,
                mu_model2=mu_model2,
                v=velocity,
                plot_flag=DEBUG_MODE_TRACKING_FLAG,
                figure_name=str(Path(folder, "macxp.png")),
                threshold=threshold,
            )
            mode_order, tracked = _get_mode_order(macxp, threshold=threshold)
            if not tracked:

                # reduce velocity increment of current step
                if index == 0:
                    velocity = Vdict["start"]
                else:
                    velocity = V[-1]
                    vinc *= 0.75
                    if vinc < Vdict["inc_min"]:
                        vinc = Vdict["inc_min"]
                    velocity += vinc
                    iteration_counter += 1

                if vinc < Vdict["inc_min"]:
                    print(
                        "No convergence of the mode tracking: reduce threshold or reduce min V increment."
                    )
                    break
                elif iteration_counter > 20:
                    print(
                        "No convergence of the mode tracking: max number of iterations reached."
                    )
                    break
                elif not all(mode_order <= macxp.shape[0] / 2):
                    print(
                        f"Mode tracking failed at V={velocity} likely due to mode moving outside tracked range. Request more modes."
                    )
                    break

                print(f"Cut-back velocity increment to {vinc} m/z.")

            else:
                pat = [(0, 1), (0, 0)]
                V_mode_id = np.append(V_mode_id, [mode_order], axis=0)
                V_eig = np.pad(V_eig, pat, mode="empty")
                V_omega = np.pad(V_omega, pat, mode="constant")
                V_damping = np.pad(V_damping, pat, mode="constant")
                V_flutter = np.pad(V_flutter, pat, mode="constant")
                V_divergence = np.pad(V_divergence, pat, mode="constant")
                if vinc < Vdict["inc0"]:
                    vinc = Vdict["inc0"]
                    print(f"Reset velocity increment to {vinc} m/s.")

        if tracked:
            try:
                for mode in np.unique(V_mode_id[index, :]):
                    ii = np.argwhere(V_mode_id[index, :] == mode)
                    col = int(mode - 1)
                    # reorder the eigenvalue output by ascending mode number (for plotting)
                    V_eig[index, int((mode - 1) * 2)] = evals_small[ii[0]]
                    V_eig[index, int((mode - 1) * 2 + 1)] = evals_small[ii[1]]
                    V_eigv_memory[:, int((mode - 1) * 2)] = evecs_small[
                        k:, ii[0]
                    ].flatten()
                    V_eigv_memory[:, int((mode - 1) * 2 + 1)] = evecs_small[
                        k:, ii[1]
                    ].flatten()
                    if np.isclose(np.conj(evals_small[ii[0]]), evals_small[ii[1]]):
                        # underdamped mode - complex conjugate modes
                        e = evals_small[ii[0]]
                        omega = np.abs(e)  # rads
                        V_omega[index, col] = omega / (2 * np.pi)  # Hz
                        V_damping[index, col] = -1.0 * e.real / omega * 100
                        if V_damping[index, col] <= 0:
                            V_flutter[index, col] = True
                            if index == 0 or V_flutter[index - 1, col] == False:
                                flutter.append(
                                    {"mode": int(mode), "V": round(velocity, 2)}
                                )
                    else:
                        # critically or overdamped mode
                        e = evals_small[ii]
                        V_omega[index, col] = 0.0  # Hz
                        V_damping[index, col] = np.min(-1.0 * e.real / np.abs(e) * 100)
                        if V_damping[index, col] <= 0:
                            V_divergence[index, col] = True
                            if index == 0 or V_divergence[index - 1, col] == False:
                                divergence.append(
                                    {"mode": int(mode), "V": round(velocity, 2)}
                                )
                V.append(velocity)
                print(f"V={velocity}m/s step completed.")
                velocity += vinc
                index += 1

            except Exception as err:
                print("ERROR - Exiting aeroelastic stability analysis.")
                print(f"Caught error: {err=}, {type(err)=}")
                V.append(velocity)
                incV_flag = False
        else:
            incV_flag = False
            print("Warning: Exiting aeroelastic stability analysis.")

        if velocity >= Vdict["end"]:
            incV_flag = False
            print("Completed aeroelastic stability analysis.")

    print("Flutter modes:", flutter)
    print("Divergence modes:", divergence)

    if plot_flag:
        colors = plt.rcParams["axes.prop_cycle"].by_key()["color"]
        repeat_colors = [
            color
            for sublist in [item for item in zip(colors, colors)]
            for color in sublist
        ]
        _plot_histories(
            [
                {
                    "x": V,
                    "y": V_omega[:, np.nonzero(V_omega[0, :])[0]],
                    "x_label": "Airspeed, m/s",
                    "y_label": "Frequency, Hz",
                    "fname": str(Path(folder, "V_omega.png")),
                    "colors": colors,
                },
                {
                    "x": V,
                    "y": V_damping[:, np.nonzero(V_damping[0, :])[0]],
                    "x_label": "Airspeed, m/s",
                    "y_label": "Damping ratio, %",
                    "fname": str(Path(folder, "V_damping.png")),
                    "colors": colors,
                },
                {
                    "x": V,
                    "y": V_eig.real,
                    "x_label": "Airspeed, m/s",
                    "y_label": "real part of eigenvalue",
                    "fname": str(Path(folder, "V_eig_real.png")),
                    "colors": repeat_colors,
                },
                {
                    "x": V,
                    "y": V_eig.imag,
                    "x_label": "Airspeed, m/s",
                    "y_label": "imaginary part of eigenvalue",
                    "fname": str(Path(folder, "V_eig_imag.png")),
                    "colors": repeat_colors,
                },
            ]
        )

    return V, V_omega, V_damping, V_eig, V_mode_id, flutter, divergence


########### Private functions that do not get called directly


def _read_matrix_csv(file, delimiter=" ", skip_lines_with=None, read_only=None):
    """Reads csv and strips empty entries."""

    if read_only is None:
        read_flag = True
    else:
        read_flag = False

    data = []
    with open(file, newline="") as csvfile:
        data = _read_matrix_csv_raw(csvfile, read_flag, delimiter, skip_lines_with)

    return np.array(data)

def _read_matrix_csv_string(contents, delimiter=" ", skip_lines_with=None, read_only=None):
    """Reads csv and strips empty entries."""

    if read_only is None:
        read_flag = True
    else:
        read_flag = False

    data = []
    with StringIO(contents) as csvfile:
        data = _read_matrix_csv_raw(csvfile, read_flag, delimiter, skip_lines_with)

    return np.array(data)

def _read_matrix_csv_raw(csvfile, read_flag, delimiter, skip_lines_with):
    """Reads csv and strips empty entries."""

    data = []
    reader = csv.reader(csvfile, delimiter=delimiter)
    if skip_lines_with is None and read_flag:
        data = [[float(val) for val in row if bool(val.strip())] for row in reader]
    elif skip_lines_with and read_flag:
        data = [
            [float(val) for val in row if bool(val.strip())]
            for row in reader
            if not skip_lines_with in row[0]
        ]
    elif not read_flag:
        data = []
        for row in reader:
            if not read_flag and read_only in row[0]:
                read_flag = True
                continue
            elif read_flag and skip_lines_with in row[0]:
                read_flag = False
                break
            elif read_flag:
                data.append([float(val) for val in row if bool(val.strip())])

    return data


def _get_matrix(data, filter_out_rows=None):
    """Transform CCX matrix csv output to sparse matrix format."""

    mask = np.ones(len(data), dtype=bool)
    if filter_out_rows:
        # set the mask to false where the index is a filtered row
        frows = []
        for row in filter_out_rows:
            # get the filtered row / col indices
            index = np.sort(
                np.hstack(
                    [np.where(data[:, 0] == row)[0], np.where(data[:, 1] == row)[0]]
                )
            )
            # index = np.sort(np.where(data[:,1] == row)[0])
            if index.size > 0:
                frows += index.tolist()
        mask[frows] = False

    # data array contains (row, col, val) in each row
    m, n = np.max(data[:, :2], axis=0)
    matrix = np.zeros((int(m), int(n)), dtype=np.float64)
    for row in data[mask, :]:
        matrix[int(row[0] - 1), int(row[1] - 1)] = row[2]
    submatrix = np.where(np.any(matrix < 0, axis=1) | np.any(matrix > 0, axis=1))[0]
    mat = matrix[np.reshape(submatrix, (-1, 1)), submatrix]
    return csr_matrix(mat + np.tril(mat.T, k=-1))


def _filter_evec(node_ids, dirs, lookup, evecs):
    """Filter eigenvector output from ccx to certain node xyz ranges and dimensions only."""

    mask = np.ones(len(lookup), dtype=bool)
    for index, row in enumerate(lookup):
        if not row[0] in node_ids or not row[1] in dirs:
            mask[index] = False

    filtered_evecs = evecs[mask, :]
    filtered_dofs = lookup[mask, :]

    return filtered_evecs, filtered_dofs


def _get_unique_evecs(filtered_evecs, filtered_dofs):
    """Average displacements at duplicate dofs - required due to expansion of shells
    to 3D elements in CCX, which results in duplicate DOFs in the eigenvector output."""

    reduced_dofs = np.unique(filtered_dofs, axis=0)
    reduced_evecs = np.zeros([len(reduced_dofs), filtered_evecs.shape[1]])
    for index, dof in enumerate(reduced_dofs):
        # get indices of repeated dofs
        indices = np.where((filtered_dofs == dof).all(axis=1))[0]
        reduced_evecs[index, :] = np.average(filtered_evecs[indices, :], axis=0)

    return reduced_evecs, reduced_dofs


def _apply_boundary_conditions(reduced_evecs, reduced_dofs, fixed):
    """Ensure that deflections are fixed at boundary condition nodes. Due to
    expansion of the shell elements to 3D elements in CCX, there may be non-zero eigenvector
    outputs at nodes corresponding to 3D element mid-height nodes, as these are not constrained
    even when all displacements and rotations are constrained on the corresponding shell element
    nodes."""

    mask = np.zeros(len(reduced_dofs), dtype=bool)
    frows = []
    for row in fixed:
        index = np.where((reduced_dofs == row).all(axis=1))[0]
        # index = np.sort(np.where(data[:,1] == row)[0])
        if index.size > 0:
            frows += index.tolist()
    mask[frows] = True

    reduced_evecs[mask, :] = 0.0

    return reduced_evecs


def _plot_modes(data_sets, modes="all"):
    """Plot overlay of the structures and aero modes to check they match."""

    if modes == "all":
        # one figure per eigenvector
        modes = data_sets[0][2].shape[1]

    for mode in range(modes):
        fig = plt.figure()
        ax = fig.add_subplot(projection="3d")
        for data in data_sets:
            ax.scatter(data[0], data[1], data[2][:, mode], label=data[3])
            if data[3] == "AERO":
                LE_indices = int(len(data[0]) / 2)
                ax.plot3D(
                    data[0][:LE_indices],
                    data[1][:LE_indices],
                    data[2][:LE_indices, mode],
                    "grey",
                )
                ax.plot3D(
                    data[0][LE_indices:],
                    data[1][LE_indices:],
                    data[2][LE_indices:, mode],
                    "grey",
                )
        ax.set_xlabel("X, m")
        ax.set_ylabel("Y, m")
        ax.set_zlabel("Z, normalised")
        ax.legend()

    plt.show()


def _get_aero_evects(
    evecs, lookup, nodes_xyz, aeronodes, fixed=None, dirs=None, plot_flag=False
):

    # filter evecs to nodes xyz and dims only
    filtered_evecs, filtered_dofs = _filter_evec(
        node_ids=nodes_xyz[:, 0].astype(int),
        dirs=dirs,
        lookup=lookup.astype(int),
        evecs=evecs,
    )

    # average duplicate dofs
    reduced_evecs, reduced_dofs = _get_unique_evecs(
        filtered_evecs, filtered_dofs.astype(int)
    )

    # set boundary conditions to zero
    if not fixed is None:
        reduced_evecs = _apply_boundary_conditions(reduced_evecs, reduced_dofs, fixed)

    # get xyz for all dof nodes
    X = np.zeros([len(reduced_dofs)])
    Y = np.zeros([len(reduced_dofs)])
    for index, dof in enumerate(reduced_dofs):
        node_index = np.where(nodes_xyz[:, 0] == dof[0])[0]
        X[index] = nodes_xyz[node_index, 1]
        # Y[index] = nodes_xyz[node_index, 2]
        Y[index] = nodes_xyz[node_index, 3] # We're on the X,Z plane

    # interpolate aero eigenvectors
    aero_evecs = np.zeros([len(aeronodes), reduced_evecs.shape[1]])
    for index, evect in enumerate(reduced_evecs.transpose()):
        f = LinearNDInterpolator((X, Y), evect, fill_value=0.0)
        for nodeid, node in enumerate(aeronodes):
            aero_evecs[nodeid, index] = f(node[0], node[1])

    # plot selected modes for visual check
    if plot_flag:
        _plot_modes(
            [
                (X, Y, reduced_evecs, "FEM"),
                (aeronodes[:, 0], aeronodes[:, 1], aero_evecs, "AERO"),
            ]
        )

    return aero_evecs


def _get_chords_from_aero_dofs(aeromodel):
    """Recover the aerodynamic chord lengths from the leading and trailing edge
    aero node positions."""

    c = np.zeros([len(aeromodel.le_nodes), 1])
    for ii in range(len(aeromodel.le_nodes)):
        c[ii] = aeromodel.te_nodes[ii, 0] - aeromodel.le_nodes[ii, 0]
    return c


def _get_lift_factor_from_aero_dofs(aeromodel, span):
    """Define the effective lift coefficient at every strip. Includes an
    approximation of the tip effects, where lift tends to 0 at the free edge."""

    aw = np.zeros([len(aeromodel.le_nodes), 1])
    for ii in range(len(aeromodel.le_nodes)):
        aw[ii] = aeromodel.aero_inputs["CL_alpha"] * (
            1 - (aeromodel.le_nodes[ii, 1] / span) ** 3
        )
    return aw


def _get_phi(aero_evecs, option):
    """Intermediary function to return eigenvector combinations related to the
    local strip average w (flapping) deflection (option == "LEplusTE") or the local
    twist (option == "LEminusTE")."""

    nnodes = int(aero_evecs.shape[0] / 2)
    phi = np.zeros([nnodes, aero_evecs.shape[1]])
    for index, col in enumerate(aero_evecs.T):
        if option == "LEplusTE":
            phi[:, index] = -col[:nnodes] - col[nnodes:]
        elif option == "LEminusTE":
            phi[:, index] = col[:nnodes] - col[nnodes:]
        else:
            raise ValueError(f"Option {option} is not recognised.")
    return phi


def _get_aero_component_matrices(aeromodel, aero_evecs):

    # get component matrices
    span = aeromodel._point_b[1]
    nstrips = aeromodel.aero_inputs["strips"]
    c = _get_chords_from_aero_dofs(aeromodel)  # vector of length dof/2
    aw = _get_lift_factor_from_aero_dofs(aeromodel, span)  # vector of length dof/2
    dy_strips = (
        np.vstack([np.array([0.5]), np.ones([nstrips - 1, 1]), np.array([0.5])])
        * span
        / (nstrips + 1)
    )  # vector of length dof/2

    # matrices of dof/2 * n eigenvectors
    phi_LEplusTE = _get_phi(aero_evecs, option="LEplusTE")
    phi_LEminusTE = _get_phi(aero_evecs, option="LEminusTE")

    return c, aw, dy_strips, phi_LEplusTE, phi_LEminusTE


def _get_aero_damping(aeromodel, aero_evecs, Mxi_dot=-1.2, e=0.25):
    """Modified strip theory aero damping, with a constant Mtheta_dot term and
    e being a load excentricity factor corresponding to the ratio of the flexural
    axis offset from the aerodynamic centre to the chord length."""

    c, aw, dy_strips, phi_LEplusTE, phi_LEminusTE = _get_aero_component_matrices(
        aeromodel, aero_evecs
    )
    mat_size = aero_evecs.shape[1]
    B_mat = np.zeros([mat_size, mat_size], dtype=np.float64)
    for index in range(mat_size):
        B_mat[index, :] = (
            (1 / 8)
            * phi_LEplusTE[:, index].transpose()
            @ np.diag((c * aw * dy_strips)[:, 0])
            @ phi_LEplusTE
            - (e / 4)
            * phi_LEminusTE[:, index].transpose()
            @ np.diag((c * aw * dy_strips)[:, 0])
            @ phi_LEplusTE
            - (Mxi_dot / 8)
            * phi_LEminusTE[:, index].transpose()
            @ np.diag((c * dy_strips)[:, 0])
            @ phi_LEminusTE
        )

    return csr_matrix(B_mat)


def _get_aero_stiffness(aeromodel, aero_evecs, e=0.25):
    """Modified strip theory aero stiffness, with e being a load excentricity factor
    corresponding to the ratio of the flexural axis offset from the aerodynamic centre
    to the chord length."""

    _, aw, dy_strips, phi_LEplusTE, phi_LEminusTE = _get_aero_component_matrices(
        aeromodel, aero_evecs
    )
    mat_size = aero_evecs.shape[1]
    C_mat = np.zeros([mat_size, mat_size], dtype=np.float64)
    for index in range(mat_size):
        C_mat[index, :] = (1 / 4) * phi_LEplusTE[:, index].transpose() @ np.diag(
            (aw * dy_strips)[:, 0]
        ) @ phi_LEminusTE - (e / 2) * phi_LEminusTE[:, index].transpose() @ np.diag(
            (aw * dy_strips)[:, 0]
        ) @ phi_LEminusTE

    return csr_matrix(C_mat)


def _get_system_matrix(problem, rho, V):
    """Define the modal aeroelastic system matrix Q.
    Ref: Olivia Stodieck, Aeroelastic Tailoring of Tow-steered Composite Wings, Phd Thesis 2016
    """

    M = problem["M"]
    K = problem["K"]
    B = problem["B"]
    C = problem["C"]
    Q = bmat(
        [
            [None, eye(M.shape[0], dtype=np.float64)],
            [-inv(M) @ (K + rho * V**2 * C), -inv(M) @ (rho * V * B)],
        ]
    )

    return Q


def _get_macpx(
    e_model1,
    e_model2,
    mu_model1,
    mu_model2,
    v,
    plot_flag=False,
    figure_name=None,
    threshold=0.6,
):
    """Calculate the MACXP criterion to identify mode switchings.
    Ref: P. Vacher, B. Jacquier, A. Bucharles, "Extensions of the MAC criterion
    to complex modes", PROCEEDINGS OF ISMA2010 INCLUDING USD2010, pp.2713-2726
    """

    # get mode shape
    modes = len(e_model1)

    # calculate the MACXP criterion from equation [28] in the reference
    macxp = np.zeros([modes, modes])
    for ii, mii in enumerate(mu_model1.T):
        for jj, mjj in enumerate(mu_model2.T):
            coef = (
                np.abs(np.vdot(mii, mjj)) / np.abs(np.conj(e_model1[ii]) + e_model2[jj])
                + np.abs(np.dot(mii, mjj)) / np.abs(e_model1[ii] + e_model2[jj])
            ) ** 2 / (
                (
                    np.vdot(mii, mii) / (2 * np.abs(e_model1[ii].real))
                    + np.abs(np.dot(mii, mii)) / (2 * np.abs(e_model1[ii]))
                )
                * (
                    np.vdot(mjj, mjj) / (2 * np.abs(e_model2[jj].real))
                    + np.abs(np.dot(mjj, mjj)) / (2 * np.abs(e_model2[jj]))
                )
            )
            macxp[ii, jj] = coef.real

    if plot_flag:
        ax = plt.figure().add_subplot()
        im = ax.imshow(macxp, cmap="jet", vmin=0.0, vmax=1.0)
        # create an axes on the right side of ax. The width of cax will be 5%
        # of ax and the padding between cax and ax will be fixed at 0.05 inch.
        divider = make_axes_locatable(ax)
        cax = divider.append_axes("right", size="5%", pad=0.1)
        colorbar = plt.colorbar(im, cax=cax)
        # Loop over data dimensions and create text annotations.
        for i in range(modes):
            for j in range(modes):
                if macxp[i, j] >= threshold:
                    text = ax.text(
                        j,
                        i,
                        "%.2f" % macxp[i, j],
                        ha="center",
                        va="center",
                        color="w",
                        fontsize=8,
                    )
        ax.set_title(f"MACXP criterion at V={v}m/s")
        if figure_name:
            plt.savefig(figure_name)
        plt.close()

    return macxp


def _get_mode_order(macxp, threshold=0.6, dthreashold=0.6):
    """Determine most likely mode numbering based on macxp criterion.
    If the order cannot be determined, the algorithm fails and the velocity
    increment is cut-back.

    Note: had to increase dthreashold to large value (0.6) to ensure plate model
    convergence with 16 modes. TODO: look at other tracking methods.
    """

    modes = macxp.shape[0]
    mode_ids = np.zeros(modes)
    mcounter = 1
    for mode in macxp:
        index = np.argwhere(mode >= threshold)
        if len(index) < 2 or len(index) > 2:
            index = np.argsort(mode)[-2:]
            if mode_ids[index[1]]:
                # this mode has already been alocated a mode_id
                continue
            elif np.abs(mode[index[0]] - threshold) <= dthreashold:
                if DEBUG_MODE_TRACKING_FLAG:
                    print(f"Mode tracking threshold set to {mode[index[0]]}.")
            elif mode[index[0]] - threshold < -dthreashold:
                break
            elif mode[index[0]] - threshold > dthreashold:
                break
        assert len(index) == 2, "Something went wrong here..."
        if not all(mode_ids[index]):
            mode_ids[index] = mcounter
            mcounter += 1

    if all(mode_ids > 0.0) and all(mode_ids <= modes / 2):
        # mode ordering successful
        return mode_ids, True
    else:
        # mode ordering failed
        return mode_ids, False


def _plot_histories(inputs):
    """Plot QOIs y over input range x."""

    for input in inputs:
        ax = plt.figure().add_subplot()
        for index, series in enumerate(input["y"].T):
            ax.plot(
                input["x"],
                series,
                marker="o",
                linestyle="-",
                color=input["colors"][index],
            )
        ax.set_xlabel(input["x_label"])
        ax.set_ylabel(input["y_label"])
        ax.grid(visible=True, which="major", color="#999999", linestyle="-", alpha=0.2)
        plt.savefig(input["fname"])
        plt.close()


if __name__ == "__main__":

    # run tests
    simple_plate_tests()
    parametric_box_tests()
