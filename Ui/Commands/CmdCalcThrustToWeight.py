# SPDX-License-Identifier: LGPL-2.1-or-later
# SPDX-File-Notice: Part of the Rocket addon.

################################################################################
#                                                                              #
#   © 2021 David Carter <dcarter@davidcarter.ca>                               #
#                                                                              #
#   This addon is free software: you can redistribute it and/or modify         #
#   it under the terms of the GNU Lesser General Public License as             #
#   published by the Free Software Foundation, either version 2.1              #
#   of the License, or (at your option) any later version.                     #
#                                                                              #
#   This addon is distributed in the hope that it will be useful,              #
#   but WITHOUT ANY WARRANTY; without even the implied warranty                #
#   of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.                    #
#   See the GNU Lesser General Public License for more details.                #
#                                                                              #
#   You should have received a copy of the GNU Lesser General Public           #
#   License along with this addon. If not, see https://www.gnu.org/licenses    #
#                                                                              #
################################################################################


"""Class for calculating thrust to weight"""

__title__ = "FreeCAD Thrust To Weight Command"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

import FreeCAD
import FreeCADGui

translate = FreeCAD.Qt.translate

from Ui.DialogThrustToWeight import DialogThrustToWeight

def calcThrustToWeight() -> None:
    form = DialogThrustToWeight()
    form.exec()

class CmdCalcThrustToWeight:
    def Activated(self) -> None:
        FreeCADGui.addModule("Ui.Commands.CmdCalcThrustToWeight")
        FreeCADGui.doCommand("Ui.Commands.CmdCalcThrustToWeight.calcThrustToWeight()")

    def IsActive(self) -> bool:
        # Always available, even without active document
        return True

    def GetResources(self):
        return {'MenuText': translate("Rocket", 'Thrust to Weight Calculator'),
                'ToolTip': translate("Rocket", 'Calculates minimum thrust to weight'),
                'Pixmap': FreeCAD.getUserAppDataDir() + "Mod/Rocket/Resources/icons/Rocket_Calculator.svg"}
