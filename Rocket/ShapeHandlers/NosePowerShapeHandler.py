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


"""Base class for drawing power series nose cones"""

__title__ = "FreeCAD Power Series Nose Shape Handler"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

import FreeCAD
import Part
import math

translate = FreeCAD.Qt.translate

from Rocket.ShapeHandlers.NoseShapeHandler import NoseShapeHandler
from Rocket.Utilities import validationError

class NosePowerShapeHandler(NoseShapeHandler):

    def isValidShape(self) -> bool:
        if self._coefficient <= 0 or self._coefficient > 1:
            validationError(translate('Rocket', "For %s nose cones the coefficient must be in the range (0 < coefficient <= 1)") % self._type)
            return False
        return super().isValidShape()

    def power_y(self, x : float, length : float, radius : float, k : float) -> float:
        y = radius * math.pow((x / length), k)
        return y

    def innerMinor(self, last, k) -> float:
        radius = self._radius - self._thickness
        length = last

        inner_minor = self.power_y(length - self._thickness, length, radius, k)
        return inner_minor

    def power_curve(self, length : float, radius : float, resolution : int, k : float, min : float = 0) -> list[FreeCAD.Vector]:
        points = []
        for i in range(0, resolution):

            x = float(i) * ((length - min) / float(resolution))
            y = self.power_y(x, length, radius, k)
            points.append(FreeCAD.Vector(min + x, y))

        points.append(FreeCAD.Vector(min + length, radius))
        return points

    def findPowerY(self, thickness : float, length : float, radius : float, k : float) -> float:
        min = thickness
        max = length
        x = 0

        # Do a binary search to see where f(x) = thickness, to 1 mm
        while (max - min) > 0.1:
            y = self.power_y(x, length, radius, k)
            if (y == thickness):
                return x
            if (y < thickness):
                min = x
            else:
                max = x
            x = (max - min) / 2 + min
        return x


    def drawSolid(self) -> list[Part.Edge]:
        outer_curve = self.power_curve(self._length, self._radius, self._resolution, self._coefficient)
        spline = self.makeSpline(outer_curve)

        edges = self.solidLines(spline)
        return edges

    def drawSolidShoulder(self) -> list[Part.Edge]:
        outer_curve = self.power_curve(self._length, self._radius, self._resolution, self._coefficient)
        spline = self.makeSpline(outer_curve)

        edges = self.solidShoulderLines(spline)
        return edges

    def drawHollow(self) -> list[Part.Edge]:
        # Find the point where the thickness matches the desired thickness, so we don't get too narrow at the tip
        x = self.findPowerY(self._thickness, self._length, self._radius, self._coefficient)

        outer_curve = self.power_curve(self._length, self._radius, self._resolution, self._coefficient)
        inner_curve = self.power_curve(self._length - x, self._radius - self._thickness, self._resolution, self._coefficient, x)

        # Create the splines.
        outerSpline = self.makeSpline(outer_curve)
        innerSpline = self.makeSpline(inner_curve)

        edges = self.hollowLines(x, outerSpline, innerSpline)
        return edges

    def drawHollowShoulder(self) -> list[Part.Edge]:
        # Find the point where the thickness matches the desired thickness, so we don't get too narrow at the tip
        x = self.findPowerY(self._thickness, self._length, self._radius, self._coefficient)
        minor_y = self.innerMinor(self._length - self._thickness - x, self._coefficient)

        outer_curve = self.power_curve(self._length, self._radius, self._resolution, self._coefficient)
        inner_curve = self.power_curve(self._length - self._thickness - x, minor_y, self._resolution, self._coefficient, x)

        # Create the splines.
        outerSpline = self.makeSpline(outer_curve)
        innerSpline = self.makeSpline(inner_curve)

        edges = self.hollowShoulderLines(x, minor_y, outerSpline, innerSpline)
        return edges

    def drawCapped(self) -> list[Part.Edge]:
        # Find the point where the thickness matches the desired thickness, so we don't get too narrow at the tip
        x = self.findPowerY(self._thickness, self._length, self._radius, self._coefficient)
        minor_y = self.innerMinor(self._length - self._thickness - x, self._coefficient)

        outer_curve = self.power_curve(self._length, self._radius, self._resolution, self._coefficient)
        inner_curve = self.power_curve(self._length - self._thickness - x, minor_y, self._resolution, self._coefficient, x)

        # Create the splines.
        outerSpline = self.makeSpline(outer_curve)
        innerSpline = self.makeSpline(inner_curve)

        edges = self.cappedLines(x, minor_y, outerSpline, innerSpline)
        return edges

    def drawCappedShoulder(self) -> list[Part.Edge]:
        # Find the point where the thickness matches the desired thickness, so we don't get too narrow at the tip
        x = self.findPowerY(self._thickness, self._length, self._radius, self._coefficient)
        minor_y = self.innerMinor(self._length - self._thickness - x, self._coefficient)

        outer_curve = self.power_curve(self._length, self._radius, self._resolution, self._coefficient)
        inner_curve = self.power_curve(self._length - self._thickness - x, minor_y, self._resolution, self._coefficient, x)

        # Create the splines.
        outerSpline = self.makeSpline(outer_curve)
        innerSpline = self.makeSpline(inner_curve)

        edges = self.cappedShoulderLines(x, minor_y, outerSpline, innerSpline)
        return edges
