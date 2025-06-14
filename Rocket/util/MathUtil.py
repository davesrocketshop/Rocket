#***************************************************************************
# *   Copyright (c) 2022-2025 David Carter <dcarter@davidcarter.ca>         *
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
"""Class for rocket components"""

__title__ = "FreeCAD Rocket Components"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

import math

EPSILON = 0.00000001 # 10mm^3 in m^3

class MathUtil:


    @classmethod
    def clamp(cls, x : float, min : float, max : float) -> float:
        """
            * Clamps the value x to the range min - max.
            * @param x    Original value.
            * @param min  Minimum value to return.
            * @param max  Maximum value to return.
            * @return     The clamped value.
        """
        if x < min:
            return min
        if x > max:
            return max
        return x

    @classmethod
    def reducePi(cls, x : float) -> float:
        """
            * Reduce the angle x to the range -PI - PI.
            * 
            * Either -PI and PI might be returned, depending on the rounding function.
            * 
            * @param x Original angle.
            * @return The equivalent angle in the range -PI ... PI.
        """
        d = math.floor(x / (2 * math.pi) + 0.5)
        return x - d * 2 * math.pi
