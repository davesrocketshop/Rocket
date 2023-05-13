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
"""Class for rocket pods"""

__title__ = "FreeCAD Rocket Pod"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

import math

from DraftTools import translate

from Rocket.events.ComponentChangeEvent import ComponentChangeEvent
from Rocket.interfaces.RingInstanceable import RingInstanceable
import Rocket.position.AngleMethod as AngleMethod
import Rocket.position.RadiusMethod as RadiusMethod
from Rocket.ComponentAssembly import ComponentAssemblyLocation
from Rocket.PodInfo import PodInfo
from Rocket.util.Coordinate import Coordinate
from Rocket.util.MathUtil import EPSILON

from Rocket.Constants import FEATURE_NOSE_CONE, FEATURE_BODY_TUBE, FEATURE_TRANSITION, FEATURE_FINCAN, FEATURE_POD

class FeaturePod(ComponentAssemblyLocation, RingInstanceable):

    def __init__(self, obj):
        super().__init__(obj)

        self.Type = FEATURE_POD

        if not hasattr(obj,"PodCount"):
            obj.addProperty('App::PropertyInteger', 'PodCount', 'RocketComponent', translate('App::Property', 'Number of pods in a radial pattern')).PodCount = 1
        if not hasattr(obj,"PodSpacing"):
            obj.addProperty('App::PropertyAngle', 'PodSpacing', 'RocketComponent', translate('App::Property', 'Angle between consecutive pods')).PodSpacing = 360
        
        if not hasattr(obj, 'AngleMethod'):
            obj.addProperty('App::PropertyPythonObject', 'AngleMethod', 'RocketComponent', translate('App::Property', 'Method for calculating angle offsets')).AngleMethod = AngleMethod.RELATIVE
        
        if not hasattr(obj, 'RadiusMethod'):
            obj.addProperty('App::PropertyPythonObject', 'RadiusMethod', 'RocketComponent', translate('App::Property', 'Method for calculating radius offsets')).RadiusMethod = RadiusMethod.SURFACE
        if not hasattr(obj, 'RadiusOffset'):
            obj.addProperty('App::PropertyAngle', 'RadiusOffset', 'RocketComponent', translate('App::Property', 'Radius offset')).RadiusOffset = 0


        if not hasattr(obj,"Group"):
            obj.addExtension("App::GroupExtensionPython")

    def setDefaults(self):
        super().setDefaults()

    def onDocumentRestored(self, obj):
        FeaturePod(obj)

        self._obj = obj

    def execute(self,obj):
        if not hasattr(obj,'Shape'):
            return

    def update(self):
        super().update()

        offsets = self.getInstanceOffsets()
        if len(offsets) > 0:
            # self._obj.Placement.Base.y = offsets[0].Y
            # self._obj.Placement.Base.z = offsets[0].Z

            podInfo = PodInfo()
            podInfo.podCount = self._obj.PodCount
            podInfo.podSpacing = self._obj.PodSpacing
            podInfo.radiusOffset = self._obj.RadiusOffset
            podInfo.offsets = offsets

            self.updatePodChild(self._obj, podInfo)

            # for curChild in self.getChildren():
            #     curChild.Placement.Base.y = offsets[0].Y
            #     curChild.Placement.Base.z = offsets[0].Z

    def updatePodChild(self, parent, podInfo):
        for curChild in parent.Proxy.getChildren():
            curChild.Proxy.setPodInfo(podInfo)

            self.updatePodChild(curChild, podInfo)

    def eligibleChild(self, childType):
        return childType in [FEATURE_NOSE_CONE, FEATURE_BODY_TUBE, FEATURE_TRANSITION, FEATURE_FINCAN]

    def onChildEdited(self):
        self._obj.Proxy.setEdited()

    def getInstanceAngleIncrement(self):
        return self._obj.PodSpacing

    def getInstanceAngles(self):
        #		, angleMethod, angleOffset_rad
        baseAngle = self.getAngleOffset()
        incrAngle =self.getInstanceAngleIncrement()
        
        result = []
        for i in range(self.getInstanceCount()):
            angle = baseAngle + incrAngle * i
            result.append(math.radians(angle))
        
        return result

    def getInstanceLocations(self):
        pass

    def getInstanceOffsets(self):
        radius = self._obj.RadiusMethod.getRadius(self.getParent(), self, self._obj.RadiusOffset)
        
        toReturn = []
        angles = self.getInstanceAngles()
        for instanceNumber in range(self._obj.PodCount):
            curY = radius * math.cos(angles[instanceNumber])
            curZ = radius * math.sin(angles[instanceNumber])
            toReturn.append(Coordinate(0, curY, curZ))
        
        return toReturn

    def isAfter(self):
        return False

    """
        Stages may be positioned relative to other stages. In that case, this will set the stage number 
        against which this stage is positioned.
    """
    def getRelativeToStage(self):
        if self.getParent() is None:
            return -1
        elif isinstance(self.getParent(), FeaturePod):
            return self.getParent().getParent().getChildPosition(self.getParent())
        
        return -1

    def setAxialMethod(self, newMethod):
        super().setAxialMethod(newMethod)
        self.fireComponentChangeEvent(ComponentChangeEvent.NONFUNCTIONAL_CHANGE)

    def getAxialOffset(self):
        return self._getAxialOffset(self._obj.AxialMethod)

    def _getAxialOffset(self, method):
        returnValue = 0.0

        if self.isAfter():
            # remember the implicit (this instanceof Stage)
            raise Exception("found a pod positioned via: AFTER, but is not on the centerline?!: " + self.getName() + "  is " + self.getAxialMethod().name())
        else:
            returnValue = super().getAxialOffset(method)


        if EPSILON > math.abs(returnValue):
            returnValue = 0.0

        return returnValue

    def getAngleOffset(self):
        return self._obj.AngleOffset

    def getPatternName(self):
        return (self.getInstanceCount() + "-ring")


    def getRadiusOffset(self):
        return self._obj.RadiusOffset

    def getInstanceCount(self):
        return self._obj.PodCount

    def setInstanceCount(self, newCount):
        for listener in self._configListeners:
            if isinstance(listener, FeaturePod):
                listener.setInstanceCount(newCount)

        if newCount < 1:
            # there must be at least one instance....   
            return

        
        self._obj.PodCount = newCount
        self._obj.PodSpacing = 360.0 / self._obj.PodCount
        self.fireComponentChangeEvent(ComponentChangeEvent.BOTH_CHANGE)

    def setAngleOffset(self, angle):
        for listener in self._configListeners:
            if isinstance(listener, FeaturePod):
                listener.setAngleOffset(angle)

        self._obj.AngleOffset = angle
        self.fireComponentChangeEvent(ComponentChangeEvent.BOTH_CHANGE)

    def getAngleMethod(self):
        return self._obj.AngleMethod

    def setAngleMethod(self, newMethod):
        pass

    def setRadiusOffset(self, radius):
        for listener in self._configListeners:
            if isinstance(listener, FeaturePod):
                listener.setRadiusOffset(radius)

        if radius == self._obj.RadiusOffset:
            return

        if self._obj.RadiusMethod.clampToZero():
            self._obj.RadiusOffset = 0.0
        else:
            self._obj.RadiusOffset = radius
        self.fireComponentChangeEvent(ComponentChangeEvent.BOTH_CHANGE)

    def getRadiusMethod(self):
        return self._obj.RadiusMethod

    def setRadiusMethod(self, newMethod):
        for listener in self._configListeners:
            if isinstance(listener, FeaturePod):
                listener.setRadiusMethod(newMethod)

        if newMethod == self._obj.RadiusMethod:
            return

        radius = self._obj.RadiusMethod.getRadius(self.getParent(), self, self._obj.RadiusOffset)	# Radius from the parent's center
        self.setRadius(newMethod, radius)

    def setRadius(self, requestMethod, requestRadius):
        for listener in self._configListeners:
            if isinstance(listener, FeaturePod):
                listener.setRadius(requestMethod, requestRadius)

        newRadius = requestRadius
        if self._obj.RadiusMethod.clampToZero():
            newRadius = 0.0

        self._obj.RadiusMethod = requestMethod
        self._obj.RadiusOffset =  self._obj.RadiusMethod.getAsOffset(self.getParent(), self, newRadius)
        self.fireComponentChangeEvent(ComponentChangeEvent.BOTH_CHANGE)

    def getLength(self):
        # Return the length of this component along the central axis
        length = 0.0
        if hasattr(self._obj, "Group"):
            for child in self._obj.Group:
                length += float(child.Proxy.getLength())

        return length
