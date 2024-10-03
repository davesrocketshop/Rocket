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
"""Class for CFD Analysis"""

__title__ = "FreeCAD CFD Analysis"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

import FreeCAD
import FreeCADGui
import Part
import os
import math

from DraftTools import translate

from PySide import QtGui

from CfdOF import CfdTools

from Rocket.cfd.CreateSolid import createSolid
from Rocket.cfd.FeatureCFDRocket import FeatureCFDRocket
from Rocket.cfd.FeatureWindTunnel import FeatureWindTunnel
from Rocket.cfd.ViewProviders.ViewProviderCFDRocket import ViewProviderCFDRocket
from Rocket.cfd.ViewProviders.ViewProviderWindTunnel import ViewProviderWindTunnel

from Ui.Commands.Command import Command
from Ui.DialogCFD import DialogCFD

def doCFD():
    # See if we have a rocket selected
    for rocket in FreeCADGui.Selection.getSelection():
        if rocket.isDerivedFrom('Part::FeaturePython') or rocket.isDerivedFrom('App::GeometryPython'):
            if hasattr(rocket,"Proxy") and hasattr(rocket.Proxy,"getRocket"):
                try:
                    root = rocket.Proxy.getRocket()
                    if root is not None:
                        CFDrocket = makeCFDRocket()
                        solid = createSolid(root)
                        CFDrocket._obj.Shape = solid
                        box = solid.BoundBox
                        print(dir(solid.Area))
                        print(solid.Area)
                        print('XMax = {}'.format(solid.BoundBox.XMax))
                        print('XMin = {}'.format(solid.BoundBox.XMin))
                        print('XLength = {}'.format(solid.BoundBox.XLength))
                        print('YMax = {}'.format(solid.BoundBox.YMax))
                        print('YMin = {}'.format(solid.BoundBox.YMin))
                        print('YLength = {}'.format(solid.BoundBox.YLength))
                        print('ZMax = {}'.format(solid.BoundBox.ZMax))
                        print('ZMin = {}'.format(solid.BoundBox.ZMin))
                        print('ZLength = {}'.format(solid.BoundBox.ZLength))
                        diameter = 2.0 * max(box.YMax, -box.YMin, box.ZMax, -box.ZMin)
                        length = solid.BoundBox.XLength

                        # Approximate the frontal area. This can be improved
                        area = solid.Volume / length
                        # Get a blockage ratio of 0.1% ? 0.1
                        tunnelDiameter = (area / 0.1) / math.pi
                        FreeCADGui.doCommand("Ui.Commands.CmdCFDAnalysis.makeWindTunnel('WindTunnel',{},{},{})".format(tunnelDiameter, 10.0 * length, 2.0 * length))
                        FreeCADGui.doCommand("Ui.Commands.CmdCFDAnalysis.makeWindTunnel('Refinement',{},{},{})".format(tunnelDiameter * 0.25, 3.5 * length, 0.5 * length))
                        FreeCADGui.doCommand("Ui.Commands.CmdCFDAnalysis.makeWindTunnel('Refinement',{},{},{})".format(tunnelDiameter * 0.5, 9.0 * length, 1.0 * length))
                        FreeCADGui.doCommand("Ui.Commands.CmdCFDAnalysis.makeWindTunnel('Refinement',{},{},{})".format(tunnelDiameter * 0.75, 9.5 * length, 1.5 * length))
                except TypeError as ex:
                    QtGui.QMessageBox.information(None, "", str(ex))
                return

    QtGui.QMessageBox.information(None, "", translate('Rocket', "Please select a rocket first"))

def makeCFDRocket(name='CFDRocket'):
    '''makeCFDRocket(name): makes a CFD Rocket'''
    obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython",name)
    FeatureCFDRocket(obj)
    # obj.Proxy.setDefaults()
    if FreeCAD.GuiUp:
        ViewProviderCFDRocket(obj.ViewObject)

    return obj.Proxy

