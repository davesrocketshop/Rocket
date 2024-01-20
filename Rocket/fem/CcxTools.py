# ***************************************************************************
# *   Copyright (c) 2015 Przemo Firszt <przemo@firszt.eu>                   *
# *   Copyright (c) 2016 Bernd Hahnebach <bernd@bimstatik.org>              *
# *                                                                         *
# *   This file is part of the FreeCAD CAx development system.              *
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

__title__ = "FemToolsCcx"
__author__ = "Przemo Firszt, Bernd Hahnebach"
__url__ = "https://www.freecad.org"

## \addtogroup FEM
#  @{

import os
import sys
import subprocess

import FreeCAD

from femtools import femutils
from femtools import membertools
from femtools.ccxtools import FemToolsCcx

from PySide import QtCore  # there might be a special reason this is not guarded ?!?
if FreeCAD.GuiUp:
    from PySide import QtGui
    import FemGui


class RocketFemToolsCcx(FemToolsCcx):
    """

    Attributes
    ----------
    analysis : Fem::FemAnalysis
        FEM group analysis object
        has to be present, will be set in __init__
    solver : Fem::FemSolverObjectPython
        FEM solver object
        has to be present, will be set in __init__
    base_name : str
        name of .inp/.frd file (without extension)
        It is used to construct .inp file path that is passed to CalculiX ccx
    ccx_binary : str
    working_dir : str
    results_present : bool
        indicating if there are calculation results ready for us
    members : class femtools/membertools/AnalysisMember
        contains references to all analysis member except solvers and mesh
        Updated with update_objects
    """

    def __init__(self, analysis=None, solver=None, test_mode=False):
        """The constructor

        Parameters
        ----------
        analysis : Fem::FemAnalysis, optional
            analysis group as a container for all  objects needed for the analysis
        solver : Fem::FemSolverObjectPython, optional
            solver object to be used for this solve
        test_mode : bool, optional
            mainly used in unit tests
        """
        super().__init__(analysis, solver, test_mode)

    def write_inp_file(self):

        # get mesh set data
        # TODO use separate method for getting the mesh set data
        from femmesh import meshsetsgetter
        meshdatagetter = meshsetsgetter.MeshSetsGetter(
            self.analysis,
            self.solver,
            self.mesh,
            membertools.AnalysisMember(self.analysis),
        )
        # save the sets into the member objects of the instanz meshdatagetter
        meshdatagetter.get_mesh_sets()

        # write input file
        import Rocket.fem.FemInputWriter as iw
        self.inp_file_name = ""
        try:
            inp_writer = iw.FemInputWriterCcx(
                self.analysis,
                self.solver,
                self.mesh,
                meshdatagetter.member,
                self.working_dir,
                meshdatagetter.mat_geo_sets
            )
            self.inp_file_name = inp_writer.write_solver_input()
        except Exception:
            FreeCAD.Console.PrintError(
                "Unexpected error when writing CalculiX input file: {}\n"
                .format(sys.exc_info()[1])
            )
            raise

    def load_results(self):
        FreeCAD.Console.PrintMessage("\n")  # because of time print in separate line
        FreeCAD.Console.PrintMessage("CalculiX read results...\n")
        self.results_present = False
        # self.load_results_ccxfrd()
        self.load_results_ccxdat()
        self.load_results_cxxsti()
        self.load_results_cxxmas()
        self.analysis.Document.recompute()

    def load_results_cxxsti(self):
        sti_result_file = os.path.splitext(self.inp_file_name)[0] + ".sti"
        sti_content = None

        if os.path.isfile(sti_result_file):
            sti_file = open(sti_result_file, "r")
            sti_content = sti_file.read()
            sti_file.close()
        else:
            FreeCAD.Console.PrintError(
                "FEM: No sti result file found at {}\n"
                .format(sti_result_file)
            )

        if sti_content:
            sti_text_obj = self.analysis.Document.addObject("App::TextDocument", "ccx_sti_file")
            sti_text_obj.Text = sti_content
            sti_text_obj.setPropertyStatus("Text", "ReadOnly")  # set property editor readonly
            if FreeCAD.GuiUp:
                sti_text_obj.ViewObject.ReadOnly = True  # set editor view readonly
            self.analysis.addObject(sti_text_obj)

    def load_results_cxxmas(self):
        mas_result_file = os.path.splitext(self.inp_file_name)[0] + ".mas"
        mas_content = None

        if os.path.isfile(mas_result_file):
            mas_file = open(mas_result_file, "r")
            mas_content = mas_file.read()
            mas_file.close()
        else:
            FreeCAD.Console.PrintError(
                "FEM: No mas result file found at {}\n"
                .format(mas_result_file)
            )

        if mas_content:
            mas_text_obj = self.analysis.Document.addObject("App::TextDocument", "ccx_mas_file")
            mas_text_obj.Text = mas_content
            mas_text_obj.setPropertyStatus("Text", "ReadOnly")  # set property editor readonly
            if FreeCAD.GuiUp:
                mas_text_obj.ViewObject.ReadOnly = True  # set editor view readonly
            self.analysis.addObject(mas_text_obj)


class CcxTools(RocketFemToolsCcx):

    def __init__(self, solver=None):
        FemToolsCcx.__init__(self, None, solver)

##  @}