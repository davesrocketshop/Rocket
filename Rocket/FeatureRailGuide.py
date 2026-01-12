# SPDX-License-Identifier: LGPL-2.1-or-later
# SPDX-File-Notice: Part of the Rocket addon.

################################################################################
#                                                                              #
#   © 2021 David Carter <dcarter@davidcarter.ca>                               #
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


"""Class for drawing launch guides"""

__title__ = "FreeCAD Launch Guide"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

import math
from typing import Any

import FreeCAD

translate = FreeCAD.Qt.translate

from Rocket.ExternalComponent import ExternalComponent
from Rocket.util.BoundingBox import BoundingBox
from Rocket.position.AxialMethod import MIDDLE
from Rocket.position.AngleMethod import AngleMethod, RELATIVE
from Rocket.position.AnglePositionable import AnglePositionable
from Rocket.interfaces.BoxBounded import BoxBounded
from Rocket.interfaces.LineInstanceable import LineInstanceable
from Rocket.util.Coordinate import Coordinate, NUL
from Rocket import Utilities
from Rocket.SymmetricComponent import SymmetricComponent

from Rocket.Constants import FEATURE_RAIL_GUIDE
from Rocket.Constants import RAIL_GUIDE_BASE_FLAT, RAIL_GUIDE_BASE_CONFORMAL, RAIL_GUIDE_BASE_V

from Rocket.ShapeHandlers.RailGuideShapeHandler import RailGuideShapeHandler
from Rocket.Utilities import _wrn