def makeWindTunnel(name='WindTunnel', diameter=10.0, length=20.0, offset=0.0):
    '''makeWindTunnel(name): makes a Wind Tunnel'''
    obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython",name)
    FeatureWindTunnel(obj)
    obj.Diameter = diameter
    obj.Length = length
    obj.Placement.Base.x = -offset
    # obj.Proxy.setDefaults()
    if FreeCAD.GuiUp:
        ViewProviderWindTunnel(obj.ViewObject)

    return obj.Proxy

class CmdCFDAnalysis(Command):
    def Activated(self):
        # self.doCFD()
        # FreeCADGui.runCommand("CfdOF_Analysis")
        FreeCAD.ActiveDocument.openTransaction("Create CFD Analysis")
        FreeCADGui.addModule("Ui.Commands.CmdCFDAnalysis")
        FreeCADGui.doCommand("Ui.Commands.CmdCFDAnalysis.doCFD()")
        # FreeCADGui.doCommand("Ui.Commands.CmdCFDAnalysis.makeWindTunnel('WindTunnel')")

        FreeCADGui.doCommand("from CfdOF import CfdAnalysis")
        FreeCADGui.doCommand("from CfdOF import CfdTools")
        FreeCADGui.doCommand("analysis = CfdAnalysis.makeCfdAnalysis('CfdAnalysis')")
        FreeCADGui.doCommand("CfdTools.setActiveAnalysis(analysis)")

        # Objects ordered according to expected workflow
        # Add physics object when CfdAnalysis container is created
        FreeCADGui.doCommand("from CfdOF.Solve import CfdPhysicsSelection")
        FreeCADGui.doCommand("analysis.addObject(CfdPhysicsSelection.makeCfdPhysicsSelection())")

        # Add fluid properties object when CfdAnalysis container is created
        FreeCADGui.doCommand("from CfdOF.Solve import CfdFluidMaterial")
        FreeCADGui.doCommand("analysis.addObject(CfdFluidMaterial.makeCfdFluidMaterial('FluidProperties'))")

        # Add initialisation object when CfdAnalysis container is created
        FreeCADGui.doCommand("from CfdOF.Solve import CfdInitialiseFlowField")
        FreeCADGui.doCommand("analysis.addObject(CfdInitialiseFlowField.makeCfdInitialFlowField())")

        # Add solver object when CfdAnalysis container is created
        FreeCADGui.doCommand("from CfdOF.Solve import CfdSolverFoam")
        FreeCADGui.doCommand("analysis.addObject(CfdSolverFoam.makeCfdSolverFoam())")

        FreeCADGui.doCommand("App.activeDocument().recompute(None,True,True)")

    def IsActive(self):
        # Available when a part is selected and CfdOF is available
        try:
            import CfdOF
            False if CfdOF.__name__ else True
        except:
            return False

        return self.partRocketSelected()

    def GetResources(self):
        icon_path = os.path.join(CfdTools.getModulePath(), "Gui", "Icons", "cfd.svg")
        return {'MenuText': translate("Rocket", 'CFD Analysis'),
                'ToolTip': translate("Rocket", 'Perform a CFD Analysis'),
                'Pixmap': icon_path}

    def doCFD(self):

        # See if we have a rocket selected
        for rocket in FreeCADGui.Selection.getSelection():
            if rocket.isDerivedFrom('Part::FeaturePython') or rocket.isDerivedFrom('App::GeometryPython'):
                if hasattr(rocket,"Proxy") and hasattr(rocket.Proxy,"getRocket"):
                    try:
                        root = rocket.Proxy.getRocket()
                        if root is not None:
                            # form = DialogCFD(rocket)
                            # form.exec_()
                            solid = createSolid(root)
                            Part.show(solid)
                    except TypeError as ex:
                        QtGui.QMessageBox.information(None, "", str(ex))
                    return
        # self.taskd = DialogCFD()
        # # FreeCADGui.Control.showDialog(self.taskd)
        # self.taskd.exec_()

        QtGui.QMessageBox.information(None, "", translate('Rocket', "Please select a rocket first"))
