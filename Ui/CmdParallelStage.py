# ***************************************************************************
# *   Copyright (c) 2021 David Carter <dcarter@davidcarter.ca>              *
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
from PySide import QtGui

from App.ShapeStage import ShapeStage
from Ui.ViewParallelStage import ViewProviderParallelStage

from DraftTools import translate

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
    ShapeStage(obj)
    if FreeCAD.GuiUp:
        ViewProviderParallelStage(obj.ViewObject)

        rocket=FreeCADGui.ActiveDocument.ActiveView.getActiveObject("rocket")
        if rocket:
            rocket.Group=rocket.Group+[obj]

    FreeCADGui.ActiveDocument.ActiveView.setActiveObject('stage', obj)
    return obj

class CmdParallelStage:
    def Activated(self):
        FreeCAD.ActiveDocument.openTransaction("Create rocket parallel stage")
        FreeCADGui.addModule("Ui.CmdParallelStage")
        FreeCADGui.doCommand("Ui.CmdParallelStage.makeParallelStage('Stage')")
        FreeCADGui.doCommand("App.activeDocument().recompute(None,True,True)")

    def IsActive(self):
        if FreeCAD.ActiveDocument:
            return True
        return False

    def GetResources(self):
        return {'MenuText': translate("Rocket", 'Parallel Stage'),
                'ToolTip': translate("Rocket", 'Rocket Parallel Stage'),
                'Pixmap': FreeCAD.getUserAppDataDir() + "Mod/Rocket/Resources/icons/Rocket_ParallelStage.svg"}


class CmdToggleParallelStage:
    "the ToggleParallelStage command definition"
    def GetResources(self):
        return {'MenuText': translate("Rocket","Toggle active stage"),
                'ToolTip' : translate("Rocket","Toggle the active stage")}

    def IsActive(self):
        return bool(FreeCADGui.Selection.getSelection())

    def Activated(self):
        view = FreeCADGui.ActiveDocument.ActiveView

        for obj in FreeCADGui.Selection.getSelection():
            if view.getActiveObject('stage') == obj:
                view.setActiveObject("stage", None)
            else:
                view.setActiveObject("stage", obj)
