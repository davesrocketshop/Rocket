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
from Ui.ViewStage import ViewProviderStage

def QT_TRANSLATE_NOOP(scope, text):
    return text

def makeStage(name='Stage'):
    obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython",name)
    ShapeStage(obj)
    if FreeCAD.GuiUp:
        ViewProviderStage(obj.ViewObject)

        rocket=FreeCADGui.ActiveDocument.ActiveView.getActiveObject("rocket")
        if rocket:
            rocket.Group=rocket.Group+[obj]

    FreeCADGui.ActiveDocument.ActiveView.setActiveObject('stage', obj)
    return obj

class CmdStage:
    def Activated(self):
        FreeCAD.ActiveDocument.openTransaction("Create rocket stage")
        FreeCADGui.addModule("Ui.CmdStage")
        FreeCADGui.doCommand("Ui.CmdStage.makeStage('Stage')")
        FreeCADGui.doCommand("FreeCADGui.activeDocument().setEdit(FreeCAD.ActiveDocument.ActiveObject.Name,0)")

    def IsActive(self):
        if FreeCAD.ActiveDocument:
            return True
        return False

    def GetResources(self):
        return {'MenuText': QT_TRANSLATE_NOOP("Rocket_Stage", 'Stage'),
                'ToolTip': QT_TRANSLATE_NOOP("Rocket_Stage", 'Rocket Stage'),
                'Pixmap': FreeCAD.getUserAppDataDir() + "Mod/Rocket/Resources/icons/Rocket_Stage.svg"}
