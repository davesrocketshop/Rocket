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
import numpy as np

from Ui.Commands.Command import Command
from Ui.ViewSolverCalculix import ViewProviderSolverCalculix

# import Fem
import FemGui
import ObjectsFem
from Rocket.fem.StripMesh import StripMesh
from Rocket.fem.FemEigenvalueAnalysis import modal_aeroelastic

def makeSolverCalculixCcxTools(
    doc,
    name="SolverCcxTools"
):
    """makeSolverCalculixCcxTools(document, [name]):
    makes a Calculix solver object for the ccx tools module"""
    obj = doc.addObject("Fem::FemSolverObjectPython", name)
    from femobjects import solver_ccxtools
    solver_ccxtools.SolverCcxTools(obj)
    ViewProviderSolverCalculix(obj.ViewObject)
    obj.EigenmodesCount = 15
    obj.AnalysisType = "frequency"
    return obj

def setFinPlacement(fin):
    fin.AutoDiameter = False
    fin.ParentRadius = 0.0
    doc = FreeCAD.ActiveDocument
    doc.recompute()

    fin.Placement.rotate(FreeCAD.Vector(0,0,0), FreeCAD.Vector(1,0,0), -90.0)
    doc.recompute()

def createAnalysis():
    doc = FreeCAD.ActiveDocument

    analyzer = ObjectsFem.makeAnalysis(doc, 'Analysis')
    FemGui.setActiveAnalysis(analyzer)

    # create a CalculiX ccx tools solver for any new analysis
    makeSolverCalculixCcxTools(doc)
    analyzer.addObject(doc.ActiveObject)

def doFemAnalysis():
    doc = FreeCAD.ActiveDocument

    # See if we have a fin selected
    for fin in FreeCADGui.Selection.getSelection():
        if fin.isDerivedFrom('Part::FeaturePython'):
            if hasattr(fin,"FinType"):
                try:
                    # Orient the fin for analysis
                    setFinPlacement(fin)

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

                    # radius = float(fin.ParentRadius)
                    mesh.Placement = fin.Placement

                    doc.commitTransaction()
                    doc.recompute()

                except TypeError as ex:
                    QtGui.QMessageBox.information(None, "", str(ex))
                    doc.abortTransaction()
                return

    QtGui.QMessageBox.information(None, "", translate('Rocket', "Please select a fin first"))

def inMeters(length):
    return float(length) #/ 1000.0

def doFemAeroelastic():
    doc = FreeCAD.ActiveDocument

    if FemGui.getActiveAnalysis() is None:
        return
    
    for fin in FreeCADGui.Selection.getSelection():
        if fin.isDerivedFrom('Part::FeaturePython'):
            if hasattr(fin,"FinType"):
                try:
                    doc.openTransaction("Create Rocket FEM strip mesh")

                    A = [0,0,0]
                    B = [inMeters(fin.SweepLength), inMeters(fin.Height), 0.0]
                    CA = inMeters(fin.RootChord)
                    CB = inMeters(fin.TipChord)
                    aero_inputs = \
                        {
                            "planform": {"A":A, "B":B, "CA":CA, "CB":CB},
                            "strips": 10,  # number of aero strips along the span >=1
                            "root_alpha": 0,  # AoA at the wing root in degrees
                            "rho": 1.225,  # air density in Pa
                            "V": {
                                "start": 10.0,
                                "end": 250.0,
                                "inc0": 5.0,
                                "inc_min": 0.01,
                            },  # air velocity range in mm/s
                            "mode_tracking_threshold": 0.60,
                            "CL_alpha": 2 * np.pi,  # ideal lift curve slope
                        }
                    
                    print("Starting modal aeroelastic stability analysis.")
                    # run aeroelastic stability analysis over a range of velocities
                    # freq_scipy, V, V_omega, V_damping, flutter, divergence = modal_aeroelastic(
                    #     "dummy", #file=inputs["analysis_file"],
                    #     "dummyFolder", #folder=run_folder,
                    #     # aero_inputs=inputs["modal_aeroelastic_parameters"]["aero_inputs"],
                    #     # box_inputs=inputs,
                    #     # k_modes=inputs["modal_aeroelastic_parameters"]["k_modes"],
                    # )
                    modal_aeroelastic(
                        FemGui.getActiveAnalysis(),
                        aero_inputs
                        # box_inputs=inputs,
                        # k_modes=inputs["modal_aeroelastic_parameters"]["k_modes"],
                    )

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

                    radius = float(fin.ParentRadius)
                    mesh.Placement.Base = FreeCAD.Vector(0.0, 0.0, radius)

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
        return self.hasActiveAnalysisAndFin()
        
    def GetResources(self):
        return {'MenuText': translate("Rocket", 'Fin strip mesh'),
                'ToolTip': translate("Rocket", 'Creates a strip mesh'),
                'Pixmap': FreeCAD.getUserAppDataDir() + "Mod/Rocket/Resources/icons/Rocket_FinFem.svg"}

class CmdFemAeroelastic(Command):
    def Activated(self):
        FreeCADGui.addModule("Ui.Commands.CmdFemAnalysis")
        FreeCADGui.doCommand("Ui.Commands.CmdFemAnalysis.doFemAeroelastic()")

    def IsActive(self):
        # Always available, even without active document
        return self.hasActiveAnalysis()
        
    def GetResources(self):
        return {'MenuText': translate("Rocket", 'Fin Aeroelastic Analysis'),
                'ToolTip': translate("Rocket", 'Runs an aeroelastic analysis'),
                'Pixmap': FreeCAD.getUserAppDataDir() + "Mod/Rocket/Resources/icons/Rocket_FinFlutter.svg"}
