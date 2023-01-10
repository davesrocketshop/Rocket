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
"""Class for drawing launch guides"""

__title__ = "FreeCAD Launch Guide"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

import FreeCAD
import math

from App.events.ComponentChangeEvent import ComponentChangeEvent

from App.ExternalComponent import ExternalComponent
from App.util.BoundingBox import BoundingBox
from App.position.AxialMethod import MIDDLE
from App.position.AngleMethod import AngleMethod
from App.position.AnglePositionable import AnglePositionable
from App.interfaces.BoxBounded import BoxBounded
from App.interfaces.LineInstanceable import LineInstanceable
from App.util.Coordinate import Coordinate, NUL
from App import Utilities
from App.SymmetricComponent import SymmetricComponent

from App.Constants import FEATURE_RAIL_GUIDE
from App.Constants import RAIL_GUIDE_BASE_FLAT, RAIL_GUIDE_BASE_CONFORMAL, RAIL_GUIDE_BASE_V

from App.ShapeHandlers.RailGuideShapeHandler import RailGuideShapeHandler

from DraftTools import translate

class FeatureRailGuide(ExternalComponent, AnglePositionable, BoxBounded, LineInstanceable):

    def __init__(self, obj):
        super().__init__(obj, MIDDLE)
        self.Type = FEATURE_RAIL_GUIDE

        if not hasattr(obj,"RailGuideBaseType"):
            obj.addProperty('App::PropertyEnumeration', 'RailGuideBaseType', 'RailGuide', translate('App::Property', 'Rail guide base type'))
            obj.RailGuideBaseType = [RAIL_GUIDE_BASE_FLAT, 
                    RAIL_GUIDE_BASE_CONFORMAL,
                    RAIL_GUIDE_BASE_V
                    ]
            obj.RailGuideBaseType = RAIL_GUIDE_BASE_FLAT

        if not hasattr(obj,"TopWidth"):
            obj.addProperty('App::PropertyLength', 'TopWidth', 'RailGuide', translate('App::Property', 'Width of the top of the launch guide')).TopWidth = 9.462
        if not hasattr(obj, 'MiddleWidth'):
            obj.addProperty('App::PropertyLength', 'MiddleWidth', 'RailGuide', translate('App::Property', 'Width of the inside of the launch guide')).MiddleWidth = 6.2375
        if not hasattr(obj, 'BaseWidth'):
            obj.addProperty('App::PropertyLength', 'BaseWidth', 'RailGuide', translate('App::Property', 'Width of the base or bottom of the launch guide')).BaseWidth = 15.0
        if not hasattr(obj,"TopThickness"):
            obj.addProperty('App::PropertyLength', 'TopThickness', 'RailGuide', translate('App::Property', 'Thickness of the top part of the launch guide')).TopThickness = 2.096
        if not hasattr(obj,"BaseThickness"):
            obj.addProperty('App::PropertyLength', 'BaseThickness', 'RailGuide', translate('App::Property', 'Thickness of the inside part of the launch guide')).BaseThickness = 3.429
        if not hasattr(obj,"Thickness"):
            obj.addProperty('App::PropertyLength', 'Thickness', 'RailGuide', translate('App::Property', 'Total thickness of the launch guide')).Thickness = 7.62
        if not hasattr(obj,"Diameter"):
            obj.addProperty('App::PropertyLength', 'Diameter', 'RailGuide', translate('App::Property', 'Diameter of the outside of the body tube for conformal base type')).Diameter = 24.79
        if not hasattr(obj, 'AutoDiameter'):
            obj.addProperty('App::PropertyBool', 'AutoDiameter', 'RailGuide', translate('App::Property', 'Automatically set the diameter when possible')).AutoDiameter = True
        if not hasattr(obj,"VAngle"):
            obj.addProperty('App::PropertyAngle', 'VAngle', 'RailGuide', translate('App::Property', 'Angle for V base type')).VAngle = 135.0
        if not hasattr(obj, 'ForwardSweep'):
            obj.addProperty('App::PropertyBool', 'ForwardSweep', 'RailGuide', translate('App::Property', 'The component has a sweep at the forward end')).ForwardSweep = False
        if not hasattr(obj,"ForwardSweepAngle"):
            obj.addProperty('App::PropertyAngle', 'ForwardSweepAngle', 'RailGuide', translate('App::Property', 'Angle for the forward end sweep')).ForwardSweepAngle = 30.0
        if not hasattr(obj, 'AftSweep'):
            obj.addProperty('App::PropertyBool', 'AftSweep', 'RailGuide', translate('App::Property', 'The component has a sweep at the aft end')).AftSweep = False
        if not hasattr(obj,"AftSweepAngle"):
            obj.addProperty('App::PropertyAngle', 'AftSweepAngle', 'RailGuide', translate('App::Property', 'Angle for the aft end sweep')).AftSweepAngle = 30.0
        if not hasattr(obj, 'Notch'):
            obj.addProperty('App::PropertyBool', 'Notch', 'RailGuide', translate('App::Property', 'The component has a notch down the middle')).Notch = False
        if not hasattr(obj,"NotchWidth"):
            obj.addProperty('App::PropertyLength', 'NotchWidth', 'RailGuide', translate('App::Property', 'Width of the notch')).NotchWidth = 3.00
        if not hasattr(obj,"NotchDepth"):
            obj.addProperty('App::PropertyLength', 'NotchDepth', 'RailGuide', translate('App::Property', 'Depth of the notch')).NotchDepth = 4.20

        if not hasattr(obj,"InstanceCount"):
            obj.addProperty('App::PropertyLength', 'InstanceCount', 'RailGuide', translate('App::Property', 'Instance count')).InstanceCount = 1
        if not hasattr(obj,"InstanceSeparation"):
            obj.addProperty('App::PropertyLength', 'InstanceSeparation', 'RailGuide', translate('App::Property', 'Instance separation')).InstanceSeparation = 0

        if not hasattr(obj,"Shape"):
            obj.addProperty('Part::PropertyPartShape', 'Shape', 'RailGuide', translate('App::Property', 'Shape of the launch guide'))

    def setDefaults(self):
        super().setDefaults()

        self._obj.Length = 20.0

    def onDocumentRestored(self, obj):
        FeatureRailGuide(obj)

        self._obj = obj

    def update(self):
        super().update()

        # Ensure any automatic variables are set
        self._setRadialOffset()
        location = self.getInstanceOffsets()

        self._obj.Placement.Base.y = location[0]._y
        self._obj.Placement.Base.z = location[0]._z

    def execute(self, obj):
        shape = RailGuideShapeHandler(obj)
        if shape is not None:
            shape.draw()

    def getLength(self):
        # Return the length of this component along the central axis
        length = self._obj.Length

        return float(length)

    def isAfter(self):
        return False

    def isCompatible(self, type):
        # Allow nothing to be attached to a LaunchLug
        return False

    def onChildEdited(self):
        self._obj.Proxy.setEdited()

    def componentChanged(self, e):
        super().componentChanged(e)

        self._setRadialOffset()

    def _setRadialOffset(self):    
        """
            shiftY and shiftZ must be computed here since calculating them
            in shiftCoordinates() would cause an infinite loop due to .toRelative
        """
        body = None
        parentRadius = 0.0
        
        body = self.getParent()
        while body is not None:
            if isinstance(body, SymmetricComponent):
                break
            body = body.getParent()
        
        if body is None:
            parentRadius = 0
        else:
            x1 = self.toRelative(NUL, body)[0]._x
            x2 = self.toRelative(Coordinate(self._obj.Length, 0, 0), body)[0]._x
            x1 = Utilities.clamp(x1, 0, body.getLength())
            x2 = Utilities.clamp(x2, 0, body.getLength())
            parentRadius = max(body.getRadius(x1), body.getRadius(x2))
        
        self._obj.RadialOffset = parentRadius #+ self.getOuterRadius()
        if self._obj.AutoDiameter:
            self._obj.Diameter = 2.0 * parentRadius

    def getPatternName(self):
        return "{0}-Line".format(self.getInstanceCount())

    def getAngleMethod(self):
        return AngleMethod.RELATIVE


    def setAngleMethod(self, newMethod):
        # no-op
        pass

    def getAngleOffset(self):
        return self._obj.AngleOffset

    def setAngleOffset(self, newAngleRadians):
        for listener in self._configListeners:
            if isinstance(listener, FeatureRailGuide):
                listener.setAngleOffset(newAngleRadians)

        rad = Utilities.clamp( newAngleRadians, -math.pi, math.pi)
        if self._obj.AngleOffset == rad:
            return

        self._obj.AngleOffset = rad
        self.fireComponentChangeEvent(ComponentChangeEvent.BOTH_CHANGE)

    def getInstanceSeparation(self):
        return self._obj.InstanceSeparation

    def setInstanceSeparation(self, separation):
        for listener in self._configListeners:
            if isinstance(listener, FeatureRailGuide):
                listener.setInstanceSeparation(separation)

        self._obj.InstanceSeparation = separation

    def setInstanceCount(self, newCount):
        for listener in self._configListeners:
            if isinstance(listener, FeatureRailGuide):
                listener.setInstanceCount(newCount)

        if newCount > 0:
            self._obj.InstanceCount = newCount

    def getInstanceCount(self):
        return int(self._obj.InstanceCount)

    def getInstanceBoundingBox(self):
        instanceBounds = BoundingBox()
        
        # instanceBounds.update(Coordinate(self.getLength(), 0,0))
        
        # r = self.getOuterRadius()
        # instanceBounds.update(Coordinate(0,r,r))
        # instanceBounds.update(Coordinate(0,-r,-r))
        
        return instanceBounds

    def getInstanceOffsets(self):
        toReturn = []
        
        yOffset = math.sin(math.radians(-self._obj.AngleOffset)) * (self._obj.RadialOffset)
        zOffset = math.cos(math.radians(-self._obj.AngleOffset)) * (self._obj.RadialOffset)
        
        for index in range(self.getInstanceCount()):
            toReturn.append(Coordinate(index*self._obj.InstanceSeparation, yOffset, zOffset))
        
        return toReturn
