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


"""Base class for drawing ogive nose cones"""

__title__ = "FreeCAD Ogive Nose Shape Handler"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

import FreeCAD
import Part
import math

from Rocket.ShapeHandlers.NoseShapeHandler import NoseShapeHandler

class NoseOgiveShapeHandler(NoseShapeHandler):

    def ogive_y(self, x : float, length : float, radius : float, rho : float) -> float:
        y = math.sqrt(rho * rho - math.pow(length - x, 2)) + radius - rho
        return y

    def innerMinor(self, last : float) -> float:
        radius = self._radius - self._thickness
        length = last
        rho = (radius * radius + length * length) / (2.0 * radius)

        inner_minor = self.ogive_y(length - self._thickness, length, radius, rho)
        return inner_minor

    def ogive_curve(self, length : float, radius : float, resolution : int, min : float = 0) -> list[FreeCAD.Vector]:
        rho = (radius * radius + length * length) / (2.0 * radius)
        points = []
        for i in range(0, resolution):

            x = float(i) * ((length - min) / float(resolution))
            y = self.ogive_y(x, length, radius, rho)
            points.append(FreeCAD.Vector(min + x, y))

        points.append(FreeCAD.Vector(min + length, radius))
        return points

    def findOgiveY(self, thickness : float, length : float, radius : float) -> float:
        rho = (radius * radius + length * length) / (2.0 * radius)

        min = thickness
        max = length
        x = 0

        # Do a binary search to see where f(x) = thickness, to 1 mm
        while (max - min) > 0.1:
            y = self.ogive_y(x, length, radius, rho)
            if (y == thickness):
                return x
            if (y > thickness):
                max = x
            else:
                min = x
            x = (max - min) / 2 + min
        return x

    def drawSolid(self) -> list[Part.Edge]:
        outer_curve = self.ogive_curve(self._length, self._radius, self._resolution)
        ogive = self.makeSpline(outer_curve)

        edges = self.solidLines(ogive)
        return edges

    def drawSolidShoulder(self) -> list[Part.Edge]:
        outer_curve = self.ogive_curve(self._length, self._radius, self._resolution)
        ogive = self.makeSpline(outer_curve)

        edges = self.solidShoulderLines(ogive)
        return edges

    def drawHollow(self) -> list[Part.Edge]:
        # Find the point where the thickness matches the desired thickness, so we don't get too narrow at the tip
        x = self.findOgiveY(self._thickness, self._length, self._radius)

        outer_curve = self.ogive_curve(self._length, self._radius, self._resolution)
        inner_curve = self.ogive_curve(self._length - x, self._radius - self._thickness, self._resolution, x)

        # Create the splines.
        ogive = self.makeSpline(outer_curve)
        innerOgive = self.makeSpline(inner_curve)

        edges = self.hollowLines(x, ogive, innerOgive)
        return edges

    def drawHollowShoulder(self) -> list[Part.Edge]:
        # Find the point where the thickness matches the desired thickness, so we don't get too narrow at the tip
        x = self.findOgiveY(self._thickness, self._length, self._radius)
        minor_y = self.innerMinor(self._length - self._thickness - x)

        outer_curve = self.ogive_curve(self._length, self._radius, self._resolution)
        inner_curve = self.ogive_curve(self._length - self._thickness - x, minor_y, self._resolution, x)

        # Create the splines.
        ogive = self.makeSpline(outer_curve)
        innerOgive = self.makeSpline(inner_curve)

        edges = self.hollowShoulderLines(x, minor_y, ogive, innerOgive)
        return edges

    def drawCapped(self) -> list[Part.Edge]:
        # Find the point where the thickness matches the desired thickness, so we don't get too narrow at the tip
        x = self.findOgiveY(self._thickness, self._length, self._radius)
        minor_y = self.innerMinor(self._length - self._thickness - x)

        outer_curve = self.ogive_curve(self._length, self._radius, self._resolution)
        inner_curve = self.ogive_curve(self._length - self._thickness - x, minor_y, self._resolution, x)

        # Create the splines.
        ogive = self.makeSpline(outer_curve)
        innerOgive = self.makeSpline(inner_curve)

        edges = self.cappedLines(x, minor_y, ogive, innerOgive)
        return edges

    def drawCappedShoulder(self) -> list[Part.Edge]:
        # Find the point where the thickness matches the desired thickness, so we don't get too narrow at the tip
        x = self.findOgiveY(self._thickness, self._length, self._radius)
        minor_y = self.innerMinor(self._length - self._thickness - x)

        outer_curve = self.ogive_curve(self._length, self._radius, self._resolution)
        inner_curve = self.ogive_curve(self._length - self._thickness - x, minor_y, self._resolution, x)

        # Create the splines.
        ogive = self.makeSpline(outer_curve)
        innerOgive = self.makeSpline(inner_curve)

        edges = self.cappedShoulderLines(x, minor_y, ogive, innerOgive)
        return edges
