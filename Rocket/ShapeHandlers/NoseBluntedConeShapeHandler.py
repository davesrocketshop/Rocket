# ***************************************************************************
# *   Copyright (c) 2021-2024 David Carter <dcarter@davidcarter.ca>         *
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
"""Base class for drawing blunted conical nose cones"""

__title__ = "FreeCAD Conical Nose Shape Handler"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"
    
import FreeCAD
import Part
import math

from Rocket.ShapeHandlers.NoseShapeHandler import NoseShapeHandler
    
    
class NoseBluntedConeShapeHandler(NoseShapeHandler):

    def __init__(self, obj):
        super().__init__(obj)

        self._offsetRadius = self._radius   # Scratch value, only valid immediately after a call to getCurve()

    def getXt(self, length, radius, noseRadius):
        return math.pow(length, 2) / radius * math.sqrt(math.pow(noseRadius, 2) / (math.pow(radius, 2) + math.pow(length, 2)))

    def getYt(self, Xt, length, radius):
        return (Xt * radius) / length

    def getXo(self, Xt, Yt, noseRadius):
        return Xt + math.sqrt(math.pow(noseRadius, 2) - math.pow(Yt, 2))

    def getXa(self, Xo, noseRadius):
        return Xo - noseRadius
            
    def getBluntedLength(self, length, radius, noseRadius):

        min = length - noseRadius
        max = (-radius * length) / (noseRadius - radius)
        counter = 0

        # Do a binary search to 0.0001 mm
        precision = 0.0001
        while (max - min) > precision:
            mid = (max + min) / 2.0
            counter += 1
            Xt = self.getXt(mid, radius, noseRadius)
            Yt = self.getYt(Xt, mid, radius)
            Xo = self.getXo(Xt, Yt, noseRadius)
            Xa = self.getXa(Xo, noseRadius)
            if (length + Xa) > mid:
                min = mid
            else:
                max = mid

        return (mid, Xt, Yt, Xo, Xa)

    def getMidArc(self, Xo, Xt, radius):
        x = math.fabs(Xt + radius - Xo) / 2.0
        y = math.sqrt(radius * radius - x * x)
        return (x + Xo, y)

    def innerMinor(self, length, radius, offset):
        intercept = radius
        slope = intercept * -1 / (length)
        inner_minor = offset * slope + intercept
        return inner_minor

    def getCurve(self, length, radius, noseRadius, offset=0.0):
        (vLength, Xt, Yt, Xo, Xa) = self.getBluntedLength(length, radius, noseRadius)

        midX, midY = self.getMidArc(vLength - Xo, vLength - Xt, noseRadius)
        blunt = Part.Arc(
            FreeCAD.Vector(length - vLength + Xt + offset, Yt),
            FreeCAD.Vector(length - midX + offset, midY),
            FreeCAD.Vector(offset, 0.0)
        )
        self._offsetRadius = radius
        # if offset > 0:
        #     self._offsetRadius = self.innerMinor(vLength, radius, offset)
        line = Part.LineSegment(FreeCAD.Vector(length, self._offsetRadius), FreeCAD.Vector(length - vLength + Xt + offset, Yt))
        curve = Part.Wire([blunt.toShape(), line.toShape()])
        # curve = Part.Wire([blunt.toShape()])

        return curve

    def getOuterCurve(self):
        return self.getCurve(self._length, self._radius, self._noseRadius)

    def drawSolid(self):
        outer_curve = self.getOuterCurve()

        edges = self.solidLines(outer_curve)
        return edges

    def drawSolidShoulder(self):
        outer_curve = self.getOuterCurve()

        edges = self.solidShoulderLines(outer_curve)
        return edges

    def drawHollow(self):
        outer_curve = self.getOuterCurve()
        inner_curve = self.getCurve(self._length, self._radius - self._thickness, self._noseRadius - self._thickness, self._thickness)

        edges = self.hollowLines(self._thickness, outer_curve, inner_curve)
        return edges

    def drawHollowShoulder(self):
        outer_curve = self.getOuterCurve()
        inner_curve = self.getCurve(self._length - self._thickness, self._radius - self._thickness, self._noseRadius - self._thickness, self._thickness)
        minor_y = self._radius - self._thickness

        edges = self.hollowShoulderLines(self._thickness, minor_y, outer_curve, inner_curve)
        return edges

    def drawCapped(self):
        outer_curve = self.getOuterCurve()
        inner_curve = self.getCurve(self._length - self._thickness, self._radius - self._thickness, self._noseRadius - self._thickness, self._thickness)
        minor_y = self._radius - self._thickness

        edges = self.cappedLines(self._thickness, minor_y, outer_curve, inner_curve)
        return edges

    def drawCappedShoulder(self):
        outer_curve = self.getOuterCurve()
        inner_curve = self.getCurve(self._length - self._thickness, self._radius - self._thickness, self._noseRadius - self._thickness, self._thickness)
        minor_y = self._radius - self._thickness

        edges = self.cappedShoulderLines(self._thickness, minor_y, outer_curve, inner_curve)
        return edges
