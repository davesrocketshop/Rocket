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

__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"


import FreeCAD
import sys
from pathlib import PurePath

# Migrate old components
from Rocket.migration.migrate_app import RocketMigrateApp
sys.meta_path.append(RocketMigrateApp())

# Add materials to the user config dir
materials = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/Material/Resources/Modules/Rocket")
matdir = str(PurePath(FreeCAD.getUserAppDataDir(), "Mod/Rocket/Resources/Material"))
materials.SetString("ModuleDir", matdir)
materials.SetString("ModuleIcon", str(PurePath(FreeCAD.getUserAppDataDir(), "Mod/Rocket/Resources/icons/RocketWorkbench.svg")))

# add Import/Export types
FreeCAD.addImportType("Open Rocket (*.ork)", "importORK")
# FreeCAD.addImportType("RASAero (*.cdx1)", "importRASAero")
FreeCAD.addImportType("Rocksim (*.rkt)", "importRKT")

FreeCAD.addExportType("Open Rocket (*.ork)", "importORK")

#App.__unit_test__ += ["TestRocketImport"]
FreeCAD.__unit_test__ += ["TestRocketApp"]
