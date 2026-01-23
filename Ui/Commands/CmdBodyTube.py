# SPDX-License-Identifier: LGPL-2.1-or-later
# SPDX-File-Notice: Part of the Rocket addon.

################################################################################
#                                                                              #
#   © 2021 David Carter <dcarter@davidcarter.ca>                               #
#                                                                              #
#   This addon is free software: you can redistribute it and/or modify         #
#   it under the terms of the GNU Lesser General Public License as             #
#   published by the Free Software Foundation, either version 2.1              #
#   of the License, or (at your option) any later version.                     #
#                                                                              #
#   This addon is distributed in the hope that it will be useful,              #
#   but WITHOUT ANY WARRANTY; without even the implied warranty                #
#   of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.                    #
#   See the GNU Lesser General Public License for more details.                #
#                                                                              #
#   You should have received a copy of the GNU Lesser General Public           #
#   License along with this addon. If not, see https://www.gnu.org/licenses    #
#                                                                              #
################################################################################


"""Class for drawing body tubes"""

__title__ = "FreeCAD Body Tubes"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

import FreeCAD
import FreeCADGui

from Rocket.FeatureBodyTube import FeatureBodyTube
from Rocket.FeatureInnerTube import FeatureInnerTube
from Rocket.FeatureTubeCoupler import FeatureTubeCoupler
from Rocket.FeatureEngineBlock import FeatureEngineBlock
if FreeCAD.GuiUp:
    from Ui.ViewBodyTube import ViewProviderBodyTube, ViewProviderInnerTube, ViewProviderCoupler, ViewProviderEngineBlock
    from Ui.Widgets.WaitCursor import WaitCursor
from Ui.Commands.Command import Command

from Rocket.Constants import FEATURE_BODY_TUBE, FEATURE_INNER_TUBE, FEATURE_TUBE_COUPLER, FEATURE_ENGINE_BLOCK

translate = FreeCAD.Qt.translate

def makeBodyTube(name : str = 'BodyTube') -> FeatureBodyTube:
    '''makeBodyTube(name): makes a Body Tube'''
    obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython",name)
    FeatureBodyTube(obj)
    obj.Proxy.setDefaults()
    if FreeCAD.GuiUp:
        ViewProviderBodyTube(obj.ViewObject)

    return obj.Proxy

def makeInnerTube(name : str = 'InnerTube') -> FeatureInnerTube:
    '''makeInnerTube(name): makes an inner Tube'''
    obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython",name)
    FeatureInnerTube(obj)
    obj.Proxy.setDefaults()
    if FreeCAD.GuiUp:
        ViewProviderInnerTube(obj.ViewObject)

    return obj.Proxy

def makeCoupler(name : str = 'Coupler') -> FeatureTubeCoupler:
    '''makeCoupler(name): makes a tube coupler'''
    obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython",name)
    FeatureTubeCoupler(obj)
    obj.Proxy.setDefaults()
    if FreeCAD.GuiUp:
        ViewProviderCoupler(obj.ViewObject)

    return obj.Proxy

def makeEngineBlock(name : str = 'EngineBlock') -> FeatureEngineBlock:
    '''makeInnerTube(name): makes an engine block'''
    obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython",name)
    FeatureEngineBlock(obj)
    obj.Proxy.setDefaults()
    if FreeCAD.GuiUp:
        ViewProviderEngineBlock(obj.ViewObject)

    return obj.Proxy

class CmdBodyTube(Command):
    def Activated(self) -> None:
        with WaitCursor():
            FreeCAD.ActiveDocument.openTransaction("Create body tube")
            FreeCADGui.addModule("Ui.Commands.CmdBodyTube")
            FreeCADGui.doCommand("obj=Ui.Commands.CmdBodyTube.makeBodyTube('BodyTube')")
            FreeCADGui.doCommand("Ui.Commands.CmdStage.addToStage(obj)")
            FreeCADGui.doCommand("FreeCADGui.Selection.clearSelection()")
            FreeCADGui.doCommand("FreeCADGui.Selection.addSelection(obj._obj)")
            FreeCADGui.doCommand("FreeCADGui.activeDocument().setEdit(FreeCAD.ActiveDocument.ActiveObject.Name,0)")

    def IsActive(self) -> bool:
        if FreeCAD.ActiveDocument:
            return self.partEligibleFeature(FEATURE_BODY_TUBE)
        return False

    def GetResources(self) -> dict:
        return {'MenuText': translate("Rocket", 'Body Tube'),
                'ToolTip': translate("Rocket", 'Adds a body tube to the selected pod or stage'),
                'Pixmap': FreeCAD.getUserAppDataDir() + "Mod/Rocket/Resources/icons/Rocket_BodyTube.svg"}

