# SPDX-License-Identifier: LGPL-2.1-or-later
# SPDX-FileCopyrightText: 2021 David Carter <dcarter@davidcarter.ca>
# SPDX-File-Notice: Part of the Rocket addon.


"""Class for drawing transitions"""

__title__ = "FreeCAD Transitions"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"


import FreeCAD
import FreeCADGui

from Rocket.FeatureTransition import FeatureTransition
if FreeCAD.GuiUp:
    from Ui.ViewTransition import ViewProviderTransition
    from Ui.Widgets.WaitCursor import WaitCursor
from Ui.Commands.Command import Command

from Rocket.Constants import FEATURE_TRANSITION

translate = FreeCAD.Qt.translate

def makeTransition(name='Transition'):
    '''makeTransition(name): makes a Transition'''
    obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython",name)
    FeatureTransition(obj)
    obj.Proxy.setDefaults()
    if FreeCAD.GuiUp:
        ViewProviderTransition(obj.ViewObject)

    return obj.Proxy

class CmdTransition(Command):
    def Activated(self):
        with WaitCursor():
            FreeCAD.ActiveDocument.openTransaction("Create transition")
            FreeCADGui.addModule("Ui.Commands.CmdTransition")
            FreeCADGui.doCommand("obj=Ui.Commands.CmdTransition.makeTransition('Transition')")
            FreeCADGui.doCommand("Ui.Commands.CmdStage.addToStage(obj)")
            FreeCADGui.doCommand("FreeCADGui.activeDocument().setEdit(FreeCAD.ActiveDocument.ActiveObject.Name,0)")

    def IsActive(self):
        if FreeCAD.ActiveDocument:
            return self.partEligibleFeature(FEATURE_TRANSITION)
        return False

    def GetResources(self):
        return {'MenuText': translate("Rocket", 'Transition'),
                'ToolTip': translate("Rocket", 'Adds a transition to the selected pod or stage'),
                'Pixmap': FreeCAD.getUserAppDataDir() + "Mod/Rocket/Resources/icons/Rocket_Transition.svg"}
