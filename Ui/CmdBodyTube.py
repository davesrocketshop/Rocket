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
"""Class for drawing body tubes"""

__title__ = "FreeCAD Body Tubes"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"
    
import FreeCAD
import FreeCADGui

from App.ShapeBodyTube import ShapeBodyTube
from Ui.ViewBodyTube import ViewProviderBodyTube
from Ui.CmdStage import addToStage

from DraftTools import translate

def makeBodyTube(name='BodyTube'):
    '''makeBodyTube(name): makes a Body Tube'''
    obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython",name)
    ShapeBodyTube(obj)
    if FreeCAD.GuiUp:
        ViewProviderBodyTube(obj.ViewObject)

        addToStage(obj)
    return obj

class CmdBodyTube:
    def Activated(self):
        FreeCAD.ActiveDocument.openTransaction("Create body tube")
        FreeCADGui.addModule("Ui.CmdBodyTube")
        FreeCADGui.doCommand("Ui.CmdBodyTube.makeBodyTube('BodyTube')")
        FreeCADGui.doCommand("FreeCADGui.activeDocument().setEdit(FreeCAD.ActiveDocument.ActiveObject.Name,0)")

    def IsActive(self):
        if FreeCAD.ActiveDocument:
            return True
        return False
            
    def GetResources(self):
        return {'MenuText': translate("Rocket", 'Body Tube'),
                'ToolTip': translate("Rocket", 'Body tube design'),
                'Pixmap': FreeCAD.getUserAppDataDir() + "Mod/Rocket/Resources/icons/Rocket_BodyTube.svg"}

class CmdCoupler:
    def Activated(self):
        FreeCAD.ActiveDocument.openTransaction("Create coupler")
        FreeCADGui.addModule("Ui.CmdBodyTube")
        FreeCADGui.doCommand("Ui.CmdBodyTube.makeBodyTube('Coupler')")
        FreeCADGui.doCommand("FreeCADGui.activeDocument().setEdit(FreeCAD.ActiveDocument.ActiveObject.Name,0)")

    def IsActive(self):
        if FreeCAD.ActiveDocument:
            return True
        return False
            
    def GetResources(self):
        return {'MenuText': translate("Rocket", 'Coupler'),
                'ToolTip': translate("Rocket", 'Coupler design'),
                'Pixmap': FreeCAD.getUserAppDataDir() + "Mod/Rocket/Resources/icons/Rocket_BodyTube.svg"}

class CmdInnerTube:
    def Activated(self):
        FreeCAD.ActiveDocument.openTransaction("Create inner tube")
        FreeCADGui.addModule("Ui.CmdBodyTube")
        FreeCADGui.doCommand("Ui.CmdBodyTube.makeBodyTube('InnerTube')")
        FreeCADGui.doCommand("FreeCADGui.activeDocument().setEdit(FreeCAD.ActiveDocument.ActiveObject.Name,0)")

    def IsActive(self):
        if FreeCAD.ActiveDocument:
            return True
        return False
            
    def GetResources(self):
        return {'MenuText': translate("Rocket", 'Inner Tube'),
                'ToolTip': translate("Rocket", 'Inner tube design'),
                'Pixmap': FreeCAD.getUserAppDataDir() + "Mod/Rocket/Resources/icons/Rocket_BodyTube.svg"}
