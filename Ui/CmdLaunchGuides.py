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

from App.ShapeRailGuide import ShapeRailGuide
from App.ShapeLaunchLug import ShapeLaunchLug
from App.ShapeRailButton import ShapeRailButton
from Ui.ViewLaunchGuide import ViewProviderRailButton, ViewProviderLaunchLug, ViewProviderRailGuide
from Ui.CmdStage import addToStage

from DraftTools import translate

def makeLaunchLug(name='LaunchLug'):
    '''makeLaunchLug(name): makes a Launch Lug'''
    obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython",name)
    ShapeLaunchLug(obj)
    if FreeCAD.GuiUp:
        ViewProviderLaunchLug(obj.ViewObject)

        addToStage(obj)
    return obj

def makeRailButton(name='RailButton'):
    '''makeRailButton(name): makes a Rail Button'''
    obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython",name)
    ShapeRailButton(obj)
    if FreeCAD.GuiUp:
        ViewProviderRailButton(obj.ViewObject)

        addToStage(obj)
    return obj

def makeRailGuide(name='RailGuide'):
    '''makeRailGuide(name): makes a Launch Guide'''
    obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython",name)
    ShapeRailGuide(obj)
    if FreeCAD.GuiUp:
        ViewProviderRailGuide(obj.ViewObject)

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
                'Pixmap': FreeCAD.getUserAppDataDir() + "Mod/Rocket/Resources/icons/Rocket_LaunchLug.svg"}

class CmdRailButton:
    def Activated(self):
        FreeCAD.ActiveDocument.openTransaction("Create rail button")
        FreeCADGui.addModule("Ui.CmdLaunchGuides")
        FreeCADGui.doCommand("Ui.CmdLaunchGuides.makeRailButton('RailButton')")
        FreeCADGui.doCommand("FreeCADGui.activeDocument().setEdit(FreeCAD.ActiveDocument.ActiveObject.Name,0)")

    def IsActive(self):
        if FreeCAD.ActiveDocument:
            return True
        return False
            
    def GetResources(self):
        return {'MenuText': translate("Rocket", 'Rail Button'),
                'ToolTip': translate("Rocket", 'Rail button design'),
                'Pixmap': FreeCAD.getUserAppDataDir() + "Mod/Rocket/Resources/icons/Rocket_RailButton.svg"}

class CmdRailGuide:
    def Activated(self):
        FreeCAD.ActiveDocument.openTransaction("Create rail guide")
        FreeCADGui.addModule("Ui.CmdLaunchGuides")
        FreeCADGui.doCommand("Ui.CmdLaunchGuides.makeRailGuide('RailGuide')")
        FreeCADGui.doCommand("FreeCADGui.activeDocument().setEdit(FreeCAD.ActiveDocument.ActiveObject.Name,0)")

    def IsActive(self):
        if FreeCAD.ActiveDocument:
            return True
        return False
            
    def GetResources(self):
        return {'MenuText': translate("Rocket", 'Rail Guide'),
                'ToolTip': translate("Rocket", 'Rail guide design'),
                'Pixmap': FreeCAD.getUserAppDataDir() + "Mod/Rocket/Resources/icons/Rocket_RailGuide.svg"}

class CmdStandOff:
    def Activated(self):
        FreeCAD.ActiveDocument.openTransaction("Create stand off")
        FreeCADGui.addModule("Ui.CmdLaunchGuides")
        FreeCADGui.doCommand("Ui.CmdLaunchGuides.makeRailGuide('StandOff')")
        FreeCADGui.doCommand("FreeCADGui.activeDocument().setEdit(FreeCAD.ActiveDocument.ActiveObject.Name,0)")

    def IsActive(self):
        if FreeCAD.ActiveDocument:
            return True
        return False
            
    def GetResources(self):
        return {'MenuText': translate("Rocket", 'Stand Off'),
                'ToolTip': translate("Rocket", 'Stand off design'),
                'Pixmap': FreeCAD.getUserAppDataDir() + "Mod/Rocket/Resources/icons/Rocket_Standoff.svg"}
