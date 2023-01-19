# ***************************************************************************
# *   Copyright (c) 2021-2023 David Carter <dcarter@davidcarter.ca>         *
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

from App.FeatureStage import FeatureStage
from Ui.Commands.Command import Command
from Ui.ViewStage import ViewProviderStage

from App.Constants import FEATURE_STAGE, FEATURE_ROCKET


from DraftTools import translate

def getRocket():
    for obj in FreeCAD.ActiveDocument.Objects:
        if hasattr(obj, "Proxy"):
            if hasattr(obj.Proxy, "getType"):
                if obj.Proxy.getType() == FEATURE_ROCKET:
                    return obj.Proxy

    return None

def addToStage(obj):
    if FreeCADGui.ActiveDocument is None:
        return

    # Only add when there's an active rocket assembly
    rocket = getRocket()
    if rocket is not None:
        sel = FreeCADGui.Selection.getSelection()
        if sel:
            if hasattr(obj, '_obj'):
                sel[0].Proxy.addChild(obj._obj)
            else:
                sel[0].Proxy.addChild(obj)
        FreeCADGui.runCommand('Std_TreeExpand')

def makeStage(name='Stage'):
    obj = FreeCAD.ActiveDocument.addObject("App::GeometryPython",name)
    FeatureStage(obj)
    obj.Proxy.setDefaults()
    if FreeCAD.GuiUp:
        ViewProviderStage(obj.ViewObject)

    FreeCADGui.ActiveDocument.ActiveView.setActiveObject('stage', obj)
    return obj.Proxy

class CmdStage(Command):
    def Activated(self):
        FreeCAD.ActiveDocument.openTransaction("Create rocket stage")
        FreeCADGui.addModule("Ui.Commands.CmdStage")
        FreeCADGui.doCommand("obj=Ui.Commands.CmdStage.makeStage('Stage')")
        FreeCADGui.doCommand("Ui.Commands.CmdStage.addToStage(obj)")
        FreeCADGui.doCommand("FreeCADGui.Selection.clearSelection()")
        FreeCADGui.doCommand("FreeCADGui.Selection.addSelection(obj._obj)")
        FreeCADGui.doCommand("App.activeDocument().recompute(None,True,True)")

    def IsActive(self):
        if FreeCAD.ActiveDocument:
            return self.part_stage_eligible_feature(FEATURE_STAGE)
        return False

    def GetResources(self):
        return {'MenuText': translate("Rocket", 'Stage'),
                'ToolTip': translate("Rocket", 'Rocket Stage'),
                'Pixmap': FreeCAD.getUserAppDataDir() + "Mod/Rocket/Resources/icons/Rocket_Stage.svg"}


class CmdToggleStage:
    "the ToggleStage command definition"
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
