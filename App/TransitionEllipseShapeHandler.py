# ***************************************************************************
# *   Copyright (c) 2021 David Carter <dcarter@davidcarter.ca>              *
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
"""Base class for drawing elliptical transitions"""

__title__ = "FreeCAD Elliptical Transition Handler"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"
    
import FreeCAD
import FreeCADGui
import Part
import math

from App.TransitionShapeHandler import TransitionShapeHandler

from App.Utilities import _err, _msg
    
    
class TransitionEllipseShapeHandler(TransitionShapeHandler):

    # def _getRadius(self, x, radius, length, param):
    #     if x < 0 or x > length:
    #         _err("Value of x is outside the transition")
    #         return 0.0
    #     if radius < 0:
    #         _err("Radius is less than 0")
    #         return 0.0
    #     x = x * radius / length
    #     return math.sqrt(2 * radius * x - x * x)

    def _radiusAt(self, major, minor, pos):
        _msg("major = %f" % major)
        _msg("minor = %f" % minor)
        _msg("pos = %f" % pos)
        y = (minor / major) * math.sqrt(major * major - pos * pos)
        _msg("y = %f" % y)
        return y

    # def _radiusAt(self, major, minor, pos):
    #     # x = x * minor / major
    #     # return math.sqrt(2 * minor * x - x * x)

    #     _msg("major = %f" % major)
    #     _msg("minor = %f" % minor)
    #     _msg("pos = %f" % pos)
    #     y = (minor / major) * math.sqrt(major * major - pos * pos)
    #     _msg("y = %f" % y)
    #     return y
    #     # a = pos
    #     # # b = self._radius - self._thickness
    #     # b = major - self._thickness
    #     # x = self._thickness

    #     # inner_minor = (b / a) * math.sqrt(a * a - x * x)
    #     # return inner_minor

    def _ellipseCurve(self):
        if self._foreRadius > self._aftRadius:
            return Part.ArcOfEllipse(Part.Ellipse(FreeCAD.Vector(self._length, self._aftRadius), self._length, self._foreRadius - self._aftRadius), math.pi/2, math.pi)
        else:
            return Part.ArcOfEllipse(Part.Ellipse(FreeCAD.Vector(0, self._foreRadius), self._length, self._aftRadius - self._foreRadius), 0.0, math.pi/2)

    def _ellipseCurveInnerHollow(self):
        if self._foreRadius > self._aftRadius:
            return Part.ArcOfEllipse(Part.Ellipse(FreeCAD.Vector(self._length, self._aftRadius - self._thickness), self._length, self._foreRadius - self._aftRadius), math.pi/2, math.pi)
        else:
            return Part.ArcOfEllipse(Part.Ellipse(FreeCAD.Vector(0, self._foreRadius - self._thickness), self._length, self._aftRadius - self._foreRadius), 0.0, math.pi/2)

    def _ellipseCurveInner(self, foreX, aftX):
        if self._foreRadius > self._aftRadius:
            return Part.ArcOfEllipse(Part.Ellipse(FreeCAD.Vector(foreX, self._aftRadius - self._thickness), foreX - aftX, self._foreRadius - self._aftRadius), math.pi/2, math.pi)
        else:
            return Part.ArcOfEllipse(Part.Ellipse(FreeCAD.Vector(aftX, self._foreRadius - self._thickness), foreX - aftX, self._aftRadius - self._foreRadius), 0.0, math.pi/2)

    def drawSolid(self):
        outer_curve = self._ellipseCurve()

        edges = self.solidLines(outer_curve)
        return edges

    def drawSolidShoulder(self):
        outer_curve = self._ellipseCurve()

        edges = self.solidShoulderLines(outer_curve)
        return edges

    def drawSolidCore(self):
        outer_curve = self._ellipseCurve()

        edges = self.solidCoreLines(outer_curve)
        return edges

    def drawSolidShoulderCore(self):
        outer_curve = self._ellipseCurve()

        edges = self.solidShoulderCoreLines(outer_curve)
        return edges

    def drawHollow(self):
        outer_curve = self._ellipseCurve()
        inner_curve = self._ellipseCurveInnerHollow()

        edges = self.hollowLines(outer_curve, inner_curve)
        return edges

    def drawHollowShoulder(self):
        innerForeX = self._length
        if self._foreShoulder:
            innerForeX = self._length - self._thickness

        innerAftX = 0.0
        if self._aftShoulder:
            innerAftX = self._thickness

        outer_curve = self._ellipseCurve()
        inner_curve = self._ellipseCurveInner(innerForeX, innerAftX)

        minor = math.fabs(self._foreRadius - self._aftRadius)
        major = math.fabs(innerForeX - innerAftX)

        if self._foreRadius > self._aftRadius:
            edges = self.hollowShoulderLines(self._radiusAt(major, minor, innerForeX - self._thickness) + self._foreRadius - self._thickness, self._radiusAt(major, minor, innerAftX - self._thickness) + self._foreRadius - self._thickness, outer_curve, inner_curve)
        else:
            edges = self.hollowShoulderLines(self._radiusAt(major, minor, innerAftX - self._thickness) + self._aftRadius  - self._thickness, self._radiusAt(major, minor, innerForeX - self._thickness) + self._aftRadius  - self._thickness, outer_curve, inner_curve)
        return edges

    def drawCapped(self):
        outer_curve = self._ellipseCurve()
        inner_curve = Part.LineSegment(FreeCAD.Vector(self._thickness, self._radiusAt(self._thickness)), FreeCAD.Vector(self._length - self._thickness, self._radiusAt(self._length - self._thickness)))

        edges = self.cappedLines(self._radiusAt(self._length - self._thickness), self._radiusAt(self._thickness), outer_curve, inner_curve)
        return edges

    def drawCappedShoulder(self):
        outer_curve = self._ellipseCurve()
        inner_curve = Part.LineSegment(FreeCAD.Vector(self._thickness, self._radiusAt(self._thickness)), FreeCAD.Vector(self._length - self._thickness, self._radiusAt(self._length - self._thickness)))

        edges = self.cappedShoulderLines(self._radiusAt(self._length - self._thickness), self._radiusAt(self._thickness), outer_curve, inner_curve)
        return edges
