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

__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

import FreeCAD
import FreeCADGui

class RocketWorkbench ( Workbench ):
    "Rocket workbench object"
    Icon = FreeCAD.getUserAppDataDir() + "Mod/Rocket/Resources/icons/RocketWorkbench.svg"
    MenuText = "Rocket"
    ToolTip = "Rocket workbench"

    def _loadFemModule(self):
        # load the FEM module
        import Fem
        import FemGui
        import femcommands.commands
        # dummy usage to get flake8 and lgtm quiet
        False if Fem.__name__ else True
        False if FemGui.__name__ else True
        False if femcommands.commands.__name__ else True

    def _loadMaterialsModule(self):
        # load the Materials module
        import Materials
        import MatGui
        # dummy usage to get flake8 and lgtm quiet
        False if Materials.__name__ else True
        False if MatGui.__name__ else True

    def _loadCfDModule(self):
        # load the CfDOF module
        print("Importing CfdOF")
        import CfdOF
        # dummy usage to get flake8 and lgtm quiet
        False if CfdOF.__name__ else True

    def Initialize(self):
        FreeCADGui.addLanguagePath(FreeCAD.getUserAppDataDir() + "Mod/Rocket/Resources/translations")

        # load the module
        import RocketGui
        import SketcherGui
        from DraftTools import translate

        self._loadFemModule()
        self._loadMaterialsModule()
        try:
            self._loadCfDModule()
        except:
            pass

        self.appendToolbar(translate('Rocket', 'Rocket'),
                        ['Rocket_Rocket', 'Rocket_Stage', 'Rocket_ParallelStage', 'Rocket_Pod', 'Rocket_NoseCone', 'Rocket_Transition', 'Rocket_BodyTube', 'Rocket_InnerTube', 'Rocket_Coupler', 'Rocket_EngineBlock',
                        'Rocket_CenteringRing', 'Rocket_Bulkhead', 'Rocket_Fin', 'Rocket_FinCan', 'Rocket_LaunchLug', 'Rocket_RailButton', 'Rocket_RailGuide',
                        ])
        self.appendToolbar(translate('Rocket', 'Rocket'),
                        ['Separator', 'Rocket_MoveUp', 'Rocket_MoveDown'])
        self.appendToolbar(translate('Rocket', 'Rocket'),
                        ['Separator', 'Rocket_NewSketch', 'Sketcher_EditSketch', 'Separator', 'Rocket_Calculators'])
        # self.appendToolbar(translate('Rocket', 'Rocket'),
        #                 ['Separator', 'Rocket_ParachuteGore'])
        try:
            self.appendToolbar(translate('Rocket', 'Rocket'),
                        # ['Separator', 'Rocket_FinFlutter', 'Rocket_FemAnalysis', 'FEM_MeshGmshFromShape', "Rocket_MaterialEditor", 'Rocket_MaterialMapping'])
                        ['Separator', 'Rocket_FinFlutter', 'Rocket_CFDAnalysis', "Rocket_MaterialEditor"])
        except:
            self.appendToolbar(translate('Rocket', 'Rocket'),
                        # ['Separator', 'Rocket_FinFlutter', 'Rocket_FemAnalysis', 'FEM_MeshGmshFromShape', "Rocket_MaterialEditor", 'Rocket_MaterialMapping'])
                        ['Separator', 'Rocket_FinFlutter', "Rocket_MaterialEditor"])

        self.appendMenu(translate('Rocket', 'Rocket'),
                        ['Rocket_Rocket', 'Rocket_Stage', 'Rocket_ParallelStage', 'Rocket_Pod', 'Rocket_NoseCone', 'Rocket_Transition', 'Rocket_BodyTube', 'Rocket_InnerTube', 'Rocket_Coupler', 'Rocket_EngineBlock',
                        'Rocket_CenteringRing', 'Rocket_Bulkhead', 'Rocket_Fin', 'Rocket_FinCan', 'Rocket_LaunchLug', 'Rocket_RailButton', 'Rocket_RailGuide',
                        #'Rocket_Parachute'
                        ])
        self.appendMenu(translate('Rocket', 'Rocket'),
                        ['Separator'])
        self.appendMenu([translate("Rocket", "Rocket"),
                         translate("Rocket", "Calculators")],
                        ['Rocket_CalcBlackPowder', 'Rocket_CalcParachute', 'Rocket_CalcThrustToWeight', 'Rocket_CalcVentHoles'])
        try:
            self.appendMenu([translate("Rocket", "Rocket"),
                            translate("Rocket", "Analysis")],
                            # ['Rocket_FinFlutter', 'Rocket_FemAnalysis', 'FEM_MeshGmshFromShape', "Rocket_MaterialEditor", 'Rocket_MaterialMapping'])
                            ['Rocket_FinFlutter', 'Rocket_CFDAnalysis', "Rocket_MaterialEditor"])
        except:
            self.appendMenu([translate("Rocket", "Rocket"),
                         translate("Rocket", "Analysis")],
                        # ['Rocket_FinFlutter', 'Rocket_FemAnalysis', 'FEM_MeshGmshFromShape', "Rocket_MaterialEditor", 'Rocket_MaterialMapping'])
                        ['Rocket_FinFlutter', "Rocket_MaterialEditor"])

    def GetClassName(self):
        return "Gui::PythonWorkbench"

FreeCADGui.addWorkbench(RocketWorkbench())

FreeCAD.__unit_test__ += ["TestRocketGui"]
