# SPDX-License-Identifier: LGPL-2.1-or-later
# SPDX-FileCopyrightText: 2021 David Carter <dcarter@davidcarter.ca>
# SPDX-File-Notice: Part of the Rocket addon.


"""Base class for drawing ogive nose cones"""

__title__ = "FreeCAD Ogive Nose Shape Handler"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

import FreeCAD
import Part
import math

from Rocket.ShapeHandlers.NoseShapeHandler import NoseShapeHandler

class NoseSecantOgiveShapeHandler(NoseShapeHandler):

    def getRho(self) -> float:
        # For a secant ogive, rho is user defined.
        return self._ogiveRadius

    def getAlpha(self, length : float, radius : float) -> float:
        rho = self.getRho()
        alpha = math.acos(math.sqrt(length * length + radius * radius) / (2.0 * rho)) - math.atan(radius / length)
        return alpha

    def ogive_y(self, x : float, length : float, rho : float, alpha : float) -> float:
        y = math.sqrt(rho * rho - math.pow(rho * math.cos(alpha) - x, 2)) - (rho * math.sin(alpha))
        return y

    def innerMinor(self, last : float) -> float:
        radius = self._radius - self._thickness
        length = last
        rho = self.getRho()
        alpha = self.getAlpha(length, radius)

        inner_minor = self.ogive_y(length - self._thickness, length, rho, alpha)
        return inner_minor

    def ogive_curve(self, length : float, radius : float, resolution : int, min : float = 0) -> list[FreeCAD.Vector]:
        rho = self.getRho()
        alpha = self.getAlpha(length, radius)

        points = []
        for i in range(0, resolution):

            x = float(i) * ((length - min) / float(resolution))
            y = self.ogive_y(x, length, rho, alpha)
            points.append(FreeCAD.Vector(min + x, y))

        points.append(FreeCAD.Vector(min + length, radius))
        return points


    def findOgiveY(self, thickness : float, length : float, radius : float) -> float:
        rho = self.getRho()

        min = thickness
        max = length
        alpha = self.getAlpha(length, radius)
        x = (max - min) / 2 + min

        # Do a binary search to see where f(x) = thickness, to 1 mm
        while (max - min) > 0.0001:
            x = (max - min) / 2 + min
            y = self.ogive_y(x, length, rho, alpha)
            if (y == thickness):
                return x
            if (y < thickness):
                min = x
            else:
                max = x
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
