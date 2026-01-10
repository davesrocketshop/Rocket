# SPDX-License-Identifier: LGPL-2.1-or-later

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
"""Base class for drawing elliptical nose cones"""

__title__ = "FreeCAD Elliptical Nose Shape Handler"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

from typing import Any

import FreeCAD
import Part
import math

from Rocket.ShapeHandlers.NoseShapeHandler import NoseShapeHandler


class NoseEllipseShapeHandler(NoseShapeHandler):

    def innerMinor(self, last : float) -> float:
        a = last
        b = self._radius - self._thickness
        x = self._thickness

        inner_minor = (b / a) * math.sqrt(a * a - x * x)
        return inner_minor

    def _arc(self, x, major, minor) -> Part.ArcOfEllipse | Part.Edge:
        if major > minor:
            arc = Part.ArcOfEllipse(Part.Ellipse(FreeCAD.Vector(x, 0), major, minor), math.pi/2, -math.pi)
        else:
            # Flip major and minor axis
            ellipse = Part.ArcOfEllipse(Part.Ellipse(FreeCAD.Vector(x, 0), minor, major), 0, math.pi/2)
            arc = ellipse.toShape().rotate(FreeCAD.Vector(x,0,0), FreeCAD.Vector(0,0,1), 90)

        return arc

    def drawSolid(self) -> list[Part.Edge]:
        outer_curve = self._arc(self._length, self._length, self._radius)

        edges = self.solidLines(outer_curve)
        return edges

    def drawSolidShoulder(self) -> list[Part.Edge]:
        outer_curve = self._arc(self._length, self._length, self._radius)

        edges = self.solidShoulderLines(outer_curve)
        return edges

    def drawHollow(self) -> list[Part.Edge]:
        outer_curve = self._arc(self._length, self._length, self._radius)
        inner_curve = self._arc(self._length, self._length - self._thickness, self._radius - self._thickness)

        edges = self.hollowLines(self._thickness, outer_curve, inner_curve)
        return edges

    def drawHollowShoulder(self) -> list[Part.Edge]:
        last = self._length - self._thickness
        minor_y = self.innerMinor(last)

        outer_curve = self._arc(self._length, self._length, self._radius)
        inner_curve = self._arc(self._length - self._thickness, self._length - 2 * self._thickness, minor_y)

        edges = self.hollowShoulderLines(self._thickness, minor_y, outer_curve, inner_curve)
        return edges

    def drawCapped(self) -> list[Part.Edge]:
        last = self._length - self._thickness
        minor_y = self.innerMinor(last)

        outer_curve = self._arc(self._length, self._length, self._radius)
        inner_curve = self._arc(self._length - self._thickness, self._length - 2 * self._thickness, minor_y)

        edges = self.cappedLines(self._thickness, minor_y, outer_curve, inner_curve)
        return edges

    def drawCappedShoulder(self) -> list[Part.Edge]:
        last = self._length - self._thickness
        minor_y = self.innerMinor(last)

        outer_curve = self._arc(self._length, self._length, self._radius)
        inner_curve = self._arc(self._length - self._thickness, self._length - 2 * self._thickness, minor_y)

        edges = self.cappedShoulderLines(self._thickness, minor_y, outer_curve, inner_curve)
        return edges
