# ***************************************************************************
# *   Copyright (c) 2021-2023 David Carter <dcarter@davidcarter.ca>         *
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
"""Provides support for importing Rocsim files."""

__title__ = "FreeCAD Rocksim Importer Common Component"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

import FreeCAD

from Rocket.Importer.Rocsim.BaseElement import BaseElement
from Rocket.Importer.Rocsim.Utilities import getAxialMethodFromCode
from Rocket.position import AxialMethod

class PositionDependentElement(BaseElement):

    def __init__(self, parent, tag, attributes, parentObj, filename, line):
        super().__init__(parent, tag, attributes, parentObj, filename, line)

        self._componentTags.extend(["xb", "locationmode"])
        
        self._locationLoaded = False
        self._location = 0

    def handleEndTag(self, tag, content):
        _tag = tag.lower().strip()
        if _tag == "xb":
            self._location = float(FreeCAD.Units.Quantity(content + " mm").Value)
            if isinstance(self._feature.getAxialMethod(), AxialMethod.BottomAxialMethod):
                self._feature._obj.AxialOffset = -self._location
            else:
                self._feature._obj.AxialOffset = self._location
            self._locationLoaded = True
        elif _tag == "locationmode":
            self._feature._obj.AxialMethod = getAxialMethodFromCode(int(content))
            # If the location is loaded before the axialMethod, we still need to correct for the different relative distance direction
            if self._locationLoaded:
                if isinstance(self._feature.getAxialMethod(), AxialMethod.BottomAxialMethod):
                    self._feature._obj.AxialOffset = -self._location
                else:
                    self._feature._obj.AxialOffset = self._location
        else:
            super().handleEndTag(tag, content)
