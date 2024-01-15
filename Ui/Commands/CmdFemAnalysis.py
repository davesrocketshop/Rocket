# ***************************************************************************
# *   Copyright (c) 2021-2024 David Carter <dcarter@davidcarter.ca>         *
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

from Ui.Commands.Command import Command

import FemGui
import ObjectsFem
from Rocket.fem.StripMesh import StripMesh

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
                    doc.openTransaction("Create Rocket FEM Analysis object")
                    if FemGui.getActiveAnalysis() is None:
                        createAnalysis()

                    # Set material type
                    FemGui.getActiveAnalysis().addObject(ObjectsFem.makeMaterialSolid(FreeCAD.ActiveDocument))
                    FreeCADGui.Selection.clearSelection()
                    FreeCADGui.ActiveDocument.setEdit(FreeCAD.ActiveDocument.ActiveObject.Name)

                    # mesh_obj_name = fin.Name + "_Mesh" #"FEMMeshGmsh"
                    # # if requested by some people add Preference for this
                    # # mesh_obj_name = self.selobj.Name + "_Mesh"
                    # mesh = ObjectsFem.makeMeshGmsh(doc, mesh_obj_name)
                    # doc.ActiveObject.Part = fin

                    # # Gmsh mesh object could be added without an active analysis
                    # # but if there is an active analysis move it in there
                    # if FemGui.getActiveAnalysis():
                    #     FemGui.getActiveAnalysis().addObject(doc.ActiveObject)

                    # FreeCADGui.Selection.clearSelection()
                    # doc.recompute()

                    # fin.ViewObject.Visibility = False
                    # doc.recompute()

                    # gmsh_mesh = RocketGmsh(mesh, FemGui.getActiveAnalysis())
                    # error = gmsh_mesh.create_mesh()
                    doc.commitTransaction()
                    doc.recompute()

                except TypeError as ex:
                    QtGui.QMessageBox.information(None, "", str(ex))
                    doc.abortTransaction()
                return

    QtGui.QMessageBox.information(None, "", translate('Rocket', "Please select a fin first"))

def doFemRootConstraint():
    doc = FreeCAD.ActiveDocument

    if FemGui.getActiveAnalysis() is None:
        return
    
    doc.openTransaction("Create Rocket FEM root constraint")
    constraint = doc.addObject("Fem::ConstraintFixed","FixedRoot")
    constraint.Scale = 1
    FemGui.getActiveAnalysis().addObject(constraint)

#     // OvG: Hide meshes and show parts
#     doCommand(Doc, "%s", gethideMeshShowPartStr(FeatName).c_str());

#     updateActive();

    FreeCADGui.activeDocument().setEdit(doc.ActiveObject.Name, 0)
    doc.commitTransaction()

def makeMesh(doc, name="FemMesh"):
    """makeMesh(document, [name]): makes a FEM mesh object"""
    obj = doc.addObject("Fem::FemMeshObjectPython", name)
    from femobjects import mesh_gmsh
    mesh_gmsh.MeshGmsh(obj)
    if FreeCAD.GuiUp:
        from femviewprovider import view_mesh_gmsh
        view_mesh_gmsh.VPMeshGmsh(obj.ViewObject)
    return obj

