# SPDX-License-Identifier: LGPL-2.1-or-later
# SPDX-File-Notice: Part of the Rocket addon.

################################################################################
#                                                                              #
#   © 2022 David Carter <dcarter@davidcarter.ca>                               #
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


"""Class for rocket components"""

from __future__ import annotations # Required prior to 3.14

__title__ = "FreeCAD Rocket Components"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

import sys
from typing import Self
import FreeCAD

import copy
from Rocket.util.Transformation import Transformation

class BoundingBox(object):

    _min : FreeCAD.Vector = FreeCAD.Vector()
    _max : FreeCAD.Vector = FreeCAD.Vector()

    def __init__(self, min : FreeCAD.Vector | None = None, max : FreeCAD.Vector | None = None) -> None:
        self.clear()

        if min:
            self._min = copy.deepcopy(min)
        if max:
            self._max = copy.deepcopy(max)

    def clear(self) -> None:
        self._min = FreeCAD.Vector(-sys.float_info.max, -sys.float_info.max, -sys.float_info.max)
        self._max = FreeCAD.Vector(sys.float_info.max, sys.float_info.max, sys.float_info.max)

    def setMinMax(self, min : FreeCAD.Vector, max : FreeCAD.Vector) -> None:
        self._min = min
        self._max = max

    def isEmpty(self) -> bool:
        return (self._min.x > self._max.x) or (self._min.y > self._max.y) or (self._min.z > self._max.z)

    def transform(self, transformation : Transformation) -> BoundingBox:
        p1 = transformation.transform(self._min)
        p2 = transformation.transform(self._max)

        newBox = BoundingBox()
        newBox.update(p1)
        newBox.update(p2)

        return newBox

    def update_x_min(self, xVal : float) -> None:
        if self._min.x > xVal:
            self._min.x = xVal

    def update_y_min(self, yVal : float) -> None:
        if self._min.y > yVal:
            self._min.y = yVal

    def update_z_min(self, zVal : float) -> None:
        if self._min.z > zVal:
            self._min.z = zVal

    def update_x_max(self, xVal : float) -> None:
        if self._max.x < xVal:
            self._max.x = xVal

    def update_y_max(self, yVal : float) -> None:
        if self._max.y < yVal:
            self._max.y = yVal

    def update_z_max(self, zVal : float) -> None:
        if self._max.z < zVal:
            self._max.z = zVal

    def update(self, c : FreeCAD.Vector) -> Self:
        self.update_x_min(c.x)
        self.update_y_min(c.y)
        self.update_z_min(c.z)

        self.update_x_max(c.x)
        self.update_y_max(c.y)
        self.update_z_max(c.z)

        return self

    def span(self) -> FreeCAD.Vector:
        return self._max.sub(self._min)
