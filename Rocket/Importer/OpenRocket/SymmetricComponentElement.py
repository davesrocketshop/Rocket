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
