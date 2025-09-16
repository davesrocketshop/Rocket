# ***************************************************************************
# *   Copyright (c) 2021-2025 David Carter <dcarter@davidcarter.ca>         *
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

from typing import Any

import FreeCAD
translate = FreeCAD.Qt.translate

from Rocket.position.DistanceMethod import DistanceMethod
from Rocket.FeatureBodyTube import FeatureBodyTube

class RadiusMethod(DistanceMethod):

    _description : str = ""

    def __init__(self, newDescription : str):
        self._description = newDescription

    def __str__(self):
        return self._description

    def clampToZero(self) -> bool:
        return False

    def getRadius(self, parentComponent : Any, thisComponent : Any, requestedOffset : float) -> float:
        return 0.0

    def getAsOffset(self, parentComponent : Any, thisComponent : Any, radius : float) -> float:
        return 0.0

class CoaxialRadiusMethod(RadiusMethod):

    def __init__(self):
        super().__init__(translate('App::Property', 'Same axis as the target component'))

    def clampToZero(self) -> bool:
        return False

    def getRadius(self, parentComponent : Any, thisComponent : Any, requestedOffset : float) -> float:
        return 0.0

    def getAsOffset(self, parentComponent : Any, thisComponent : Any, radius : float) -> float:
        return 0.0

class FreeRadiusMethod(RadiusMethod):

    def __init__(self):
        super().__init__(translate('App::Property', 'Center of the parent component'))

    def clampToZero(self) -> bool:
        return False

    def getRadius(self, parentComponent : Any, thisComponent : Any, requestedOffset : float) -> float:
        return requestedOffset

    def getAsOffset(self, parentComponent : Any, thisComponent : Any, radius : float) -> float:
        return radius

class RelativeRadiusMethod(RadiusMethod):

    def __init__(self):
        super().__init__(translate('App::Property', 'Surface of the parent component'))

    def clampToZero(self) -> bool:
        return False

    def getRadius(self, parentComponent : Any, thisComponent : Any, requestedOffset : float) -> float:
        radius = requestedOffset
        if isinstance(parentComponent, FeatureBodyTube):
            radius += parentComponent.getOuterRadius(0)

        from Rocket.position.RadiusPositionable import RadiusPositionable
        if isinstance(thisComponent, RadiusPositionable):
            radius += thisComponent.getBoundingRadius()

        return radius

    def getAsOffset(self, parentComponent : Any, thisComponent : Any, radius : float) -> float:
        offset = radius
        if isinstance(parentComponent, FeatureBodyTube):
            offset -= parentComponent.getOuterRadius(0)

        from Rocket.position.RadiusPositionable import RadiusPositionable
        if isinstance(thisComponent, RadiusPositionable):
            offset -= thisComponent.getBoundingRadius()

        return offset

class SurfaceRadiusMethod(RadiusMethod):

    def __init__(self):
        super().__init__(translate('App::Property', 'Surface of the parent component (without offset)'))

    def clampToZero(self) -> bool:
        return False

    def getRadius(self, parentComponent : Any, thisComponent : Any, requestedOffset : float) -> float:
        radius = 0.0
        if isinstance(parentComponent, FeatureBodyTube):
            radius += parentComponent.getOuterRadius(0)

        from Rocket.position.RadiusPositionable import RadiusPositionable
        if isinstance(thisComponent, RadiusPositionable):
            radius += thisComponent.getBoundingRadius()

        return radius

    def getAsOffset(self, parentComponent : Any, thisComponent : Any, radius : float) -> float:
        return 0.0

FREE = FreeRadiusMethod()
SURFACE = SurfaceRadiusMethod()
RELATIVE = RelativeRadiusMethod()
COAXIAL = CoaxialRadiusMethod()
