# ***************************************************************************
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
"""Class for axial placement strategies"""

__title__ = "FreeCAD Rocket Components"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

import math
from typing import Any

from DraftTools import translate

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
