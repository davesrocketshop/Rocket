# ***************************************************************************
# *   Copyright (c) 2024 David Carter <dcarter@davidcarter.ca>              *
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
"""Class for CFD Analyzer"""

__title__ = "FreeCAD CFD Analyzer"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

import FreeCAD
import FreeCADGui
import os
import math

from DraftTools import translate

from PySide import QtGui, QtCore
from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QGridLayout

from CfdOF.Mesh import CfdMesh, CfdMeshRefinement
from CfdOF import CfdAnalysis, CfdTools
from CfdOF.Solve import CfdPhysicsSelection, CfdFluidBoundary, CfdFluidMaterial, CfdInitialiseFlowField, CfdSolverFoam

from Rocket.cfd.CFDUtil import caliber, createSolid, makeCFDRocket, makeWindTunnel

from Ui.UIPaths import getUIPath

class TaskPanelCFD(QtCore.QObject):

    def __init__(self, rocket):
        super().__init__()

        self._rocket = rocket

        self.form = FreeCADGui.PySideUic.loadUi(os.path.join(getUIPath(), 'Resources', 'ui', "DialogCFD.ui"))
        # self.form = FreeCADGui.PySideUic.loadUi(':/ui/DialogCFD.ui')

        self._studies = (translate("Rocket", "Coarse"),
                         translate("Rocket", "Fine"),
                         )
        self.form.comboStudy.addItems(self._studies)

        self.form.buttonCreate.clicked.connect(self.onCreate)

        FreeCAD.setActiveTransaction("Create Rocket CFD Study")
        self.initialize()

    def initialize(self):
        # Set Nproc to the number of available threads
        if hasattr(os, "sched_getaffinity"):
            self.form.spinNproc.setValue(len(os.sched_getaffinity(0)))
        else:
            self.form.spinNproc.setValue(os.cpu_count())

        self._solid = createSolid(self._rocket)
        diameter = caliber(self._rocket)
        box = self._solid.BoundBox
        length = box.XLength

        self.form.inputLength.setText(str(length))
        self.form.inputDiameter.setText(str(diameter))

        self._CFDrocket = None
        self._refinement0 = None
        self._refinement1 = None
        self._refinement2 = None


    def onCreate(self):
        self.makeSolid()
        self.makeWindTunnel()
        self.makeAnalysisContainer()
        self.makeCfdMesh()
        self.makeBoundaryConstraints()
        self.adjustPhysicsModel()
        self.adjustFluidProperties()
        self.adjustInitializeFields()
        self.adjustCFDSolver()

        # Don't try to make things twice
        self.form.buttonCreate.setEnabled(False)

    def accept(self):
        self.deactivate()
        FreeCAD.closeActiveTransaction()
        return True

    def reject(self):
        self.deactivate()
        FreeCAD.closeActiveTransaction(True)
        return True

    def deactivate(self):
        if FreeCADGui.Control.activeDialog():
            FreeCADGui.Control.closeDialog()

    def makeSolid(self):
        self._CFDrocket = makeCFDRocket()
        self._CFDrocket._obj.Shape = self._solid

    def makeWindTunnel(self):
        diameter = FreeCAD.Units.Quantity(self.form.inputDiameter.text()).Value
        length = FreeCAD.Units.Quantity(self.form.inputLength.text()).Value

        # Get a blockage ratio of 0.1%
        area = (diameter * diameter) / 0.001
        tunnelDiameter = math.sqrt(area)
        self._outer = makeWindTunnel('WindTunnel', tunnelDiameter, 10.0 * length, 2.0 * length)
        self._refinement0 = makeWindTunnel('Refinement', tunnelDiameter * 0.25, 3.5 * length, 0.5 * length)
        self._refinement1 = makeWindTunnel('Refinement', tunnelDiameter * 0.5, 9.0 * length, 1.0 * length)
        self._refinement2 = makeWindTunnel('Refinement', tunnelDiameter * 0.75, 9.5 * length, 1.5 * length)
        # FreeCADGui.doCommand("Ui.Commands.CmdCFDAnalysis.makeWindTunnel('WindTunnel',{},{},{})".format(tunnelDiameter, 10.0 * length, 2.0 * length))
        # FreeCADGui.doCommand("Ui.Commands.CmdCFDAnalysis.makeWindTunnel('Refinement',{},{},{})".format(tunnelDiameter * 0.25, 3.5 * length, 0.5 * length))
        # FreeCADGui.doCommand("Ui.Commands.CmdCFDAnalysis.makeWindTunnel('Refinement',{},{},{})".format(tunnelDiameter * 0.5, 9.0 * length, 1.0 * length))
        # FreeCADGui.doCommand("Ui.Commands.CmdCFDAnalysis.makeWindTunnel('Refinement',{},{},{})".format(tunnelDiameter * 0.75, 9.5 * length, 1.5 * length))
        FreeCAD.ActiveDocument.recompute()

        self.makeCompound()
        FreeCAD.ActiveDocument.recompute()

        self._rocket._obj.ViewObject.Visibility = False
        FreeCAD.ActiveDocument.recompute()

    def makeCompound(self):
        self._compound = FreeCAD.activeDocument().addObject("Part::Compound", "WindTunnelCompund")
        self._compound.Links = [self._CFDrocket._obj, self._outer._obj]
        self._compound.ViewObject.Transparency = 70

    def makeAnalysisContainer(self):
        analysis = CfdAnalysis.makeCfdAnalysis('CfdAnalysis')
        CfdTools.setActiveAnalysis(analysis)

        # Objects ordered according to expected workflow
        # Add physics object when CfdAnalysis container is created
        self._physicsModel = CfdPhysicsSelection.makeCfdPhysicsSelection()
        analysis.addObject(self._physicsModel)

        # Add fluid properties object when CfdAnalysis container is created
        self._fluidProperties = CfdFluidMaterial.makeCfdFluidMaterial('FluidProperties')
        analysis.addObject(self._fluidProperties)

        # Add initialisation object when CfdAnalysis container is created
        self._initializeFields = CfdInitialiseFlowField.makeCfdInitialFlowField()
        analysis.addObject(self._initializeFields)

        # Add solver object when CfdAnalysis container is created
        self._solver = CfdSolverFoam.makeCfdSolverFoam()
        analysis.addObject(self._solver)
        FreeCAD.ActiveDocument.recompute()

    def makeCfdMesh(self):
        self._CFDMesh = CfdMesh.makeCfdMesh('WindTunnelCompund_Mesh')
        self._CFDMesh.CharacteristicLengthMax = 100.0 # 100 mm
        FreeCAD.ActiveDocument.ActiveObject.Part = self._compound
        CfdTools.getActiveAnalysis().addObject(FreeCAD.ActiveDocument.ActiveObject)
        FreeCAD.ActiveDocument.recompute()

        # Progressive volume refinements
        refinement = CfdMeshRefinement.makeCfdMeshRefinement(self._CFDMesh, 'VolumeRefinement')
        refinement.ShapeRefs = [self._refinement0._obj, ('Solid1', )]
        refinement.Internal = True
        refinement.RelativeLength = 0.125
        FreeCAD.ActiveDocument.recompute()

        refinement = CfdMeshRefinement.makeCfdMeshRefinement(self._CFDMesh, 'VolumeRefinement')
        refinement.ShapeRefs = [self._refinement1._obj, ('Solid1', )]
        refinement.Internal = True
        refinement.RelativeLength = 0.250
        FreeCAD.ActiveDocument.recompute()

        refinement = CfdMeshRefinement.makeCfdMeshRefinement(self._CFDMesh, 'VolumeRefinement')
        refinement.ShapeRefs = [self._refinement2._obj, ('Solid1', )]
        refinement.Internal = True
        refinement.RelativeLength = 0.500
        FreeCAD.ActiveDocument.recompute()

        # Surface refinement
        refinement = CfdMeshRefinement.makeCfdMeshRefinement(self._CFDMesh, 'SurfaceRefinement')
        refinement.ShapeRefs = [self._CFDrocket._obj, ('', )]
        refinement.RelativeLength = 0.0625
        refinement.RefinementThickness = '10.0 mm'
        FreeCAD.ActiveDocument.recompute()

    def makeBoundaryConstraints(self):
        length = len(self._compound.Shape.Faces)
        self._inlet = CfdFluidBoundary.makeCfdFluidBoundary("Inlet")
        CfdTools.getActiveAnalysis().addObject(self._inlet)
        self._inlet.ShapeRefs = [self._compound, ('Face{}'.format(length), )]
        self._inlet.BoundaryType = "inlet"
        self._inlet.BoundarySubType = "uniformVelocityInlet"
        self._inlet.Ux = 102000 # 102 m/s = 0.3 Mach
        FreeCAD.ActiveDocument.recompute()

        self._outlet = CfdFluidBoundary.makeCfdFluidBoundary("Outlet")
        CfdTools.getActiveAnalysis().addObject(self._outlet)
        self._outlet.ShapeRefs = [self._compound, ('Face{}'.format(length-1), )]
        self._outlet.BoundaryType = "outlet"
        self._outlet.BoundarySubType = "staticPressureOutlet"
        FreeCAD.ActiveDocument.recompute()

        self._wall = CfdFluidBoundary.makeCfdFluidBoundary("Wall")
        CfdTools.getActiveAnalysis().addObject(self._wall)
        self._wall.ShapeRefs = [self._compound, ('Face{}'.format(length-2), )]
        self._wall.BoundaryType = "wall"
        self._wall.BoundarySubType = "fixedWall"
        FreeCAD.ActiveDocument.recompute()

    def adjustPhysicsModel(self):
        self._physicsModel.Flow = "NonIsothermal"
        self._physicsModel.Turbulence = "RANS"
        FreeCAD.ActiveDocument.recompute()

    def adjustFluidProperties(self):
        materials, material_name_path_list = CfdTools.importMaterials()
        for mat in material_name_path_list:
            material = materials[mat[1]]
            # print("Name {} Type {}".format(material['Name'], material['Type']))
            if material['Name'] == "Air" and material['Type'] == "Compressible":
                self._fluidProperties.Material = material
                self._fluidProperties.Label = material['Name']
                FreeCAD.ActiveDocument.recompute()
                return

    def adjustInitializeFields(self):
        self._initializeFields.PotentialFlow = False
        self._initializeFields.PotentialFlowP = False
        self._initializeFields.BoundaryU = self._inlet
        self._initializeFields.BoundaryP = self._outlet
        self._initializeFields.UseInletUValues = True
        self._initializeFields.UseOutletPValue = True
        FreeCAD.ActiveDocument.recompute()

    def adjustCFDSolver(self):
        cores = self.form.spinNproc.value()
        self._solver.ParallelCores = cores
        FreeCAD.ActiveDocument.recompute()
