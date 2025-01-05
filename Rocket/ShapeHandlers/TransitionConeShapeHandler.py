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
"""Base class for drawing conical transitions"""

__title__ = "FreeCAD Conical Transition Shape Handler"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

import FreeCAD
import Part

from Rocket.ShapeHandlers.TransitionShapeHandler import TransitionShapeHandler


class TransitionConeShapeHandler(TransitionShapeHandler):

    def isClippable(self):
        # Clipped shape is the same as the unclipped
        return False

    def _radiusAt(self, r1, r2, length, pos):
        if r1 < r2:
            intercept = r1
            x = pos
            slope = (r2 - r1) / length
        else:
            intercept = r2
            x = length - pos
            slope = (r1 - r2) / length

        y = x * slope + intercept
        return y

    # Override the default to use native shapes
    def _generateCurve(self, r1, r2, length, min = 0, max = 0):
        if max == 0.0:
            max = length
        # if r1 > r2:
        #     tmp = r1
        #     r1 = r2
        #     r2 = tmp
        curve = Part.LineSegment(FreeCAD.Vector(min, r1), FreeCAD.Vector(max, r2))
        return curve
