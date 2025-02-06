# ***************************************************************************
# *   Copyright (c) 2024-2025 David Carter <dcarter@davidcarter.ca>         *
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
import Part
import os
import math

from DraftTools import translate

from PySide import  QtCore, QtGui

from CfdOF.Mesh import CfdMeshRefinement
from CfdOF import CfdTools
from CfdOF.Solve import CfdPhysicsSelection, CfdFluidBoundary, CfdFluidMaterial, CfdInitialiseFlowField, \
    CfdSolverFoam
from CfdOF.PostProcess import CfdReportingFunction

from Analyzers.pyatmos import coesa76
from Analyzers.pyatmos.utils.Const import gamma, R_air

from Rocket.cfd.CFDUtil import caliber, finThickness, createSolid, makeCFDRocket, makeMultiCFDAnalysis, \
    makeWindTunnel, makeCfdMesh
from Rocket.cfd.FeatureCFDRocket import calcFrontalArea

from Ui.UIPaths import getUIPath

class TaskPanelCFD(QtCore.QObject):

    def __init__(self, rocket):
        super().__init__()

        self._rocket = rocket

        self.form = FreeCADGui.PySideUic.loadUi(os.path.join(getUIPath(), 'Resources', 'ui', "DialogCFD.ui"))
        self.form.inputAltitude.textEdited.connect(self.onAltitude)

        FreeCAD.setActiveTransaction("Create Rocket CFD Study")
        self.initialize()

    def getStandardButtons(self):
        return QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Close

    def modifyStandardButtons(self, box):
        createButton = box.button(QtGui.QDialogButtonBox.Ok)
        createButton.setText(translate("Rocket", "Create"))

    def initialize(self):
        # Set Nproc to the number of available threads
        if hasattr(os, "sched_getaffinity"):
            self.form.spinNproc.setValue(len(os.sched_getaffinity(0)))
        else:
            self.form.spinNproc.setValue(os.cpu_count())

        self._solid = createSolid(self._rocket)
        self._frontalArea = calcFrontalArea(self._solid)
        diameter = caliber(self._rocket)
        thickness = finThickness(self._rocket)
        box = self._solid.BoundBox
        length = box.XLength

        self.form.inputLength.setText(FreeCAD.Units.Quantity("{} mm".format(length)).UserString)
        self.form.inputDiameter.setText(FreeCAD.Units.Quantity("{} mm".format(diameter)).UserString)
        self.form.inputFinThickness.setText(FreeCAD.Units.Quantity("{} mm".format(thickness)).UserString)
        self.form.inputArea.setText(FreeCAD.Units.Quantity("{} mm^2".format(self._frontalArea)).UserString)

        self.form.inputAltitude.setText(FreeCAD.Units.Quantity("1000 m").UserString)
        self.form.inputMach.setText("0.3")
        self.onAltitude("1000 m")

        self._CFDrocket = None
        self._refinement_wake = None
        self._refinement_transition1 = None
        self._refinement_transition2 = None

        self.form.editAOA.textChanged.connect(self.onAOAChanged)
        self.form.spinRotation.valueChanged.connect(self.onSpinChanged)

    def onAOAChanged(self):
        """ Calculate the frontal area when the AOA or rotation changes """
        angles = self.getAOAList()
        if self._CFDrocket is not None:
            if len(angles) > 0:
                self._CFDrocket._obj.AngleOfAttack = angles[0]
            else:
                self._CFDrocket._obj.AngleOfAttack = 0.0
        self.AOAChanged()
        FreeCAD.ActiveDocument.recompute()

    def AOAChanged(self):
        """ Calculate the frontal area when the AOA or rotation changes """
        solid = self.applyTranslations(self._solid)
        self._frontalArea = calcFrontalArea(solid)
        self.form.inputArea.setText(FreeCAD.Units.Quantity("{} mm^2".format(self._frontalArea)).UserString)

    def onSpinChanged(self, value):
        if self._CFDrocket is not None:
            self._CFDrocket._obj.AngleOfRotation = value
        self.AOAChanged()
        FreeCAD.ActiveDocument.recompute()

    def atmosphericConditions(self, altitude):

        # Get the atmospheric conditions at the specified altitude (convert mm to km)
        # Uses the coesa76 model which is an extension of US Standard Atmosphere 1976 model to work above 84K
        atmo = coesa76([altitude / (1000.0 * 1000.0)])

        temp = float(atmo.T[0])
        pressure = float(atmo.P[0])

        # speed of sound
        mach = math.sqrt(gamma * R_air * temp)

        return mach,pressure

    def onAltitude(self, value):
        altitude = FreeCAD.Units.Quantity(value).Value
        mach, _ = self.atmosphericConditions(altitude)
        self.form.inputSpeed.setText(FreeCAD.Units.Quantity("{} m/s".format(mach * 0.3)).UserString)

    def airPressure(self):
        altitude = FreeCAD.Units.Quantity(self.form.inputAltitude.text()).Value
        _, pressure = self.atmosphericConditions(altitude)
        return FreeCAD.Units.Quantity("{} Pa".format(pressure))

    def speed(self):
        # return FreeCAD.Units.Quantity("100 m/s")
        return FreeCAD.Units.Quantity(self.form.inputSpeed.text())

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
        self.makeReportingFunctions()

        FreeCADGui.SendMsgToActiveView("ViewFit")

    def accept(self):
        self.onCreate()
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
        self._CFDrocket._obj.Shape = self._solid # self.applyTranslations(self._solid)

        angles = self.getAOAList()
        if len(angles) > 0:
            self._CFDrocket._obj.AngleOfAttack = angles[0]
        else:
            self._CFDrocket._obj.AngleOfAttack = 0.0
        self._CFDrocket._obj.AngleOfRotation = self.form.spinRotation.value()
        FreeCAD.ActiveDocument.recompute()

    def getCenter(self, solid):
        box = solid.BoundBox
        center = box.XLength / 2.0

        return center

    def getAOAList(self):
        listText = self.form.editAOA.toPlainText()
        textList = listText.split('\n')
        angles = []
        for angle in textList:
            if len(angle) > 0:
                try:
                    angles.append(float(angle))
                except ValueError:
                    print("Illegal float value '{}'".format(angle))
        return angles

    def applyTranslations(self, solid, maxAOA=False):
        center = self.getCenter(solid)

        solid1 = Part.makeCompound([solid]) # Needed to create a copy so translations aren't applied multiple times
        self._rotation = self.form.spinRotation.value()
        if self._rotation != 0.0:
            solid1.rotate(FreeCAD.Vector(0, 0, 0),FreeCAD.Vector(1, 0, 0), self._rotation)
        angles = self.getAOAList()
        if len(angles) > 0:
            if maxAOA:
                self._aoa = max(angles)
            else:
                self._aoa = angles[0]
        else:
            self._aoa = 0.0
        if self._aoa != 0.0:
            solid1.rotate(FreeCAD.Vector(center, 0, 0),FreeCAD.Vector(0, 1, 0), self._aoa)
        solid1.translate(FreeCAD.Vector(-center, 0, 0))
        return solid1

    def getTunnelDimensions(self):
        # diameter = FreeCAD.Units.Quantity(self.form.inputDiameter.text()).Value
        length = FreeCAD.Units.Quantity(self.form.inputLength.text()).Value

        # Get a blockage ratio of 0.1%
        solid = self.applyTranslations(self._solid, maxAOA=True)
        frontalArea = calcFrontalArea(solid)
        area = (frontalArea) / 0.001
        tunnelDiameter = 2.0 * math.sqrt(area / math.pi)
        return tunnelDiameter, length

    def makeWindTunnel(self):
        center = self.getCenter(self._solid)
        diameter, length = self.getTunnelDimensions()
        self._outer = makeWindTunnel('WindTunnel', diameter, 10.0 * length, 2.0 * length + center)
        self._refinement_wake = makeWindTunnel('WindTunnel-wake', diameter * 0.25, 3.5 * length, 0.5 * length + center)
        self._refinement_transition1 = makeWindTunnel('WindTunnel-transition1', diameter * 0.5, 9.0 * length, 1.0 * length + center)
        self._refinement_transition2 = makeWindTunnel('WindTunnel-transition2', diameter * 0.75, 9.5 * length, 1.5 * length + center)
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
        analysis = makeMultiCFDAnalysis('MultiCfdAnalysis')
        analysis.Shape = self._solid # No AOA applied
        analysis.AOAList = self.getAOAList()
        analysis.CFDRocket = self._CFDrocket._obj
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
        self._CFDMesh = makeCfdMesh('WindTunnelCompund_Mesh')
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
        thickness = FreeCAD.Units.Quantity(self.form.inputFinThickness.text())
        relativeLength = (thickness / 2.0) / self._CFDMesh.CharacteristicLengthMax
        defaultLength = FreeCAD.Units.Quantity("0.0625")
        if relativeLength > 0.0:
            relativeLength = min(relativeLength, defaultLength)
        else:
            relativeLength = defaultLength
        refinement = CfdMeshRefinement.makeCfdMeshRefinement(self._CFDMesh, 'SurfaceRefinement')
        refinement.ShapeRefs = [self._CFDrocket._obj, ('', )]
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
        self._inlet.Pressure = 0
        self._inlet.Ux = self.speed()
        FreeCAD.ActiveDocument.recompute()

        self._outlet = CfdFluidBoundary.makeCfdFluidBoundary("Outlet")
        CfdTools.getActiveAnalysis().addObject(self._outlet)
        self._outlet.ShapeRefs = [self._compound, ('Face{}'.format(length-1), )]
        self._outlet.BoundaryType = "outlet"
        self._outlet.BoundarySubType = "staticPressureOutlet"
        self._outlet.Pressure = 0 # self.airPressure()
        FreeCAD.ActiveDocument.recompute()

        self._wall = CfdFluidBoundary.makeCfdFluidBoundary("Wall")
        CfdTools.getActiveAnalysis().addObject(self._wall)
        self._wall.ShapeRefs = [self._compound, ('Face{}'.format(length-2), )]
        self._wall.BoundaryType = "wall"
        self._wall.BoundarySubType = "slipWall"
        FreeCAD.ActiveDocument.recompute()

        self._rocketWall = CfdFluidBoundary.makeCfdFluidBoundary("RocketWall")
        CfdTools.getActiveAnalysis().addObject(self._rocketWall)
        self._rocketWall.ShapeRefs = [self._CFDrocket._obj]
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

    def makeReportingFunctions(self):
        self._force = CfdReportingFunction.makeCfdReportingFunction("ForceReportingFunction")
        CfdTools.getActiveAnalysis().addObject(self._force)
        self._force.ReportingFunctionType = "Force"
        # q = (p / 2) * v^2
        self._force.ReferencePressure = self.airPressure()
        self._force.Patch = self._rocketWall
        FreeCAD.ActiveDocument.recompute()

        self._forceCoefficient = CfdReportingFunction.makeCfdReportingFunction("ForceCoefficientReportingFunction")
        CfdTools.getActiveAnalysis().addObject(self._forceCoefficient)
        self._forceCoefficient.ReportingFunctionType = "ForceCoefficients"
        self._forceCoefficient.Patch = self._rocketWall
        # q = (p / 2) * v^2
        self._forceCoefficient.ReferencePressure = 0 # self.airPressure()
        self._forceCoefficient.Lift = FreeCAD.Vector(0, 0, 1)
        self._forceCoefficient.Drag = FreeCAD.Vector(1, 0, 0)
        self._forceCoefficient.MagnitudeUInf = self.speed()
        self._forceCoefficient.LengthRef = FreeCAD.Units.Quantity(self.form.inputLength.text())
        self._forceCoefficient.AreaRef = self._frontalArea
        FreeCAD.ActiveDocument.recompute()
