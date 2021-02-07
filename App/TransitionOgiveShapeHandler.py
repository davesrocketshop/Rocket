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
"""Base class for drawing ogive transitions"""

__title__ = "FreeCAD Ogive Transition Handler"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"
    
import FreeCAD
import FreeCADGui
import Part
import math

from App.TransitionShapeHandler import TransitionShapeHandler

from App.Utilities import _err, _msg
    
    
class TransitionOgiveShapeHandler(TransitionShapeHandler):

    def __init__(self, obj):
        super().__init__(obj)

        self._resolution = 100
            
    def _radiusAt(self, r1, r2, length, pos):
        if r1 > r2:
            radius = r1 - r2
            center = r2
            x = length - pos
        else:
            radius = r2 - r1
            center = r1
            x = pos
        rho = (radius * radius + length * length) / (2.0 * radius)

        y = math.sqrt(rho * rho - math.pow(length - x, 2)) + radius - rho
        return y + center

    def _ogive(self, r1, r2, length, min = 0):
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

    def _ogiveCurve(self):
        curve = self._ogive(self._foreRadius, self._aftRadius, self._length)
        ogive = self.makeSpline(curve)

        return ogive

    def _ogiveCurveInnerHollow(self):
        curve = self._ogive(self._foreRadius - self._thickness, self._aftRadius - self._thickness, self._length)
        ogive = self.makeSpline(curve)

        return ogive

    def _ogiveCurveInner(self, foreX, aftX, foreY, aftY):
        curve = self._ogive(foreY, aftY, foreX, aftX)
        ogive = self.makeSpline(curve)

        return ogive

    def drawSolid(self):
        outer_curve = self._ogiveCurve()

        edges = self.solidLines(outer_curve)
        return edges

    def drawSolidShoulder(self):
        outer_curve = self._ogiveCurve()

        edges = self.solidShoulderLines(outer_curve)
        return edges

    def drawSolidCore(self):
        outer_curve = self._ogiveCurve()

        edges = self.solidCoreLines(outer_curve)
        return edges

    def drawSolidShoulderCore(self):
        outer_curve = self._ogiveCurve()

        edges = self.solidShoulderCoreLines(outer_curve)
        return edges

    def drawHollow(self):
        outer_curve = self._ogiveCurve()
        inner_curve = self._ogiveCurveInnerHollow()

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

        outer_curve = self._ogiveCurve()
        inner_curve = self._ogiveCurveInner(innerForeX, innerAftX, innerForeY, innerAftY)

        edges = self.hollowShoulderLines(innerForeY, innerAftY, outer_curve, inner_curve)
        return edges

    def drawCapped(self):
        innerForeX = self._length - self._thickness
        innerAftX = self._thickness

        innerForeY = self._radiusAt(self._aftRadius - self._thickness, self._foreRadius - self._thickness, self._length, innerForeX)
        innerAftY = self._radiusAt(self._aftRadius - self._thickness, self._foreRadius - self._thickness, self._length, innerAftX)

        outer_curve = self._ogiveCurve()
        inner_curve = self._ogiveCurveInner(innerForeX, innerAftX, innerForeY, innerAftY)

        edges = self.cappedLines(innerForeY, innerAftY, outer_curve, inner_curve)
        return edges

    def drawCappedShoulder(self):
        innerForeX = self._length - self._thickness
        innerAftX = self._thickness

        innerForeY = self._radiusAt(self._aftRadius - self._thickness, self._foreRadius - self._thickness, self._length, innerForeX)
        innerAftY = self._radiusAt(self._aftRadius - self._thickness, self._foreRadius - self._thickness, self._length, innerAftX)

        outer_curve = self._ogiveCurve()
        inner_curve = self._ogiveCurveInner(innerForeX, innerAftX, innerForeY, innerAftY)

        edges = self.cappedShoulderLines(innerForeY, innerAftY, outer_curve, inner_curve)
        return edges
