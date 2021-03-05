# ***************************************************************************
# *   Copyright (c) 2021 David Carter <dcarter@davidcarter.ca>              *
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

__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

import FreeCAD
import FreeCADGui

from DraftTools import translate

from Ui.CmdRocket import CmdRocket, CmdToggleRocket
from Ui.CmdStage import CmdStage, CmdToggleStage
from Ui.CmdNoseCone import CmdNoseCone
from Ui.CmdTransition import CmdTransition
from Ui.CmdCenteringRing import CmdCenteringRing
from Ui.CmdBodyTube import CmdBodyTube
from Ui.CmdBulkhead import CmdBulkhead
from Ui.CmdFin import CmdFin

# Calculators
from Ui.CmdCalcBlackPowder import CmdCalcBlackPowder
from Ui.CmdCalcParachute import CmdCalcParachute
from Ui.CmdCalcThrustToWeight import CmdCalcThrustToWeight
from Ui.CmdCalcVentHoles import CmdCalcVentHoles

FreeCADGui.addCommand('Rocket_Rocket', CmdRocket())
FreeCADGui.addCommand('Rocket_ToggleRocket', CmdToggleRocket())
FreeCADGui.addCommand('Rocket_Stage', CmdStage())
FreeCADGui.addCommand('Rocket_ToggleStage', CmdToggleStage())

FreeCADGui.addCommand('Rocket_NoseCone', CmdNoseCone())
FreeCADGui.addCommand('Rocket_Transition', CmdTransition())
FreeCADGui.addCommand('Rocket_CenteringRing', CmdCenteringRing())
FreeCADGui.addCommand('Rocket_BodyTube', CmdBodyTube())
FreeCADGui.addCommand('Rocket_Bulkhead', CmdBulkhead())
FreeCADGui.addCommand('Rocket_Fin', CmdFin())

FreeCADGui.addCommand('Rocket_CalcBlackPowder', CmdCalcBlackPowder())
FreeCADGui.addCommand('Rocket_CalcParachute', CmdCalcParachute())
FreeCADGui.addCommand('Rocket_CalcThrustToWeight', CmdCalcThrustToWeight())
FreeCADGui.addCommand('Rocket_CalcVentHoles', CmdCalcVentHoles())

class _CalculatorGroupCommand:

    def GetCommands(self):
        return tuple(['Rocket_CalcBlackPowder', 'Rocket_CalcParachute', 'Rocket_CalcThrustToWeight', 'Rocket_CalcVentHoles'])
    def GetResources(self):
        return {
            'MenuText': translate('Rocket', 'Calculators'),
            'ToolTip': translate('Rocket', 'Calculators'),
            'Pixmap': FreeCAD.getUserAppDataDir() + "Mod/Rocket/Resources/icons/Rocket_Calculator.svg"
        }
    def IsActive(self):
        # Always available, even without active document
        return True

FreeCADGui.addCommand('Rocket_Calculators', _CalculatorGroupCommand())
