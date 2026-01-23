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


"""Class for drawing nose cones"""

__title__ = "FreeCAD Nose Cones"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"


import FreeCAD
import FreeCADGui

from Rocket.FeatureStage import FeatureStage
from Ui.Commands.Command import Command, getRocket
if FreeCAD.GuiUp:
    from Ui.ViewStage import ViewProviderStage
    from Ui.Widgets.WaitCursor import WaitCursor

from Rocket.Constants import FEATURE_STAGE

translate = FreeCAD.Qt.translate

def addToStage(obj : FreeCAD.DocumentObject) -> None:
    if FreeCADGui.ActiveDocument is None:
        return

    # Only add when there's an active rocket assembly
    rocket = getRocket()
    if rocket:
        sel = FreeCADGui.Selection.getSelection()
        if sel and hasattr(sel[0], "Proxy"):
            if hasattr(obj, '_obj'):
                sel[0].Proxy.addChild(obj._obj)
            else:
                sel[0].Proxy.addChild(obj)
        FreeCADGui.runCommand('Std_TreeExpand')

def makeStage(name : str = 'Stage') -> FeatureStage:
    # obj = FreeCAD.ActiveDocument.addObject("App::GeometryPython",name)
    obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython",name)
    FeatureStage(obj)
    obj.Proxy.setDefaults()
    if FreeCAD.GuiUp:
        ViewProviderStage(obj.ViewObject)

    FreeCADGui.ActiveDocument.ActiveView.setActiveObject('stage', obj)
    return obj.Proxy

class CmdStage(Command):
    def Activated(self) -> None:
        with WaitCursor():
            FreeCAD.ActiveDocument.openTransaction("Create rocket stage")
            FreeCADGui.addModule("Ui.Commands.CmdStage")
            FreeCADGui.doCommand("obj=Ui.Commands.CmdStage.makeStage('Stage')")
            FreeCADGui.doCommand("Ui.Commands.CmdStage.addToStage(obj)")
            FreeCADGui.doCommand("FreeCADGui.Selection.clearSelection()")
            FreeCADGui.doCommand("FreeCADGui.Selection.addSelection(obj._obj)")
            FreeCADGui.doCommand("App.ActiveDocument.commitTransaction()")
            FreeCADGui.doCommand("App.activeDocument().recompute(None,True,True)")

    def IsActive(self) -> bool:
        if FreeCAD.ActiveDocument:
            return self.partStageEligibleFeature(FEATURE_STAGE)
        return False

    def GetResources(self) -> dict:
        return {'MenuText': translate("Rocket", 'Stage'),
                'ToolTip': translate("Rocket", 'Adds a stage to the rocket assembly'),
                'Pixmap': FreeCAD.getUserAppDataDir() + "Mod/Rocket/Resources/icons/Rocket_Stage.svg"}


class CmdToggleStage:
    "the ToggleStage command definition"
    def GetResources(self) -> dict:
        return {'MenuText': translate("Rocket","Toggle active stage"),
                'ToolTip' : translate("Rocket","Toggle the active stage")}

    def IsActive(self) -> bool:
        return bool(FreeCADGui.Selection.getSelection())

    def Activated(self) -> None:
        with WaitCursor():
            view = FreeCADGui.ActiveDocument.ActiveView

            for obj in FreeCADGui.Selection.getSelection():
                if view.getActiveObject('stage') == obj:
                    view.setActiveObject("stage", None)
                else:
                    view.setActiveObject("stage", obj)
