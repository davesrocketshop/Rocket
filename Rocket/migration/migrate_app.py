# SPDX-License-Identifier: LGPL-2.1-or-later
# SPDX-FileCopyrightText: 2020 Bernd Hahnebach <bernd@bimstatik.org>
# SPDX-FileCopyrightText: 2023 David Carter <dcarter@davidcarter.ca>
# SPDX-File-Notice: Part of the Rocket addon.


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
