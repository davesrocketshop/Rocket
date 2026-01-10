# SPDX-License-Identifier: LGPL-2.1-or-later
# SPDX-FileCopyrightText: 2021 David Carter <dcarter@davidcarter.ca>
# SPDX-File-Notice: Part of the Rocket addon.


"""Class for drawing bulkheads"""

__title__ = "FreeCAD Bulkheads"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

import FreeCAD
import FreeCADGui

from Rocket.FeatureBulkhead import FeatureBulkhead
if FreeCAD.GuiUp:
    from Ui.ViewBulkhead import ViewProviderBulkhead
    from Ui.Widgets.WaitCursor import WaitCursor
from Ui.Commands.Command import Command

from Rocket.Constants import FEATURE_BULKHEAD

translate = FreeCAD.Qt.translate

def makeBulkhead(name='Bulkhead'):
    '''makeBulkhead(name): makes a bulkhead'''
    obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython",name)
    FeatureBulkhead(obj)
    obj.Proxy.setDefaults()
    if FreeCAD.GuiUp:
        ViewProviderBulkhead(obj.ViewObject)

    return obj.Proxy

class CmdBulkhead(Command):
    def Activated(self):
        with WaitCursor():
            FreeCAD.ActiveDocument.openTransaction("Create bulkhead")
            FreeCADGui.addModule("Ui.Commands.CmdBulkhead")
            FreeCADGui.doCommand("obj=Ui.Commands.CmdBulkhead.makeBulkhead('Bulkhead')")
            FreeCADGui.doCommand("Ui.Commands.CmdStage.addToStage(obj)")
            FreeCADGui.doCommand("FreeCADGui.activeDocument().setEdit(FreeCAD.ActiveDocument.ActiveObject.Name,0)")

    def IsActive(self):
        if FreeCAD.ActiveDocument:
            return self.partEligibleFeature(FEATURE_BULKHEAD)
        return False

    def GetResources(self):
        return {'MenuText': translate("Rocket", 'Bulkhead'),
                'ToolTip': translate("Rocket", 'Adds a bulkhead to the selected component'),
                'Pixmap': FreeCAD.getUserAppDataDir() + "Mod/Rocket/Resources/icons/Rocket_Bulkhead.svg"}
