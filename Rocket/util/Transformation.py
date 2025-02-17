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
"""Class for rocket component coordinates"""

__title__ = "FreeCAD Rocket Components"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

from Rocket.util.Coordinate import Coordinate

class Transformation():
    """ Defines an affine transformation of the form  A*x+c,  where x and c are Coordinates and
        A is a 3x3 matrix.

        The Transformations are immutable.  All modification methods return a new transformation."""

    _translate = Coordinate()
    _rotation = [[0 for i in range(3)] for j in range(3)]

    X = 0
    Y = 1
    Z = 2

    # Create transformation with given rotation matrix and translation.
    def __init__(self, rotation = None, translation = None):
        if rotation is None:
            self._rotation[self.X][self.X] = 1
            self._rotation[self.Y][self.Y] = 1
            self._rotation[self.Z][self.Z] = 1
        else:
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
