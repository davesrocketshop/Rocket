# ***************************************************************************
# *   Copyright (c) 2025 David Carter <dcarter@davidcarter.ca>              *
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
"""Class for finding scale body tubes"""

__title__ = "FreeCAD Scaling Calculator"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

import FreeCAD
import FreeCADGui

from DraftTools import translate

from Ui.DialogScaling import DialogScaling

def scalingPairs():
    form = DialogScaling()
    form.exec_()

class CmdScalingPairs:
    def Activated(self):
        FreeCADGui.addModule("Ui.Commands.CmdScaling")
        FreeCADGui.doCommand("Ui.Commands.CmdScaling.scalingPairs()")

    def IsActive(self):
        # Always available, even without active document
        return True

    def GetResources(self):
        return {'MenuText': translate("Rocket", 'Match body tube pairs'),
                'ToolTip': translate("Rocket", 'Match body tube pairs suitable for scale'),
                'Pixmap': FreeCAD.getUserAppDataDir() + "Mod/Rocket/Resources/icons/Rocket_Scaling.svg"}

class CmdScalingTubes:
    def Activated(self):
        FreeCADGui.addModule("Ui.Commands.CmdScaling")
        FreeCADGui.doCommand("Ui.Commands.CmdScaling.scalingPairs()")

    def IsActive(self):
        # Always available, even without active document
        return True

    def GetResources(self):
        return {'MenuText': translate("Rocket", 'Find scale body tubes'),
                'ToolTip': translate("Rocket", 'Find scale body tubes'),
                'Pixmap': FreeCAD.getUserAppDataDir() + "Mod/Rocket/Resources/icons/Rocket_Scaling.svg"}
