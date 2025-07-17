# ***************************************************************************
# *   Copyright (c) 2025 David Carter <dcarter@davidcarter.ca>              *
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
"""Class for drawing greeblies"""

__title__ = "FreeCAD Greebly"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

import math
from typing import Any

from Rocket.Constants import FEATURE_GREEBLY
from Rocket.Constants import GREEBLY_TYPE_UNIVERSAL, GREEBLY_TYPE_PROXY

from Rocket.Tube import Tube
from Rocket.position import AxialMethod
from Rocket.position.AngleMethod import AngleMethod, RELATIVE
from Rocket.position.AnglePositionable import AnglePositionable
from Rocket.interfaces.BoxBounded import BoxBounded
from Rocket.interfaces.LineInstanceable import LineInstanceable
from Rocket.util.BoundingBox import BoundingBox
from Rocket.util.Coordinate import Coordinate, NUL
from Rocket import Utilities
from Rocket.SymmetricComponent import SymmetricComponent
from Rocket.ShapeHandlers.LaunchLugShapeHandler import LaunchLugShapeHandler

from DraftTools import translate

class FeatureGreebly(Tube, AnglePositionable, BoxBounded, LineInstanceable):

    def __init__(self, obj : Any) -> None:
        super().__init__(obj, AxialMethod.MIDDLE)

        self.Type = FEATURE_GREEBLY

        if not hasattr(obj, 'GreeblyType'):
            obj.addProperty('App::PropertyEnumeration', 'GreeblyType', 'RocketComponent', translate('App::Property', 'Greebly type'))
            obj.GreeblyType = [GREEBLY_TYPE_UNIVERSAL,
                        GREEBLY_TYPE_PROXY]
            obj.GreeblyType = GREEBLY_TYPE_UNIVERSAL
        else:
            obj.GreeblyType = [GREEBLY_TYPE_UNIVERSAL,
                        GREEBLY_TYPE_PROXY]

        if not hasattr(obj,"InstanceCount"):
            obj.addProperty('App::PropertyLength', 'InstanceCount', 'RocketComponent', translate('App::Property', 'Instance count')).InstanceCount = 1
        if not hasattr(obj,"InstanceSpacing"):
            obj.addProperty('App::PropertyAngle', 'InstanceSpacing', 'RocketComponent', translate('App::Property', 'Angle between consecutive greeblies')).InstanceSpacing = 360

        if not hasattr(obj, 'Base'):
            obj.addProperty('App::PropertyLink', 'Base', 'RocketComponent', translate('App::Property', 'The base object used to define the greebly shape'))

    def setDefaults(self) -> None:
        super().setDefaults()

        self._obj.Length = 25.4

    def onDocumentRestored(self, obj : Any) -> None:
        FeatureGreebly(obj)

        self._obj = obj

    def update(self) -> None:
        super().update()

        # Ensure any automatic variables are set
        self._setRadialOffset()
        location = self.getInstanceOffsets()

        self._obj.Placement.Base.y = location[0]._y
        self._obj.Placement.Base.z = location[0]._z

    def execute(self, obj : Any) -> None:
        # shape = LaunchLugShapeHandler(obj)
        # if shape is not None:
        #     shape.draw()
        pass

    def eligibleChild(self, childType : str) -> bool:
        return False

    def getLength(self) -> float:
        # Return the length of this component along the central axis
        length = self._obj.Length

        return float(length)

    def getOuterRadius(self, pos : float) -> float:
        return self.getOuterDiameter(pos) / 2.0

    def getOuterDiameter(self, pos : float) -> float:
        return float(self._obj.Diameter)

    def setOuterRadius(self, radius : float) -> None:
        self.setOuterDiameter(radius * 2.0)

    def setOuterDiameter(self, diameter : float) -> None:
        if self._obj.Diameter == diameter:
            return

        self._obj.Diameter = diameter
        self._obj.Thickness = min(self._obj.Thickness, self._obj.Diameter / 2.0)
        self.clearPreset()
        self.notifyComponentChanged()

    def getInnerRadius(self, pos : float) -> float:
        return self.getInnerDiameter(pos) / 2.0

    def getInnerDiameter(self, pos : float) -> float:
        return self._obj.Diameter - (2.0 * self._obj.Thickness)

    def setInnerRadius(self, radius : float) -> None:
        self.setInnerDiameter(radius * 2.0)

    def setInnerDiameter(self, diameter : float) -> None:
        self.setThickness((float(self._obj.Diameter) - float(diameter)) / 2.0)

    def getThickness(self) -> float:
        return self._obj.Thickness

    def setThickness(self, thickness : float) -> None:
        if self._obj.Thickness == thickness:
            return

        self._obj.Thickness = Utilities.clamp(thickness, 0, self._obj.Diameter / 2.0)
        self.clearPreset()
        self.notifyComponentChanged()

    def getAngleOffset(self) -> float:
        return self._obj.AngleOffset

    def setAngleOffset(self, angle : float) -> None:
        rad = math.fmod(angle, 360)
        if self._obj.AngleOffset == rad:
            return

        self._obj.AngleOffset = rad
        self.notifyComponentChanged()

    def setLength(self, length : float) -> None:
        if self._obj.Length == length:
            return

        self._obj.Length = length
        self.notifyComponentChanged()

    def isAfter(self) -> bool:
        return False

    def getInstanceOffsets(self) -> list:
        toReturn = []

        yOffset = math.sin(math.radians(-self._obj.AngleOffset)) * (self._obj.RadialOffset)
        zOffset = math.cos(math.radians(-self._obj.AngleOffset)) * (self._obj.RadialOffset)

        for index in range(self.getInstanceCount()):
            toReturn.append(Coordinate(index*self._obj.InstanceSeparation, yOffset, zOffset))

        return toReturn

    def componentChanged(self) -> None:
        super().componentChanged()

        self._setRadialOffset()

    def _setRadialOffset(self) -> None:
        body = None
        parentRadius = 0.0

        if self.hasParent():
            body = self.getParent()
        while body is not None:
            if isinstance(body, SymmetricComponent):
                break
            if body.hasParent():
                body = body.getParent()
            else:
                body = None

        if body is None:
            parentRadius = 0
        else:
            x1 = self.toRelative(NUL, body)[0]._x
            x2 = self.toRelative(Coordinate(self._obj.Length, 0, 0), body)[0]._x
            x1 = Utilities.clamp(x1, 0, body.getLength())
            x2 = Utilities.clamp(x2, 0, body.getLength())
            parentRadius = max(body.getRadius(x1), body.getRadius(x2))

        self._obj.RadialOffset = parentRadius + self.getOuterRadius(0)

    def getInstanceSeparation(self) -> float:
        return self._obj.InstanceSeparation

    def setInstanceSeparation(self, separation : float) -> None:
        self._obj.InstanceSeparation = separation

    def setInstanceCount(self, newCount : int) -> None:
        if newCount > 0:
            self._obj.InstanceCount = newCount

    def getInstanceCount(self) -> int:
        return int(self._obj.InstanceCount)

    def getInstanceBoundingBox(self) -> BoundingBox:
        instanceBounds = BoundingBox()

        instanceBounds.update(Coordinate(self.getLength(), 0,0))

        r = self.getOuterRadius(0)
        instanceBounds.update(Coordinate(0,r,r))
        instanceBounds.update(Coordinate(0,-r,-r))

        return instanceBounds

    def getPatternName(self) -> str:
        return "{0}-Line".format(self.getInstanceCount())

    def getAngleMethod(self) -> AngleMethod:
        return RELATIVE

    def setAngleMethod(self, newMethod : AngleMethod) -> None:
        # no-op
        pass
