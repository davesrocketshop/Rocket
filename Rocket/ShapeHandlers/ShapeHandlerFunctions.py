# SPDX-License-Identifier: LGPL-2.1-or-later
# SPDX-File-Notice: Part of the Rocket addon.

################################################################################
#                                                                              #
#   © 2026 David Carter <dcarter@davidcarter.ca>                               #
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


"""Base class for drawing shapes"""

__title__ = "FreeCAD Shape Handler Functions"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

from abc import ABC, abstractmethod
import math

class ShapeHandlerFunctions(ABC):

    @abstractmethod
    def _radiusAt(self, r1 : float, r2 : float, length : float, pos : float) -> float:
        ...

    def _coneRadiusAt(self, r1 : float, r2 : float, length : float, pos : float) -> float:
        if r1 < r2:
            intercept = r1
            x = pos
            slope = (r2 - r1) / length
        else:
            intercept = r2
            x = length - pos
            slope = (r1 - r2) / length

        y = float(x) * float(slope) + float(intercept)
        return y

    def _ogiveRadiusAt(self, r1 : float, r2 : float, length : float, pos : float) -> float:
        length = float(length)
        if r1 > r2:
            radius = float(r1) - float(r2)
            center = float(r2)
            x = float(pos)
        else:
            radius = float(r2) - float(r1)
            center = float(r1)
            x = length - float(pos)
        rho = (radius * radius + length * length) / (2.0 * radius)

        y = math.sqrt(rho * rho - math.pow(x, 2)) + radius - rho
        return y + center

    def _ellipseRadiusAt(self, r1 : float, r2 : float, length : float, pos : float) -> float:
        major = float(length)
        if r1 > r2:
            minor = float(r1) - float(r2)
            center = float(r2)
            x = float(pos)
        else:
            minor = float(r2) - float(r1)
            center = float(r1)
            x = float(length) - float(pos)

        try:
            y = (minor / major) * math.sqrt(major * major - x * x)
        except Exception as ex:
            raise ex
        return y + center

    def _haackTheta(self, x : float, length : float) -> float:
        return  math.acos(1 - 2 * float(x) / float(length))

    def _haackRadiusAt(self, r1 : float, r2 : float, length : float, pos : float, coefficient : float) -> float:
        if r1 > r2:
            radius = float(r1) - float(r2)
            center = float(r2)
            x = float(length) - float(pos)
        else:
            radius = float(r2) - float(r1)
            center = float(r1)
            x = float(pos)

        theta = self._haackTheta(x, length)
        y = radius * math.sqrt(theta - math.sin(2 * theta)/2
            + coefficient * math.pow(math.sin(theta), 3)) / math.sqrt(math.pi)
        return y + center

    def _parabolicRadiusAt(self, r1 : float, r2 : float, length : float, pos : float, coefficient : float) -> float:
        if r1 > r2:
            radius = float(r1) - float(r2)
            center = float(r2)
            x = float(length) - float(pos)
        else:
            radius = float(r2) - float(r1)
            center = float(r1)
            x = float(pos)

        ratio = x / float(length)
        y = radius * ((2 * ratio) - (coefficient * ratio * ratio)) / (2 - coefficient)
        return y + center

    def _powerRadiusAt(self, r1 : float, r2 : float, length : float, pos : float, coefficient : float) -> float:
        if r1 > r2:
            radius = float(r1) - float(r2)
            center = float(r2)
            x = float(length) - float(pos)
        else:
            radius = float(r2) - float(r1)
            center = float(r1)
            x = float(pos)

        y = radius * math.pow((x / float(length)), coefficient)
        return y + center
