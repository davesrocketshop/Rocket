# ***************************************************************************
# *   Copyright (c) 2021 David Carter <dcarter@davidcarter.ca>              *
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
"""Class for rocket component coordinates"""

__title__ = "FreeCAD Rocket Components"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

import math
import sys

class Coordinate():
    """ An mutable class of weighted coordinates.  The weights are non-negative.

        Can also be used as non-weighted coordinates with weight=0."""

    _translate = None
    _rotation = [[0 for i in range(3)] for j in range(3)]
    X = 0
    Y = 1
    Z = 2

    def __init__(self, x=0, y=0, z=0, weight=0):
        self._x = x
        self._y = y
        self._z = z
        self._weight = weight

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, value):
        self._x = value

    @x.deleter
    def x(self):
        del self._x

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, value):
        self._y = value

    @y.deleter
    def y(self):
        del self._y

    @property
    def z(self):
        return self._z

    @z.setter
    def z(self, value):
        self._z = value

    @z.deleter
    def z(self):
        del self._z

    @property
    def weight(self):
        return self._weight

    @weight.setter
    def x(self, value):
        self._weight = value

    @weight.deleter
    def weight(self):
        del self._weight
    
    # Create transformation with given rotation matrix and translation.
    def Transformation(self, rotation, translation = None):
        for i in range(3):
            for j in range(3):
                self._rotation[i][j] = rotation[i][j]

        if translation is None:
            self._translate = Coordinate(0,0,0,0)
        else:
            self._translate = translation

    # Transform a coordinate according to this transformation.
    def transform(self, orig):
        x = self._rotation[self.X][self.X]*orig.x + self._rotation[self.X][self.Y]*orig.y + self._rotation[self.X][self.Z]*orig.z + self._translate.x;
        y = self._rotation[self.Y][self.X]*orig.x + self._rotation[self.Y][self.Y]*orig.y + self._rotation[self.Y][self.Z]*orig.z + self._translate.y;
        z = self._rotation[self.Z][self.X]*orig.x + self._rotation[self.Z][self.Y]*orig.y + self._rotation[self.Z][self.Z]*orig.z + self._translate.z;
        
        return Coordinate(x,y,z,orig.weight);

    # Subtract a Coordinate from this Coordinate.  The weight of the resulting Coordinate
    # is the same as of this Coordinate; i.e. the weight of the argument is ignored.
    def sub(self, other):
        return Coordinate(self.x - other.x, self.y - other.y, self.z - other.z, self.weight);

ZERO = Coordinate(0, 0, 0, 0);
NUL = Coordinate(0, 0, 0, 0);
NAN = Coordinate(math.nan, math.nan,math.nan, math.nan);
MAX = Coordinate( sys.float_info.max, sys.float_info.max, sys.float_info.max,sys.float_info.max);
MIN = Coordinate(-sys.float_info.max,-sys.float_info.max,-sys.float_info.max,0.0);

X_UNIT = Coordinate(1, 0, 0);
Y_UNIT = Coordinate(0, 1, 0);
Z_UNIT = Coordinate(0, 0, 1);
