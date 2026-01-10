# SPDX-License-Identifier: LGPL-2.1-or-later
# SPDX-FileCopyrightText: 2021 David Carter <dcarter@davidcarter.ca>
# SPDX-File-Notice: Part of the Rocket addon.


"""Class for calculatingparachute size"""

__title__ = "FreeCAD Parachute Calculator"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

import FreeCAD
import FreeCADGui

translate = FreeCAD.Qt.translate

from Ui.Widgets.WaitCursor import WaitCursor

def newSketchNoEdit(name='Sketch'):
    obj = FreeCAD.ActiveDocument.addObject("Sketcher::SketchObject", name)
    # Select the XZ plane for consistency
    obj.Placement = FreeCAD.Placement(FreeCAD.Vector(0, 0, 0), FreeCAD.Vector(1, 0, 0), 90)
    obj.MapMode = "Deactivated"

    return obj

def newSketch(name='Sketch'):
    obj = newSketchNoEdit(name)
    FreeCADGui.activeDocument().setEdit(obj.Name,0)

    return obj

class CmdNewSketch:
    def Activated(self):
        with WaitCursor():
            FreeCADGui.addModule("Ui.Commands.CmdSketcher")
            FreeCADGui.doCommand("Ui.Commands.CmdSketcher.newSketch()")

    def IsActive(self):
        if FreeCAD.ActiveDocument:
            return True
        return False

    def GetResources(self):
        return {'MenuText': translate("Rocket", 'Create sketch'),
                'ToolTip': translate("Rocket", 'Creates a new sketch'),
                'Pixmap': "Sketcher_NewSketch" }
