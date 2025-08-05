# ***************************************************************************
# *   Copyright (c) 2020 Bernd Hahnebach <bernd@bimstatik.org>              *
# *   Copyright (c) 2023-2025 David Carter <dcarter@davidcarter.ca>         *
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

from importlib.abc import MetaPathFinder, Loader
from importlib.util import spec_from_loader

class RocketLoader(Loader):

    def create_module(self, spec):
        return None

    def exec_module(self, module):
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

        return None

class RocketMigrateApp(MetaPathFinder):

    def find_spec(self, fullname, path, target=None):

        if fullname in [
            "App",
            "App.ShapeBodyTube",
            "App.ShapeBulkhead",
            "App.ShapeCenteringRing",
            "App.ShapeFin",
            "App.ShapeFinCan",
            "App.ShapeLaunchLug",
            "App.ShapeNoseCone",
            "App.ShapeRailButton",
            "App.ShapeRailGuide",
            "App.ShapeTransition",
        ]:
            return spec_from_loader(fullname, RocketLoader())

        return None
