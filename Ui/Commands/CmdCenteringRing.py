# SPDX-License-Identifier: LGPL-2.1-or-later
# SPDX-FileCopyrightText: 2021 David Carter <dcarter@davidcarter.ca>
# SPDX-File-Notice: Part of the Rocket addon.


"""Class for drawing centering rings"""

__title__ = "FreeCAD Centering Rings"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

import FreeCAD
import FreeCADGui

from Rocket.FeatureCenteringRing import FeatureCenteringRing
if FreeCAD.GuiUp:
    from Ui.ViewCenteringRing import ViewProviderCenteringRing
    from Ui.Widgets.WaitCursor import WaitCursor
from Ui.Commands.Command import Command

from Rocket.Constants import FEATURE_CENTERING_RING

translate = FreeCAD.Qt.translate

def makeCenteringRing(name='CenteringRing'):
    '''makeCenteringRing(name): makes a centering ring'''
    obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython",name)
    FeatureCenteringRing(obj)
    obj.Proxy.setDefaults()
    if FreeCAD.GuiUp:
        ViewProviderCenteringRing(obj.ViewObject)

    return obj.Proxy

class CmdCenteringRing(Command):
    def Activated(self):
        with WaitCursor():
            FreeCAD.ActiveDocument.openTransaction("Create centering ring")
            FreeCADGui.addModule("Ui.Commands.CmdCenteringRing")
            FreeCADGui.doCommand("obj=Ui.Commands.CmdCenteringRing.makeCenteringRing('CenteringRing')")
            FreeCADGui.doCommand("Ui.Commands.CmdStage.addToStage(obj)")
            FreeCADGui.doCommand("FreeCADGui.activeDocument().setEdit(FreeCAD.ActiveDocument.ActiveObject.Name,0)")

    def IsActive(self):
        if FreeCAD.ActiveDocument:
            return self.partEligibleFeature(FEATURE_CENTERING_RING)
        return False

    def GetResources(self):
        return {'MenuText': translate("Rocket", 'Centering Ring'),
                'ToolTip': translate("Rocket", 'Adds a centering ring to the selected component'),
                'Pixmap': FreeCAD.getUserAppDataDir() + "Mod/Rocket/Resources/icons/Rocket_CenteringRing.svg"}
