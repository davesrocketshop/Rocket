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
"""Base class for drawing ogive transitions"""

__title__ = "FreeCAD Ogive Transition Handler"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"
    
import math

from App.ShapeHandlers.TransitionShapeHandler import TransitionShapeHandler

class TransitionOgiveShapeHandler(TransitionShapeHandler):

    def isClippable(self):
        # Clipped shape is the same as the unclipped
        return False
            
    def _radiusAt(self, r1, r2, length, pos):
        if r1 > r2:
            radius = r1 - r2
            center = r2
            x = length - pos
        else:
            radius = r2 - r1
            center = r1
            x = pos
        rho = (radius * radius + length * length) / (2.0 * radius)

        y = math.sqrt(rho * rho - math.pow(x, 2)) + radius - rho
        return y + center
