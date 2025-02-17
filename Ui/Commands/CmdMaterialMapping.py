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
"""Class for mapping materials"""

__title__ = "FreeCAD Material Mapping"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

import FreeCAD
import FreeCADGui

from DraftTools import translate

from Ui.DialogMaterialMapping import DialogMaterialMapping
from Ui.Commands.Command import Command

def mapMaterials():
    form = DialogMaterialMapping()
    form.exec_()

class CmdMaterialMapping(Command):
    def Activated(self):
        FreeCADGui.addModule("Ui.Commands.CmdMaterialMapping")
        FreeCADGui.doCommand("Ui.Commands.CmdMaterialMapping.mapMaterials()")

    def IsActive(self):
        return True

    def GetResources(self):
        return {'MenuText': translate("Rocket", 'Material Mapping'),
                'ToolTip': translate("Rocket", 'Map part database materials to FreeCAD materials'),
                'Pixmap': FreeCAD.getUserAppDataDir() + "Mod/Rocket/Resources/icons/Rocket_MaterialMapping.svg"}
