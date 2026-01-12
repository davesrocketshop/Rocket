# SPDX-License-Identifier: LGPL-2.1-or-later
# SPDX-File-Notice: Part of the Rocket addon.

################################################################################
#                                                                              #
#   © 2021 David Carter <dcarter@davidcarter.ca>                               #
#                                                                              #
#   This addon is free software: you can redistribute it and/or modify         #
#   it under the terms of the GNU Lesser General Public License as             #
#   published by the Free Software Foundation, either version 2.1              #
#   of the License, or (at your option) any later version.                     #
#                                                                              #
#   This addon is distributed in the hope that it will be useful,              #
#   but WITHOUT ANY WARRANTY; without even the implied warranty                #
#   of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.                    #
#   See the GNU Lesser General Public License for more details.                #
#                                                                              #
#   You should have received a copy of the GNU Lesser General Public           #
#   License along with this addon. If not, see https://www.gnu.org/licenses    #
#                                                                              #
################################################################################


"""Class for calculating fin flutter using FEM"""

__title__ = "FreeCAD FEM Analyzer"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

import FreeCAD
import FreeCADGui

translate = FreeCAD.Qt.translate

from PySide import QtGui

from Ui.Commands.Command import Command

import FemGui
import ObjectsFem
from Rocket.fem.Gmsh import RocketGmsh

def createAnalysis():
    doc = FreeCAD.ActiveDocument

    analyzer = ObjectsFem.makeAnalysis(doc, 'Analysis')
    FemGui.setActiveAnalysis(analyzer)

    # create a CalculiX ccx tools solver for any new analysis
    ObjectsFem.makeSolverCalculixCcxTools(doc)
    analyzer.addObject(doc.ActiveObject)

def doFemAnalysis():
    doc = FreeCAD.ActiveDocument

    # See if we have a fin selected
    for fin in FreeCADGui.Selection.getSelection():
        if fin.isDerivedFrom('Part::FeaturePython'):
            if hasattr(fin,"FinType"):
                try:
                    # a mesh could be made with and without an analysis,
                    # we're going to check not for an analysis in command manager module
                    doc.openTransaction("Create FEM mesh by Gmsh")
                    if FemGui.getActiveAnalysis() is None:
                        createAnalysis()

                    mesh_obj_name = fin.Name + "_Mesh" #"FEMMeshGmsh"
                    # if requested by some people add Preference for this
                    # mesh_obj_name = self.selobj.Name + "_Mesh"
                    mesh = ObjectsFem.makeMeshGmsh(doc, mesh_obj_name)
                    doc.ActiveObject.Part = fin

                    # Gmsh mesh object could be added without an active analysis
                    # but if there is an active analysis move it in there
                    if FemGui.getActiveAnalysis():
                        FemGui.getActiveAnalysis().addObject(doc.ActiveObject)

                    FreeCADGui.Selection.clearSelection()
                    doc.recompute()

                    fin.ViewObject.Visibility = False
                    doc.recompute()

                    gmsh_mesh = RocketGmsh(mesh)
                    error = gmsh_mesh.create_mesh()
                    FreeCAD.ActiveDocument.commitTransaction()
                    doc.recompute()

                except TypeError as ex:
                    FreeCAD.ActiveDocument.abortTransaction()
                    QtGui.QMessageBox.information(None, "", str(ex))
                return

    QtGui.QMessageBox.information(None, "", translate('Rocket', "Please select a fin first"))

class CmdFemAnalysis(Command):
    def Activated(self):
        FreeCADGui.addModule("Ui.Commands.CmdFemAnalysis")
        FreeCADGui.doCommand("Ui.Commands.CmdFemAnalysis.doFemAnalysis()")

    def IsActive(self):
        # Always available, even without active document
        return self.partFinSelected()

    def GetResources(self):
        return {'MenuText': translate("Rocket", 'Fin FEM Analysis'),
                'ToolTip': translate("Rocket", 'Performs a FEM analysis of the selected fin'),
                'Pixmap': FreeCAD.getUserAppDataDir() + "Mod/Rocket/Resources/icons/Rocket_FinFem.svg"}
