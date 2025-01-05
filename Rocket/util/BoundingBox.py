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

import copy
from Rocket.util.Coordinate import Coordinate, MAX, MIN

class BoundingBox(object):

    _min = Coordinate()
    _max = Coordinate()

    def __init__(self, min=None, max=None):
        self.clear()

        if min is not None:
            self._min = copy.deepcopy(min)
        if max is not None:
            self._max = copy.deepcopy(max)

    def clear(self):
        self._min = MAX
        self._min._weight = 0.0
        self._max = MIN
        self._max._weight = 0.0

    def setMinMax(self, min, max):
        self._min = min
        self._max = max

    def isEmpty(self):
        return (self._min.x > self._max.x) or (self._min.y > self._max.y) or (self._min.z > self._max.z)

    def transform(self, transformation):
        p1 = transformation.transform(self._min)
        p2 = transformation.transform(self._max)

        newBox = BoundingBox()
        newBox.update(p1)
        newBox.update(p2)

        return newBox

    def update_x_min(self, xVal):
        if self._min.x > xVal:
           self._min.x = xVal

    def update_y_min(self, yVal):
        if self._min.y > yVal:
            self._min.y = yVal

    def update_z_min(self, zVal):
        if self._min.z > zVal:
            self._min.z = zVal

    def update_x_max(self, xVal):
        if self._max.x < xVal:
            self._max.x = xVal

    def update_y_max(self, yVal):
        if self._max.y < yVal:
            self._max.y = yVal

    def update_z_max(self, zVal):
        if self._max.z < zVal:
            self._max.z = zVal

    def update(self, c):
        self.update_x_min(c.x);
        self.update_y_min(c.y);
        self.update_z_min(c.z);

        self.update_x_max(c.x);
        self.update_y_max(c.y);
        self.update_z_max(c.z);

        return self

    def span(self):
        return self._max.sub(self._min)
