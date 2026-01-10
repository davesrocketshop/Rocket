# SPDX-License-Identifier: LGPL-2.1-or-later
# SPDX-FileCopyrightText: 2021 David Carter <dcarter@davidcarter.ca>
# SPDX-File-Notice: Part of the Rocket addon.


"""Base class for drawing Haack transitions"""

__title__ = "FreeCAD Haack Transition Handler"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

import math

import FreeCAD
translate = FreeCAD.Qt.translate

from Rocket.ShapeHandlers.TransitionShapeHandler import TransitionShapeHandler

from Rocket.Utilities import validationError

class TransitionHaackShapeHandler(TransitionShapeHandler):

    def isValidShape(self) -> bool:
        if self._coefficient < 0:
            validationError(translate('Rocket', "For %s transitions the coefficient must be >= 0") % self._type)
            return False
        return super().isValidShape()

    def _theta(self, x : float, length : float) -> float:
        return  math.acos(1 - 2*x/length)

    def _radiusAt(self, r1 : float, r2 : float, length : float, pos : float) -> float:
        if r1 > r2:
            radius = r1 - r2
            center = r2
            x = length - pos
        else:
            radius = r2 - r1
            center = r1
            x = pos

        theta = self._theta(x, length)
        y = radius * math.sqrt(theta - math.sin(2 * theta)/2
            + self._coefficient * math.pow(math.sin(theta), 3)) / math.sqrt(math.pi)
        return y + center
