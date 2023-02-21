# ***************************************************************************
# *   Copyright (c) 2021-2023 David Carter <dcarter@davidcarter.ca>         *
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

from Ui.Commands.Command import Command
from Ui.Commands.CmdRocket import CmdRocket, CmdToggleRocket
from Ui.Commands.CmdStage import CmdStage, CmdToggleStage
from Ui.Commands.CmdParallelStage import CmdParallelStage, CmdToggleParallelStage
from Ui.Commands.CmdNoseCone import CmdNoseCone
from Ui.Commands.CmdTransition import CmdTransition
from Ui.Commands.CmdCenteringRing import CmdCenteringRing
from Ui.Commands.CmdBodyTube import CmdBodyTube, CmdCoupler, CmdInnerTube, CmdEngineBlock
from Ui.Commands.CmdPod import CmdPod
from Ui.Commands.CmdBulkhead import CmdBulkhead
from Ui.Commands.CmdLaunchGuides import CmdLaunchLug, CmdRailButton, CmdRailGuide, CmdStandOff
from Ui.Commands.CmdFin import CmdFin
from Ui.Commands.CmdFinCan import CmdFinCan
from Ui.Commands.CmdParachute import CmdParachute
from Ui.Commands.CmdEditTree import CmdMoveUp, CmdMoveDown

# Calculators
from Ui.Commands.CmdCalcBlackPowder import CmdCalcBlackPowder
from Ui.Commands.CmdCalcParachute import CmdCalcParachute
from Ui.Commands.CmdCalcThrustToWeight import CmdCalcThrustToWeight
from Ui.Commands.CmdCalcVentHoles import CmdCalcVentHoles

# Rocket specific sketcher
from Ui.Commands.CmdSketcher import CmdNewSketch

# Template generators
from Ui.Commands.CmdParachuteGore import CmdParachuteGore

# Analysis
from Ui.Commands.CmdFlutterAnalysis import CmdFinFlutter
from Ui.Commands.CmdFemAnalysis import CmdFemAnalysis
from Ui.Commands.CmdMaterialEditor import CmdMaterialEditor
from Ui.Commands.CmdMaterialMapping import CmdMaterialMapping

from App.Constants import FEATURE_BODY_TUBE
from App.Constants import FEATURE_LAUNCH_LUG, FEATURE_RAIL_BUTTON, FEATURE_RAIL_GUIDE, FEATURE_OFFSET

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
FreeCADGui.addCommand('Rocket_EngineBlock', CmdEngineBlock())

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

FreeCADGui.addCommand('Rocket_NewSketch', CmdNewSketch())

FreeCADGui.addCommand('Rocket_ParachuteGore', CmdParachuteGore())

FreeCADGui.addCommand('Rocket_FinFlutter', CmdFinFlutter())
FreeCADGui.addCommand('Rocket_FemAnalysis', CmdFemAnalysis())
FreeCADGui.addCommand('Rocket_MaterialEditor', CmdMaterialEditor())
FreeCADGui.addCommand('Rocket_MaterialMapping', CmdMaterialMapping())

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

class _TubeGroupCommand(Command):

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
            return self.partEligibleFeature(FEATURE_BODY_TUBE)
        return False

class _GuidesGroupCommand(Command):

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
            return self.partEligibleFeature([FEATURE_LAUNCH_LUG, FEATURE_RAIL_BUTTON, FEATURE_RAIL_GUIDE, FEATURE_OFFSET])
        return False

FreeCADGui.addCommand('Rocket_Calculators', _CalculatorGroupCommand())
FreeCADGui.addCommand('Rocket_BodyTubes', _TubeGroupCommand())
FreeCADGui.addCommand('Rocket_LaunchGuides', _GuidesGroupCommand())
