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

from PySide import  QtCore, QtGui

from CfdOF.Mesh import CfdMesh, CfdMeshRefinement
from CfdOF import CfdAnalysis, CfdTools
from CfdOF.Solve import CfdPhysicsSelection, CfdFluidBoundary, CfdFluidMaterial, CfdInitialiseFlowField, \
    CfdSolverFoam
from CfdOF.PostProcess import CfdReportingFunction

from Rocket.cfd.CFDUtil import caliber, finThickness, createSolid, createFinsets, makeCFDRocket, makeCFDFinSet, makeWindTunnel

from Ui.UIPaths import getUIPath

class TaskPanelCFD(QtCore.QObject):

    def __init__(self, rocket):
        super().__init__()

        self._rocket = rocket

        self.form = FreeCADGui.PySideUic.loadUi(os.path.join(getUIPath(), 'Resources', 'ui', "DialogCFD.ui"))
        # self.form = FreeCADGui.PySideUic.loadUi(':/ui/DialogCFD.ui')

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
        self._finsets = createFinsets(self._rocket)
        diameter = caliber(self._rocket)
        thickness = finThickness(self._rocket)
        box = self._solid.BoundBox
        length = box.XLength

        self.form.inputLength.setText(str(length))
        self.form.inputDiameter.setText(str(diameter))
        self.form.inputFinThickness.setText(str(thickness))

        self._CFDrocket = None
        self._CFDFinSets = []
        self._refinement_wake = None
        self._refinement_transition1 = None
        self._refinement_transition2 = None


    def onCreate(self):
        self.makeSolid()
        self.makeFinSets()
        self.makeWindTunnel()
        self.makeAnalysisContainer()
        self.makeCfdMesh()
        self.makeBoundaryConstraints()
        self.adjustPhysicsModel()
        self.adjustFluidProperties()
        self.adjustInitializeFields()
        self.adjustCFDSolver()
        self.makeReportingFunction()

        # Don't try to make things twice
        # self.form.buttonCreate.setEnabled(False)
        self.accept()

    def getStandardButtons(self):
        return QtGui.QDialogButtonBox.Close

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
        box = self._solid.BoundBox
        center = box.XLength / 2.0

        solid1 = self._solid
        self._rotation = self.form.spinRotation.value()
        if self._rotation != 0.0:
            solid1.rotate(FreeCAD.Vector(0, 0, 0),FreeCAD.Vector(1, 0, 0), self._rotation)
        self._aoa = self.form.spinAOA.value()
        if self._aoa != 0.0:
            solid1.rotate(FreeCAD.Vector(center, 0, 0),FreeCAD.Vector(0, 1, 0), self._aoa)
        self._CFDrocket._obj.Shape = solid1
        FreeCAD.ActiveDocument.recompute()

    def makeFinSets(self):
        self._CFDFinSets = []
        box = self._solid.BoundBox
        center = box.XLength / 2.0
        self._rotation = self.form.spinRotation.value()
        self._aoa = self.form.spinAOA.value()

        for finset in self._finsets:
            fins = makeCFDFinSet()
            solid1 = finset[0]
            if self._rotation != 0.0:
                solid1.rotate(FreeCAD.Vector(0, 0, 0),FreeCAD.Vector(1, 0, 0), self._rotation)
            if self._aoa != 0.0:
                solid1.rotate(FreeCAD.Vector(center, 0, 0),FreeCAD.Vector(0, 1, 0), self._aoa)
            fins._obj.Shape = solid1
            fins._obj.Thickness = finset[1]
            self._CFDFinSets.append(fins)

    def getTunnelDimensions(self):
        diameter = FreeCAD.Units.Quantity(self.form.inputDiameter.text()).Value
        length = FreeCAD.Units.Quantity(self.form.inputLength.text()).Value

        # Get a blockage ratio of 0.1%
        area = (diameter * diameter) / 0.001
        tunnelDiameter = math.sqrt(area)
        return tunnelDiameter, length

    def makeWindTunnel(self):
        diameter, length = self.getTunnelDimensions()
        self._outer = makeWindTunnel('WindTunnel', diameter, 10.0 * length, 2.0 * length)
        self._refinement0 = makeWindTunnel('WindTunnel-wake', diameter * 0.25, 3.5 * length, 0.5 * length)
        self._refinement1 = makeWindTunnel('WindTunnel-transition1', diameter * 0.5, 9.0 * length, 1.0 * length)
        self._refinement2 = makeWindTunnel('WindTunnel-transition2', diameter * 0.75, 9.5 * length, 1.5 * length)
        FreeCAD.ActiveDocument.recompute()

        self.makeCompound()
        FreeCAD.ActiveDocument.recompute()

        self._rocket._obj.ViewObject.Visibility = False
        FreeCAD.ActiveDocument.recompute()

    def makeCompound(self):
        self._compound = FreeCAD.activeDocument().addObject("Part::Compound", "WindTunnelCompund")
        links = [self._outer._obj, self._CFDrocket._obj]
        for fins in self._CFDFinSets:
            links.append(fins._obj)
        self._compound.Links = links
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
        diameter, _ = self.getTunnelDimensions()
        self._CFDMesh = CfdMesh.makeCfdMesh('WindTunnelCompund_Mesh')
        self._CFDMesh.CharacteristicLengthMax = diameter / 10.0
        FreeCAD.ActiveDocument.ActiveObject.Part = self._compound
        CfdTools.getActiveAnalysis().addObject(FreeCAD.ActiveDocument.ActiveObject)
        FreeCAD.ActiveDocument.recompute()

        # Progressive volume refinements
        refinement = CfdMeshRefinement.makeCfdMeshRefinement(self._CFDMesh, 'VolumeRefinement-wake')
        refinement.ShapeRefs = [self._refinement_wake._obj, ('Solid1', )]
        refinement.Internal = True
        refinement.RelativeLength = 0.125
        FreeCAD.ActiveDocument.recompute()

        refinement = CfdMeshRefinement.makeCfdMeshRefinement(self._CFDMesh, 'VolumeRefinement-transition1')
        refinement.ShapeRefs = [self._refinement_transition1._obj, ('Solid1', )]
        refinement.Internal = True
        refinement.RelativeLength = 0.250
        FreeCAD.ActiveDocument.recompute()

        refinement = CfdMeshRefinement.makeCfdMeshRefinement(self._CFDMesh, 'VolumeRefinement-transition2')
        refinement.ShapeRefs = [self._refinement_transition2._obj, ('Solid1', )]
        refinement.Internal = True
        refinement.RelativeLength = 0.500
        FreeCAD.ActiveDocument.recompute()

        # Surface refinement
        box = self._CFDrocket._obj.Shape.BoundBox
        diameter = box.YLength
        relativeLength = (math.pi * diameter / 50.0) / self._CFDMesh.CharacteristicLengthMax

        defaultLength = 0.0625 # Last volume refinement / 2
        if relativeLength > 0.0:
            relativeLength = min(relativeLength, defaultLength)
        else:
            relativeLength = defaultLength
        refinement = CfdMeshRefinement.makeCfdMeshRefinement(self._CFDMesh, 'SurfaceRefinement-Body')
        refinement.ShapeRefs = [self._CFDrocket._obj, ('', )]
        refinement.RelativeLength = relativeLength.Value
        refinement.RefinementThickness = '10.0 mm'
        FreeCAD.ActiveDocument.recompute()

        # Fin surface refinements
        defaultLength = FreeCAD.Units.Quantity("0.0625")
        for fin in self._CFDFinSets:
            thickness = FreeCAD.Units.Quantity(fin._obj.Thickness)
            relativeLength = (thickness / 2.0) / self._CFDMesh.CharacteristicLengthMax
            if relativeLength > 0.0:
                relativeLength = min(relativeLength, defaultLength)
            else:
                relativeLength = defaultLength

            refinement = CfdMeshRefinement.makeCfdMeshRefinement(self._CFDMesh, 'SurfaceRefinement-FinSet')
            refinement.ShapeRefs = [fin._obj, ('', )]
            refinement.RelativeLength = relativeLength.Value
            refinement.RefinementThickness = '10.0 mm'
            FreeCAD.ActiveDocument.recompute()

    def makeBoundaryConstraints(self):
        length = len(self._compound.Shape.Faces)
        self._inlet = CfdFluidBoundary.makeCfdFluidBoundary("Inlet")
        CfdTools.getActiveAnalysis().addObject(self._inlet)
        self._inlet.ShapeRefs = [self._compound, ('Face{}'.format(length), )]
        self._inlet.BoundaryType = "inlet"
        self._inlet.BoundarySubType = "uniformVelocityInlet"
        self._inlet.Ux = 100000 # 100 m/s = 0.3 Mach
        FreeCAD.ActiveDocument.recompute()

        self._outlet = CfdFluidBoundary.makeCfdFluidBoundary("Outlet")
        CfdTools.getActiveAnalysis().addObject(self._outlet)
        self._outlet.ShapeRefs = [self._compound, ('Face{}'.format(length-1), )]
        self._outlet.BoundaryType = "outlet"
        self._outlet.BoundarySubType = "staticPressureOutlet"
        self._outlet.Pressure = "0 kPa" #?
        FreeCAD.ActiveDocument.recompute()

        self._wall = CfdFluidBoundary.makeCfdFluidBoundary("Wall")
        CfdTools.getActiveAnalysis().addObject(self._wall)
        self._wall.ShapeRefs = [self._compound, ('Face{}'.format(length-2), )]
        self._wall.BoundaryType = "wall"
        self._wall.BoundarySubType = "slipWall"
        FreeCAD.ActiveDocument.recompute()

        self._rocketWall = CfdFluidBoundary.makeCfdFluidBoundary("RocketWall")
        CfdTools.getActiveAnalysis().addObject(self._rocketWall)
        refs = [self._CFDrocket._obj]
        for fin in self._CFDFinSets:
            refs.append(fin._obj)
        self._rocketWall.ShapeRefs = refs

        self._rocketWall.BoundaryType = "wall"
        self._rocketWall.BoundarySubType = "fixedWall"
        FreeCAD.ActiveDocument.recompute()

    def adjustPhysicsModel(self):
        self._physicsModel.Flow = "Isothermal"
        self._physicsModel.Turbulence = "RANS"
        FreeCAD.ActiveDocument.recompute()

    def adjustFluidProperties(self):
        materials, material_name_path_list = CfdTools.importMaterials()
        for mat in material_name_path_list:
            material = materials[mat[1]]
            # print("Name {} Type {}".format(material['Name'], material['Type']))
            if material['Name'] == "Air" and material['Type'] == "Isothermal":
                self._fluidProperties.Material = material
                self._fluidProperties.Label = material['Name']
                FreeCAD.ActiveDocument.recompute()
                return

    def adjustInitializeFields(self):
        self._initializeFields.PotentialFlow = True
        self._initializeFields.PotentialFlowP = True
        # self._initializeFields.BoundaryU = self._inlet
        # self._initializeFields.BoundaryP = self._outlet
        self._initializeFields.UseInletUValues = False
        self._initializeFields.UseOutletPValue = False
        FreeCAD.ActiveDocument.recompute()

    def adjustCFDSolver(self):
        cores = self.form.spinNproc.value()
        self._solver.ParallelCores = cores
        FreeCAD.ActiveDocument.recompute()

    def makeReportingFunction(self):
        self._force = CfdReportingFunction.makeCfdReportingFunction("ForceReportingFunction")
        CfdTools.getActiveAnalysis().addObject(self._force)
        self._force.ReportingFunctionType = "Force"
        # q = (p / 2) * v^2
        self._force.ReferencePressure = "25000 Pa"
        self._force.Patch = self._rocketWall
        FreeCAD.ActiveDocument.recompute()
