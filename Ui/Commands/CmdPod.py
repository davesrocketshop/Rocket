# SPDX-License-Identifier: LGPL-2.1-or-later
# SPDX-FileCopyrightText: 2021 David Carter <dcarter@davidcarter.ca>
# SPDX-File-Notice: Part of the Rocket addon.


"""Class for drawing pods"""

__title__ = "FreeCAD Pods"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

import FreeCAD
import FreeCADGui

from Rocket.FeaturePod import FeaturePod
if FreeCAD.GuiUp:
    from Ui.ViewPod import ViewProviderPod
    from Ui.Widgets.WaitCursor import WaitCursor
from Ui.Commands.Command import Command

from Rocket.Constants import FEATURE_POD

translate = FreeCAD.Qt.translate

def makePod(name='Pod'):
    '''makePod(name): makes a Pod'''
    obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython",name)
    FeaturePod(obj)
    obj.Proxy.setDefaults()
    if FreeCAD.GuiUp:
        ViewProviderPod(obj.ViewObject)

    return obj.Proxy

class CmdPod(Command):
    def Activated(self):
        with WaitCursor():
            FreeCAD.ActiveDocument.openTransaction("Create pod")
            FreeCADGui.addModule("Ui.Commands.CmdPod")
            FreeCADGui.doCommand("obj=Ui.Commands.CmdPod.makePod('Pod')")
            FreeCADGui.doCommand("Ui.Commands.CmdStage.addToStage(obj)")
            FreeCADGui.doCommand("FreeCADGui.Selection.clearSelection()")
            FreeCADGui.doCommand("FreeCADGui.Selection.addSelection(obj._obj)")
            FreeCADGui.doCommand("FreeCADGui.activeDocument().setEdit(FreeCAD.ActiveDocument.ActiveObject.Name,0)")

    def IsActive(self):
        # Pods are still under development
        # if FreeCAD.ActiveDocument:
        #     return self.partStageEligibleFeature(FEATURE_POD)
        return False

    def GetResources(self):
        return {'MenuText': translate("Rocket", 'Pod'),
                'ToolTip': translate("Rocket", 'Adds an external pod to the selected component'),
                'Pixmap': FreeCAD.getUserAppDataDir() + "Mod/Rocket/Resources/icons/Rocket_Pod.svg"}
