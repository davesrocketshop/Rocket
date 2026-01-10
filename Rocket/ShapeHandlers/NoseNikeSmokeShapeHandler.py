# SPDX-License-Identifier: LGPL-2.1-or-later

# ***************************************************************************
# *   Copyright (c) 2025 David Carter <dcarter@davidcarter.ca>              *
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
"""Class for drawing Nike Smoke nose cones"""

__title__ = "FreeCAD Nike Smoke Nose Shape Handler"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

from typing import Any

import FreeCAD
import Part

from Rocket.ShapeHandlers.NoseShapeHandler import NoseShapeHandler


class NoseNikeSmokeShapeHandler(NoseShapeHandler):

    def __init__(self, obj : Any) -> None:
        super().__init__(obj)

        # Set the scale based on the body diameter being 16.5 inches on the original
        self._scale = (16.5 * 25.4) / (self._radius * 2.0)

    def innerMinor(self, x) -> float:
        intercept = self._radius - self._thickness
        # slope = intercept * -1 / (offset - self._thickness)
        slope = intercept * -1 / (self._length)
        inner_minor = x * slope + intercept
        return inner_minor

    def drawSolid(self) -> list[Part.Edge]:
        outer_curve = Part.LineSegment(FreeCAD.Vector(0.0, 0.0), FreeCAD.Vector(self._length, self._radius))

        edges = self.solidLines(outer_curve)
        return edges

    def drawSolidShoulder(self) -> list[Part.Edge]:
        outer_curve = Part.LineSegment(FreeCAD.Vector(0.0, 0.0), FreeCAD.Vector(self._length, self._radius))

        edges = self.solidShoulderLines(outer_curve)
        return edges

    def drawHollow(self) -> list[Part.Edge]:
        # Calculate the offset from the end to maintain the thickness
        offset = self._length * self._thickness / self._radius

        outer_curve = Part.LineSegment(FreeCAD.Vector(0.0, 0.0), FreeCAD.Vector(self._length, self._radius))
        inner_curve = Part.LineSegment(FreeCAD.Vector(offset, 0.0), FreeCAD.Vector(self._length, self._radius - self._thickness))

        edges = self.hollowLines(offset, outer_curve, inner_curve)
        return edges

    def drawHollowShoulder(self) -> list[Part.Edge]:
        # Calculate the offset from the end to maintain the thickness
        offset = self._length * self._thickness / self._radius
        minor_y = self.innerMinor(self._thickness)

        outer_curve = Part.LineSegment(FreeCAD.Vector(0.0, 0.0), FreeCAD.Vector(self._length, self._radius))
        inner_curve = Part.LineSegment(FreeCAD.Vector(offset, 0.0), FreeCAD.Vector(self._length - self._thickness, minor_y))

        edges = self.hollowShoulderLines(offset, minor_y, outer_curve, inner_curve)
        # for edge in edges:
        #     Part.show(edge)
        return edges

    def drawCapped(self) -> list[Part.Edge]:
        # Calculate the offset from the end to maintain the thickness
        offset = self._length * self._thickness / self._radius
        minor_y = self.innerMinor(self._thickness)

        outer_curve = Part.LineSegment(FreeCAD.Vector(0.0, 0.0), FreeCAD.Vector(self._length, self._radius))
        inner_curve = Part.LineSegment(FreeCAD.Vector(offset, 0.0), FreeCAD.Vector(self._length - self._thickness, minor_y))

        edges = self.cappedLines(offset, minor_y, outer_curve, inner_curve)
        return edges

    def drawCappedShoulder(self) -> list[Part.Edge]:
        # Calculate the offset from the end to maintain the thickness
        offset = self._length * self._thickness / self._radius
        minor_y = self.innerMinor(self._thickness)

        outer_curve = Part.LineSegment(FreeCAD.Vector(0.0, 0.0), FreeCAD.Vector(self._length, self._radius))
        inner_curve = Part.LineSegment(FreeCAD.Vector(offset, 0.0), FreeCAD.Vector(self._length - self._thickness, minor_y))

        edges = self.cappedShoulderLines(offset, minor_y, outer_curve, inner_curve)
        return edges
