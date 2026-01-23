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


"""Class for drawing parachutes"""

__title__ = "FreeCAD Parachutes"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

import FreeCAD
import FreeCADGui

from Rocket.FeatureFin import FeatureFin
if FreeCAD.GuiUp:
    from Ui.ViewParachute import ViewProviderParachute
    from Ui.Widgets.WaitCursor import WaitCursor

translate = FreeCAD.Qt.translate

def makeParachute(name : str) -> FeatureFin:
    '''makeParachute(name): makes a Parachute'''
    obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython",name)
    FeatureFin(obj)
    obj.Proxy.setDefaults()

    if FreeCAD.GuiUp:
        ViewProviderParachute(obj.ViewObject)

    return obj.Proxy

class CmdParachute:
    def Activated(self) -> None:
        with WaitCursor():
            FreeCAD.ActiveDocument.openTransaction("Create parachute")
            FreeCADGui.addModule("Ui.Commands.CmdParachute")
            FreeCADGui.doCommand("obj=Ui.Commands.CmdParachute.makeParachute('Parachute')")
            FreeCADGui.doCommand("Ui.Commands.CmdStage.addToStage(obj)")
            FreeCADGui.doCommand("FreeCADGui.activeDocument().setEdit(FreeCAD.ActiveDocument.ActiveObject.Name,0)")

    def IsActive(self) -> bool:
        if FreeCAD.ActiveDocument:
            return True
        return False

    def GetResources(self) -> dict:
        return {'MenuText': translate("Rocket", 'Parachute'),
                'ToolTip': translate("Rocket", 'Adds a parachute to the selected component'),
                'Pixmap': FreeCAD.getUserAppDataDir() + "Mod/Rocket/Resources/icons/Rocket_Parachute.svg"}
