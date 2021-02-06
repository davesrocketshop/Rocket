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

import FreeCAD, FreeCADGui

from Ui.CmdNoseCone import CmdNoseCone
from Ui.CmdTransition import CmdTransition
from Ui.CmdCenteringRing import CmdCenteringRing
from Ui.CmdBodyTube import CmdBodyTube
from Ui.CmdBulkhead import CmdBulkhead
from Ui.CmdFin import CmdFin
from Ui.CmdFinCan import CmdFinCan

FreeCADGui.addCommand('Rocket_NoseCone', CmdNoseCone())
FreeCADGui.addCommand('Rocket_Transition', CmdTransition())
FreeCADGui.addCommand('Rocket_CenteringRing', CmdCenteringRing())
FreeCADGui.addCommand('Rocket_BodyTube', CmdBodyTube())
FreeCADGui.addCommand('Rocket_Bulkhead', CmdBulkhead())
FreeCADGui.addCommand('Rocket_Fin', CmdFin())
FreeCADGui.addCommand('Rocket_FinCan', CmdFinCan())
