# ***************************************************************************
# *   Copyright (c) 2025 David Carter <dcarter@davidcarter.ca>              *
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
"""Class for drawing Aero Pack style retainers"""

__title__ = "FreeCAD Retainers"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

import FreeCAD
import FreeCADGui

from Rocket.FeatureRetainer import FeatureRetainer
if FreeCAD.GuiUp:
    from Ui.ViewRetainer import ViewProviderRetainer
    from Ui.Widgets.WaitCursor import WaitCursor
from Ui.Commands.Command import Command

from Rocket.Constants import FEATURE_RETAINER

translate = FreeCAD.Qt.translate

def makeRetainer(name='Retainer'):
    '''makeRetainer(name): makes a retainer'''
    obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython",name)
    FeatureRetainer(obj)
    obj.Proxy.setDefaults()
    if FreeCAD.GuiUp:
        ViewProviderRetainer(obj.ViewObject)

    return obj.Proxy

class CmdRetainer(Command):
    def Activated(self):
        with WaitCursor():
            FreeCAD.ActiveDocument.openTransaction("Create retainer")
            FreeCADGui.addModule("Ui.Commands.CmdRetainer")
            FreeCADGui.doCommand("obj=Ui.Commands.CmdRetainer.makeRetainer('Retainer')")
            FreeCADGui.doCommand("Ui.Commands.CmdStage.addToStage(obj)")
            FreeCADGui.doCommand("FreeCADGui.Selection.clearSelection()")
            FreeCADGui.doCommand("FreeCADGui.Selection.addSelection(obj._obj)")
            FreeCADGui.doCommand("FreeCADGui.activeDocument().setEdit(FreeCAD.ActiveDocument.ActiveObject.Name,0)")

    def IsActive(self):
        if FreeCAD.ActiveDocument:
            return self.partEligibleFeature(FEATURE_RETAINER)
        return False

    def GetResources(self):
        return {'MenuText': translate("Rocket", 'Retainer'),
                'ToolTip': translate("Rocket", 'Adds an Aero Pack style retainer to the selected component'),
                'Pixmap': FreeCAD.getUserAppDataDir() + "Mod/Rocket/Resources/icons/Rocket_Retainer.svg"}
