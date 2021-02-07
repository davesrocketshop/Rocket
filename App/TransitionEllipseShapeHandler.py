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

    # Override the default to use native shapes
    def _generateCurve(self, r1, r2, length, min = 0):
        if r1 > r2:
            radius = r1 - r2
            curve = Part.ArcOfEllipse(Part.Ellipse(FreeCAD.Vector(length, r2), length - min, radius), math.pi/2, math.pi)
            return curve

        radius = r2 - r1
        curve = Part.ArcOfEllipse(Part.Ellipse(FreeCAD.Vector(min, r1), length - min, radius), 0.0, math.pi/2)
        return curve
