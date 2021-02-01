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
"""Base class for drawing conical nose cones"""

__title__ = "FreeCAD Conical Nose Shape Handler"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"
    
import FreeCAD
import FreeCADGui
import Part
import math

from App.TransitionShapeHandler import TransitionShapeHandler

from App.Utilities import _msg, _err, _trace
    
    
class TransitionConeShapeHandler(TransitionShapeHandler):

	def radiusAt(self, x):
		intercept = self._foreRadius - self._thickness
		# Slope is the same for inner and outer curves
		#slope = (self._foreRadius - self._aftRadius) / self._length
		slope = (self._aftRadius - self._foreRadius) / self._length
		y = x * slope + intercept
		_msg("radiusAt(%f)-> %f: Slope %f, Intercept %f" % (x,y,slope,intercept))
		return y
 
	def drawSolid(self):
		outer_curve = Part.LineSegment(FreeCAD.Vector(self._length, self._aftRadius), FreeCAD.Vector(0.0, self._foreRadius))

		edges = self.solidLines(outer_curve)
		return edges
    
	def drawSolidShoulder(self):
		outer_curve = Part.LineSegment(FreeCAD.Vector(self._length, self._aftRadius), FreeCAD.Vector(0.0, self._foreRadius))

		edges = self.solidShoulderLines(outer_curve)
		return edges
 
	def drawSolidCore(self):
		outer_curve = Part.LineSegment(FreeCAD.Vector(self._length, self._aftRadius), FreeCAD.Vector(0.0, self._foreRadius))

		edges = self.solidCoreLines(outer_curve)
		return edges
    
	def drawSolidCoreShoulder(self):
		outer_curve = Part.LineSegment(FreeCAD.Vector(self._length, self._aftRadius), FreeCAD.Vector(0.0, self._foreRadius))

		edges = self.solidShoulderCoreLines(outer_curve)
		return edges
    
	def drawHollow(self):
		outer_curve = Part.LineSegment(FreeCAD.Vector(self._length, self._aftRadius), FreeCAD.Vector(0.0, self._foreRadius))
		inner_curve = Part.LineSegment(FreeCAD.Vector(self._length, self._aftRadius - self._thickness), FreeCAD.Vector(0.0, self._foreRadius - self._thickness))

		edges = self.hollowLines(outer_curve, inner_curve)
		return edges
    
	def drawHollowShoulder(self):
		# Calculate the offset from the end to maintain the thickness
		offset = self._length * self._thickness / self._radius
		last = self._length - offset
		minor_y = self.innerMinor(last)

		outer_curve = Part.LineSegment(FreeCAD.Vector(self._length, 0.0), FreeCAD.Vector(0.0, self._radius))
		inner_curve = Part.LineSegment(FreeCAD.Vector(last, 0.0), FreeCAD.Vector(self._thickness, minor_y))

		edges = self.hollowShoulderLines(last, minor_y, outer_curve, inner_curve)
		return edges
    
	def drawCapped(self):
		outer_curve = Part.LineSegment(FreeCAD.Vector(self._length, self._aftRadius), FreeCAD.Vector(0.0, self._foreRadius))
		inner_curve = Part.LineSegment(FreeCAD.Vector(self._length - self._thickness, self._aftRadius - self._thickness), FreeCAD.Vector(self._thickness, self._foreRadius - self._thickness))

		edges = self.cappedLines(self.radiusAt(self._thickness), self.radiusAt(self._length - self._thickness), outer_curve, inner_curve)
		return edges
    
	def drawCappedShoulder(self):
		# Calculate the offset from the end to maintain the thickness
		offset = self._length * self._thickness / self._radius
		last = self._length - offset
		minor_y = self.innerMinor(last)

		outer_curve = Part.LineSegment(FreeCAD.Vector(self._length, 0.0), FreeCAD.Vector(0.0, self._radius))
		inner_curve = Part.LineSegment(FreeCAD.Vector(last, 0.0), FreeCAD.Vector(self._thickness, minor_y))

		edges = self.cappedShoulderLines(last, minor_y, outer_curve, inner_curve)
		return edges
