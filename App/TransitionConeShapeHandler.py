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
"""Base class for drawing conical transitions"""

__title__ = "FreeCAD Conical Transition Shape Handler"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"
    
import FreeCAD
import FreeCADGui
import Part

from App.TransitionShapeHandler import TransitionShapeHandler
    
    
class TransitionConeShapeHandler(TransitionShapeHandler):

    def _radiusAt(self, r1, r2, length, pos):
        if r1 > r2:
            intercept = r1
        else:
            intercept = r2

        slope = (r1 - r2) / length
        y = pos * slope + intercept
        return y

    # def _radiusAt(self, x):
    #     intercept = self._aftRadius - self._thickness

    #     # Slope is the same for inner and outer curves
    #     slope = (self._foreRadius - self._aftRadius) / self._length
    #     y = x * slope + intercept
    #     return y

    # Override the default to use native shapes
    def _generateCurve(self, r1, r2, length, min = 0):
        curve = Part.LineSegment(FreeCAD.Vector(min, r2), FreeCAD.Vector(length, r1))
        return curve

    # def drawSolid(self):
    # 	outer_curve = Part.LineSegment(FreeCAD.Vector(0.0, self._aftRadius), FreeCAD.Vector(self._length, self._foreRadius))

    # 	edges = self.solidLines(outer_curve)
    # 	return edges

    # def drawSolidShoulder(self):
    # 	outer_curve = Part.LineSegment(FreeCAD.Vector(0.0, self._aftRadius), FreeCAD.Vector(self._length, self._foreRadius))

    # 	edges = self.solidShoulderLines(outer_curve)
    # 	return edges

    # def drawSolidCore(self):
    # 	outer_curve = Part.LineSegment(FreeCAD.Vector(0.0, self._aftRadius), FreeCAD.Vector(self._length, self._foreRadius))

    # 	edges = self.solidCoreLines(outer_curve)
    # 	return edges

    # def drawSolidShoulderCore(self):
    # 	outer_curve = Part.LineSegment(FreeCAD.Vector(0.0, self._aftRadius), FreeCAD.Vector(self._length, self._foreRadius))

    # 	edges = self.solidShoulderCoreLines(outer_curve)
    # 	return edges

    # def drawHollow(self):
    # 	outer_curve = Part.LineSegment(FreeCAD.Vector(0.0, self._aftRadius), FreeCAD.Vector(self._length, self._foreRadius))
    # 	inner_curve = Part.LineSegment(FreeCAD.Vector(0.0, self._aftRadius - self._thickness), FreeCAD.Vector(self._length, self._foreRadius - self._thickness))

    # 	edges = self.hollowLines(outer_curve, inner_curve)
    # 	return edges

    # def drawHollowShoulder(self):
    # 	innerForeX = 0.0
    # 	if self._foreShoulder:
    # 		innerForeX = self._length - self._thickness

    # 	innerAftX = self._length
    # 	if self._aftShoulder:
    # 		innerAftX = self._thickness

    # 	outer_curve = Part.LineSegment(FreeCAD.Vector(0.0, self._aftRadius), FreeCAD.Vector(self._length, self._foreRadius))
    # 	inner_curve = Part.LineSegment(FreeCAD.Vector(innerAftX, self._radiusAt(innerAftX)), FreeCAD.Vector(innerForeX, self._radiusAt(innerForeX)))

    # 	edges = self.hollowShoulderLines(self._radiusAt(innerForeX), self._radiusAt(innerAftX), outer_curve, inner_curve)
    # 	return edges

    # def drawCapped(self):
    # 	outer_curve = Part.LineSegment(FreeCAD.Vector(0.0, self._aftRadius), FreeCAD.Vector(self._length, self._foreRadius))
    # 	inner_curve = Part.LineSegment(FreeCAD.Vector(self._thickness, self._radiusAt(self._thickness)), FreeCAD.Vector(self._length - self._thickness, self._radiusAt(self._length - self._thickness)))

    # 	edges = self.cappedLines(self._radiusAt(self._length - self._thickness), self._radiusAt(self._thickness), outer_curve, inner_curve)
    # 	return edges

    # def drawCappedShoulder(self):
    # 	outer_curve = Part.LineSegment(FreeCAD.Vector(0.0, self._aftRadius), FreeCAD.Vector(self._length, self._foreRadius))
    # 	inner_curve = Part.LineSegment(FreeCAD.Vector(self._thickness, self._radiusAt(self._thickness)), FreeCAD.Vector(self._length - self._thickness, self._radiusAt(self._length - self._thickness)))

    # 	edges = self.cappedShoulderLines(self._radiusAt(self._length - self._thickness), self._radiusAt(self._thickness), outer_curve, inner_curve)
    # 	return edges
