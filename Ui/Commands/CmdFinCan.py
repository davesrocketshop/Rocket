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


"""Class for drawing fin cans"""

__title__ = "FreeCAD Fin Can"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

import FreeCAD
import FreeCADGui

from Rocket.FeatureFinCan import FeatureFinCan

if FreeCAD.GuiUp:
    from Ui.ViewFinCan import ViewProviderFinCan
    from Ui.Widgets.WaitCursor import WaitCursor
from Ui.Commands.Command import Command

from Rocket.Constants import FEATURE_FINCAN
from Rocket.Constants import FIN_TYPE_SKETCH

translate = FreeCAD.Qt.translate

def makeFinCan(name : str = 'FinCan') -> FeatureFinCan:
    '''makeFinCan(name): makes a Fin Can'''
    obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython",name)
    FeatureFinCan(obj)
    obj.Proxy.setDefaults()

    # See if we have a sketch selected. If so, this is a custom fin
    if FreeCAD.GuiUp:
        for sketch in FreeCADGui.Selection.getSelection():
            if sketch.isDerivedFrom('Sketcher::SketchObject'):
                obj.FinType = FIN_TYPE_SKETCH
                obj.Profile = sketch
                sketch.Visibility = False

        ViewProviderFinCan(obj.ViewObject)

    return obj.Proxy

class CmdFinCan(Command):
    def Activated(self) -> None:
        with WaitCursor():
            FreeCAD.ActiveDocument.openTransaction("Create fin can")
            FreeCADGui.addModule("Ui.Commands.CmdFinCan")
            FreeCADGui.doCommand("obj=Ui.Commands.CmdFinCan.makeFinCan('FinCan')")
            FreeCADGui.doCommand("Ui.Commands.CmdStage.addToStage(obj)")
            FreeCADGui.doCommand("FreeCADGui.Selection.clearSelection()")
            FreeCADGui.doCommand("FreeCADGui.Selection.addSelection(obj._obj)")
            FreeCADGui.doCommand("FreeCADGui.activeDocument().setEdit(FreeCAD.ActiveDocument.ActiveObject.Name,0)")

    def IsActive(self) -> bool:
        if FreeCAD.ActiveDocument:
            return self.partEligibleFeature(FEATURE_FINCAN)
        return False

    def GetResources(self) -> dict:
        return {'MenuText': translate("Rocket", 'Fin Can'),
                'ToolTip': translate("Rocket", 'Adds a fin can to the selected component'),
                'Pixmap': FreeCAD.getUserAppDataDir() + "Mod/Rocket/Resources/icons/Rocket_FinCan.svg"}
