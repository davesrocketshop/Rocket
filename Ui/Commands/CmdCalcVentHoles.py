# SPDX-License-Identifier: LGPL-2.1-or-later
# SPDX-FileCopyrightText: 2021 David Carter <dcarter@davidcarter.ca>
# SPDX-File-Notice: Part of the Rocket addon.


"""Class for calculating vent hole size"""

__title__ = "FreeCAD Vent Hole Calculator"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

import FreeCAD
import FreeCADGui

translate = FreeCAD.Qt.translate

from Ui.DialogVentHoles import DialogVentHole

def calcVentHoles():
    form = DialogVentHole()
    form.exec()

class CmdCalcVentHoles:
    def Activated(self):
        FreeCADGui.addModule("Ui.Commands.CmdCalcVentHoles")
        FreeCADGui.doCommand("Ui.Commands.CmdCalcVentHoles.calcVentHoles()")

    def IsActive(self):
        # Always available, even without active document
        return True

    def GetResources(self):
        return {'MenuText': translate("Rocket", 'Vent Hole Size Calculator'),
                'ToolTip': translate("Rocket", 'Calculates required vent hole size'),
                'Pixmap': FreeCAD.getUserAppDataDir() + "Mod/Rocket/Resources/icons/Rocket_Calculator.svg"}
