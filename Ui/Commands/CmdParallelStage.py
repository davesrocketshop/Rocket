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

from Rocket.FeatureParallelStage import FeatureParallelStage
if FreeCAD.GuiUp:
    from Ui.ViewParallelStage import ViewProviderParallelStage
    from Ui.Widgets.WaitCursor import WaitCursor
from Ui.Commands.Command import Command

from Rocket.Constants import FEATURE_PARALLEL_STAGE

translate = FreeCAD.Qt.translate

def _addChild(stage, parent, child) -> None:
    child.Proxy.setParent(parent)
    parent.addObject(child)
    stage.Proxy.positionChildren()

def addToParallelStage(obj):
    stage=FreeCADGui.ActiveDocument.ActiveView.getActiveObject("stage")
    if stage:
        # Add to the last item in the stage if it is a group object
        if len(stage.SubComponent) > 0:
            groupObj = stage.SubComponent[len(stage.SubComponent) - 1]
            if groupObj.Proxy.eligibleChild(obj.Proxy.Type):
                _addChild(stage, groupObj, obj)
                return

        _addChild(stage, stage, obj)

def makeParallelStage(name : str = 'Stage') -> FeatureParallelStage:
    obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython",name)
    FeatureParallelStage(obj)
    obj.Proxy.setDefaults()
    if FreeCAD.GuiUp:
        ViewProviderParallelStage(obj.ViewObject)

    FreeCADGui.ActiveDocument.ActiveView.setActiveObject('stage', obj)
    return obj.Proxy

class CmdParallelStage(Command):
    def Activated(self) -> None:
        with WaitCursor():
            FreeCAD.ActiveDocument.openTransaction("Create rocket parallel stage")
            FreeCADGui.addModule("Ui.Commands.CmdParallelStage")
            FreeCADGui.doCommand("obj=Ui.Commands.CmdParallelStage.makeParallelStage('Stage')")
            FreeCADGui.doCommand("Ui.Commands.CmdStage.addToStage(obj)")
            FreeCADGui.doCommand("FreeCADGui.Selection.clearSelection()")
            FreeCADGui.doCommand("FreeCADGui.Selection.addSelection(obj._obj)")
            FreeCADGui.doCommand("FreeCADGui.activeDocument().setEdit(FreeCAD.ActiveDocument.ActiveObject.Name,0)")

    def IsActive(self) -> bool:
        if FreeCAD.ActiveDocument:
            return self.partStageEligibleFeature(FEATURE_PARALLEL_STAGE)
        return False

    def GetResources(self) -> dict:
        return {'MenuText': translate("Rocket", 'Parallel Stage'),
                'ToolTip': translate("Rocket", 'Adds a parallel stage to the rocket assembly'),
                'Pixmap': FreeCAD.getUserAppDataDir() + "Mod/Rocket/Resources/icons/Rocket_ParallelStage.svg"}


class CmdToggleParallelStage:
    "the ToggleParallelStage command definition"
    def GetResources(self) -> dict:
        return {'MenuText': translate("Rocket","Toggle active stage"),
                'ToolTip' : translate("Rocket","Toggles the active stage")}

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