class CmdCoupler(Command):
    def Activated(self) -> None:
        with WaitCursor():
            FreeCAD.ActiveDocument.openTransaction("Create coupler")
            FreeCADGui.addModule("Ui.Commands.CmdBodyTube")
            FreeCADGui.doCommand("obj=Ui.Commands.CmdBodyTube.makeCoupler('Coupler')")
            FreeCADGui.doCommand("Ui.Commands.CmdStage.addToStage(obj)")
            FreeCADGui.doCommand("FreeCADGui.Selection.clearSelection()")
            FreeCADGui.doCommand("FreeCADGui.Selection.addSelection(obj._obj)")
            FreeCADGui.doCommand("FreeCADGui.activeDocument().setEdit(FreeCAD.ActiveDocument.ActiveObject.Name,0)")

    def IsActive(self) -> bool:
        if FreeCAD.ActiveDocument:
            return self.partEligibleFeature(FEATURE_TUBE_COUPLER)
        return False

    def GetResources(self) -> dict:
        return {'MenuText': translate("Rocket", 'Coupler'),
                'ToolTip': translate("Rocket", 'Adds a coupler to the selected component'),
                'Pixmap': FreeCAD.getUserAppDataDir() + "Mod/Rocket/Resources/icons/Rocket_Coupler.svg"}

class CmdInnerTube(Command):
    def Activated(self) -> None:
        with WaitCursor():
            FreeCAD.ActiveDocument.openTransaction("Create inner tube")
            FreeCADGui.addModule("Ui.Commands.CmdBodyTube")
            FreeCADGui.doCommand("obj=Ui.Commands.CmdBodyTube.makeInnerTube('InnerTube')")
            FreeCADGui.doCommand("Ui.Commands.CmdStage.addToStage(obj)")
            FreeCADGui.doCommand("FreeCADGui.Selection.clearSelection()")
            FreeCADGui.doCommand("FreeCADGui.Selection.addSelection(obj._obj)")
            FreeCADGui.doCommand("FreeCADGui.activeDocument().setEdit(FreeCAD.ActiveDocument.ActiveObject.Name,0)")

    def IsActive(self) -> bool:
        if FreeCAD.ActiveDocument:
            return self.partEligibleFeature(FEATURE_INNER_TUBE)
        return False

    def GetResources(self) -> dict:
        return {'MenuText': translate("Rocket", 'Inner Tube'),
                'ToolTip': translate("Rocket", 'Adds an inner tube or motor mount to the selected component'),
                'Pixmap': FreeCAD.getUserAppDataDir() + "Mod/Rocket/Resources/icons/Rocket_InnerTube.svg"}

class CmdEngineBlock(Command):
    def Activated(self) -> None:
        with WaitCursor():
            FreeCAD.ActiveDocument.openTransaction("Create engine block")
            FreeCADGui.addModule("Ui.Commands.CmdBodyTube")
            FreeCADGui.doCommand("obj=Ui.Commands.CmdBodyTube.makeEngineBlock('EngineBlock')")
            FreeCADGui.doCommand("Ui.Commands.CmdStage.addToStage(obj)")
            FreeCADGui.doCommand("FreeCADGui.Selection.clearSelection()")
            FreeCADGui.doCommand("FreeCADGui.Selection.addSelection(obj._obj)")
            FreeCADGui.doCommand("FreeCADGui.activeDocument().setEdit(FreeCAD.ActiveDocument.ActiveObject.Name,0)")

    def IsActive(self) -> bool:
        if FreeCAD.ActiveDocument:
            return self.partEligibleFeature(FEATURE_ENGINE_BLOCK)
        return False

    def GetResources(self) -> dict:
        return {'MenuText': translate("Rocket", 'Engine Block'),
                'ToolTip': translate("Rocket", 'Adds an engine block to the selected component'),
                'Pixmap': FreeCAD.getUserAppDataDir() + "Mod/Rocket/Resources/icons/Rocket_EngineBlock.svg"}
