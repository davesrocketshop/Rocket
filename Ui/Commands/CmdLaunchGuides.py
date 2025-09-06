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
"""Class for drawing launch guides"""

__title__ = "FreeCAD Launch Guides"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

import FreeCAD
import FreeCADGui

from Rocket.FeatureRailGuide import FeatureRailGuide
from Rocket.FeatureLaunchLug import FeatureLaunchLug
from Rocket.FeatureRailButton import FeatureRailButton
if FreeCAD.GuiUp:
    from Ui.ViewLaunchGuide import ViewProviderRailButton, ViewProviderLaunchLug, ViewProviderRailGuide
    from Ui.Widgets.WaitCursor import WaitCursor
from Ui.Commands.Command import Command

from Rocket.Constants import FEATURE_LAUNCH_LUG, FEATURE_RAIL_BUTTON, FEATURE_RAIL_GUIDE, FEATURE_OFFSET

from Rocket.Utilities import translate

def makeLaunchLug(name='LaunchLug'):
    '''makeLaunchLug(name): makes a Launch Lug'''
    obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython",name)
    FeatureLaunchLug(obj)
    obj.Proxy.setDefaults()
    if FreeCAD.GuiUp:
        ViewProviderLaunchLug(obj.ViewObject)

    return obj.Proxy

def makeRailButton(name='RailButton'):
    '''makeRailButton(name): makes a Rail Button'''
    obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython",name)
    FeatureRailButton(obj)
    obj.Proxy.setDefaults()
    if FreeCAD.GuiUp:
        ViewProviderRailButton(obj.ViewObject)

    return obj.Proxy

def makeRailGuide(name='RailGuide'):
    '''makeRailGuide(name): makes a Launch Guide'''
    obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython",name)
    FeatureRailGuide(obj)
    obj.Proxy.setDefaults()
    if FreeCAD.GuiUp:
        ViewProviderRailGuide(obj.ViewObject)

    return obj.Proxy

class CmdLaunchLug(Command):
    def Activated(self):
        with WaitCursor():
            FreeCAD.ActiveDocument.openTransaction("Create launch lug")
            FreeCADGui.addModule("Ui.Commands.CmdLaunchGuides")
            FreeCADGui.doCommand("obj=Ui.Commands.CmdLaunchGuides.makeLaunchLug('LaunchLug')")
            FreeCADGui.doCommand("Ui.Commands.CmdStage.addToStage(obj)")
            FreeCADGui.doCommand("FreeCADGui.activeDocument().setEdit(FreeCAD.ActiveDocument.ActiveObject.Name,0)")

    def IsActive(self):
        if FreeCAD.ActiveDocument:
            return self.partEligibleFeature(FEATURE_LAUNCH_LUG)
        return False

    def GetResources(self):
        return {'MenuText': translate("Rocket", 'Launch Lug'),
                'ToolTip': translate("Rocket", 'Launch lug design'),
                'Pixmap': FreeCAD.getUserAppDataDir() + "Mod/Rocket/Resources/icons/Rocket_LaunchLug.svg"}

class CmdRailButton(Command):
    def Activated(self):
        with WaitCursor():
            FreeCAD.ActiveDocument.openTransaction("Create rail button")
            FreeCADGui.addModule("Ui.Commands.CmdLaunchGuides")
            FreeCADGui.doCommand("obj=Ui.Commands.CmdLaunchGuides.makeRailButton('RailButton')")
            FreeCADGui.doCommand("Ui.Commands.CmdStage.addToStage(obj)")
            FreeCADGui.doCommand("FreeCADGui.activeDocument().setEdit(FreeCAD.ActiveDocument.ActiveObject.Name,0)")

    def IsActive(self):
        if FreeCAD.ActiveDocument:
            return self.partEligibleFeature(FEATURE_RAIL_BUTTON)
        return False

    def GetResources(self):
        return {'MenuText': translate("Rocket", 'Rail Button'),
                'ToolTip': translate("Rocket", 'Rail button design'),
                'Pixmap': FreeCAD.getUserAppDataDir() + "Mod/Rocket/Resources/icons/Rocket_RailButton.svg"}

class CmdRailGuide(Command):
    def Activated(self):
        with WaitCursor():
            FreeCAD.ActiveDocument.openTransaction("Create rail guide")
            FreeCADGui.addModule("Ui.Commands.CmdLaunchGuides")
            FreeCADGui.doCommand("obj=Ui.Commands.CmdLaunchGuides.makeRailGuide('RailGuide')")
            FreeCADGui.doCommand("Ui.Commands.CmdStage.addToStage(obj)")
            FreeCADGui.doCommand("FreeCADGui.activeDocument().setEdit(FreeCAD.ActiveDocument.ActiveObject.Name,0)")

    def IsActive(self):
        if FreeCAD.ActiveDocument:
            return self.partEligibleFeature(FEATURE_RAIL_GUIDE)
        return False

    def GetResources(self):
        return {'MenuText': translate("Rocket", 'Rail Guide'),
                'ToolTip': translate("Rocket", 'Rail guide design'),
                'Pixmap': FreeCAD.getUserAppDataDir() + "Mod/Rocket/Resources/icons/Rocket_RailGuide.svg"}

class CmdStandOff(Command):
    def Activated(self):
        with WaitCursor():
            FreeCAD.ActiveDocument.openTransaction("Create stand off")
            FreeCADGui.addModule("Ui.Commands.CmdLaunchGuides")
            FreeCADGui.doCommand("obj=Ui.Commands.CmdLaunchGuides.makeRailGuide('StandOff')")
            FreeCADGui.doCommand("Ui.Commands.CmdStage.addToStage(obj)")
            FreeCADGui.doCommand("FreeCADGui.activeDocument().setEdit(FreeCAD.ActiveDocument.ActiveObject.Name,0)")

    def IsActive(self):
        if FreeCAD.ActiveDocument:
            return self.partEligibleFeature(FEATURE_OFFSET)
        return False

    def GetResources(self):
        return {'MenuText': translate("Rocket", 'Stand Off'),
                'ToolTip': translate("Rocket", 'Stand off design'),
                'Pixmap': FreeCAD.getUserAppDataDir() + "Mod/Rocket/Resources/icons/Rocket_Standoff.svg"}
