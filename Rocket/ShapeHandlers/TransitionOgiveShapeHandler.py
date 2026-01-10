# SPDX-License-Identifier: LGPL-2.1-or-later
# SPDX-FileCopyrightText: 2021 David Carter <dcarter@davidcarter.ca>
# SPDX-File-Notice: Part of the Rocket addon.


"""Base class for drawing ogive transitions"""

__title__ = "FreeCAD Ogive Transition Handler"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

import math

from Rocket.ShapeHandlers.TransitionShapeHandler import TransitionShapeHandler

class TransitionOgiveShapeHandler(TransitionShapeHandler):

    def isClippable(self) -> bool:
        # Clipped shape is the same as the unclipped
        return False

    def _radiusAt(self, r1 : float, r2 : float, length : float, pos : float) -> float:
        if r1 > r2:
            radius = r1 - r2
            center = r2
            x = pos
        else:
            radius = r2 - r1
            center = r1
            x = length - pos
        rho = (radius * radius + length * length) / (2.0 * radius)

        y = math.sqrt(rho * rho - math.pow(x, 2)) + radius - rho
        return y + center
