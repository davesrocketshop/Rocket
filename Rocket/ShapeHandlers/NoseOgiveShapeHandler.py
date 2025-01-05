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
"""Base class for drawing ogive nose cones"""

__title__ = "FreeCAD Ogive Nose Shape Handler"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

import FreeCAD
import math

from Rocket.ShapeHandlers.NoseShapeHandler import NoseShapeHandler

class NoseOgiveShapeHandler(NoseShapeHandler):

    def ogive_y(self, x, length, radius, rho):
        y = math.sqrt(rho * rho - math.pow(length - x, 2)) + radius - rho
        return y

    def innerMinor(self, last):
        radius = self._radius - self._thickness
        length = last
        rho = (radius * radius + length * length) / (2.0 * radius)

        inner_minor = self.ogive_y(length - self._thickness, length, radius, rho)
        return inner_minor

    def ogive_curve(self, length, radius, resolution, min = 0):
        rho = (radius * radius + length * length) / (2.0 * radius)
        points = []
        for i in range(0, resolution):

            x = float(i) * ((length - min) / float(resolution))
            y = self.ogive_y(x, length, radius, rho)
            points.append(FreeCAD.Vector(min + x, y))

        points.append(FreeCAD.Vector(min + length, radius))
        return points

    def findOgiveY(self, thickness, length, radius):
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

    def drawSolid(self):
        outer_curve = self.ogive_curve(self._length, self._radius, self._resolution)
        ogive = self.makeSpline(outer_curve)

        edges = self.solidLines(ogive)
        return edges

    def drawSolidShoulder(self):
        outer_curve = self.ogive_curve(self._length, self._radius, self._resolution)
        ogive = self.makeSpline(outer_curve)

        edges = self.solidShoulderLines(ogive)
        return edges

    def drawHollow(self):
        # Find the point where the thickness matches the desired thickness, so we don't get too narrow at the tip
        x = self.findOgiveY(self._thickness, self._length, self._radius)

        outer_curve = self.ogive_curve(self._length, self._radius, self._resolution)
        inner_curve = self.ogive_curve(self._length - x, self._radius - self._thickness, self._resolution, x)

        # Create the splines.
        ogive = self.makeSpline(outer_curve)
        innerOgive = self.makeSpline(inner_curve)

        edges = self.hollowLines(x, ogive, innerOgive)
        return edges

    def drawHollowShoulder(self):
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

    def drawCapped(self):
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

    def drawCappedShoulder(self):
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
