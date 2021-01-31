# -*- coding: utf-8 -*-
# FreeCAD init script of the Rocket module
# (c) 2001 Juergen Riegel
# License LGPL

import FreeCAD as App

# add Import/Export types
App.addImportType("Open Rocket (*.ork)", "importORK")
App.addImportType("Rocksim (*.rkt)", "importRKT")

#App.__unit_test__ += ["TestRocketImport"]
