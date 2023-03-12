# ***************************************************************************
# *   Copyright (c) 2021-2023 David Carter <dcarter@davidcarter.ca>         *
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
"""Base class for drawing parabolic series transitions"""

__title__ = "FreeCAD Parabolic Series Transition Handler"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"
    
from DraftTools import translate

from App.ShapeHandlers.TransitionShapeHandler import TransitionShapeHandler

from App.Utilities import validationError    
    
class TransitionParabolicShapeHandler(TransitionShapeHandler):

    def isValidShape(self):
        if self._coefficient < 0 or self._coefficient > 1:
            validationError(translate('Rocket', "For %s transitions the coefficient must be in the range (0 <= coefficient <= 1)") % self._type)
            return False
        return super().isValidShape()
            
    def _radiusAt(self, r1, r2, length, pos):
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
