# SPDX-License-Identifier: LGPL-2.1-or-later
# SPDX-FileCopyrightText: 2021 David Carter <dcarter@davidcarter.ca>
# SPDX-File-Notice: Part of the Rocket addon.


"""Base class for drawing parabolic series transitions"""

__title__ = "FreeCAD Parabolic Series Transition Handler"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

import FreeCAD
translate = FreeCAD.Qt.translate

from Rocket.ShapeHandlers.TransitionShapeHandler import TransitionShapeHandler

from Rocket.Utilities import validationError

class TransitionParabolicShapeHandler(TransitionShapeHandler):

    def isValidShape(self) -> bool:
        if self._coefficient < 0 or self._coefficient > 1:
            validationError(translate('Rocket', "For %s transitions the coefficient must be in the range (0 <= coefficient <= 1)") % self._type)
            return False
        return super().isValidShape()

    def _radiusAt(self, r1 : float, r2 : float, length : float, pos : float) -> float:
        if r1 > r2:
            radius = r1 - r2
            center = r2
            x = length - pos
        else:
            radius = r2 - r1
            center = r1
            x = pos

        ratio = x / length
        y = radius * ((2 * ratio) - (self._coefficient * ratio * ratio)) / (2 - self._coefficient)
        return y + center
