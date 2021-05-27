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
"""Class for drawing launch guides"""

__title__ = "FreeCAD Launch Guides"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"
    
import FreeCAD
import FreeCADGui

from App.ShapeBodyTube import ShapeBodyTube
from App.ShapeLaunchLug import ShapeLaunchLug
from Ui.ViewBodyTube import ViewProviderBodyTube
from Ui.CmdStage import addToStage

from DraftTools import translate

def makeLaunchLug(name='LaunchLug'):
    '''makeBodyTube(name): makes a Launch Lug'''
    obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython",name)
    ShapeLaunchLug(obj)
    if FreeCAD.GuiUp:
        ViewProviderBodyTube(obj.ViewObject)

        addToStage(obj)
    return obj

def makeLaunchGuide(name='LaunchGuide'):
    '''makeBodyTube(name): makes a Launch Guide'''
    obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython",name)
    ShapeBodyTube(obj)
    if FreeCAD.GuiUp:
        ViewProviderBodyTube(obj.ViewObject)

        addToStage(obj)
    return obj

class CmdLaunchLug:
    def Activated(self):
        FreeCAD.ActiveDocument.openTransaction("Create launch lug")
        FreeCADGui.addModule("Ui.CmdLaunchGuides")
        FreeCADGui.doCommand("Ui.CmdLaunchGuides.makeLaunchLug('LaunchLug')")
        FreeCADGui.doCommand("FreeCADGui.activeDocument().setEdit(FreeCAD.ActiveDocument.ActiveObject.Name,0)")

    def IsActive(self):
        if FreeCAD.ActiveDocument:
            return True
        return False
            
    def GetResources(self):
        return {'MenuText': translate("Rocket", 'Launch Lug'),
                'ToolTip': translate("Rocket", 'Launch lug design'),
                'Pixmap': FreeCAD.getUserAppDataDir() + "Mod/Rocket/Resources/icons/Rocket_BodyTube.svg"}

class CmdRailButton:
    def Activated(self):
        FreeCAD.ActiveDocument.openTransaction("Create rail button")
        FreeCADGui.addModule("Ui.CmdLaunchGuides")
        FreeCADGui.doCommand("Ui.CmdLaunchGuides.makeLaunchGuide('RailButton')")
        FreeCADGui.doCommand("FreeCADGui.activeDocument().setEdit(FreeCAD.ActiveDocument.ActiveObject.Name,0)")

    def IsActive(self):
        if FreeCAD.ActiveDocument:
            return True
        return False
            
    def GetResources(self):
        return {'MenuText': translate("Rocket", 'Rail Button'),
                'ToolTip': translate("Rocket", 'Rail button design'),
                'Pixmap': FreeCAD.getUserAppDataDir() + "Mod/Rocket/Resources/icons/Rocket_BodyTube.svg"}

class CmdLaunchGuide:
    def Activated(self):
        FreeCAD.ActiveDocument.openTransaction("Create launch guide")
        FreeCADGui.addModule("Ui.CmdLaunchGuides")
        FreeCADGui.doCommand("Ui.CmdLaunchGuides.makeLaunchGuide('LaunchGuide')")
        FreeCADGui.doCommand("FreeCADGui.activeDocument().setEdit(FreeCAD.ActiveDocument.ActiveObject.Name,0)")

    def IsActive(self):
        if FreeCAD.ActiveDocument:
            return True
        return False
            
    def GetResources(self):
        return {'MenuText': translate("Rocket", 'Launch Guide'),
                'ToolTip': translate("Rocket", 'Launch guide design'),
                'Pixmap': FreeCAD.getUserAppDataDir() + "Mod/Rocket/Resources/icons/Rocket_BodyTube.svg"}

class CmdStandOff:
    def Activated(self):
        FreeCAD.ActiveDocument.openTransaction("Create stand off")
        FreeCADGui.addModule("Ui.CmdLaunchGuides")
        FreeCADGui.doCommand("Ui.CmdLaunchGuides.makeLaunchGuide('StandOff')")
        FreeCADGui.doCommand("FreeCADGui.activeDocument().setEdit(FreeCAD.ActiveDocument.ActiveObject.Name,0)")

    def IsActive(self):
        if FreeCAD.ActiveDocument:
            return True
        return False
            
    def GetResources(self):
        return {'MenuText': translate("Rocket", 'Stand Off'),
                'ToolTip': translate("Rocket", 'Stand off design'),
                'Pixmap': FreeCAD.getUserAppDataDir() + "Mod/Rocket/Resources/icons/Rocket_BodyTube.svg"}
