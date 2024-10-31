# ***************************************************************************
# *   Copyright (c) 2020 Bernd Hahnebach <bernd@bimstatik.org>              *
# *   Copyright (c) 2023-2024 David Carter <dcarter@davidcarter.ca>         *
# *                                                                         *
# *   This file is part of the FreeCAD CAx development system.              *
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
""" Class and methods to migrate old Rocket App objects

see module end as well as forum topic
https://forum.freecadweb.org/viewtopic.php?&t=46218
"""

__title__ = "Rocket class and methods that migrates old App objects"
__author__ = "Bernd Hahnebach"
__url__ = "https://www.freecadweb.org"

import sys
from importlib.abc import MetaPathFinder, Loader
from importlib.machinery import ModuleSpec
from importlib.util import find_spec, module_from_spec

class RocketMigrateApp(MetaPathFinder, Loader):

    def find_spec(self, fullname, path, target=None):
        print("find_spec({}, {})".format(fullname, path))

        #     return self.find_module(fullname, path)

        # def find_module(self, fullname, path):

        specDict = {
            "App" : "Rocket",
            "App.ShapeBodyTube" : "Rocket.migration.ShapeBodyTube.ShapeBodyTube",
            "App.ShapeBulkhead" : "App.ShapeBulkhead",
            "App.ShapeCenteringRing" : "App.ShapeCenteringRing",
            "App.ShapeFin" : "App.ShapeFin",
            "App.ShapeFinCan" : "App.ShapeFinCan",
            "App.ShapeLaunchLug" : "App.ShapeLaunchLug",
            "App.ShapeNoseCone" : "App.ShapeNoseCone",
            "App.ShapeRailButton" : "App.ShapeRailButton",
            "App.ShapeRailGuide" : "App.ShapeRailGuide",
            "App.ShapeTransition" : "App.ShapeTransition",
            "App.util" : "Rocket.util",
            "App.position" : "Rocket.position",
        }
        if fullname in specDict.keys() or fullname.startswith("App"):
            spec = ModuleSpec(fullname, self)
            return spec

        return None

    def create_module(self, spec):
        return None

    def exec_module(self, module):
        print("exec_module({})".format(module.__name__))
        self._load_module(module)
        try:
            _ = sys.modules.pop(module.__name__)
        except KeyError:
            # log.error("module %s is not in sys.modules", module.__name__)
            print("module {} is not in sys.modules".format(module.__name__))
        sys.modules[module.__name__] = module
        globals()[module.__name__] = module

    def _load_module(self, module):
        # print("load_module({}, {})".format(module.__name__, module.__path__))

        # if module.__name__ == "App":
        #     module.__path__ = "Rocket"
        if module.__name__ == "App.ShapeBodyTube":
            import Rocket.migration.ShapeBodyTube
            module.ShapeBodyTube = Rocket.migration.ShapeBodyTube.ShapeBodyTube
        if module.__name__ == "App.ShapeBulkhead":
            import Rocket.migration.ShapeBulkhead
            module.ShapeBulkhead = Rocket.migration.ShapeBulkhead.ShapeBulkhead
        if module.__name__ == "App.ShapeCenteringRing":
            import Rocket.migration.ShapeCenteringRing
            module.ShapeCenteringRing = Rocket.migration.ShapeCenteringRing.ShapeCenteringRing
        if module.__name__ == "App.ShapeFin":
            import Rocket.migration.ShapeFin
            module.ShapeFin = Rocket.migration.ShapeFin.ShapeFin
        if module.__name__ == "App.ShapeFinCan":
            import Rocket.migration.ShapeFinCan
            module.ShapeFinCan = Rocket.migration.ShapeFinCan.ShapeFinCan
        if module.__name__ == "App.ShapeLaunchLug":
            import Rocket.migration.ShapeLaunchLug
            module.ShapeLaunchLug = Rocket.migration.ShapeLaunchLug.ShapeLaunchLug
        if module.__name__ == "App.ShapeNoseCone":
            import Rocket.migration.ShapeNoseCone
            module.ShapeNoseCone = Rocket.migration.ShapeNoseCone.ShapeNoseCone
        if module.__name__ == "App.ShapeRailButton":
            import Rocket.migration.ShapeRailButton
            module.ShapeRailButton = Rocket.migration.ShapeRailButton.ShapeRailButton
        if module.__name__ == "App.ShapeRailGuide":
            import Rocket.migration.ShapeRailGuide
            module.ShapeRailGuide = Rocket.migration.ShapeRailGuide.ShapeRailGuide
        if module.__name__ == "App.ShapeTransition":
            import Rocket.migration.ShapeTransition
            module.ShapeTransition = Rocket.migration.ShapeTransition.ShapeTransition
        # if module.__name__ == "App.util":
        #     import Rocket.util
        #     module.__path__ = "Rocket.util"
        # if module.__name__ == "App.position":
        #     # import Rocket.position
        #     # return Rocket.position
        #     module.__path__ = "Rocket.position"
        if module.__name__.startswith("App"):
            module.__path__ = module.__name__.replace("App", "Rocket", 1)

        return None
