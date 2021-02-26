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
"""Class for drawing rocket assemblies"""

__title__ = "FreeCAD Rocket Assembly"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"
    

import FreeCAD
import FreeCADGui
from PySide import QtGui

from App.ShapeRocket import ShapeRocket
from Ui.ViewRocket import ViewProviderRocket
from Ui.CmdStage import makeStage

def QT_TRANSLATE_NOOP(scope, text):
    return text

def makeRocket(name='Rocket', makeSustainer=True):
    obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython",name)
    ShapeRocket(obj)
    if FreeCAD.GuiUp:
        ViewProviderRocket(obj.ViewObject)

        # body=FreeCADGui.ActiveDocument.ActiveView.getActiveObject("pdbody")
        # part=FreeCADGui.ActiveDocument.ActiveView.getActiveObject("part")
        # if body:
        #     body.Group=body.Group+[obj]
        # elif part:
        #     part.Group=part.Group+[obj]

    if makeSustainer:
        sustainer = makeStage()
        sustainer.Label = 'Sustainer'
        obj.addObject(sustainer)
        FreeCADGui.ActiveDocument.ActiveView.setActiveObject('stage', sustainer)
    
    FreeCADGui.ActiveDocument.ActiveView.setActiveObject('rocket', obj)
    return obj

class CmdRocket:
    def Activated(self):
        FreeCAD.ActiveDocument.openTransaction("Create rocket assembly")
        FreeCADGui.addModule("Ui.CmdRocket")
        FreeCADGui.doCommand("Ui.CmdRocket.makeRocket('Rocket')")
        FreeCADGui.doCommand("FreeCADGui.activeDocument().setEdit(FreeCAD.ActiveDocument.ActiveObject.Name,0)")

    def IsActive(self):
        if FreeCAD.ActiveDocument:
            return True
        return False

    def GetResources(self):
        return {'MenuText': QT_TRANSLATE_NOOP("Rocket_Rocket", 'Rocket'),
                'ToolTip': QT_TRANSLATE_NOOP("Rocket_Rocket", 'Rocket assembly'),
                'Pixmap': FreeCAD.getUserAppDataDir() + "Mod/Rocket/Resources/icons/Rocket_Rocket.svg"}
