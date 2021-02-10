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
"""Base class for drawing Haack transitions"""

__title__ = "FreeCAD Haack Transition Handler"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"
    
import FreeCAD
import FreeCADGui
import Part
import math

from App.TransitionShapeHandler import TransitionShapeHandler

from App.Utilities import _err, _translate
    
    
class TransitionPowerShapeHandler(TransitionShapeHandler):

    def isValidShape(self):
        if self._coefficient <= 0 or self._coefficient > 1:
            _err(_translate("For %s transitions the coefficient must be in the range (0 < coefficient <= 1)") % self._type)
            return False
        return super().isValidShape()
            
    def _radiusAt(self, r1, r2, length, pos):
        if r1 > r2:
            radius = r1 - r2
            center = r2
            x = pos
        else:
            radius = r2 - r1
            center = r1
            x = length - pos

        y = radius * math.pow((x / length), self._coefficient)
        return y + center
