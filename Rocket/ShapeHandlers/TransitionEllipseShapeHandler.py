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
"""Base class for drawing elliptical transitions"""

__title__ = "FreeCAD Elliptical Transition Handler"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

from typing import Any

import FreeCAD
import Part
import math

from Rocket.ShapeHandlers.TransitionShapeHandler import TransitionShapeHandler

class TransitionEllipseShapeHandler(TransitionShapeHandler):

    def _radiusAt(self, r1 : float, r2 : float, length : float, pos : float) -> float:
        major = length
        if r1 > r2:
            minor = r1 - r2
            center = r2
            x = pos
        else:
            minor = r2 - r1
            center = r1
            x = length - pos

        try:
            y = (minor / major) * math.sqrt(major * major - x * x)
        except Exception as ex:
            raise ex
        return y + center

    def _eTheta(self, major : float, minor : float, tanTheta : float) -> float:
        #
        # Adgusts the angle to account for the eccentric anomalies. Refer to
        #  https://forum.freecadweb.org/viewtopic.php?f=22&t=55655
        eTheta = math.atan(major / minor * tanTheta)
        return eTheta

    # Override the default to use native shapes
    #
    # Doesn't work at the moment due to the extreme precision required in calculating the angles. The math is right
    # but the points are off by thousandths of a mm resulting in discontinuities. Kept here for further
    # development if desired
    def _generateClippedCurve(self, r1 : float, r2 : float, length : float, min : float = 0, max : float = 0) -> Any:
        if max == 0.0:
            max = self._length

        if r1 > r2:
            major = length - min
            minor = r1
            if min <= 0:
                theta1 = math.pi/2
            else:
                theta1 = self._eTheta(major, minor, (r1 / min))
            theta2 = math.pi - self._eTheta(major, minor, (r2 / max))

            curve = Part.ArcOfEllipse(Part.Ellipse(FreeCAD.Vector(max, 0.0), major, minor), theta1, theta2)
            return curve

        major = length - min
        minor = r2
        if min <= 0:
            theta2 = math.pi/2
        else:
            theta2 = self._eTheta(major, minor, (r2 / min))
        theta1 = self._eTheta(major, minor, (r1 / max))
        curve = Part.ArcOfEllipse(Part.Ellipse(FreeCAD.Vector(min, 0.0), major, minor), theta1, theta2)

        return curve

    # Override the default to use native shapes
    def _generateCurve(self, r1 : float, r2 : float, length : float, min : float = 0, max : float = 0) -> Any:
        if self._clipped:
            return super()._generateCurve(r1, r2, length, min, max)

        if max == 0.0:
            max = length - min
        if r1 > r2:
            radius = r1 - r2
            curve = Part.ArcOfEllipse(Part.Ellipse(FreeCAD.Vector(min, r2), max - min, radius), 0.0, math.pi/2)
            return curve

        radius = r2 - r1
        curve = Part.ArcOfEllipse(Part.Ellipse(FreeCAD.Vector(max, r1), max - min, radius), math.pi/2, math.pi)
        return curve
