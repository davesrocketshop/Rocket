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
"""Class for drawing rail buttons"""

__title__ = "FreeCAD Rail Buttons"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

import math
from typing import Any

import FreeCAD

translate = FreeCAD.Qt.translate

from Rocket.ExternalComponent import ExternalComponent
from Rocket.util.BoundingBox import BoundingBox
from Rocket.position.AxialMethod import AxialMethod, MIDDLE
from Rocket.position.AngleMethod import AngleMethod, RELATIVE
from Rocket.position.AnglePositionable import AnglePositionable
from Rocket.interfaces.BoxBounded import BoxBounded
from Rocket.interfaces.LineInstanceable import LineInstanceable
from Rocket.util.Coordinate import Coordinate, NUL
from Rocket import Utilities
from Rocket.SymmetricComponent import SymmetricComponent

from Rocket.Constants import FEATURE_RAIL_BUTTON, FEATURE_FIN, FEATURE_FINCAN
from Rocket.Constants import RAIL_BUTTON_ROUND, RAIL_BUTTON_AIRFOIL
from Rocket.Constants import COUNTERSINK_ANGLE_60, COUNTERSINK_ANGLE_82, COUNTERSINK_ANGLE_90, COUNTERSINK_ANGLE_100, \
                            COUNTERSINK_ANGLE_110, COUNTERSINK_ANGLE_120, COUNTERSINK_ANGLE_NONE


from Rocket.ShapeHandlers.RailButtonShapeHandler import RailButtonShapeHandler
from Rocket.Utilities import _wrn

#
# Button dimensions were obtained here: https://www.rocketryforum.com/threads/rail-button-dimensions.30354/
# These have not been verified
#

