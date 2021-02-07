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

    def _radiusAt(self, r1, r2, length, pos):
        major = length
        if r1 > r2:
            minor = r1 - r2
            center = r2
            x = length - pos
        else:
            minor = r2 - r1
            center = r1
            x = pos
        y = (minor / major) * math.sqrt(major * major - x * x)
        return y + center

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

    def _ellipseCurveInner(self, foreX, aftX, foreY, aftY):
        if self._foreRadius > self._aftRadius:
            return Part.ArcOfEllipse(Part.Ellipse(FreeCAD.Vector(foreX, aftY), foreX - aftX, foreY - aftY), math.pi/2, math.pi)
        else:
            return Part.ArcOfEllipse(Part.Ellipse(FreeCAD.Vector(aftX, foreY), foreX - aftX, aftY - foreY), 0.0, math.pi/2)

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

        innerForeY = self._radiusAt(self._foreRadius - self._thickness, self._aftRadius - self._thickness, self._length, innerForeX)
        innerAftY = self._radiusAt(self._foreRadius - self._thickness, self._aftRadius - self._thickness, self._length, innerAftX)

        outer_curve = self._ellipseCurve()
        inner_curve = self._ellipseCurveInner(innerForeX, innerAftX, innerForeY, innerAftY)

        edges = self.hollowShoulderLines(innerForeY, innerAftY, outer_curve, inner_curve)
        return edges

    def drawCapped(self):
        innerForeX = self._length - self._thickness
        innerAftX = self._thickness

        innerForeY = self._radiusAt(self._foreRadius - self._thickness, self._aftRadius - self._thickness, self._length, innerForeX)
        innerAftY = self._radiusAt(self._foreRadius - self._thickness, self._aftRadius - self._thickness, self._length, innerAftX)

        outer_curve = self._ellipseCurve()
        inner_curve = self._ellipseCurveInner(innerForeX, innerAftX, innerForeY, innerAftY)

        edges = self.cappedLines(innerForeY, innerAftY, outer_curve, inner_curve)
        return edges

    def drawCappedShoulder(self):
        innerForeX = self._length - self._thickness
        innerAftX = self._thickness

        innerForeY = self._radiusAt(self._foreRadius - self._thickness, self._aftRadius - self._thickness, self._length, innerForeX)
        innerAftY = self._radiusAt(self._foreRadius - self._thickness, self._aftRadius - self._thickness, self._length, innerAftX)

        outer_curve = self._ellipseCurve()
        inner_curve = self._ellipseCurveInner(innerForeX, innerAftX, innerForeY, innerAftY)

        edges = self.cappedShoulderLines(innerForeY, innerAftY, outer_curve, inner_curve)
        return edges
