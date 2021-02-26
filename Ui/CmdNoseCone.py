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

from App.ShapeNoseCone import ShapeNoseCone
from Ui.ViewNoseCone import ViewProviderNoseCone

def QT_TRANSLATE_NOOP(scope, text):
    return text

def makeNoseCone(name='NoseCone'):
    '''makeNoseCone(name): makes a Nose Cone'''
    obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython",name)
    ShapeNoseCone(obj)
    if FreeCAD.GuiUp:
        ViewProviderNoseCone(obj.ViewObject)

        stage=FreeCADGui.ActiveDocument.ActiveView.getActiveObject("stage")
        if stage:
            stage.Group=stage.Group+[obj]
    return obj

class CmdNoseCone:
    def Activated(self):
        FreeCAD.ActiveDocument.openTransaction("Create nose cone")
        FreeCADGui.addModule("Ui.CmdNoseCone")
        FreeCADGui.doCommand("Ui.CmdNoseCone.makeNoseCone('NoseCone')")
        FreeCADGui.doCommand("FreeCADGui.activeDocument().setEdit(FreeCAD.ActiveDocument.ActiveObject.Name,0)")

    def IsActive(self):
        if FreeCAD.ActiveDocument:
            return True
        return False

    def GetResources(self):
        return {'MenuText': QT_TRANSLATE_NOOP("Rocket_NoseCone", 'Nose Cone'),
                'ToolTip': QT_TRANSLATE_NOOP("Rocket_NoseCone", 'Nose cone design'),
                'Pixmap': FreeCAD.getUserAppDataDir() + "Mod/Rocket/Resources/icons/Rocket_NoseCone.svg"}
