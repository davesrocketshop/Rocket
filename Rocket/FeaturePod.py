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
"""Class for rocket pods"""

__title__ = "FreeCAD Rocket Pod"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

import math
from typing import Any

from Rocket.Utilities import translate

from Rocket.interfaces.RingInstanceable import RingInstanceable
import Rocket.position.AngleMethod as AngleMethod
from Rocket.position.AxialMethod import AxialMethod
import Rocket.position.RadiusMethod as RadiusMethod
from Rocket.ComponentAssembly import ComponentAssembly
from Rocket.util.Coordinate import Coordinate
from Rocket.Utilities import EPSILON

from Rocket.Constants import FEATURE_ROCKET, FEATURE_STAGE, FEATURE_PARALLEL_STAGE, FEATURE_POD

class FeaturePod(ComponentAssembly, RingInstanceable):

    def __init__(self, obj : Any) -> None:
        super().__init__(obj)

        self.Type = FEATURE_POD

        if not hasattr(obj,"PodCount"):
            obj.addProperty('App::PropertyInteger', 'PodCount', 'RocketComponent', translate('App::Property', 'Number of pods in a radial pattern')).PodCount = 1
        if not hasattr(obj,"PodSpacing"):
            obj.addProperty('App::PropertyAngle', 'PodSpacing', 'RocketComponent', translate('App::Property', 'Angle between consecutive pods')).PodSpacing = 360

        if not hasattr(obj, 'AngleMethod'):
            obj.addProperty('App::PropertyPythonObject', 'AngleMethod', 'RocketComponent', translate('App::Property', 'Method for calculating angle offsets')).AngleMethod = AngleMethod.RELATIVE
        if not hasattr(obj, 'AngleSeparation'):
            obj.addProperty('App::PropertyAngle', 'AngleSeparation', 'RocketComponent', translate('App::Property', 'Angle separation')).AngleSeparation = 180.0

        if not hasattr(obj, 'RadiusMethod'):
            obj.addProperty('App::PropertyPythonObject', 'RadiusMethod', 'RocketComponent', translate('App::Property', 'Method for calculating radius offsets')).RadiusMethod = RadiusMethod.RELATIVE
        if not hasattr(obj, 'RadiusOffset'):
            obj.addProperty('App::PropertyAngle', 'RadiusOffset', 'RocketComponent', translate('App::Property', 'Radius offset')).RadiusOffset = 0


        if not hasattr(obj,"Group"):
            obj.addExtension("App::GroupExtensionPython")

    def setDefaults(self) -> None:
        super().setDefaults()

    def onDocumentRestored(self, obj : Any) -> None:
        FeaturePod(obj)

        # Convert from the pre-1.0 material system if required
        self.convertMaterialAndAppearance(obj)

        self._obj = obj

    def execute(self, obj : Any) -> None:
        if not hasattr(obj,'Shape'):
            return

    def eligibleChild(self, childType : str) -> bool:
        return childType not in [FEATURE_ROCKET, FEATURE_STAGE, FEATURE_PARALLEL_STAGE]

    def onChildEdited(self) -> None:
        self._obj.Proxy.setEdited()

    def getInstanceAngleIncrement(self) -> float:
        return self._obj.AngleSeparation

    def getInstanceAngles(self) -> list:
        #		, angleMethod, angleOffset_rad
        baseAngle = self.getAngleOffset()
        incrAngle = self.getInstanceAngleIncrement()

        result = []
        for i in range(self.getInstanceCount()):
            result.append(baseAngle + incrAngle * i)

        return result

    def getInstanceLocations(self) -> list:
        return []

    def getInstanceOffsets(self) -> list:
        radius = self.radiusMethod.getRadius(self.getParent(), self, self._obj.RadiusOffset)

        toReturn = []
        angles = self.getInstanceAngles()
        for instanceNumber in range(self._obj.PodCount):
            curY = radius * math.cos(angles[instanceNumber])
            curZ = radius * math.sin(angles[instanceNumber])
            toReturn[instanceNumber] = Coordinate(0, curY, curZ)

        return toReturn

    def isAfter(self) -> bool:
        return False

    """
        Stages may be positioned relative to other stages. In that case, this will set the stage number
        against which this stage is positioned.
    """
    def getRelativeToStage(self) -> int:
        if not self.hasParent():
            return -1
        elif isinstance(self.getParent(), FeaturePod):
            return self.getParent().getParent().getChildPosition(self.getParent())

        return -1

    def setAxialMethod(self, newAxialMethod : AxialMethod) -> None:
        super().setAxialMethod(newAxialMethod)
        self.notifyComponentChanged()

    def getAxialOffset(self) -> float:
        return self._getAxialOffset(self._obj.AxialMethod)

    def _getAxialOffset(self, method : AxialMethod) -> float:
        returnValue = 0.0

        if self.isAfter():
            # remember the implicit (this instanceof Stage)
            raise Exception(translate("Rocket", "found a pod positioned via: AFTER, but is not on the centerline?!: {}  is {}")
                            .format(self.getName(), self.getAxialMethod().name()))
        else:
            returnValue = super().getAxialOffset(method)


        if EPSILON > math.abs(returnValue):
            returnValue = 0.0

        return returnValue

    def getAngleOffset(self) -> float:
        return self._obj.AngleOffset

    def getPatternName(self) -> str:
        return (self.getInstanceCount() + "-ring")

    def getRadiusOffset(self) -> float:
        return self._obj.RadiusOffset

    def getInstanceCount(self) -> int:
        return self._obj.PodCount

    def setInstanceCount(self, newCount : int) -> None:
        if newCount < 1:
            # there must be at least one instance....
            return

        self._obj.PodCount = newCount
        self._obj.AngleSeparation = math.pi * 2 / self._obj.PodCount
        self.notifyComponentChanged()

    def setAngleOffset(self, angle : float) -> None:
        self._obj.AngleOffset = angle
        self.notifyComponentChanged()

    def getAngleMethod(self) -> AngleMethod.AngleMethod:
        return self._obj.AngleMethod

    def setAngleMethod(self, method : AngleMethod.AngleMethod) -> None:
        pass

    def setRadiusOffset(self, radius : float) -> None:
        if radius == self._obj.RadiusOffset:
            return

        if self._obj.RadiusMethod.clampToZero():
            self._obj.RadiusOffset = 0.0
        else:
            self._obj.RadiusOffset = radius
        self.notifyComponentChanged()

    def getRadiusMethod(self) -> RadiusMethod.RadiusMethod:
        return self._obj.RadiusMethod

    def setRadiusMethod(self, method : RadiusMethod.RadiusMethod) -> None:
        if method == self._obj.RadiusMethod:
            return

        radius = self._obj.RadiusMethod.getRadius(self.getParent(), self, self._obj.RadiusOffset)	# Radius from the parent's center
        self.setRadius(method, radius)

    def setRadius(self, requestMethod : RadiusMethod.RadiusMethod, requestRadius : float) -> None:
        newRadius = requestRadius
        if self._obj.RadiusMethod.clampToZero():
            newRadius = 0.0

        self._obj.RadiusMethod = requestMethod
        self._obj.RadiusOffset =  self._obj.RadiusMethod.getAsOffset(self.getParent(), self, newRadius)
        self.notifyComponentChanged()
