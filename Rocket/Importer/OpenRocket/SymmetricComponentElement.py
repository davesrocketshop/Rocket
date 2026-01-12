# SPDX-License-Identifier: LGPL-2.1-or-later
# SPDX-File-Notice: Part of the Rocket addon.

################################################################################
#                                                                              #
#   © 2021 David Carter <dcarter@davidcarter.ca>                               #
#                                                                              #
#   This addon is free software: you can redistribute it and/or modify         #
#   it under the terms of the GNU Lesser General Public License as             #
#   published by the Free Software Foundation, either version 2.1              #
#   of the License, or (at your option) any later version.                     #
#                                                                              #
#   This addon is distributed in the hope that it will be useful,              #
#   but WITHOUT ANY WARRANTY; without even the implied warranty                #
#   of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.                    #
#   See the GNU Lesser General Public License for more details.                #
#                                                                              #
#   You should have received a copy of the GNU Lesser General Public           #
#   License along with this addon. If not, see https://www.gnu.org/licenses    #
#                                                                              #
################################################################################


"""Provides support for importing Open Rocket files."""

__title__ = "FreeCAD Open Rocket Importer Common Component"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

import FreeCAD

from Rocket.Importer.OpenRocket.ComponentElement import BodyComponentElement
from Rocket.SymmetricComponent import SymmetricComponent

class SymmetricComponentElement(BodyComponentElement):

    def __init__(self, parent, tag, attributes, parentObj, filename, line):
        super().__init__(parent, tag, attributes, parentObj, filename, line)

        self._knownTags.extend(["thickness"])


    def handleEndTag(self, tag, content):
        _tag = tag.lower().strip()
        if _tag == "thickness":
            if content == 'filled':
                self.onFilled(True)
            else:
                self.onFilled(False)
                thickness = FreeCAD.Units.Quantity(content + " m").Value
                if thickness <= 0:
                    thickness = SymmetricComponent.DEFAULT_THICKNESS
                self.onThickness(thickness)
        else:
            super().handleEndTag(tag, content)

    def onThickness(self, thickness):
        pass

    def onFilled(self, filled):
        pass
