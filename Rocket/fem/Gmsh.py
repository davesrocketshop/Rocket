# ***************************************************************************
# *   Copyright (c) 2021-2025 David Carter <dcarter@davidcarter.ca>         *
# *                                                                         *
# *   This program is free software; you can redistribute it and/or modify  *
# *   it under the terms of the GNU Lesser General Public License (LGPL)    *
# *   as published by the Free Software Foundation; either version 2 of     *
# *   the License, or (at your option) any later version.                   *
# *   for detail see the LICENCE text file.                                 *
# *                                                                         *
# *   This program is distributed in the hope that it will be useful,       *
# *   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
# *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
# *   GNU Library General Public License for more details.                  *
# *                                                                         *
# *   You should have received a copy of the GNU Library General Public     *
# *   License along with this program; if not, write to the Free Software   *
# *   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  *
# *   USA                                                                   *
# *                                                                         *
# ***************************************************************************
"""Class for generating FEM meshes"""

__title__ = "FreeCAD FEM Mesh"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

import os

from Rocket.Utilities import translate

from femmesh.gmshtools import GmshTools, GmshError

class RocketGmsh(GmshTools):

    def __init__(self, gmsh_mesh_obj, analysis=None):
        super().__init__(gmsh_mesh_obj, analysis)

    def create_mesh(self):
        error = ""
        try:
            self.update_mesh_data()
            self.get_tmp_file_paths()
            self.get_gmsh_command()
            self.write_gmsh_input_files()
            error = self.run_gmsh_with_geo()
            self.read_and_set_new_mesh()
        except GmshError as e:
            error = str(e)
        return error

    def write_geo(self):
        geo = open(self.temp_file_geo, "w")
        geo.write("// geo file for meshing with Gmsh meshing software created by FreeCAD Rocket Workbench\n")
        geo.write("\n")

        cpu_count = os.cpu_count()
        if cpu_count is not None and cpu_count > 1:
            geo.write("// enable multi-core processing\n")
            geo.write(f"General.NumThreads = {cpu_count};\n")
            geo.write("\n")

        geo.write("// open brep geometry\n")
        # explicit use double quotes in geo file
        geo.write('Merge "{}";\n'.format(self.temp_file_geometry))
        geo.write("\n")

        # groups
        self.write_groups(geo)

        # Characteristic Length of the elements
        geo.write("// Characteristic Length\n")
        if self.ele_length_map:
            # we use the index FreeCAD which starts with 0
            # we need to add 1 for the index in Gmsh
            geo.write("// Characteristic Length according CharacteristicLengthMap\n")
            for e in self.ele_length_map:
                ele_nodes = (
                    "".join((str(n + 1) + ", ") for n in self.ele_node_map[e])
                ).rstrip(", ")
                geo.write("// " + e + "\n")
                elestr1 = "{"
                elestr2 = "}"
                geo.write(
                    "Characteristic Length {} {} {} = {};\n"
                    .format(
                        elestr1,
                        ele_nodes,
                        elestr2,
                        self.ele_length_map[e]
                    )
                )
            geo.write("\n")

        # boundary layer generation may need special setup
        # of Gmsh properties, set them in Gmsh TaskPanel
        self.write_boundary_layer(geo)

        # mesh parameter
        geo.write("// min, max Characteristic Length\n")
        geo.write("Mesh.CharacteristicLengthMax = " + str(self.clmax) + ";\n")
        if len(self.bl_setting_list):
            # if minLength must smaller than first layer of boundary_layer
            # it is safer to set it as zero (default value) to avoid error
            geo.write("Mesh.CharacteristicLengthMin = " + str(0) + ";\n")
        else:
            geo.write("Mesh.CharacteristicLengthMin = " + str(self.clmin) + ";\n")
        if hasattr(self.mesh_obj, "MeshSizeFromCurvature"):
            geo.write(
                "Mesh.MeshSizeFromCurvature = {}"
                "; // number of elements per 2*pi radians, 0 to deactivate\n"
                .format(self.mesh_obj.MeshSizeFromCurvature)
            )
        geo.write("\n")
        # if hasattr(self.mesh_obj, "RecombineAll") and self.mesh_obj.RecombineAll is True:
        #     geo.write("// recombination for surfaces\n")
        #     geo.write("Mesh.RecombineAll = 1;\n")
        # if hasattr(self.mesh_obj, "Recombine3DAll") and self.mesh_obj.Recombine3DAll is True:
        #     geo.write("// recombination for volumes\n")
        #     geo.write("Mesh.Recombine3DAll = 1;\n")
        # if (
        #     (hasattr(self.mesh_obj, "RecombineAll") and self.mesh_obj.RecombineAll is True)
        #     or (hasattr(self.mesh_obj, "Recombine3DAll") and self.mesh_obj.Recombine3DAll is True)
        # ):
        #     geo.write("// recombination algorithm\n")
        #     geo.write("Mesh.RecombinationAlgorithm = " + self.RecombinationAlgorithm + ";\n")
        #     geo.write("\n")
        geo.write("// recombination for surfaces\n")
        geo.write("Mesh.RecombineAll = 1;\n")
        geo.write("// recombination for volumes\n")
        geo.write("Mesh.Recombine3DAll = 1;\n")
        geo.write("// recombination algorithm\n")
        geo.write("Mesh.RecombinationAlgorithm = 1; // Blossom\n")
        geo.write("\n")

        geo.write("// optimize the mesh\n")
        # Gmsh tetra optimizer
        # if hasattr(self.mesh_obj, "OptimizeStd") and self.mesh_obj.OptimizeStd is True:
        #     geo.write("Mesh.Optimize = 1;\n")
        # else:
        #     geo.write("Mesh.Optimize = 0;\n")
        geo.write("Mesh.Optimize = 0;\n")
        # Netgen optimizer in Gmsh
        if hasattr(self.mesh_obj, "OptimizeNetgen") and self.mesh_obj.OptimizeNetgen is True:
            geo.write("Mesh.OptimizeNetgen = 1;\n")
        else:
            geo.write("Mesh.OptimizeNetgen = 0;\n")
        # higher order mesh optimizing
        geo.write(
            "// High-order meshes optimization (0=none, 1=optimization, 2=elastic+optimization, "
            "3=elastic, 4=fast curving)\n"
        )
        geo.write("Mesh.HighOrderOptimize = " + self.HighOrderOptimize + ";\n")
        geo.write("\n")

        geo.write("// mesh order\n")
        geo.write("Mesh.ElementOrder = " + self.order + ";\n")
        if self.order == "2":
            if (
                hasattr(self.mesh_obj, "SecondOrderLinear")
                and self.mesh_obj.SecondOrderLinear is True
            ):
                geo.write(
                    "Mesh.SecondOrderLinear = 1; // Second order nodes are created "
                    "by linear interpolation instead by curvilinear\n"
                )
            else:
                geo.write(
                    "Mesh.SecondOrderLinear = 0; // Second order nodes are created "
                    "by linear interpolation instead by curvilinear\n"
                )
        geo.write("\n")

        geo.write(
            "// mesh algorithm, only a few algorithms are "
            "usable with 3D boundary layer generation\n"
        )
        geo.write(
            "// 2D mesh algorithm (1=MeshAdapt, 2=Automatic, "
            "5=Delaunay, 6=Frontal, 7=BAMG, 8=DelQuad, 9=Packing Parallelograms)\n"
        )
        # if len(self.bl_setting_list) and self.dimension == 3:
        #     geo.write("Mesh.Algorithm = " + "DelQuad" + ";\n")  # Frontal/DelQuad are tested
        # else:
        #     geo.write("Mesh.Algorithm = " + self.algorithm2D + ";\n")
        geo.write("Mesh.Algorithm = 8;\n")  # Frontal/DelQuad are tested
        geo.write(
            "// 3D mesh algorithm (1=Delaunay, 2=New Delaunay, 4=Frontal, "
            "7=MMG3D, 9=R-tree, 10=HTX)\n"
        )
        geo.write("Mesh.Algorithm3D = " + self.algorithm3D + ";\n")
        geo.write("\n")

        geo.write("// meshing\n")
        # remove duplicate vertices
        # see https://forum.freecadweb.org/viewtopic.php?f=18&t=21571&start=20#p179443
        if hasattr(self.mesh_obj, "CoherenceMesh") and self.mesh_obj.CoherenceMesh is True:
            geo.write(
                "Geometry.Tolerance = {}; // set geometrical "
                "tolerance (also used for merging nodes)\n"
                .format(self.geotol)
            )
            geo.write("Mesh  " + self.dimension + ";\n")
            geo.write("Coherence Mesh; // Remove duplicate vertices\n")
        else:
            geo.write("Mesh  " + self.dimension + ";\n")
        geo.write("\n")

        # save mesh
        geo.write("// save\n")
        geo.write("Mesh.Format = 2;\n")  # unv
        if self.group_elements and self.group_nodes_export:
            geo.write("// For each group save not only the elements but the nodes too.;\n")
            geo.write("Mesh.SaveGroupsOfNodes = 1;\n")
            # belongs to Mesh.SaveAll but only needed if there are groups
            geo.write(
                "// Needed for Group meshing too, because "
                "for one material there is no group defined;\n")
        geo.write("// Ignore Physical definitions and save all elements;\n")
        geo.write("Mesh.SaveAll = 1;\n")
        # explicit use double quotes in geo file
        geo.write('Save "{}";\n'.format(self.temp_file_mesh))
        geo.write("\n\n")

        # some useful information
        geo.write("// " + "*" * 70 + "\n")
        geo.write("// Gmsh documentation:\n")
        geo.write("// https://gmsh.info/doc/texinfo/gmsh.html#Mesh\n")
        geo.write("//\n")
        geo.write(
            "// We do not check if something went wrong, like negative "
            "jacobians etc. You can run Gmsh manually yourself: \n"
        )
        geo.write("//\n")
        geo.write("// to see full Gmsh log, run in bash:\n")
        geo.write("// " + self.gmsh_bin + " - " + self.temp_file_geo + "\n")
        geo.write("//\n")
        geo.write("// to run Gmsh and keep file in Gmsh GUI (with log), run in bash:\n")
        geo.write("// " + self.gmsh_bin + " " + self.temp_file_geo + "\n")
        geo.close()
