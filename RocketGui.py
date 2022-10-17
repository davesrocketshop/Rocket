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
from Ui.CmdParallelStage import CmdParallelStage, CmdToggleParallelStage
from Ui.CmdNoseCone import CmdNoseCone
from Ui.CmdTransition import CmdTransition
from Ui.CmdCenteringRing import CmdCenteringRing
from Ui.CmdBodyTube import CmdBodyTube, CmdCoupler, CmdInnerTube
from Ui.CmdPod import CmdPod
from Ui.CmdBulkhead import CmdBulkhead
from Ui.CmdLaunchGuides import CmdLaunchLug, CmdRailButton, CmdRailGuide, CmdStandOff
from Ui.CmdFin import CmdFin
from Ui.CmdFinCan import CmdFinCan
from Ui.CmdParachute import CmdParachute
from Ui.CmdEditTree import CmdMoveUp, CmdMoveDown, CmdEdit, CmdDelete

# Calculators
from Ui.CmdCalcBlackPowder import CmdCalcBlackPowder
from Ui.CmdCalcParachute import CmdCalcParachute
from Ui.CmdCalcThrustToWeight import CmdCalcThrustToWeight
from Ui.CmdCalcVentHoles import CmdCalcVentHoles

# Rocket specific sketcher
from Ui.CmdSketcher import CmdNewSketch

# Template generators
from Ui.CmdParachuteGore import CmdParachuteGore

# Analysis
from Ui.CmdFlutterAnalysis import CmdFinFlutter
from Ui.CmdMaterialEditor import CmdMaterialEditor

FreeCADGui.addCommand('Rocket_Rocket', CmdRocket())
FreeCADGui.addCommand('Rocket_ToggleRocket', CmdToggleRocket())
FreeCADGui.addCommand('Rocket_Stage', CmdStage())
FreeCADGui.addCommand('Rocket_ToggleStage', CmdToggleStage())
FreeCADGui.addCommand('Rocket_ParallelStage', CmdParallelStage())
FreeCADGui.addCommand('Rocket_ToggleParallelStage', CmdToggleParallelStage())

FreeCADGui.addCommand('Rocket_NoseCone', CmdNoseCone())
FreeCADGui.addCommand('Rocket_Transition', CmdTransition())
FreeCADGui.addCommand('Rocket_CenteringRing', CmdCenteringRing())
FreeCADGui.addCommand('Rocket_Bulkhead', CmdBulkhead())
FreeCADGui.addCommand('Rocket_Fin', CmdFin())
FreeCADGui.addCommand('Rocket_FinCan', CmdFinCan())

FreeCADGui.addCommand('Rocket_BodyTube', CmdBodyTube())
FreeCADGui.addCommand('Rocket_Coupler', CmdCoupler())
FreeCADGui.addCommand('Rocket_InnerTube', CmdInnerTube())

FreeCADGui.addCommand('Rocket_Pod', CmdPod())

FreeCADGui.addCommand('Rocket_LaunchLug', CmdLaunchLug())
FreeCADGui.addCommand('Rocket_RailButton', CmdRailButton())
FreeCADGui.addCommand('Rocket_RailGuide', CmdRailGuide())
FreeCADGui.addCommand('Rocket_Standoff', CmdStandOff())

FreeCADGui.addCommand('Rocket_Parachute', CmdParachute())

FreeCADGui.addCommand('Rocket_CalcBlackPowder', CmdCalcBlackPowder())
FreeCADGui.addCommand('Rocket_CalcParachute', CmdCalcParachute())
FreeCADGui.addCommand('Rocket_CalcThrustToWeight', CmdCalcThrustToWeight())
FreeCADGui.addCommand('Rocket_CalcVentHoles', CmdCalcVentHoles())

FreeCADGui.addCommand('Rocket_MoveUp', CmdMoveUp())
FreeCADGui.addCommand('Rocket_MoveDown', CmdMoveDown())
FreeCADGui.addCommand('Rocket_Edit', CmdEdit())
FreeCADGui.addCommand('Rocket_Delete', CmdDelete())

FreeCADGui.addCommand('Rocket_NewSketch', CmdNewSketch())

FreeCADGui.addCommand('Rocket_ParachuteGore', CmdParachuteGore())

FreeCADGui.addCommand('Rocket_FinFlutter', CmdFinFlutter())
FreeCADGui.addCommand('Rocket_MaterialEditor', CmdMaterialEditor())

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

class _TubeGroupCommand:

    def GetCommands(self):
        return tuple(['Rocket_BodyTube', 'Rocket_Coupler', 'Rocket_InnerTube'])
    def GetResources(self):
        return {
            'MenuText': translate('Rocket', 'Body Tubes'),
            'ToolTip': translate('Rocket', 'Body Tubes'),
            'Pixmap': FreeCAD.getUserAppDataDir() + "Mod/Rocket/Resources/icons/Rocket_BodyTube.svg"
        }
    def IsActive(self):
        if FreeCAD.ActiveDocument:
            return True
        return False

class _GuidesGroupCommand:

    def GetCommands(self):
        return tuple(['Rocket_LaunchLug', 'Rocket_RailButton', 'Rocket_RailGuide'])
    def GetResources(self):
        return {
            'MenuText': translate('Rocket', 'Launch Guides'),
            'ToolTip': translate('Rocket', 'Launch Guides'),
            'Pixmap': FreeCAD.getUserAppDataDir() + "Mod/Rocket/Resources/icons/Rocket_LaunchLug.svg"
        }
    def IsActive(self):
        if FreeCAD.ActiveDocument:
            return True
        return False

FreeCADGui.addCommand('Rocket_Calculators', _CalculatorGroupCommand())
FreeCADGui.addCommand('Rocket_BodyTubes', _TubeGroupCommand())
FreeCADGui.addCommand('Rocket_LaunchGuides', _GuidesGroupCommand())
