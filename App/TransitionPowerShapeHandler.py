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
"""Base class for drawing Haack transitions"""

__title__ = "FreeCAD Haack Transition Handler"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"
    
import FreeCAD
import FreeCADGui
import Part
import math

from App.TransitionShapeHandler import TransitionShapeHandler

from App.Utilities import _err, _msg
    
    
class TransitionPowerShapeHandler(TransitionShapeHandler):

    def isValidShape(self):
        if self._coefficient <= 0 or self._coefficient > 1:
            _err("For %s transitions the coefficient must be in the range (0 < coefficient <= 1)" % self._type)
            return False
        return super().isValidShape()
            
    def _radiusAt(self, r1, r2, length, pos):
        if r1 > r2:
            radius = r1 - r2
            center = r2
            x = length - pos
        else:
            radius = r2 - r1
            center = r1
            x = pos

        y = radius * math.pow((x / length), self._coefficient)
        return y + center

    def _power(self, r1, r2, length, min = 0):
        if r1 > r2:
            radius = r1 - r2
        else:
            radius = r2 - r1

        points = []
        for i in range(0, self._resolution):
            
            x = float(i) * ((length - min) / float(self._resolution))
            y = self._radiusAt(r1, r2, length, x)
            points.append(FreeCAD.Vector(length - x, y))

        points.append(FreeCAD.Vector(min, r2))
        return points

    def _curve(self):
        curve = self._power(self._foreRadius, self._aftRadius, self._length)
        return self.makeSpline(curve)

    def _curveInnerHollow(self):
        curve = self._power(self._foreRadius - self._thickness, self._aftRadius - self._thickness, self._length)
        ogive = self.makeSpline(curve)

        return ogive

    def _curveInner(self, foreX, aftX, foreY, aftY):
        curve = self._power(foreY, aftY, foreX, aftX)
        ogive = self.makeSpline(curve)

        return ogive

    def drawSolid(self):
        outer_curve = self._curve()

        edges = self.solidLines(outer_curve)
        return edges

    def drawSolidShoulder(self):
        outer_curve = self._curve()

        edges = self.solidShoulderLines(outer_curve)
        return edges

    def drawSolidCore(self):
        outer_curve = self._curve()

        edges = self.solidCoreLines(outer_curve)
        return edges

    def drawSolidShoulderCore(self):
        outer_curve = self._curve()

        edges = self.solidShoulderCoreLines(outer_curve)
        return edges

    def drawHollow(self):
        outer_curve = self._curve()
        inner_curve = self._curveInnerHollow()

        edges = self.hollowLines(outer_curve, inner_curve)
        return edges

    def drawHollowShoulder(self):
        innerForeX = self._length
        if self._foreShoulder:
            innerForeX = self._length - self._thickness

        innerAftX = 0.0
        if self._aftShoulder:
            innerAftX = self._thickness

        innerForeY = self._radiusAt(self._aftRadius - self._thickness, self._foreRadius - self._thickness, self._length, innerForeX)
        innerAftY = self._radiusAt(self._aftRadius - self._thickness, self._foreRadius - self._thickness, self._length, innerAftX)

        outer_curve = self._curve()
        inner_curve = self._curveInner(innerForeX, innerAftX, innerForeY, innerAftY)

        edges = self.hollowShoulderLines(innerForeY, innerAftY, outer_curve, inner_curve)
        return edges

    def drawCapped(self):
        innerForeX = self._length - self._thickness
        innerAftX = self._thickness

        innerForeY = self._radiusAt(self._aftRadius - self._thickness, self._foreRadius - self._thickness, self._length, innerForeX)
        innerAftY = self._radiusAt(self._aftRadius - self._thickness, self._foreRadius - self._thickness, self._length, innerAftX)

        outer_curve = self._curve()
        inner_curve = self._curveInner(innerForeX, innerAftX, innerForeY, innerAftY)

        edges = self.cappedLines(innerForeY, innerAftY, outer_curve, inner_curve)
        return edges

    def drawCappedShoulder(self):
        innerForeX = self._length - self._thickness
        innerAftX = self._thickness

        innerForeY = self._radiusAt(self._aftRadius - self._thickness, self._foreRadius - self._thickness, self._length, innerForeX)
        innerAftY = self._radiusAt(self._aftRadius - self._thickness, self._foreRadius - self._thickness, self._length, innerAftX)

        outer_curve = self._curve()
        inner_curve = self._curveInner(innerForeX, innerAftX, innerForeY, innerAftY)

        edges = self.cappedShoulderLines(innerForeY, innerAftY, outer_curve, inner_curve)
        return edges