class FeatureRailGuide(ExternalComponent, AnglePositionable, BoxBounded, LineInstanceable):

    def __init__(self, obj : Any) -> None:
        super().__init__(obj)
        self.Type = FEATURE_RAIL_GUIDE

        if not hasattr(obj,"RailGuideBaseType"):
            obj.addProperty('App::PropertyEnumeration', 'RailGuideBaseType', 'RocketComponent', translate('App::Property', 'Rail guide base type'))
            obj.RailGuideBaseType = [RAIL_GUIDE_BASE_FLAT,
                    RAIL_GUIDE_BASE_CONFORMAL,
                    RAIL_GUIDE_BASE_V
                    ]
            obj.RailGuideBaseType = RAIL_GUIDE_BASE_FLAT

        if not hasattr(obj,"FlangeWidth"):
            obj.addProperty('App::PropertyLength', 'FlangeWidth', 'RocketComponent', translate('App::Property', 'Width of the top of the launch guide')).FlangeWidth = 9.462
        if not hasattr(obj, 'MiddleWidth'):
            obj.addProperty('App::PropertyLength', 'MiddleWidth', 'RocketComponent', translate('App::Property', 'Width of the inside of the launch guide')).MiddleWidth = 6.2375
        if not hasattr(obj, 'BaseWidth'):
            obj.addProperty('App::PropertyLength', 'BaseWidth', 'RocketComponent', translate('App::Property', 'Width of the base or bottom of the launch guide')).BaseWidth = 15.0
        if not hasattr(obj,"FlangeHeight"):
            obj.addProperty('App::PropertyLength', 'FlangeHeight', 'RocketComponent', translate('App::Property', 'Height of the top part of the launch guide')).FlangeHeight = 2.096
        if not hasattr(obj,"BaseHeight"):
            obj.addProperty('App::PropertyLength', 'BaseHeight', 'RocketComponent', translate('App::Property', 'Height of the inside part of the launch guide')).BaseHeight = 3.429
        if not hasattr(obj,"Height"):
            obj.addProperty('App::PropertyLength', 'Height', 'RocketComponent', translate('App::Property', 'Total height of the launch guide')).Height = 7.62
        if not hasattr(obj,"Diameter"):
            obj.addProperty('App::PropertyLength', 'Diameter', 'RocketComponent', translate('App::Property', 'Diameter of the outside of the body tube for conformal base type')).Diameter = 24.79
        if not hasattr(obj, 'AutoDiameter'):
            obj.addProperty('App::PropertyBool', 'AutoDiameter', 'RocketComponent', translate('App::Property', 'Automatically set the diameter when possible')).AutoDiameter = True
        if not hasattr(obj,"VAngle"):
            obj.addProperty('App::PropertyAngle', 'VAngle', 'RocketComponent', translate('App::Property', 'Angle for V base type')).VAngle = 135.0
        if not hasattr(obj, 'ForwardSweep'):
            obj.addProperty('App::PropertyBool', 'ForwardSweep', 'RocketComponent', translate('App::Property', 'The component has a sweep at the forward end')).ForwardSweep = False
        if not hasattr(obj,"ForwardSweepAngle"):
            obj.addProperty('App::PropertyAngle', 'ForwardSweepAngle', 'RocketComponent', translate('App::Property', 'Angle for the forward end sweep')).ForwardSweepAngle = 30.0
        if not hasattr(obj, 'AftSweep'):
            obj.addProperty('App::PropertyBool', 'AftSweep', 'RocketComponent', translate('App::Property', 'The component has a sweep at the aft end')).AftSweep = False
        if not hasattr(obj,"AftSweepAngle"):
            obj.addProperty('App::PropertyAngle', 'AftSweepAngle', 'RocketComponent', translate('App::Property', 'Angle for the aft end sweep')).AftSweepAngle = 30.0
        if not hasattr(obj, 'Notch'):
            obj.addProperty('App::PropertyBool', 'Notch', 'RocketComponent', translate('App::Property', 'The component has a notch down the middle')).Notch = False
        if not hasattr(obj,"NotchWidth"):
            obj.addProperty('App::PropertyLength', 'NotchWidth', 'RocketComponent', translate('App::Property', 'Width of the notch')).NotchWidth = 3.00
        if not hasattr(obj,"NotchDepth"):
            obj.addProperty('App::PropertyLength', 'NotchDepth', 'RocketComponent', translate('App::Property', 'Depth of the notch')).NotchDepth = 4.20

        if not hasattr(obj,"InstanceCount"):
            obj.addProperty('App::PropertyInteger', 'InstanceCount', 'RocketComponent', translate('App::Property', 'Instance count')).InstanceCount = 1
        if not hasattr(obj,"InstanceSeparation"):
            obj.addProperty('App::PropertyLength', 'InstanceSeparation', 'RocketComponent', translate('App::Property', 'Instance separation')).InstanceSeparation = 0

    def setDefaults(self) -> None:
        super().setDefaults()

        self._obj.Length = 20.0
        self._obj.AxialMethod = MIDDLE

    def _migrate_from_3_0(self, obj : Any) -> None:
        _wrn("Rail guide migrating object from 3.0")

        width = obj.TopWidth
        top = obj.TopThickness
        base = obj.BaseThickness
        thickness = obj.Thickness
        angle = obj.CountersinkAngle

        obj.removeProperty("TopWidth")
        obj.removeProperty("TopThickness")
        obj.removeProperty("BaseThickness")
        obj.removeProperty("Thickness")
        obj.removeProperty("CountersinkAngle") # Enumeration values have changed

        obj.Proxy = FeatureRailGuide(obj)
        obj.Proxy._obj = obj

        obj.TopWidth = width
        obj.FlangeHeight = top
        obj.BaseHeight = base
        obj.Height = thickness
        obj.CountersinkAngle = angle

        # Convert from the pre-1.0 material system if required
        self.convertMaterialAndAppearance(obj)

    def onDocumentRestored(self, obj : Any) -> None:
        if hasattr(self, "TopWidth"):
            self._migrate_from_3_0(obj)
            return

        count = -1
        if hasattr(obj, "InstanceCount"):
            count = int(obj.InstanceCount)
            obj.removeProperty("InstanceCount")

        FeatureRailGuide(obj)

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
        shape = RailGuideShapeHandler(obj)
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
        body = None
        parentRadius = 0.0

        if self.hasParent():
            body = self.getParent()
        while body:
            if isinstance(body, SymmetricComponent):
                break
            if body.hasParent():
                body = body.getParent()
            else:
                body = None

        if body is None:
            parentRadius = 0
        else:
            x1 = self.toRelative(NUL, body)[0].x
            x2 = self.toRelative(Coordinate(self._obj.Length, 0, 0), body)[0].x
            x1 = Utilities.clamp(x1, 0, body.getLength())
            x2 = Utilities.clamp(x2, 0, body.getLength())
            parentRadius = max(body.getRadius(x1), body.getRadius(x2))

        if self._obj.AutoDiameter:
            self._obj.Diameter = 2.0 * parentRadius

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

        # instanceBounds.update(Coordinate(self.getLength(), 0,0))

        # r = self.getOuterRadius(0)
        # instanceBounds.update(Coordinate(0,r,r))
        # instanceBounds.update(Coordinate(0,-r,-r))

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

        Rail guides are never scaled.
        """
        return 1.0

    def isScaled(self) -> bool:
        """ Return True if the object or any of its parental lineage is scaled """
        return False

    def resetScale(self) -> None:
        pass
