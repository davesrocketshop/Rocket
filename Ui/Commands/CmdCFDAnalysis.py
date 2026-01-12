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


"""Class for CFD Analysis"""

__title__ = "FreeCAD CFD Analysis"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

import FreeCAD
import FreeCADGui
import os

translate = FreeCAD.Qt.translate

from PySide import QtGui

from CfdOF import CfdTools

from Rocket.cfd.FeatureCFDRocket import FeatureCFDRocket
from Rocket.cfd.FeatureWindTunnel import FeatureWindTunnel
from Rocket.cfd.ViewProviders.ViewProviderCFDRocket import ViewProviderCFDRocket
from Rocket.cfd.ViewProviders.ViewProviderWindTunnel import ViewProviderWindTunnel

from Ui.Commands.Command import Command
from Ui.TaskPanelCFD import TaskPanelCFD

def doCFD():

    # See if we have a rocket selected
    for rocket in FreeCADGui.Selection.getSelection():
        if rocket.isDerivedFrom('Part::FeaturePython') or rocket.isDerivedFrom('App::GeometryPython'):
            if hasattr(rocket,"Proxy") and hasattr(rocket.Proxy,"getRocket"):
                try:
                    root = rocket.Proxy.getRocket()
                    if root:
                        taskd = TaskPanelCFD(root)
                        FreeCADGui.Control.showDialog(taskd)
                except TypeError as ex:
                    QtGui.QMessageBox.information(None, "", str(ex))
                return

    QtGui.QMessageBox.information(None, "", translate('Rocket', "Please select a rocket first"))

def makeCFDRocket(name='CFDRocket'):
    '''makeCFDRocket(name): makes a CFD Rocket'''
    obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython",name)
    FeatureCFDRocket(obj)
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
        FreeCAD.ActiveDocument.openTransaction("Create CFD Analysis")
        FreeCADGui.addModule("Ui.Commands.CmdCFDAnalysis")
        FreeCADGui.doCommand("Ui.Commands.CmdCFDAnalysis.doCFD()")
        FreeCADGui.doCommand("App.ActiveDocument.commitTransaction()")

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
                'ToolTip': translate("Rocket", 'Performs a CFD Analysis'),
                'Pixmap': icon_path}
