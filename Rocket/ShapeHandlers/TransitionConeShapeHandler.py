# SPDX-License-Identifier: LGPL-2.1-or-later
# SPDX-File-Notice: Part of the Rocket addon.

################################################################################
#                                                                              #
#   © 2021 David Carter <dcarter@davidcarter.ca>                               #
#                                                                              #
#   This addon is free software: you can redistribute it and/or modify         #
#   it under the terms of the GNU Lesser General Public License as             #
#   published by the Free Software Foundation, either version 2.1              #
#   of the License, or (at your option) any later version.                     #
#                                                                              #
#   This addon is distributed in the hope that it will be useful,              #
#   but WITHOUT ANY WARRANTY; without even the implied warranty                #
#   of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.                    #
#   See the GNU Lesser General Public License for more details.                #
#                                                                              #
#   You should have received a copy of the GNU Lesser General Public           #
#   License along with this addon. If not, see https://www.gnu.org/licenses    #
#                                                                              #
################################################################################


"""Base class for drawing conical transitions"""

__title__ = "FreeCAD Conical Transition Shape Handler"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

from typing import Any

import FreeCAD
import Part

from Rocket.ShapeHandlers.TransitionShapeHandler import TransitionShapeHandler


class TransitionConeShapeHandler(TransitionShapeHandler):

    def isClippable(self) -> bool:
        # Clipped shape is the same as the unclipped
        return False

    def _radiusAt(self, r1 : float, r2 : float, length : float, pos : float) -> float:
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
    def _generateCurve(self, r1 : float, r2 : float, length : float, min : float = 0, max : float = 0) -> Any:
        if max == 0.0:
            max = length
        # if r1 > r2:
        #     tmp = r1
        #     r1 = r2
        #     r2 = tmp
        curve = Part.LineSegment(FreeCAD.Vector(min, r1), FreeCAD.Vector(max, r2))
        return curve
