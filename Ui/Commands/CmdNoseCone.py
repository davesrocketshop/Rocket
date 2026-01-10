# SPDX-License-Identifier: LGPL-2.1-or-later
# SPDX-FileCopyrightText: 2021 David Carter <dcarter@davidcarter.ca>
# SPDX-File-Notice: Part of the Rocket addon.


"""Class for drawing nose cones"""

__title__ = "FreeCAD Nose Cones"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"


import FreeCAD
import FreeCADGui

from Rocket.FeatureNoseCone import FeatureNoseCone
if FreeCAD.GuiUp:
    from Ui.ViewNoseCone import ViewProviderNoseCone
    from Ui.Widgets.WaitCursor import WaitCursor
from Ui.Commands.Command import Command

from Rocket.Constants import FEATURE_NOSE_CONE

translate = FreeCAD.Qt.translate

def makeNoseCone(name='NoseCone'):
    '''makeNoseCone(name): makes a Nose Cone'''
    obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython",name)
    FeatureNoseCone(obj)
    obj.Proxy.setDefaults()
    if FreeCAD.GuiUp:
        ViewProviderNoseCone(obj.ViewObject)

    return obj.Proxy

class CmdNoseCone(Command):
    def Activated(self):
        with WaitCursor():
            FreeCAD.ActiveDocument.openTransaction("Create nose cone")
            FreeCADGui.addModule("Ui.Commands.CmdNoseCone")
            FreeCADGui.doCommand("obj=Ui.Commands.CmdNoseCone.makeNoseCone('NoseCone')")
            FreeCADGui.doCommand("Ui.Commands.CmdStage.addToStage(obj)")
            FreeCADGui.doCommand("FreeCADGui.activeDocument().setEdit(FreeCAD.ActiveDocument.ActiveObject.Name,0)")

    def IsActive(self):
        if FreeCAD.ActiveDocument:
            return self.partEligibleFeature(FEATURE_NOSE_CONE)
        return False

    def GetResources(self):
        return {'MenuText': translate("Rocket", 'Nose Cone'),
                'ToolTip': translate("Rocket", 'Adds a nose cone to the selected pod or stage'),
                'Pixmap': FreeCAD.getUserAppDataDir() + "Mod/Rocket/Resources/icons/Rocket_NoseCone.svg"}
