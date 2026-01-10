# SPDX-License-Identifier: LGPL-2.1-or-later
# SPDX-FileCopyrightText: 2021 David Carter <dcarter@davidcarter.ca>
# SPDX-File-Notice: Part of the Rocket addon.


"""Base class for drawing Haack nose cones"""

__title__ = "FreeCAD Haack Nose Shape Handler"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

import FreeCAD
import Part
import math

translate = FreeCAD.Qt.translate

from Rocket.ShapeHandlers.NoseShapeHandler import NoseShapeHandler
from Rocket.Utilities import validationError

class NoseHaackShapeHandler(NoseShapeHandler):

    def isValidShape(self) -> bool:
        if self._coefficient < 0:
            validationError(translate('Rocket', "For %s nose cones the coefficient must be >= 0") % self._type)
            return False
        return super().isValidShape()

    def innerMinor(self, last : float) -> float:
        radius = self._radius - self._thickness
        length = last

        inner_minor = self.haack_y(length - self._thickness, length, radius, self._coefficient)
        return inner_minor

    def theta(self, x : float, length : float) -> float:
        return  math.acos(1 - 2*x/length);

    def haack_y(self, x : float, length : float, radius : float, coefficient : float) -> float:
        theta = self.theta(x, length)
        return  radius * math.sqrt(theta - math.sin(2 * theta)/2
            + coefficient * math.pow(math.sin(theta), 3)) / math.sqrt(math.pi);

    def haack_curve(self, length : float, radius : float, resolution : int, coefficient : float, min : float = 0) -> list[FreeCAD.Vector]:
        points = []
        for i in range(0, resolution):

            x = float(i) * ((length - min) / float(resolution))
            y = self.haack_y(x, length, radius, coefficient)
            # if x > min:
            points.append(FreeCAD.Vector(min + x, y))

        points.append(FreeCAD.Vector(length, radius))
        return points

    def findHaackY(self, thickness : float, length : float, radius : float, coefficient : float) -> float:
        min = 0
        max = length
        x = 0

        # Do a binary search to see where f(x) = thickness, to 1 mm
        while (max - min) > 0.1:
            y = self.haack_y(x, length, radius, coefficient)
            if (y == thickness):
                return x
            if (y > thickness):
                max = x
            else:
                min = x
            x = (max - min) / 2 + min
        return x

    def drawSolid(self) -> list[Part.Edge]:
        outer_curve = self.haack_curve(self._length, self._radius, self._resolution, self._coefficient)
        spline = self.makeSpline(outer_curve)

        edges = self.solidLines(spline)
        return edges

    def drawSolidShoulder(self) -> list[Part.Edge]:
        outer_curve = self.haack_curve(self._length, self._radius, self._resolution, self._coefficient)
        spline = self.makeSpline(outer_curve)

        edges = self.solidShoulderLines(spline)
        return edges

    def drawHollow(self) -> list[Part.Edge]:
        # Find the point where the thickness matches the desired thickness, so we don't get too narrow at the tip
        x = self.findHaackY(self._thickness, self._length, self._radius, self._coefficient)

        outer_curve = self.haack_curve(self._length, self._radius, self._resolution, self._coefficient)
        inner_curve = self.haack_curve(self._length, self._radius - self._thickness, self._resolution, self._coefficient, x)

        # Create the splines.
        outerSpline = self.makeSpline(outer_curve)
        innerSpline = self.makeSpline(inner_curve)

        edges = self.hollowLines(x, outerSpline, innerSpline)
        return edges

    def drawHollowShoulder(self) -> list[Part.Edge]:
        # Find the point where the thickness matches the desired thickness, so we don't get too narrow at the tip
        x = self.findHaackY(self._thickness, self._length, self._radius, self._coefficient)
        minor_y = self.innerMinor(self._length)

        outer_curve = self.haack_curve(self._length, self._radius, self._resolution, self._coefficient)
        inner_curve = self.haack_curve(self._length - self._thickness, minor_y, self._resolution, self._coefficient, x)

        # Create the splines.
        outerSpline = self.makeSpline(outer_curve)
        innerSpline = self.makeSpline(inner_curve)

        edges = self.hollowShoulderLines(x, minor_y, outerSpline, innerSpline)
        return edges

    def drawCapped(self) -> list[Part.Edge]:
        # Find the point where the thickness matches the desired thickness, so we don't get too narrow at the tip
        x = self.findHaackY(self._thickness, self._length, self._radius, self._coefficient)
        minor_y = self.innerMinor(self._length)

        outer_curve = self.haack_curve(self._length, self._radius, self._resolution, self._coefficient)
        inner_curve = self.haack_curve(self._length - self._thickness, minor_y, self._resolution, self._coefficient, x)

        # Create the splines.
        outerSpline = self.makeSpline(outer_curve)
        innerSpline = self.makeSpline(inner_curve)

        edges = self.cappedLines(x, minor_y, outerSpline, innerSpline)
        return edges

    def drawCappedShoulder(self) -> list[Part.Edge]:
        # Find the point where the thickness matches the desired thickness, so we don't get too narrow at the tip
        x = self.findHaackY(self._thickness, self._length, self._radius, self._coefficient)
        minor_y = self.innerMinor(self._length)

        outer_curve = self.haack_curve(self._length, self._radius, self._resolution, self._coefficient)
        inner_curve = self.haack_curve(self._length - self._thickness, minor_y, self._resolution, self._coefficient, x)

        # Create the splines.
        outerSpline = self.makeSpline(outer_curve)
        innerSpline = self.makeSpline(inner_curve)

        edges = self.cappedShoulderLines(x, minor_y, outerSpline, innerSpline)
        return edges
