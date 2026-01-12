# SPDX-License-Identifier: LGPL-2.1-or-later
# SPDX-File-Notice: Part of the Rocket addon.

################################################################################
#                                                                              #
#   © 2022 David Carter <dcarter@davidcarter.ca>                               #
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


"""Class for axial placement strategies"""

__title__ = "FreeCAD Rocket Components"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

import math
from typing import Any

import FreeCAD
translate = FreeCAD.Qt.translate

from Rocket.Utilities import reduce2Pi
from Rocket.position.DistanceMethod import DistanceMethod

class AngleMethod(DistanceMethod):

    _description : str = ""

    def __init__(self, newDescription : str):
        self._description = newDescription

    def __str__(self) -> str:
        return self._description

    def clampToZero(self) -> bool:
        return False

    def getAngle(self, parentComponent : Any, thisComponent : Any, angleOffset_radians : float) -> float:
        return 0.0

class RelativeAngleMethod(AngleMethod):

    def __init__(self):
        super().__init__(translate('App::Property', 'Relative to the parent component'))

    def clampToZero(self) -> bool:
        return True

    def getAngle(self, parentComponent : Any, thisComponent : Any, angleOffset_radians : float) -> float:
        return parentComponent.getAngleOffset() + angleOffset_radians

class FixedAngleMethod(AngleMethod):

    def __init__(self):
        super().__init__(translate('App::Property', 'Angle is fixed'))

    def clampToZero(self) -> bool:
        return True

    def getAngle(self, parentComponent : Any, thisComponent : Any, angleOffset_radians : float) -> float:
        return 0.0

class MirrorXYAngleMethod(AngleMethod):

    def __init__(self):
        super().__init__(translate('App::Property', "Mirror relative to the rocket's x-y plane"))

    def getAngle(self, parentComponent : Any, thisComponent : Any, angleOffset_radians : float) -> float:
        combinedAngle = reduce2Pi( parentComponent.getAngleOffset() + angleOffset_radians )

        if math.pi > combinedAngle:
            combinedAngle = -(combinedAngle - math.pi)

        return combinedAngle

RELATIVE = RelativeAngleMethod()
FIXED = FixedAngleMethod()
MIRROR_XY = MirrorXYAngleMethod()
