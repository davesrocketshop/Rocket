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

    def __str__(self):
        return f'({self._x},{self._y},{self._z},{self._weight})'

    def __eq__(self, other):
        return self._x == other._x and self._y == other._y and self._z == other._z and self._weight == other._weight

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
    def transformation(self, rotation, translation = None):
        for i in range(3):
            for j in range(3):
                self._rotation[i][j] = rotation[i][j]

        if translation is None:
            self._translate = Coordinate(0,0,0,0)
        else:
            self._translate = translation

    # # Transform a coordinate according to this transformation.
    def transform(self, orig):
        x = self._rotation[self.X][self.X]*orig._x + self._rotation[self.X][self.Y]*orig._y + self._rotation[self.X][self.Z]*orig._z + self._translate._x
        y = self._rotation[self.Y][self.X]*orig._x + self._rotation[self.Y][self.Y]*orig._y + self._rotation[self.Y][self.Z]*orig._z + self._translate._y
        z = self._rotation[self.Z][self.X]*orig._x + self._rotation[self.Z][self.Y]*orig._y + self._rotation[self.Z][self.Z]*orig._z + self._translate._z
        
        return Coordinate(x,y,z,orig.weight)

    """ Add the coordinate and weight of two coordinates. """
    def add(self, other):
        return Coordinate(self._x + other._x, self._y + other._y, self._z + other._z,
                self._weight + other._weight)

    def addValues(self, x1, y1, z1, w1=0.0):
        return Coordinate(self._x + x1, self._y + y1, self._z + z1, self._weight + w1)

    """
        Subtract a Coordinate from this Coordinate.  The weight of the resulting Coordinate
        is the same as of this Coordinate; i.e. the weight of the argument is ignored.
    """
    def sub(self, other):
        return Coordinate(self._x - other._x, self._y - other._y, self._z - other._z, self._weight)

    """
        Subtract the specified values from this Coordinate.  The weight of the result
        is the same as the weight of this Coordinate.
    """
    def subValues(self, x1, y1, z1):
        return Coordinate(self._x - x1, self._y - y1, self._z - z1, self._weight)


    """
        Multiply the <code>Coordinate</code> with a scalar.  All coordinates and the
        weight are multiplied by the given scalar.
    """
    def multiply(self, m):
        return Coordinate(self._x * m, self._y * m, self._z * m, self._weight * m)

    """
         Dot product of two Coordinates, taken as vectors.  Equal to
         x1*x2+y1*y2+z1*z2
    """
    def dot(self, other, v2=None):
        if v2 is not None:
            return self._dot(other, v2)
        return self._x * other._x + self._y * other._y + self._z * other._z

    """
        Dot product of two Coordinates.
    """
    def _dot(self, v1, v2):
        return v1._x * v2._x + v1._y * v2._y + v1._z * v2._z

    """
        Cross product of two Coordinates taken as vectors
    """
    def cross(self, other):
        return Coordinate(self._y * other._z - self._z * other._y, self._z * other._x - self._x * other._z, self._x * other._y - self._y * other._x)

    """
        Distance from the origin to the Coordinate.
    """
    def length(self):
        if self.length < 0:
            length = math.sqrt(self.length2())

        return length

    """
        Square of the distance from the origin to the Coordinate.
    """
    def length2(self):
        return self._x * self._x + self._y * self._y + self._z * self._z


    """
        Return the largest of the absolute values of the coordinates.  This can be
        used as a norm of the vector that is faster to calculate than the
        2-norm.
    """
    def max(self):
        return max(math.abs(self._x), math.abs(self._y), math.abs(self._z))


    """
        Returns a new coordinate which has the same direction from the origin as this
        coordinate but is at a distance of one.  If this coordinate is the origin,
        this method throws an <code>IllegalStateException</code>.  The weight of the
        coordinate is unchanged.
    """
    def normalize(self):
        l = self.length()
        if l < 0.0000001:
            #raise IllegalStateException("Cannot normalize zero coordinate")
            raise Exception("Cannot normalize zero coordinate")

        return Coordinate(self._x / l, self._y / l, self._z / l, self._weight)

    """
        Weighted average of two coordinates.  If either of the weights are positive,
        the result is the weighted average of the coordinates and the weight is the sum
        of the original weights.  If the sum of the weights is zero (and especially if
        both of the weights are zero), the result is the unweighted average of the 
        coordinates with weight zero.
        
        If <code>other</code> is <code>null</code> then this <code>Coordinate</code> is
        returned.
    """
    def average(self, other):
        
        if other is None:
            return self
        
        w1 = self._weight + other._weight
        if abs(w1) < math.pow2(math.EPSILON):
            x1 = (self._x + other._x) / 2
            y1 = (self._y + other._y) / 2
            z1 = (self._z + other._z) / 2
            w1 = 0
        else:
            x1 = (self._x * self._weight + other._x * other._weight) / w1
            y1 = (self._y * self._weight + other._y * other._weight) / w1
            z1 = (self._z * self._weight + other._z * other._weight) / w1

        return Coordinate(x1, y1, z1, w1)

ZERO = Coordinate(0, 0, 0, 0)
NUL = Coordinate(0, 0, 0, 0)
NAN = Coordinate(math.nan, math.nan,math.nan, math.nan)
MAX = Coordinate( sys.float_info.max, sys.float_info.max, sys.float_info.max,sys.float_info.max)
MIN = Coordinate(-sys.float_info.max,-sys.float_info.max,-sys.float_info.max,0.0)

X_UNIT = Coordinate(1, 0, 0)
Y_UNIT = Coordinate(0, 1, 0)
Z_UNIT = Coordinate(0, 0, 1)
