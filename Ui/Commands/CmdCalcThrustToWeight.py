# SPDX-License-Identifier: LGPL-2.1-or-later
# SPDX-FileCopyrightText: 2021 David Carter <dcarter@davidcarter.ca>
# SPDX-File-Notice: Part of the Rocket addon.


"""Class for calculating thrust to weight"""

__title__ = "FreeCAD Thrust To Weight Command"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

import FreeCAD
import FreeCADGui

translate = FreeCAD.Qt.translate

from Ui.DialogThrustToWeight import DialogThrustToWeight

def calcThrustToWeight():
    form = DialogThrustToWeight()
    form.exec()

class CmdCalcThrustToWeight:
    def Activated(self):
        FreeCADGui.addModule("Ui.Commands.CmdCalcThrustToWeight")
        FreeCADGui.doCommand("Ui.Commands.CmdCalcThrustToWeight.calcThrustToWeight()")

    def IsActive(self):
        # Always available, even without active document
        return True

    def GetResources(self):
        return {'MenuText': translate("Rocket", 'Thrust to Weight Calculator'),
                'ToolTip': translate("Rocket", 'Calculates minimum thrust to weight'),
                'Pixmap': FreeCAD.getUserAppDataDir() + "Mod/Rocket/Resources/icons/Rocket_Calculator.svg"}
