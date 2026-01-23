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


"""Class for drawing bulkheads"""

__title__ = "FreeCAD Bulkheads"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

import FreeCAD
import FreeCADGui

from Rocket.FeatureBulkhead import FeatureBulkhead
if FreeCAD.GuiUp:
    from Ui.ViewBulkhead import ViewProviderBulkhead
    from Ui.Widgets.WaitCursor import WaitCursor
from Ui.Commands.Command import Command

from Rocket.Constants import FEATURE_BULKHEAD

translate = FreeCAD.Qt.translate

def makeBulkhead(name : str = 'Bulkhead') -> FeatureBulkhead:
    '''makeBulkhead(name): makes a bulkhead'''
    obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython",name)
    FeatureBulkhead(obj)
    obj.Proxy.setDefaults()
    if FreeCAD.GuiUp:
        ViewProviderBulkhead(obj.ViewObject)

    return obj.Proxy

class CmdBulkhead(Command):
    def Activated(self) -> None:
        with WaitCursor():
            FreeCAD.ActiveDocument.openTransaction("Create bulkhead")
            FreeCADGui.addModule("Ui.Commands.CmdBulkhead")
            FreeCADGui.doCommand("obj=Ui.Commands.CmdBulkhead.makeBulkhead('Bulkhead')")
            FreeCADGui.doCommand("Ui.Commands.CmdStage.addToStage(obj)")
            FreeCADGui.doCommand("FreeCADGui.activeDocument().setEdit(FreeCAD.ActiveDocument.ActiveObject.Name,0)")

    def IsActive(self) -> bool:
        if FreeCAD.ActiveDocument:
            return self.partEligibleFeature(FEATURE_BULKHEAD)
        return False

    def GetResources(self) -> dict:
        return {'MenuText': translate("Rocket", 'Bulkhead'),
                'ToolTip': translate("Rocket", 'Adds a bulkhead to the selected component'),
                'Pixmap': FreeCAD.getUserAppDataDir() + "Mod/Rocket/Resources/icons/Rocket_Bulkhead.svg"}