def doFemStripMesh():
    doc = FreeCAD.ActiveDocument

    if FemGui.getActiveAnalysis() is None:
        return
    
    for fin in FreeCADGui.Selection.getSelection():
        if fin.isDerivedFrom('Part::FeaturePython'):
            if hasattr(fin,"FinType"):
                try:
                    doc.openTransaction("Create Rocket FEM strip mesh")

                    mesh_obj_name = fin.Name + "_Mesh"
                    # if requested by some people add Preference for this
                    # mesh_obj_name = self.selobj.Name + "_Mesh"
                    # mesh = ObjectsFem.makeMeshGmsh(doc, mesh_obj_name)
                    mesh = makeMesh(doc, mesh_obj_name)
                    # mesh = doc.addObject("Fem::FemMeshObjectPython", mesh_obj_name)
                    # gmsh_mesh = StripMesh(mesh, FemGui.getActiveAnalysis())
                    # doc.ActiveObject.Part = fin
                    mesh.Part = fin

                    # Mesh object could be added without an active analysis
                    # but if there is an active analysis move it in there
                    if FemGui.getActiveAnalysis():
                        FemGui.getActiveAnalysis().addObject(mesh)

                    FreeCADGui.Selection.clearSelection()
                    doc.recompute()

                    fin.ViewObject.Visibility = False
                    doc.recompute()

                    strip_mesh = StripMesh(mesh, FemGui.getActiveAnalysis())
                    error = strip_mesh.create_mesh()
                    print(error)
                    doc.commitTransaction()
                    doc.recompute()

                except TypeError as ex:
                    QtGui.QMessageBox.information(None, "", str(ex))
                    doc.abortTransaction()
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
                'ToolTip': translate("Rocket", 'Fin FEM Analysis'),
                'Pixmap': FreeCAD.getUserAppDataDir() + "Mod/Rocket/Resources/icons/Rocket_FinFem.svg"}

class CmdFemRootConstraint(Command):
    def Activated(self):
        FreeCADGui.addModule("Ui.Commands.CmdFemAnalysis")
        FreeCADGui.doCommand("Ui.Commands.CmdFemAnalysis.doFemRootConstraint()")

    def IsActive(self):
        # Always available, even without active document
        return self.hasActiveAnalysis()
        
    def GetResources(self):
        return {'MenuText': translate("Rocket", 'Fin Root fixed boundary condition'),
                'ToolTip': translate("Rocket", 'Creates a fixed boundary condition for the fin root'),
                'Pixmap': FreeCAD.getUserAppDataDir() + "Mod/Rocket/Resources/icons/Rocket_FinFem.svg"}

class CmdFemStripMesh(Command):
    def Activated(self):
        FreeCADGui.addModule("Ui.Commands.CmdFemAnalysis")
        FreeCADGui.doCommand("Ui.Commands.CmdFemAnalysis.doFemStripMesh()")

    def IsActive(self):
        # Always available, even without active document
        return self.hasActiveAnalysis()
        
    def GetResources(self):
        return {'MenuText': translate("Rocket", 'Fin strip mesh'),
                'ToolTip': translate("Rocket", 'Creates a strip mesh'),
                'Pixmap': FreeCAD.getUserAppDataDir() + "Mod/Rocket/Resources/icons/Rocket_FinFem.svg"}

# class _MaterialSolid(CommandManager):
#     "The FEM_MaterialSolid command definition"

#     def __init__(self):
#         super(_MaterialSolid, self).__init__()
#         self.menutext = Qt.QT_TRANSLATE_NOOP(
#             "FEM_MaterialSolid",
#             "Material for solid"
#         )
#         self.accel = "M, S"
#         self.tooltip = Qt.QT_TRANSLATE_NOOP(
#             "FEM_MaterialSolid",
#             "Creates a FEM material for solid"
#         )
#         self.is_active = "with_analysis"
#         self.do_activated = "add_obj_on_gui_set_edit"

# class _SolverControl(CommandManager):
#     "The FEM_SolverControl command definition"

#     def __init__(self):
#         super(_SolverControl, self).__init__()
#         self.menutext = Qt.QT_TRANSLATE_NOOP(
#             "FEM_SolverControl",
#             "Solver job control"
#         )
#         self.accel = "S, T"
#         self.tooltip = Qt.QT_TRANSLATE_NOOP(
#             "FEM_SolverControl",
#             "Changes solver attributes and runs the calculations for the selected solver"
#         )
#         self.is_active = "with_solver"

#     def Activated(self):
#         FreeCADGui.ActiveDocument.setEdit(self.selobj, 0)
