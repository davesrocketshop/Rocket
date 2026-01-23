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


"""Class for drawing fins"""

__title__ = "FreeCAD Fins"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

import FreeCAD
import FreeCADGui

from Rocket.Constants import FEATURE_FIN, FIN_TYPE_SKETCH
from Rocket.FeatureFin import FeatureFin

if FreeCAD.GuiUp:
    from Ui.ViewFin import ViewProviderFin
    from Ui.Widgets.WaitCursor import WaitCursor
from Ui.Commands.Command import Command

translate = FreeCAD.Qt.translate

def makeFin(name : str = 'Fin') -> FeatureFin:
    '''makeFin(name): makes a Fin'''
    obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython",name)
    FeatureFin(obj)
    obj.Proxy.setDefaults()

    # See if we have a sketch selected. If so, this is a custom fin
    if FreeCAD.GuiUp:
        for sketch in FreeCADGui.Selection.getSelection():
            if sketch.isDerivedFrom('Sketcher::SketchObject'):
                obj.FinType = FIN_TYPE_SKETCH
                obj.Profile = sketch
                sketch.Visibility = False

        ViewProviderFin(obj.ViewObject)

    return obj.Proxy

class CmdFin(Command):
    def Activated(self) -> None:
        with WaitCursor():
            FreeCAD.ActiveDocument.openTransaction("Create fin")
            FreeCADGui.addModule("Ui.Commands.CmdFin")
            FreeCADGui.doCommand("obj=Ui.Commands.CmdFin.makeFin('Fin')")
            FreeCADGui.doCommand("Ui.Commands.CmdStage.addToStage(obj)")
            FreeCADGui.doCommand("FreeCADGui.Selection.clearSelection()")
            FreeCADGui.doCommand("FreeCADGui.Selection.addSelection(obj._obj)")
            FreeCADGui.doCommand("FreeCADGui.activeDocument().setEdit(FreeCAD.ActiveDocument.ActiveObject.Name,0)")

    def IsActive(self) -> bool:
        if FreeCAD.ActiveDocument:
            return self.partEligibleFeature(FEATURE_FIN)
        return False

    def GetResources(self) -> dict:
        return {'MenuText': translate("Rocket", 'Fin'),
                'ToolTip': translate("Rocket", 'Adds a fin or fin set to the selected component'),
                'Pixmap': FreeCAD.getUserAppDataDir() + "Mod/Rocket/Resources/icons/Rocket_Fin.svg"}
