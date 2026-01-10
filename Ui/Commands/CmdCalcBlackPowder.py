# SPDX-License-Identifier: LGPL-2.1-or-later
# SPDX-FileCopyrightText: 2021 David Carter <dcarter@davidcarter.ca>
# SPDX-File-Notice: Part of the Rocket addon.


"""Class for calculating ejection charge size"""

__title__ = "FreeCAD Black Powder Calculator"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

import FreeCAD
import FreeCADGui

translate = FreeCAD.Qt.translate

from Ui.DialogBlackPowder import DialogBlackPowder

def calcBlackPowder():
    form = DialogBlackPowder()
    form.exec()

class CmdCalcBlackPowder:
    def Activated(self):
        FreeCADGui.addModule("Ui.Commands.CmdCalcBlackPowder")
        FreeCADGui.doCommand("Ui.Commands.CmdCalcBlackPowder.calcBlackPowder()")

    def IsActive(self):
        # Always available, even without active document
        return True

    def GetResources(self):
        return {'MenuText': translate("Rocket", 'Ejection Charge Calculator'),
                'ToolTip': translate("Rocket", 'Calculates required ejection charge'),
                'Pixmap': FreeCAD.getUserAppDataDir() + "Mod/Rocket/Resources/icons/Rocket_Calculator.svg"}