class FeatureRailButton(ExternalComponent, AnglePositionable, BoxBounded, LineInstanceable):

    def __init__(self, obj : Any) -> None:
        super().__init__(obj)
        self.Type = FEATURE_RAIL_BUTTON

        # Default set to a BT-50
        if not hasattr(obj,"RailButtonType"):
            obj.addProperty('App::PropertyEnumeration', 'RailButtonType', 'RocketComponent', translate('App::Property', 'Rail button type'))
            obj.RailButtonType = [RAIL_BUTTON_ROUND,
                    RAIL_BUTTON_AIRFOIL
                    ]
            obj.RailButtonType = RAIL_BUTTON_ROUND

        if not hasattr(obj,"Diameter"):
            obj.addProperty('App::PropertyLength', 'Diameter', 'RocketComponent', translate('App::Property', 'Diameter of the outside of the rail button')).Diameter = 9.462
        if not hasattr(obj, 'InnerDiameter'):
            obj.addProperty('App::PropertyLength', 'InnerDiameter', 'RocketComponent', translate('App::Property', 'Diameter of the inside of the rail button')).InnerDiameter = 6.2375
        if not hasattr(obj,"FlangeHeight"):
            obj.addProperty('App::PropertyLength', 'FlangeHeight', 'RocketComponent', translate('App::Property', 'Height of the top part of the rail button')).FlangeHeight = 2.096
        if not hasattr(obj,"BaseHeight"):
            obj.addProperty('App::PropertyLength', 'BaseHeight', 'RocketComponent', translate('App::Property', 'Height of the bottom part of the rail button')).BaseHeight = 3.429
        if not hasattr(obj,"Height"):
            obj.addProperty('App::PropertyLength', 'Height', 'RocketComponent', translate('App::Property', 'Total height of the rail button')).Height = 7.62

        # Default fastener is a #6 screw
        if not hasattr(obj, 'Fastener'):
            obj.addProperty('App::PropertyBool', 'Fastener', 'RocketComponent', translate('App::Property', 'Create a countersunk hole for the fastener')).Fastener = True
        if not hasattr(obj,"CountersinkAngle"):
            obj.addProperty('App::PropertyEnumeration', 'CountersinkAngle', 'RocketComponent', translate('App::Property', 'Fastener countersink angle'))
            obj.CountersinkAngle = [COUNTERSINK_ANGLE_NONE,
                    COUNTERSINK_ANGLE_60,
                    COUNTERSINK_ANGLE_82,
                    COUNTERSINK_ANGLE_90,
                    COUNTERSINK_ANGLE_100,
                    COUNTERSINK_ANGLE_110,
                    COUNTERSINK_ANGLE_120
                    ]
            obj.CountersinkAngle = COUNTERSINK_ANGLE_82
        if not hasattr(obj,"ShankDiameter"):
            obj.addProperty('App::PropertyLength', 'ShankDiameter', 'RocketComponent', translate('App::Property', 'Fastener shank diameter')).ShankDiameter = 3.51
        if not hasattr(obj,"HeadDiameter"):
            obj.addProperty('App::PropertyLength', 'HeadDiameter', 'RocketComponent', translate('App::Property', 'Fastener head diameter')).HeadDiameter = 7.80

        if not hasattr(obj, 'FilletedTop'):
            obj.addProperty('App::PropertyBool', 'FilletedTop', 'RocketComponent', translate('App::Property', 'Apply a fillet to the top of the rail button')).FilletedTop = False
        if not hasattr(obj,"FilletRadius"):
            obj.addProperty('App::PropertyLength', 'FilletRadius', 'RocketComponent', translate('App::Property', 'Fillet radius')).FilletRadius = 0.5

        if not hasattr(obj,"InstanceCount"):
            obj.addProperty('App::PropertyInteger', 'InstanceCount', 'RocketComponent', translate('App::Property', 'Instance count')).InstanceCount = 1
        if not hasattr(obj,"InstanceSeparation"):
            obj.addProperty('App::PropertyLength', 'InstanceSeparation', 'RocketComponent', translate('App::Property', 'Instance separation')).InstanceSeparation = 0

    def setDefaults(self) -> None:
        super().setDefaults()

        self._obj.Length = 12.0
        self._obj.AxialMethod = MIDDLE

    def _migrate_from_3_0(self, obj : Any) -> None:
        _wrn("Rail button migrating object from 3.0")

        top = obj.TopThickness
        base = obj.BaseThickness
        thickness = obj.Thickness
        angle = obj.CountersinkAngle

        obj.removeProperty("TopThickness")
        obj.removeProperty("BaseThickness")
        obj.removeProperty("Thickness")
        obj.removeProperty("CountersinkAngle") # Enumeration values have changed

        obj.Proxy = FeatureRailButton(obj)
        obj.Proxy._obj = obj

        obj.FlangeHeight = top
        obj.BaseHeight = base
        obj.Height = thickness
        obj.CountersinkAngle = angle

        # Convert from the pre-1.0 material system if required
        self.convertMaterialAndAppearance(obj)

    def onDocumentRestored(self, obj : Any) -> None:
        if hasattr(self, "TopThickness"):
            self._migrate_from_3_0(obj)
            return

        count = -1
        if hasattr(obj, "InstanceCount"):
            count = int(obj.InstanceCount)
            obj.removeProperty("InstanceCount")

        FeatureRailButton(obj)

        if count > 0:
            obj.InstanceCount = count

        # Convert from the pre-1.0 material system if required
        self.convertMaterialAndAppearance(obj)

        self._obj = obj

    def update(self) -> None:
        super().update()

        # Ensure any automatic variables are set
        self._setRadialOffset()
        location = self.getInstanceOffsets()

        self._obj.Placement.Base.y = location[0].y
        self._obj.Placement.Base.z = location[0].z

    def execute(self, obj : Any) -> None:
        shape = RailButtonShapeHandler(obj)
        if shape:
            shape.draw()

    def getLength(self) -> float:
        # Return the length of this component along the central axis
        return float(self._obj.Length) / self.getScale()

    def isAfter(self) -> bool:
        return False

    def onChildEdited(self) -> None:
        self._obj.Proxy.setEdited()

    def componentChanged(self) -> None:
        super().componentChanged()

        self._setRadialOffset()

    def _setRadialOffset(self) -> None:
        """
            shiftY and shiftZ must be computed here since calculating them
            in shiftCoordinates() would cause an infinite loop due to .toRelative
        """
        body = None
        parentRadius = 0.0

        if self.hasParent():
            body = self.getParent()
        while body:
            if isinstance(body, SymmetricComponent):
                break
            if body.Type in [FEATURE_FIN, FEATURE_FINCAN]:
                break
            if body.hasParent():
                body = body.getParent()
            else:
                body = None

        if body is None:
            parentRadius = 0
        elif body.Type in [FEATURE_FIN, FEATURE_FINCAN]:
            body.setParentDiameter() # Set any auto values
            parentRadius = body.getForeRadius()
        else:
            x1 = self.toRelative(NUL, body)[0].x
            x2 = self.toRelative(Coordinate(self._obj.Length, 0, 0), body)[0].x
            x1 = Utilities.clamp(x1, 0, body.getLength())
            x2 = Utilities.clamp(x2, 0, body.getLength())
            parentRadius = max(body.getRadius(x1), body.getRadius(x2))

        self._obj.RadialOffset = parentRadius

    def getPatternName(self) -> str:
        return f"{self.getInstanceCount()}-Line"

    def getAngleMethod(self) -> AngleMethod:
        return RELATIVE

    def setAngleMethod(self, newMethod : AngleMethod) -> None:
        # no-op
        pass

    def getAngleOffset(self) -> float:
        return float(self._obj.AngleOffset)

    def setAngleOffset(self, angle : float) -> None:
        rad = Utilities.clamp(angle, -math.pi, math.pi)
        if self._obj.AngleOffset == rad:
            return

        self._obj.AngleOffset = rad
        self.notifyComponentChanged()

    def getInstanceSeparation(self) -> float:
        return float(self._obj.InstanceSeparation)

    def setInstanceSeparation(self, separation : float) -> None:
        self._obj.InstanceSeparation = separation

    def setInstanceCount(self, newCount : int) -> None:
        if newCount > 0:
            self._obj.InstanceCount = newCount

    def getInstanceCount(self) -> int:
        return int(self._obj.InstanceCount)

    def getInstanceBoundingBox(self) -> BoundingBox:
        instanceBounds = BoundingBox()
        return instanceBounds

    def getInstanceOffsets(self) -> list:
        toReturn = []

        yOffset = math.sin(math.radians(-self._obj.AngleOffset)) * (self._obj.RadialOffset)
        zOffset = math.cos(math.radians(-self._obj.AngleOffset)) * (self._obj.RadialOffset)

        for index in range(self.getInstanceCount()):
            toReturn.append(Coordinate(index*self._obj.InstanceSeparation, yOffset, zOffset))

        return toReturn

    def getScale(self) -> float:
        """
        Return the scale value

        Rail buttons are never scaled.
        """
        return 1.0

    def isScaled(self) -> bool:
        """ Return True if the object or any of its parental lineage is scaled """
        return False

    def resetScale(self) -> None:
        pass
