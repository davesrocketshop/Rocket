# ***************************************************************************
# *   Copyright (c) 2021 David Carter <dcarter@davidcarter.ca>              *
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
"""Class for calculating fin flutter using FEM"""

__title__ = "FreeCAD FEM Analyzer"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"
    
import FreeCAD
import FreeCADGui

from DraftTools import translate

from PySide import QtGui

from Ui.DialogFinFlutter import DialogFinFlutter
from Ui.Commands.Command import Command

import FemGui
import ObjectsFem
from App.fem.Gmsh import RocketGmsh

def createAnalysis():
    doc = FreeCAD.ActiveDocument

    analyzer = ObjectsFem.makeAnalysis(doc, 'Analysis')
    FemGui.setActiveAnalysis(analyzer)

    # create a CalculiX ccx tools solver for any new analysis
    ObjectsFem.makeSolverCalculixCcxTools(doc)
    analyzer.addObject(doc.ActiveObject)

def doFemAnalysis():
    doc = FreeCAD.ActiveDocument

    print("0")
    # See if we have a fin selected
    for fin in FreeCADGui.Selection.getSelection():
        if fin.isDerivedFrom('Part::FeaturePython'):
            if hasattr(fin,"FinType"):
                try:
                    print("1")
                    # a mesh could be made with and without an analysis,
                    # we're going to check not for an analysis in command manager module
                    doc.openTransaction("Create FEM mesh by Gmsh")
                    if FemGui.getActiveAnalysis() is None:
                        createAnalysis()

                    print("2")
                    mesh_obj_name = fin.Name + "_Mesh" #"FEMMeshGmsh"
                    # if requested by some people add Preference for this
                    # mesh_obj_name = self.selobj.Name + "_Mesh"
                    mesh = ObjectsFem.makeMeshGmsh(doc, mesh_obj_name)
                    doc.ActiveObject.Part = fin

                    print("3")
                    # Gmsh mesh object could be added without an active analysis
                    # but if there is an active analysis move it in there
                    if FemGui.getActiveAnalysis():
                        FemGui.getActiveAnalysis().addObject(doc.ActiveObject)

                    FreeCADGui.Selection.clearSelection()
                    doc.recompute()

                    print("4")
                    fin.ViewObject.Visibility = False
                    doc.recompute()

                    print("5")
                    gmsh_mesh = RocketGmsh(mesh)
                    error = gmsh_mesh.create_mesh()
                    print("6")
                    print(error)
                    doc.recompute()

                except TypeError as ex:
                    QtGui.QMessageBox.information(None, "", str(ex))
                    print("7")
                return

    QtGui.QMessageBox.information(None, "", translate('Rocket', "Please select a fin first"))

class CmdFemAnalysis(Command):
    def Activated(self):
        print("0.1")
        FreeCADGui.addModule("Ui.Commands.CmdFemAnalysis")
        FreeCADGui.doCommand("Ui.Commands.CmdFemAnalysis.doFemAnalysis()")

    def IsActive(self):
        # Always available, even without active document
        return self.part_fin_selected()
        
    def GetResources(self):
        return {'MenuText': translate("Rocket", 'Fin FEM Analysis'),
                'ToolTip': translate("Rocket", 'Fin FEM Analysis'),
                'Pixmap': FreeCAD.getUserAppDataDir() + "Mod/Rocket/Resources/icons/Rocket_FinFem.svg"}
