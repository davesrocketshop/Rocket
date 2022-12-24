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

from App.FeatureRailGuide import FeatureRailGuide
from App.FeatureLaunchLug import FeatureLaunchLug
from App.FeatureRailButton import FeatureRailButton
from Ui.ViewLaunchGuide import ViewProviderRailButton, ViewProviderLaunchLug, ViewProviderRailGuide
from Ui.Commands.Command import Command
from Ui.Commands.CmdStage import addToStage

from App.Constants import FEATURE_LAUNCH_LUG, FEATURE_RAIL_BUTTON, FEATURE_RAIL_GUIDE, FEATURE_OFFSET

from DraftTools import translate

def makeLaunchLug(name='LaunchLug', addToTree=False):
    '''makeLaunchLug(name): makes a Launch Lug'''
    obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython",name)
    FeatureLaunchLug(obj)
    if FreeCAD.GuiUp:
        ViewProviderLaunchLug(obj.ViewObject)

        if addToTree:
            addToStage(obj)
    return obj

def makeRailButton(name='RailButton', addToTree=False):
    '''makeRailButton(name): makes a Rail Button'''
    obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython",name)
    FeatureRailButton(obj)
    if FreeCAD.GuiUp:
        ViewProviderRailButton(obj.ViewObject)

        if addToTree:
            addToStage(obj)
    return obj

def makeRailGuide(name='RailGuide', addToTree=False):
    '''makeRailGuide(name): makes a Launch Guide'''
    obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython",name)
    FeatureRailGuide(obj)
    if FreeCAD.GuiUp:
        ViewProviderRailGuide(obj.ViewObject)

        if addToTree:
            addToStage(obj)
    return obj

class CmdLaunchLug(Command):
    def Activated(self):
        FreeCAD.ActiveDocument.openTransaction("Create launch lug")
        FreeCADGui.addModule("Ui.Commands.CmdLaunchGuides")
        FreeCADGui.doCommand("Ui.Commands.CmdLaunchGuides.makeLaunchLug('LaunchLug', True)")
        FreeCADGui.doCommand("FreeCADGui.activeDocument().setEdit(FreeCAD.ActiveDocument.ActiveObject.Name,0)")

    def IsActive(self):
        if FreeCAD.ActiveDocument:
            return self.part_eligible_feature(FEATURE_LAUNCH_LUG)
        return False
            
    def GetResources(self):
        return {'MenuText': translate("Rocket", 'Launch Lug'),
                'ToolTip': translate("Rocket", 'Launch lug design'),
                'Pixmap': FreeCAD.getUserAppDataDir() + "Mod/Rocket/Resources/icons/Rocket_LaunchLug.svg"}

class CmdRailButton(Command):
    def Activated(self):
        FreeCAD.ActiveDocument.openTransaction("Create rail button")
        FreeCADGui.addModule("Ui.Commands.CmdLaunchGuides")
        FreeCADGui.doCommand("Ui.Commands.CmdLaunchGuides.makeRailButton('RailButton', True)")
        FreeCADGui.doCommand("FreeCADGui.activeDocument().setEdit(FreeCAD.ActiveDocument.ActiveObject.Name,0)")

    def IsActive(self):
        if FreeCAD.ActiveDocument:
            return self.part_eligible_feature(FEATURE_RAIL_BUTTON)
        return False
            
    def GetResources(self):
        return {'MenuText': translate("Rocket", 'Rail Button'),
                'ToolTip': translate("Rocket", 'Rail button design'),
                'Pixmap': FreeCAD.getUserAppDataDir() + "Mod/Rocket/Resources/icons/Rocket_RailButton.svg"}

class CmdRailGuide(Command):
    def Activated(self):
        FreeCAD.ActiveDocument.openTransaction("Create rail guide")
        FreeCADGui.addModule("Ui.Commands.CmdLaunchGuides")
        FreeCADGui.doCommand("Ui.Commands.CmdLaunchGuides.makeRailGuide('RailGuide', True)")
        FreeCADGui.doCommand("FreeCADGui.activeDocument().setEdit(FreeCAD.ActiveDocument.ActiveObject.Name,0)")

    def IsActive(self):
        if FreeCAD.ActiveDocument:
            return self.part_eligible_feature(FEATURE_RAIL_GUIDE)
        return False
            
    def GetResources(self):
        return {'MenuText': translate("Rocket", 'Rail Guide'),
                'ToolTip': translate("Rocket", 'Rail guide design'),
                'Pixmap': FreeCAD.getUserAppDataDir() + "Mod/Rocket/Resources/icons/Rocket_RailGuide.svg"}

class CmdStandOff(Command):
    def Activated(self):
        FreeCAD.ActiveDocument.openTransaction("Create stand off")
        FreeCADGui.addModule("Ui.Commands.CmdLaunchGuides")
        FreeCADGui.doCommand("Ui.Commands.CmdLaunchGuides.makeRailGuide('StandOff', True)")
        FreeCADGui.doCommand("FreeCADGui.activeDocument().setEdit(FreeCAD.ActiveDocument.ActiveObject.Name,0)")

    def IsActive(self):
        if FreeCAD.ActiveDocument:
            return self.part_eligible_feature(FEATURE_OFFSET)
        return False
            
    def GetResources(self):
        return {'MenuText': translate("Rocket", 'Stand Off'),
                'ToolTip': translate("Rocket", 'Stand off design'),
                'Pixmap': FreeCAD.getUserAppDataDir() + "Mod/Rocket/Resources/icons/Rocket_Standoff.svg"}
