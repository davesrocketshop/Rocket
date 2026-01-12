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


"""Class for rocket component coordinates"""

from __future__ import annotations # Required prior to 3.14

__title__ = "FreeCAD Rocket Components"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

import math
import sys

from Rocket.Utilities import EPSILON

class Coordinate():
    """ An mutable class of weighted coordinates.  The weights are non-negative.

        Can also be used as non-weighted coordinates with weight=0."""

    _translate = None
    _rotation = [[0 for i in range(3)] for j in range(3)]

    _X = 0
    _Y = 1
    _Z = 2

    def __init__(self, x : float = 0, y : float = 0, z : float = 0, weight : float = 0) -> None:
        self.x = x
        self.y = y
        self.z = z
        self._weight = weight

    def __str__(self) -> str:
        return f'({self.x},{self.y},{self.z},{self._weight})'

    def __eq__(self, other) -> bool:
        return self.x == other.x and self.y == other.y and self.z == other.z and self._weight == other._weight

    # Create transformation with given rotation matrix and translation.
    def transformation(self, rotation, translation : Coordinate | None = None) -> None:
        for i in range(3):
            for j in range(3):
                self._rotation[i][j] = rotation[i][j]

        if translation is None:
            self._translate = Coordinate(0,0,0,0)
        else:
            self._translate = translation

    # # Transform a coordinate according to this transformation.
    def transform(self, orig : Coordinate) -> Coordinate:
        if self._translate is None:
            self._translate = Coordinate(0,0,0,0)

        x = self._rotation[self._X][self._X]*orig.x + self._rotation[self._X][self._Y]*orig.y + self._rotation[self._X][self._Z]*orig.z + self._translate.x
        y = self._rotation[self._Y][self._X]*orig.x + self._rotation[self._Y][self._Y]*orig.y + self._rotation[self._Y][self._Z]*orig.z + self._translate.y
        z = self._rotation[self._Z][self._X]*orig.x + self._rotation[self._Z][self._Y]*orig.y + self._rotation[self._Z][self._Z]*orig.z + self._translate.z

        return Coordinate(x,y,z,orig._weight)

    """ Add the coordinate and weight of two coordinates. """
    def add(self, other : Coordinate) -> Coordinate:
        return Coordinate(float(self.x) + float(other.x), float(self.y) + float(other.y), float(self.z) + float(other.z),
                float(self._weight) + float(other._weight))

    def addValues(self, x1 : float, y1 : float, z1 : float, w1 : float = 0.0) -> Coordinate:
        return Coordinate(float(self.x) + float(x1), float(self.y) + float(y1), float(self.z) + float(z1), float(self._weight) + float(w1))

    """
        Subtract a Coordinate from this Coordinate.  The weight of the resulting Coordinate
        is the same as of this Coordinate; i.e. the weight of the argument is ignored.
    """
    def sub(self, other : Coordinate) -> Coordinate:
        return Coordinate(float(self.x) - float(other.x), float(self.y) - float(other.y), float(self.z) - float(other.z), float(self._weight))

    """
        Subtract the specified values from this Coordinate.  The weight of the result
        is the same as the weight of this Coordinate.
    """
    def subValues(self, x1 : float, y1 : float, z1 : float) -> Coordinate:
        return Coordinate(float(self.x) - float(x1), float(self.y) - float(y1), float(self.z) - float(z1), float(self._weight))


    """
        Multiply the <code>Coordinate</code> with a scalar.  All coordinates and the
        weight are multiplied by the given scalar.
    """
    def multiply(self, m : float) -> Coordinate:
        return Coordinate(float(self.x) * float(m), float(self.y) * float(m), float(self.z) * float(m), float(self._weight) * float(m))

    """
         Dot product of two Coordinates, taken as vectors.  Equal to
         x1*x2+y1*y2+z1*z2
    """
    def dot(self, other : Coordinate, v2 : Coordinate | None = None) -> float:
        if v2:
            return self._dot(other, v2)
        return float(self.x) * float(other.x) + float(self.y) * float(other.y) + float(self.z) * float(other.z)

    """
        Dot product of two Coordinates.
    """
    def _dot(self, v1 : Coordinate, v2 : Coordinate) -> float:
        return float(v1.x) * float(v2.x) + float(v1.y) * float(v2.y) + float(v1.z) * float(v2.z)

    """
        Cross product of two Coordinates taken as vectors
    """
    def cross(self, other : Coordinate) -> Coordinate:
        return Coordinate(float(self.y) * float(other.z) - float(self.z) * float(other.y), float(self.z) * float(other.x) - float(self.x) * float(other.z), float(self.x) * float(other.y) - float(self.y) * float(other.x))

    """
        Distance from the origin to the Coordinate.
    """
    def length(self) -> float:
        return math.sqrt(self.length2())

    """
        Square of the distance from the origin to the Coordinate.
    """
    def length2(self) -> float:
        return float(self.x) * float(self.x) + float(self.y) * float(self.y) + float(self.z) * float(self.z)


    """
        Return the largest of the absolute values of the coordinates.  This can be
        used as a norm of the vector that is faster to calculate than the
        2-norm.
    """
    def max(self) -> float:
        return max(math.fabs(self.x), math.fabs(self.y), math.fabs(self.z))


    """
        Returns a new coordinate which has the same direction from the origin as this
        coordinate but is at a distance of one.  If this coordinate is the origin,
        this method throws an <code>IllegalStateException</code>.  The weight of the
        coordinate is unchanged.
    """
    def normalize(self) -> Coordinate:
        l = self.length()
        if l < 0.0000001:
            #raise IllegalStateException("Cannot normalize zero coordinate")
            raise Exception("Cannot normalize zero coordinate")

        return Coordinate(self.x / l, self.y / l, self.z / l, self._weight)

    """
        Weighted average of two coordinates.  If either of the weights are positive,
        the result is the weighted average of the coordinates and the weight is the sum
        of the original weights.  If the sum of the weights is zero (and especially if
        both of the weights are zero), the result is the unweighted average of the
        coordinates with weight zero.

        If <code>other</code> is <code>null</code> then this <code>Coordinate</code> is
        returned.
    """
    def average(self, other : Coordinate) -> Coordinate:

        if other is None:
            return self

        w1 = self._weight + other._weight
        if abs(w1) < self.pow2(EPSILON):
            x1 = (self.x + other.x) / 2
            y1 = (self.y + other.y) / 2
            z1 = (self.z + other.z) / 2
            w1 = 0
        else:
            x1 = (self.x * self._weight + other.x * other._weight) / w1
            y1 = (self.y * self._weight + other.y * other._weight) / w1
            z1 = (self.z * self._weight + other.z * other._weight) / w1

        return Coordinate(x1, y1, z1, w1)
    
    def pow2(self, x : float) -> float:
        return x * x

ZERO = Coordinate(0, 0, 0, 0)
NUL = Coordinate(0, 0, 0, 0)
NAN = Coordinate(math.nan, math.nan,math.nan, math.nan)
MAX = Coordinate( sys.float_info.max, sys.float_info.max, sys.float_info.max,sys.float_info.max)
MIN = Coordinate(-sys.float_info.max,-sys.float_info.max,-sys.float_info.max,0.0)

X_UNIT = Coordinate(1, 0, 0)
Y_UNIT = Coordinate(0, 1, 0)
Z_UNIT = Coordinate(0, 0, 1)
