# SPDX-License-Identifier: LGPL-2.1-or-later
# SPDX-FileCopyrightText: 2021 David Carter <dcarter@davidcarter.ca>
# SPDX-File-Notice: Part of the Rocket addon.


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
