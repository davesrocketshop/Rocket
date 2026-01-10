# SPDX-License-Identifier: LGPL-2.1-or-later
# SPDX-FileCopyrightText: 2021 David Carter <dcarter@davidcarter.ca>
# SPDX-File-Notice: Part of the Rocket addon.


"""Class for drawing parachute gores"""

__title__ = "FreeCAD Parachute Gores"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

import FreeCAD
import FreeCADGui

from Rocket.FeatureFin import FeatureFin
if FreeCAD.GuiUp:
    from Ui.ViewParachuteGore import ViewProviderParachuteGore
    from Ui.Widgets.WaitCursor import WaitCursor

translate = FreeCAD.Qt.translate

def makeParachuteGore(name):
    '''makeParachuteGore(name): makes a Fin'''
    obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython",name)
    FeatureFin(obj)

    if FreeCAD.GuiUp:
        ViewProviderParachuteGore(obj.ViewObject)

        body=FreeCADGui.ActiveDocument.ActiveView.getActiveObject("pdbody")
        part=FreeCADGui.ActiveDocument.ActiveView.getActiveObject("part")
        if body:
            body.Group=body.Group+[obj]
        elif part:
            part.Group=part.Group+[obj]
    return obj

class CmdParachuteGore:
    def Activated(self):
        with WaitCursor():
            FreeCAD.ActiveDocument.openTransaction("Create parachute  gore")
            FreeCADGui.addModule("Ui.Commands.CmdParachuteGore")
            FreeCADGui.doCommand("Ui.Commands.CmdParachuteGore.makeParachuteGore('Gore')")
            FreeCADGui.doCommand("FreeCADGui.activeDocument().setEdit(FreeCAD.ActiveDocument.ActiveObject.Name,0)")

    def IsActive(self):
        if FreeCAD.ActiveDocument:
            return True
        return False

    def GetResources(self):
        return {'MenuText': translate("Rocket", 'Parachute Gore'),
                'ToolTip': translate("Rocket", 'Creates a parachute gore'),
                'Pixmap': FreeCAD.getUserAppDataDir() + "Mod/Rocket/Resources/icons/Rocket_ParachuteGore.svg"}
