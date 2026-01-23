# SPDX-License-Identifier: LGPL-2.1-or-later
# SPDX-File-Notice: Part of the Rocket addon.

################################################################################
#                                                                              #
#   © 2025 David Carter <dcarter@davidcarter.ca>                               #
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


"""Class for drawing ring tails"""

__title__ = "FreeCAD Ring Tails"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

import FreeCAD
import FreeCADGui

from Rocket.FeatureRingtail import FeatureRingtail
if FreeCAD.GuiUp:
    from Ui.ViewRingtail import ViewProviderRingtail
    from Ui.Widgets.WaitCursor import WaitCursor
from Ui.Commands.Command import Command

from Rocket.Constants import FEATURE_RINGTAIL

translate = FreeCAD.Qt.translate

def makeRingtail(name : str = 'Ringtail') -> FeatureRingtail:
    '''makeRingtail(name): makes a ring tail'''
    obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython",name)
    FeatureRingtail(obj)
    obj.Proxy.setDefaults()
    if FreeCAD.GuiUp:
        ViewProviderRingtail(obj.ViewObject)

    return obj.Proxy

class CmdRingtail(Command):
    def Activated(self) -> None:
        with WaitCursor():
            FreeCAD.ActiveDocument.openTransaction("Create ring tail")
            FreeCADGui.addModule("Ui.Commands.CmdRingtail")
            FreeCADGui.doCommand("obj=Ui.Commands.CmdRingtail.makeRingtail('Ringtail')")
            FreeCADGui.doCommand("Ui.Commands.CmdStage.addToStage(obj)")
            FreeCADGui.doCommand("FreeCADGui.Selection.clearSelection()")
            FreeCADGui.doCommand("FreeCADGui.Selection.addSelection(obj._obj)")
            FreeCADGui.doCommand("FreeCADGui.activeDocument().setEdit(FreeCAD.ActiveDocument.ActiveObject.Name,0)")

    def IsActive(self) -> bool:
        if FreeCAD.ActiveDocument:
            return self.partEligibleFeature(FEATURE_RINGTAIL)
        return False

    def GetResources(self) -> dict:
        return {'MenuText': translate("Rocket", 'Ring tail'),
                'ToolTip': translate("Rocket", 'Adds a ring tail to the selected component'),
                'Pixmap': FreeCAD.getUserAppDataDir() + "Mod/Rocket/Resources/icons/Rocket_Ringtail.svg"}
