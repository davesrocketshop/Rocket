#***************************************************************************
# *   Copyright (c) 2022-2025 David Carter <dcarter@davidcarter.ca>         *
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
"""Class for rocket components"""

__title__ = "FreeCAD Rocket Components"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

from typing import Any

import copy
from Rocket.util.Coordinate import Coordinate, MAX, MIN

class BoundingBox(object):

    _min : Coordinate = Coordinate()
    _max : Coordinate = Coordinate()

    def __init__(self, min : Coordinate | None = None, max : Coordinate | None = None) -> None:
        self.clear()

        if min is not None:
            self._min = copy.deepcopy(min)
        if max is not None:
            self._max = copy.deepcopy(max)

    def clear(self) -> None:
        self._min = MAX
        self._min._weight = 0.0
        self._max = MIN
        self._max._weight = 0.0

    def setMinMax(self, min : Coordinate, max : Coordinate) -> None:
        self._min = min
        self._max = max

    def isEmpty(self) -> bool:
        return (self._min._x > self._max._x) or (self._min._y > self._max._y) or (self._min._z > self._max._z)

    def transform(self, transformation) -> Any:
        p1 = transformation.transform(self._min)
        p2 = transformation.transform(self._max)

        newBox = BoundingBox()
        newBox.update(p1)
        newBox.update(p2)

        return newBox

    def update_x_min(self, xVal : float) -> None:
        if self._min._x > xVal:
           self._min._x = xVal

    def update_y_min(self, yVal : float) -> None:
        if self._min._y > yVal:
            self._min._y = yVal

    def update_z_min(self, zVal : float) -> None:
        if self._min._z > zVal:
            self._min._z = zVal

    def update_x_max(self, xVal : float) -> None:
        if self._max._x < xVal:
            self._max._x = xVal

    def update_y_max(self, yVal : float) -> None:
        if self._max._y < yVal:
            self._max._y = yVal

    def update_z_max(self, zVal : float) -> None:
        if self._max._z < zVal:
            self._max._z = zVal

    def update(self, c : Coordinate) -> Any:
        self.update_x_min(c._x)
        self.update_y_min(c._y)
        self.update_z_min(c._z)

        self.update_x_max(c._x)
        self.update_y_max(c._y)
        self.update_z_max(c._z)

        return self

    def span(self) -> Any:
        return self._max.sub(self._min)
