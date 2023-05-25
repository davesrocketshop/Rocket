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
"""Base class for rocket component assemblies"""

__title__ = "FreeCAD Rocket Components"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

from tokenize import Double

from Rocket.position import AxialMethod
from Rocket.position.AxialPositionable import AxialPositionable
from Rocket.util.BoundingBox import BoundingBox
from Rocket.RocketComponentShapeless import RocketComponentShapeless
from Rocket.events.ComponentChangeEvent import ComponentChangeEvent

from Rocket.Constants import FEATURE_ROCKET, FEATURE_STAGE, FEATURE_PARALLEL_STAGE, FEATURE_POD, FEATURE_BODY_TUBE, FEATURE_NOSE_CONE, FEATURE_TRANSITION
from Rocket.Constants import LOCATION_PARENT_TOP, LOCATION_PARENT_MIDDLE, LOCATION_PARENT_BOTTOM, LOCATION_BASE
from Rocket.position.AxialMethod import AXIAL_METHOD_MAP

from DraftTools import translate

class ComponentAssembly(RocketComponentShapeless, AxialPositionable):

    def __init__(self, obj):
        super().__init__(obj)

        super().setAxialMethod(AxialMethod.AFTER)
        self._length = 0

    def setDefaults(self):
        super().setDefaults()

    def getAxialOffset(self) -> Double:
        return self.getAxialOffsetFromMethod(self._obj.AxialMethod)
	
    def setAxialOffset(self, newAxialOffset) -> None:
        self._updateBounds()
        super()._setAxialOffset(self._obj.AxialMethod, newAxialOffset)
        self.fireComponentChangeEvent(ComponentChangeEvent.BOTH_CHANGE)
	
    def getAxialMethod(self) -> AxialMethod:
        return self._obj.AxialMethod
	
    def setAxialMethod(self, newMethod) -> None:
        # self._obj.AxialMethod = newMethod
        for listener in self._configListeners:
            if isinstance(listener, ComponentAssembly):
                listener.setAxialMethod(newMethod)

        if self.getParent is None:
            raise Exception(translate("Exception", " a Stage requires a parent before any positioning! "))

        if self.getType() == FEATURE_PARALLEL_STAGE or self.getType() == FEATURE_POD:
            if newMethod == AxialMethod.AFTER:
                # log.warn("Stages (or Pods) cannot be relative to other stages via AFTER! Ignoring.");
                super().setAxialMethod(AxialMethod.TOP)
            else:
                super().setAxialMethod(newMethod)
        elif self.getType() == FEATURE_STAGE:
            # Centerline stages must be set via AFTER-- regardless of what was requested:
            super().setAxialMethod(AxialMethod.AFTER)
        elif self.getType() == FEATURE_ROCKET:
            # Main rocket must be set via ABSOLUTE-- regardless of what was requested:
            super().setAxialMethod(AxialMethod.ABSOLUTE)
        else:
            raise Exception(translate("Exception", "Unrecognized subclass of Component Assembly.  Please update this method."))

        self.fireComponentChangeEvent(ComponentChangeEvent.NONFUNCTIONAL_CHANGE);

    def getInstanceBoundingBox (self):
        return BoundingBox()

    def getBoundingRadius(self):
        outerRadius = 0
        for comp in self.getChildren():
            thisRadius = 0
            if comp.Proxy.Type in [FEATURE_BODY_TUBE]:
                thisRadius = comp.Proxy.getOuterRadius()
            elif comp.Proxy.Type in [FEATURE_TRANSITION, FEATURE_NOSE_CONE]:
                thisRadius = max(comp.Proxy.getForeRadius(), comp.Proxy.getAftRadius())
            
            outerRadius = max(outerRadius, thisRadius)

        return outerRadius

    # Components have no aerodynamic effect, so return false.
    def isAerodynamic(self):
        return False

    # Component have no effect on mass, so return false (even though the override values
    # may have an effect).
    def isMassive(self):
        return False

    def update(self):
        self.updateBounds()
        if self.isAfter():
            self.setAfter()
        else:
            super().update()

        self.updateChildSequence()

    def updateBounds(self):
        # currently only updates the length 
        self._length = 0
        for  curChild in self.getChildren():
            if curChild.Proxy.isAfter():
                self._length += float(curChild.Proxy.getLength())

    def updateChildSequence(self):
        for  curChild in self.getChildren():
            if curChild.Proxy.isAfter():
                curChild.Proxy.setAfter()

class ComponentAssemblyLocation(ComponentAssembly):

    def __init__(self, obj):
        super().__init__(obj)
        
        # This also appears in RocketComponent
        if not hasattr(obj, 'LocationReference'):
            obj.addProperty('App::PropertyEnumeration', 'LocationReference', 'RocketComponent', translate('App::Property', 'Reference location for the location'))
            obj.LocationReference = [
                        LOCATION_PARENT_TOP,
                        LOCATION_PARENT_MIDDLE,
                        LOCATION_PARENT_BOTTOM,
                        LOCATION_BASE
                    ]
            obj.LocationReference = LOCATION_PARENT_BOTTOM
        else:
            obj.LocationReference = [
                        LOCATION_PARENT_TOP,
                        LOCATION_PARENT_MIDDLE,
                        LOCATION_PARENT_BOTTOM,
                        LOCATION_BASE
                    ]

    def setDefaults(self):
        super().setDefaults()

        self._obj.LocationReference = LOCATION_PARENT_BOTTOM
        self._obj.AxialMethod = AxialMethod.BOTTOM

    def copy(self, component):
        self._obj.LocationReference = component._obj.LocationReference

        super().copy(component)

    def setLocationReference(self, reference):
        self.setAxialMethod(AXIAL_METHOD_MAP[reference])
