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
"""Class for drawing rail buttons"""

__title__ = "FreeCAD Rail Buttons"
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

from App.Constants import FEATURE_RAIL_BUTTON, FEATURE_FIN, FEATURE_FINCAN
from App.Constants import RAIL_BUTTON_ROUND, RAIL_BUTTON_AIRFOIL
from App.Constants import CONTERSINK_ANGLE_60, CONTERSINK_ANGLE_82, CONTERSINK_ANGLE_90, CONTERSINK_ANGLE_100, \
                            CONTERSINK_ANGLE_110, CONTERSINK_ANGLE_120


from App.ShapeHandlers.RailButtonShapeHandler import RailButtonShapeHandler

from DraftTools import translate

#
# Button dimensions were obtained here: https://www.rocketryforum.com/threads/rail-button-dimensions.30354/
# These have not been verified
#

class FeatureRailButton(ExternalComponent, AnglePositionable, BoxBounded, LineInstanceable):

    def __init__(self, obj):
        super().__init__(obj, MIDDLE)
        self.Type = FEATURE_RAIL_BUTTON

        # Default set to a BT-50
        if not hasattr(obj,"RailButtonType"):
            obj.addProperty('App::PropertyEnumeration', 'RailButtonType', 'RailButton', translate('App::Property', 'Rail button type'))
            obj.RailButtonType = [RAIL_BUTTON_ROUND, 
                    RAIL_BUTTON_AIRFOIL
                    ]
            obj.RailButtonType = RAIL_BUTTON_ROUND

        if not hasattr(obj,"OuterDiameter"):
            obj.addProperty('App::PropertyLength', 'OuterDiameter', 'RailButton', translate('App::Property', 'Diameter of the outside of the rail button')).OuterDiameter = 9.462
        if not hasattr(obj, 'InnerDiameter'):
            obj.addProperty('App::PropertyLength', 'InnerDiameter', 'RailButton', translate('App::Property', 'Diameter of the inside of the rail button')).InnerDiameter = 6.2375
        if not hasattr(obj,"TopThickness"):
            obj.addProperty('App::PropertyLength', 'TopThickness', 'RailButton', translate('App::Property', 'Thickness of the outboard part of the rail button')).TopThickness = 2.096
        if not hasattr(obj,"BaseThickness"):
            obj.addProperty('App::PropertyLength', 'BaseThickness', 'RailButton', translate('App::Property', 'Thickness of the inside part of the rail button')).BaseThickness = 3.429
        if not hasattr(obj,"Thickness"):
            obj.addProperty('App::PropertyLength', 'Thickness', 'RailButton', translate('App::Property', 'Total thickness of the rail button')).Thickness = 7.62

        # Default fastener is a #6 screw
        if not hasattr(obj, 'Fastener'):
            obj.addProperty('App::PropertyBool', 'Fastener', 'RailButton', translate('App::Property', 'Create a countersunk hole for the fastener')).Fastener = True
        if not hasattr(obj,"CountersinkAngle"):
            obj.addProperty('App::PropertyEnumeration', 'CountersinkAngle', 'RailButton', translate('App::Property', 'Fastener countersink angle'))
            obj.CountersinkAngle = [CONTERSINK_ANGLE_60,
                    CONTERSINK_ANGLE_82,
                    CONTERSINK_ANGLE_90,
                    CONTERSINK_ANGLE_100,
                    CONTERSINK_ANGLE_110,
                    CONTERSINK_ANGLE_120
                    ]
            obj.CountersinkAngle = CONTERSINK_ANGLE_82
        if not hasattr(obj,"ShankDiameter"):
            obj.addProperty('App::PropertyLength', 'ShankDiameter', 'RailButton', translate('App::Property', 'Fastener shank diameter')).ShankDiameter = 3.51
        if not hasattr(obj,"HeadDiameter"):
            obj.addProperty('App::PropertyLength', 'HeadDiameter', 'RailButton', translate('App::Property', 'Fastener head diameter')).HeadDiameter = 7.80

        if not hasattr(obj, 'FilletedTop'):
            obj.addProperty('App::PropertyBool', 'FilletedTop', 'RailButton', translate('App::Property', 'Apply a fillet to the top of the rail button')).FilletedTop = False
        if not hasattr(obj,"FilletRadius"):
            obj.addProperty('App::PropertyLength', 'FilletRadius', 'RailButton', translate('App::Property', 'Fillet radius')).FilletRadius = 0.5

        if not hasattr(obj,"InstanceCount"):
            obj.addProperty('App::PropertyLength', 'InstanceCount', 'RailGuide', translate('App::Property', 'Instance count')).InstanceCount = 1
        if not hasattr(obj,"InstanceSeparation"):
            obj.addProperty('App::PropertyLength', 'InstanceSeparation', 'RailGuide', translate('App::Property', 'Instance separation')).InstanceSeparation = 0

    def setDefaults(self):
        super().setDefaults()

        self._obj.Length = 12.0

    def onDocumentRestored(self, obj):
        FeatureRailButton(obj)

        self._obj = obj

    def update(self):
        super().update()

        # Ensure any automatic variables are set
        self._setRadialOffset()
        location = self.getInstanceOffsets()

        self._obj.Placement.Base.y = location[0]._y
        self._obj.Placement.Base.z = location[0]._z

    def execute(self, obj):
        shape = RailButtonShapeHandler(obj)
        if shape is not None:
            shape.draw()

    def getLength(self):
        # Return the length of this component along the central axis
        return float(self._obj.Length)

    def isAfter(self):
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
            if body.Type in [FEATURE_FIN, FEATURE_FINCAN]:
                break
            body = body.getParent()
        
        if body is None:
            parentRadius = 0
        elif body.Type in [FEATURE_FIN, FEATURE_FINCAN]:
            body.setParentDiameter() # Set any auto values
            parentRadius = body.getForeRadius()
        else:
            x1 = self.toRelative(NUL, body)[0]._x
            x2 = self.toRelative(Coordinate(self._obj.Length, 0, 0), body)[0]._x
            x1 = Utilities.clamp(x1, 0, body.getLength())
            x2 = Utilities.clamp(x2, 0, body.getLength())
            parentRadius = max(body.getRadius(x1), body.getRadius(x2))
        
        self._obj.RadialOffset = parentRadius #+ self.getOuterRadius()

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
