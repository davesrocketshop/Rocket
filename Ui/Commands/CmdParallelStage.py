# ***************************************************************************
# *   Copyright (c) 2021-2025 David Carter <dcarter@davidcarter.ca>         *
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

def QT_TRANSLATE_NOOP(context, text):
    return text

def _addChild(stage, parent, child):
    child.Proxy.setParent(parent)
    parent.addObject(child)
    stage.Proxy.positionChildren()

def addToParallelStage(obj):
    stage=FreeCADGui.ActiveDocument.ActiveView.getActiveObject("stage")
    if stage:
        # Add to the last item in the stage if it is a group object
        if len(stage.Group) > 0:
            groupObj = stage.Group[len(stage.Group) - 1]
            if groupObj.Proxy.eligibleChild(obj.Proxy.Type):
                _addChild(stage, groupObj, obj)
                return

        _addChild(stage, stage, obj)

def makeParallelStage(name='Stage'):
    obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython",name)
    FeatureParallelStage(obj)
    obj.Proxy.setDefaults()
    if FreeCAD.GuiUp:
        ViewProviderParallelStage(obj.ViewObject)

    FreeCADGui.ActiveDocument.ActiveView.setActiveObject('stage', obj)
    return obj.Proxy

class CmdParallelStage(Command):
    def Activated(self):
        with WaitCursor():
            FreeCAD.ActiveDocument.openTransaction("Create rocket parallel stage")
            FreeCADGui.addModule("Ui.Commands.CmdParallelStage")
            FreeCADGui.doCommand("obj=Ui.Commands.CmdParallelStage.makeParallelStage('Stage')")
            FreeCADGui.doCommand("Ui.Commands.CmdStage.addToStage(obj)")
            FreeCADGui.doCommand("FreeCADGui.Selection.clearSelection()")
            FreeCADGui.doCommand("FreeCADGui.Selection.addSelection(obj._obj)")
            FreeCADGui.doCommand("FreeCADGui.activeDocument().setEdit(FreeCAD.ActiveDocument.ActiveObject.Name,0)")

    def IsActive(self):
        if FreeCAD.ActiveDocument:
            return self.partStageEligibleFeature(FEATURE_PARALLEL_STAGE)
        return False

    def GetResources(self):
        return {'MenuText': QT_TRANSLATE_NOOP("Rocket", 'Parallel Stage'),
                'ToolTip': QT_TRANSLATE_NOOP("Rocket", 'Rocket Parallel Stage'),
                'Pixmap': FreeCAD.getUserAppDataDir() + "Mod/Rocket/Resources/icons/Rocket_ParallelStage.svg"}


class CmdToggleParallelStage:
    "the ToggleParallelStage command definition"
    def GetResources(self):
        return {'MenuText': QT_TRANSLATE_NOOP("Rocket","Toggle active stage"),
                'ToolTip' : QT_TRANSLATE_NOOP("Rocket","Toggle the active stage")}

    def IsActive(self):
        return bool(FreeCADGui.Selection.getSelection())

    def Activated(self):
        with WaitCursor():
            view = FreeCADGui.ActiveDocument.ActiveView

            for obj in FreeCADGui.Selection.getSelection():
                if view.getActiveObject('stage') == obj:
                    view.setActiveObject("stage", None)
                else:
                    view.setActiveObject("stage", obj)
