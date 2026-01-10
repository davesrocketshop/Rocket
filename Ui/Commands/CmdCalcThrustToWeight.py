# SPDX-License-Identifier: LGPL-2.1-or-later

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
