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
"""Class for drawing body tubes"""

__title__ = "FreeCAD Body Tubes"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

import math
    
from Rocket.Constants import FEATURE_LAUNCH_LUG, FEATURE_FIN, FEATURE_FINCAN

from Rocket.Tube import Tube
from Rocket.position import AxialMethod
from Rocket.position.AngleMethod import AngleMethod
from Rocket.position.AnglePositionable import AnglePositionable
from Rocket.interfaces.BoxBounded import BoxBounded
from Rocket.interfaces.LineInstanceable import LineInstanceable
from Rocket.events.ComponentChangeEvent import ComponentChangeEvent
from Rocket.util.BoundingBox import BoundingBox
from Rocket.util.Coordinate import Coordinate, NUL
from Rocket import Utilities
from Rocket.SymmetricComponent import SymmetricComponent
from Rocket.ShapeHandlers.LaunchLugShapeHandler import LaunchLugShapeHandler

from DraftTools import translate

class FeatureLaunchLug(Tube, AnglePositionable, BoxBounded, LineInstanceable):

    def __init__(self, obj):
        super().__init__(obj, AxialMethod.MIDDLE)

        self.Type = FEATURE_LAUNCH_LUG

        # Default set to 1/8" launch lug
        if not hasattr(obj,"Diameter"):
            obj.addProperty('App::PropertyLength', 'Diameter', 'RocketComponent', translate('App::Property', 'Diameter of the outside of the body tube')).Diameter = 4.06
        if not hasattr(obj,"Thickness"):
            obj.addProperty('App::PropertyLength', 'Thickness', 'RocketComponent', translate('App::Property', 'Diameter of the inside of the body tube')).Thickness = 0.25

        if not hasattr(obj,"InstanceCount"):
            obj.addProperty('App::PropertyLength', 'InstanceCount', 'RocketComponent', translate('App::Property', 'Instance count')).InstanceCount = 1
        if not hasattr(obj,"InstanceSeparation"):
            obj.addProperty('App::PropertyLength', 'InstanceSeparation', 'RocketComponent', translate('App::Property', 'Instance separation')).InstanceSeparation = 0

    def setDefaults(self):
        super().setDefaults()

        self._obj.Length = 25.4

    def onDocumentRestored(self, obj):
        FeatureLaunchLug(obj)

        self._obj = obj

    def update(self):
        super().update()

        # Ensure any automatic variables are set
        self._setRadialOffset()
        location = self.getInstanceOffsets()

        self._obj.Placement.Base.y = location[0].Y
        self._obj.Placement.Base.z = location[0].Z

    def execute(self, obj):
        shape = LaunchLugShapeHandler(obj)
        if shape is not None:
            shape.draw()

    def eligibleChild(self, childType):
        return False

    def getLength(self):
        # Return the length of this component along the central axis
        length = self._obj.Length

        return float(length)

    def getOuterRadius(self):
        return self.getOuterDiameter() / 2.0

    def getOuterDiameter(self):
        return float(self._obj.Diameter)

    def setOuterRadius(self, radius):
        self.setOuterDiameter(radius * 2.0)

    def setOuterDiameter(self, diameter):
        for listener in self._configListeners:
            if isinstance(listener, FeatureLaunchLug):
                listener.setOuterDiameter(diameter)

        if self._obj.Diameter == diameter:
            return

        self._obj.Diameter = diameter
        self._obj.Thickness = min(self._obj.Thickness, self._obj.Diameter / 2.0)
        self.clearPreset()
        self.fireComponentChangeEvent(ComponentChangeEvent.BOTH_CHANGE)

    def getInnerRadius(self):
        return self.getInnerDiameter() / 2.0

    def getInnerDiameter(self, pos=0):
        return self._obj.Diameter - (2.0 * self._obj.Thickness)

    def setInnerRadius(self, radius):
        self.setInnerDiameter(radius * 2.0)

    def setInnerDiameter(self, diameter):
        for listener in self._configListeners:
            if isinstance(listener, FeatureLaunchLug):
                listener.setInnerDiameter(diameter)

        self.setThickness((float(self._obj.Diameter) - float(diameter)) / 2.0)

    def getThickness(self):
        return self._obj.Thickness

    def setThickness(self, thickness):
        for listener in self._configListeners:
            if isinstance(listener, FeatureLaunchLug):
                listener.setThickness(thickness)

        if self._obj.Thickness == thickness:
            return

        self._obj.Thickness = Utilities.clamp(thickness, 0, self._obj.Diameter / 2.0)
        self.clearPreset()
        self.fireComponentChangeEvent(ComponentChangeEvent.BOTH_CHANGE)

    def getAngleOffset(self):
        return self._obj.AngleOffset

    def setAngleOffset(self, degrees):
        for listener in self._configListeners:
            if isinstance(listener, FeatureLaunchLug):
                listener.setAngleOffset(degrees)

        if self._obj.AngleOffset == degrees:
            return

        self._obj.AngleOffset = degrees
        self.fireComponentChangeEvent(ComponentChangeEvent.BOTH_CHANGE)

    def setLength(self, length):
        for listener in self._configListeners:
            if isinstance(listener, FeatureLaunchLug):
                listener.setLength(length)

        if self._obj.Length == length:
            return

        self._obj.Length = length
        self.fireComponentChangeEvent(ComponentChangeEvent.BOTH_CHANGE)

    def isAfter(self):
        return False

    def getInstanceOffsets(self):
        toReturn = []
        
        yOffset = math.sin(math.radians(-self._obj.AngleOffset)) * (self._obj.RadialOffset)
        zOffset = math.cos(math.radians(-self._obj.AngleOffset)) * (self._obj.RadialOffset)
        
        for index in range(self.getInstanceCount()):
            toReturn.append(Coordinate(index*self._obj.InstanceSeparation, yOffset, zOffset))
        
        return toReturn

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
            x1 = self.toRelative(NUL, body)[0].X
            x2 = self.toRelative(Coordinate(self._obj.Length, 0, 0), body)[0].X
            x1 = Utilities.clamp(x1, 0, body.getLength())
            x2 = Utilities.clamp(x2, 0, body.getLength())
            parentRadius = max(body.getRadius(x1), body.getRadius(x2))
        
        self._obj.RadialOffset = parentRadius + self.getOuterRadius()

    def getInstanceSeparation(self):
        return self._obj.InstanceSeparation

    def setInstanceSeparation(self, separation):
        for listener in self._configListeners:
            if isinstance(listener, FeatureLaunchLug):
                listener.setInstanceSeparation(separation)

        self._obj.InstanceSeparation = separation

    def setInstanceCount(self, newCount):
        for listener in self._configListeners:
            if isinstance(listener, FeatureLaunchLug):
                listener.setInstanceCount(newCount)

        if newCount > 0:
            self._obj.InstanceCount = newCount

    def getInstanceCount(self):
        return int(self._obj.InstanceCount)

    def getInstanceBoundingBox(self):
        instanceBounds = BoundingBox()
        
        instanceBounds.update(Coordinate(self.getLength(), 0,0))
        
        r = self.getOuterRadius()
        instanceBounds.update(Coordinate(0,r,r))
        instanceBounds.update(Coordinate(0,-r,-r))
        
        return instanceBounds

    def getPatternName(self):
        return "{0}-Line".format(self.getInstanceCount())

    def getAngleMethod(self):
        return AngleMethod.RELATIVE


    def setAngleMethod(self, newMethod):
        # no-op
        pass
    
    def explodeRadially(self):
        return True

    def explodedSize(self):
        length = float(self._obj.Length)
        height = float(self._obj.Diameter)

        for index, child in enumerate(self.getChildren()):
            childLength, childHeight = child.Proxy.explodedSize()
            if index > 0:
                length += childLength + float(self._obj.AnimationDistance)
            else:
                length = childLength
            height = max(height, childHeight) # TODO: Not true for non-radial components like fins, true for things like CRs


        return length, height
