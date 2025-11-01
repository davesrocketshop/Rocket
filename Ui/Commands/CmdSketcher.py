# ***************************************************************************
# *   Copyright (c) 2021-2025 David Carter <dcarter@davidcarter.ca>         *
# *                                                                         *
# *   This program is free software; you can redistribute it and/or modify  *
# *   it under the terms of the GNU Lesser General Public License (LGPL)    *
# *   as published by the Free Software Foundation; either version 2 of     *
# *   the License, or (at your option) any later version.                   *
# *   for detail see the LICENCE text file.                                 *
# *                                                                         *
# *   This program is distributed in the hope that it will be useful,       *
# *   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
# *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
# *   GNU Library General Public License for more details.                  *
# *                                                                         *
# *   You should have received a copy of the GNU Library General Public     *
# *   License along with this program; if not, write to the Free Software   *
# *   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  *
# *   USA                                                                   *
# *                                                                         *
# ***************************************************************************
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
