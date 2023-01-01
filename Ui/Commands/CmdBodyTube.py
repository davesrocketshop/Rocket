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

from App.FeatureBodyTube import FeatureBodyTube
from App.FeatureInnerTube import FeatureInnerTube
from App.FeatureEngineBlock import FeatureEngineBlock
from Ui.ViewBodyTube import ViewProviderBodyTube
from Ui.Commands.Command import Command

from App.Constants import FEATURE_BODY_TUBE, FEATURE_INNER_TUBE, FEATURE_ENGINE_BLOCK

from DraftTools import translate

def makeBodyTube(name='BodyTube'):
    '''makeBodyTube(name): makes a Body Tube'''
    obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython",name)
    FeatureBodyTube(obj)
    if FreeCAD.GuiUp:
        ViewProviderBodyTube(obj.ViewObject)

    return obj.Proxy

def makeInnerTube(name='InnerTube'):
    '''makeInnerTube(name): makes an inner Tube'''
    obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython",name)
    FeatureInnerTube(obj)
    if FreeCAD.GuiUp:
        ViewProviderBodyTube(obj.ViewObject)

    return obj.Proxy

def makeEngineBlock(name='EngineBlock'):
    '''makeInnerTube(name): makes an engine block'''
    obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython",name)
    FeatureEngineBlock(obj)
    if FreeCAD.GuiUp:
        ViewProviderBodyTube(obj.ViewObject)

    return obj.Proxy

class CmdBodyTube(Command):
    def Activated(self):
        FreeCAD.ActiveDocument.openTransaction("Create body tube")
        FreeCADGui.addModule("Ui.Commands.CmdBodyTube")
        FreeCADGui.doCommand("obj=Ui.Commands.CmdBodyTube.makeBodyTube('BodyTube')")
        FreeCADGui.doCommand("Ui.Commands.CmdStage.addToStage(obj)")
        FreeCADGui.doCommand("FreeCADGui.Selection.clearSelection()")
        FreeCADGui.doCommand("FreeCADGui.Selection.addSelection(obj._obj)")
        FreeCADGui.doCommand("FreeCADGui.activeDocument().setEdit(FreeCAD.ActiveDocument.ActiveObject.Name,0)")

    def IsActive(self):
        if FreeCAD.ActiveDocument:
            return self.part_eligible_feature(FEATURE_BODY_TUBE)
        return False
            
    def GetResources(self):
        return {'MenuText': translate("Rocket", 'Body Tube'),
                'ToolTip': translate("Rocket", 'Body tube design'),
                'Pixmap': FreeCAD.getUserAppDataDir() + "Mod/Rocket/Resources/icons/Rocket_BodyTube.svg"}

class CmdCoupler(Command):
    def Activated(self):
        FreeCAD.ActiveDocument.openTransaction("Create coupler")
        FreeCADGui.addModule("Ui.Commands.CmdBodyTube")
        FreeCADGui.doCommand("Ui.Commands.CmdBodyTube.makeBodyTube('Coupler')")
        FreeCADGui.doCommand("FreeCADGui.activeDocument().setEdit(FreeCAD.ActiveDocument.ActiveObject.Name,0)")

    def IsActive(self):
        if FreeCAD.ActiveDocument:
            return self.part_eligible_feature(FEATURE_BODY_TUBE)
        return False
            
    def GetResources(self):
        return {'MenuText': translate("Rocket", 'Coupler'),
                'ToolTip': translate("Rocket", 'Coupler design'),
                'Pixmap': FreeCAD.getUserAppDataDir() + "Mod/Rocket/Resources/icons/Rocket_BodyTube.svg"}

class CmdInnerTube(Command):
    def Activated(self):
        FreeCAD.ActiveDocument.openTransaction("Create inner tube")
        FreeCADGui.addModule("Ui.Commands.CmdBodyTube")
        FreeCADGui.doCommand("obj=Ui.Commands.CmdBodyTube.makeInnerTube('InnerTube')")
        FreeCADGui.doCommand("Ui.Commands.CmdStage.addToStage(obj)")
        FreeCADGui.doCommand("FreeCADGui.Selection.clearSelection()")
        FreeCADGui.doCommand("FreeCADGui.Selection.addSelection(obj._obj)")
        FreeCADGui.doCommand("FreeCADGui.activeDocument().setEdit(FreeCAD.ActiveDocument.ActiveObject.Name,0)")

    def IsActive(self):
        if FreeCAD.ActiveDocument:
            return self.part_eligible_feature(FEATURE_INNER_TUBE)
        return False
            
    def GetResources(self):
        return {'MenuText': translate("Rocket", 'Inner Tube'),
                'ToolTip': translate("Rocket", 'Inner tube design'),
                'Pixmap': FreeCAD.getUserAppDataDir() + "Mod/Rocket/Resources/icons/Rocket_BodyTube.svg"}

class CmdEngineBlock(Command):
    def Activated(self):
        FreeCAD.ActiveDocument.openTransaction("Create engine block")
        FreeCADGui.addModule("Ui.Commands.CmdBodyTube")
        FreeCADGui.doCommand("obj=Ui.Commands.CmdBodyTube.makeEngineBlock('EngineBlock')")
        FreeCADGui.doCommand("Ui.Commands.CmdStage.addToStage(obj)")
        FreeCADGui.doCommand("FreeCADGui.Selection.clearSelection()")
        FreeCADGui.doCommand("FreeCADGui.Selection.addSelection(obj._obj)")
        FreeCADGui.doCommand("FreeCADGui.activeDocument().setEdit(FreeCAD.ActiveDocument.ActiveObject.Name,0)")

    def IsActive(self):
        if FreeCAD.ActiveDocument:
            return self.part_eligible_feature(FEATURE_ENGINE_BLOCK)
        return False
            
    def GetResources(self):
        return {'MenuText': translate("Rocket", 'Engine Block'),
                'ToolTip': translate("Rocket", 'Engine block design'),
                'Pixmap': FreeCAD.getUserAppDataDir() + "Mod/Rocket/Resources/icons/Rocket_BodyTube.svg"}
