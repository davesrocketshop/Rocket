# SPDX-License-Identifier: LGPL-2.1-or-later
# SPDX-FileCopyrightText: 2021 David Carter <dcarter@davidcarter.ca>
# SPDX-File-Notice: Part of the Rocket addon.


"""Class for drawing parachutes"""

__title__ = "FreeCAD Parachutes"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

import FreeCAD
import FreeCADGui

from Rocket.FeatureFin import FeatureFin
if FreeCAD.GuiUp:
    from Ui.ViewParachute import ViewProviderParachute
    from Ui.Widgets.WaitCursor import WaitCursor

translate = FreeCAD.Qt.translate

def makeParachute(name):
    '''makeParachute(name): makes a Parachute'''
    obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython",name)
    FeatureFin(obj)
    obj.Proxy.setDefaults()

    if FreeCAD.GuiUp:
        ViewProviderParachute(obj.ViewObject)

    return obj.Proxy

class CmdParachute:
    def Activated(self):
        with WaitCursor():
            FreeCAD.ActiveDocument.openTransaction("Create parachute")
            FreeCADGui.addModule("Ui.Commands.CmdParachute")
            FreeCADGui.doCommand("obj=Ui.Commands.CmdParachute.makeParachute('Parachute')")
            FreeCADGui.doCommand("Ui.Commands.CmdStage.addToStage(obj)")
            FreeCADGui.doCommand("FreeCADGui.activeDocument().setEdit(FreeCAD.ActiveDocument.ActiveObject.Name,0)")

    def IsActive(self):
        if FreeCAD.ActiveDocument:
            return True
        return False

    def GetResources(self):
        return {'MenuText': translate("Rocket", 'Parachute'),
                'ToolTip': translate("Rocket", 'Adds a parachute to the selected component'),
                'Pixmap': FreeCAD.getUserAppDataDir() + "Mod/Rocket/Resources/icons/Rocket_Parachute.svg"}
