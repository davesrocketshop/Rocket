# SPDX-License-Identifier: LGPL-2.1-or-later
# SPDX-FileCopyrightText: 2021 David Carter <dcarter@davidcarter.ca>
# SPDX-File-Notice: Part of the Rocket addon.


"""Class for drawing fins"""

__title__ = "FreeCAD Fins"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

import FreeCAD
import FreeCADGui

from Rocket.Constants import FIN_TYPE_SKETCH
from Rocket.FeatureFin import FeatureFin
from Ui.ViewFin import ViewProviderFin

translate = FreeCAD.Qt.translate

def makeFin(name):
    '''makeFin(name): makes a Fin'''
    obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython",name)
    FeatureFin(obj)

    # See if we have a sketch selected. If so, this is a custom fin
    for sketch in FreeCADGui.Selection.getSelection():
        if sketch.isDerivedFrom('Sketcher::SketchObject'):
            obj.FinType = FIN_TYPE_SKETCH
            obj.Profile = sketch
            sketch.Visibility = False

    if FreeCAD.GuiUp:
        ViewProviderFin(obj.ViewObject)

        body=FreeCADGui.ActiveDocument.ActiveView.getActiveObject("pdbody")
        part=FreeCADGui.ActiveDocument.ActiveView.getActiveObject("part")
        if body:
            body.Group=body.Group+[obj]
        elif part:
            part.Group=part.Group+[obj]
    return obj

class CmdFin:
    def Activated(self):
        FreeCAD.ActiveDocument.openTransaction("Create fin")
        FreeCADGui.addModule("Ui.Commands.CmdFin")
        FreeCADGui.doCommand("Ui.Commands.CmdFin.makeFin('Fin')")
        FreeCADGui.doCommand("FreeCADGui.activeDocument().setEdit(FreeCAD.ActiveDocument.ActiveObject.Name,0)")

    def IsActive(self):
        if FreeCAD.ActiveDocument:
            return True
        return False

    def GetResources(self):
        return {'MenuText': translate("Rocket", 'Fin'),
                'ToolTip': translate("Rocket", 'Fin design'),
                'Pixmap': FreeCAD.getUserAppDataDir() + "Mod/Rocket/Resources/icons/Rocket_Fin.svg"}
