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
"""Class for rocket components"""

__title__ = "FreeCAD Rocket Components"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

from abc import abstractmethod
import math

from Rocket.InternalComponent import InternalComponent
from Rocket.interfaces.BoxBounded import BoxBounded
from Rocket.interfaces.Coaxial import Coaxial

from Rocket.events.ComponentChangeEvent import ComponentChangeEvent

from Rocket.Utilities import reducePi
from Rocket.util.BoundingBox import BoundingBox
from Rocket.util.Coordinate import Coordinate

from DraftTools import translate

"""
    An inner component that consists of a hollow cylindrical component.  This can be
    an inner tube, tube coupler, centering ring, bulkhead etc.

    The properties include the inner and outer radii, length and radial position.
"""
class RingComponent(InternalComponent, BoxBounded, Coaxial):

    def __init__(self, obj):
        super().__init__(obj)

        if not hasattr(obj, 'Diameter'):
            obj.addProperty('App::PropertyLength', 'Diameter', 'RocketComponent', translate('App::Property', 'Outer diameter of the object')).Diameter = 25.0
        if not hasattr(obj, 'AutoDiameter'):
            obj.addProperty('App::PropertyBool', 'AutoDiameter', 'RocketComponent', translate('App::Property', 'Automatically set the outer diameter when possible')).AutoDiameter = False
        if not hasattr(obj, 'CenterAutoDiameter'):
            obj.addProperty('App::PropertyBool', 'CenterAutoDiameter', 'RocketComponent', translate('App::Property', 'Automatically set the center diameter when possible')).CenterAutoDiameter = False
        if not hasattr(obj, 'RadialDirection'):
            obj.addProperty('App::PropertyLength', 'RadialDirection', 'RocketComponent', translate('App::Property', 'Inner diameter of the bulkhead')).RadialDirection = 0.0
        if not hasattr(obj, 'RadialPosition'):
            obj.addProperty('App::PropertyLength', 'RadialPosition', 'RocketComponent', translate('App::Property', 'Outer diameter of the bulkhead')).RadialPosition = 0.0
        if not hasattr(obj, 'ShiftY'):
            obj.addProperty('App::PropertyLength', 'ShiftY', 'RocketComponent', translate('App::Property', 'Outer diameter of the bulkhead')).ShiftY = 0.0
        if not hasattr(obj, 'ShiftZ'):
            obj.addProperty('App::PropertyLength', 'ShiftZ', 'RocketComponent', translate('App::Property', 'Outer diameter of the bulkhead')).ShiftZ = 0.0

    def setDefaults(self):
        super().setDefaults()

    @abstractmethod
    def getOuterRadius(self):
        pass

    @abstractmethod
    def setOuterRadius(self, r):
        pass

    @abstractmethod
    def getInnerRadius(self, r):
        pass

    @abstractmethod
    def setInnerRadius(self, r):
        pass

    @abstractmethod
    def getThickness(self):
        pass

    @abstractmethod
    def setThickness(self, thickness):
        pass

    def isOuterRadiusAutomatic(self):
        return self._obj.AutoDiameter

    def isOuterDiameterAutomatic(self):
        return self._obj.AutoDiameter

    def setOuterRadiusAutomatic(self, auto):
        self.setOuterDiameterAutomatic(auto)

    def setOuterDiameterAutomatic(self, auto):
        for listener in self._configListeners:
            if isinstance(listener, RingComponent):
                listener.setOuterDiameterAutomatic(auto)

        if self._obj.AutoDiameter == auto:
            return
        self._obj.AutoDiameter = auto
        self.fireComponentChangeEvent(ComponentChangeEvent.MASS_CHANGE);

    def isInnerRadiusAutomatic(self):
        return self._obj.CenterAutoDiameter

    def isInnerDiameterAutomatic(self):
        return self._obj.CenterAutoDiameter

    def setInnerRadiusAutomatic(self, auto):
        self.setInnerDiameterAutomatic(auto)

    def setInnerDiameterAutomatic(self, auto):
        for listener in self._configListeners:
            if isinstance(listener, RingComponent):
                listener.setInnerDiameterAutomatic(auto)

        if self._obj.CenterAutoDiameter == auto:
            return
        self._obj.CenterAutoDiameter = auto
        self.fireComponentChangeEvent(ComponentChangeEvent.MASS_CHANGE);

    def setLength(self, length):
        for listener in self._configListeners:
            if isinstance(listener, RingComponent):
                listener.setLength(length)

        l = max(length, 0)
        if self._obj.Length == l:
            return

        self._obj.Length = l
        # clearPreset();
        self.fireComponentChangeEvent(ComponentChangeEvent.MASS_CHANGE)

    """
        Return the radial direction of displacement of the component.  Direction 0
        is equivalent to the Y-direction.
    """
    def getRadialDirection(self):
        return float(self._obj.RadialDirection)

    """
        Set the radial direction of displacement of the component.  Direction 0
        is equivalent to the Y-direction.
    """
    def setRadialDirection(self, dir):
        for listener in self._configListeners:
            if isinstance(listener, RingComponent):
                listener.setRadialDirection(dir)

        dir = reducePi(dir)
        if self._obj.RadialDirection == dir:
            return
        self._obj.RadialDirection = dir
        self._obj.ShiftY = self._obj.RadialPosition * math.cos(self._obj.RadialDirection)
        self._obj.ShiftZ = self._obj.RadialPosition * math.sin(self._obj.RadialDirection)
        self.fireComponentChangeEvent(ComponentChangeEvent.MASS_CHANGE)

    def getInstanceBoundingBox(self):
        instanceBounds = BoundingBox()

        instanceBounds.update(Coordinate(self.getLength(), 0,0))

        r = self.getOuterRadius()
        instanceBounds.update(Coordinate(0,r,r))
        instanceBounds.update(Coordinate(0,-r,-r))

        return instanceBounds

    """
        Return the radial position of the component.  The position is the distance
        of the center of the component from the center of the parent component.
    """
    def getRadialPosition(self):
        return self._obj.RadialPosition

    """
        Set the radial position of the component.  The position is the distance
        of the center of the component from the center of the parent component.
    """
    def setRadialPosition(self, pos):
        pos = max(pos, 0);

        for listener in self._configListeners:
            if isinstance(listener, RingComponent):
                listener.setRadialPosition(pos)

        if self._obj.RadialPosition == pos:
            return
        self._obj.RadialPosition = pos
        self._obj.ShiftY = self._obj.RadialPosition * math.cos(self._obj.RadialDirection)
        self._obj.ShiftZ = self._obj.RadialPosition * math.sin(self._obj.RadialDirection)
        self.fireComponentChangeEvent(ComponentChangeEvent.MASS_CHANGE)

    def getRadialShiftY(self):
        return self._obj.ShiftY

    def getRadialShiftZ(self):
        return self._obj.ShiftZ

    def setRadialShift(self, y, z):
        for listener in self._configListeners:
            if isinstance(listener, RingComponent):
                listener.setRadialShift(y, z)

        self._obj.RadialPosition = math.hypot(y, z);
        self._obj.RadialDirection = math.atan2(z, y);

        # Re-calculate to ensure consistency
        self._obj.ShiftY = self._obj.RadialPosition * math.cos(self._obj.RadialDirection)
        self._obj.ShiftZ = self._obj.RadialPosition * math.sin(self._obj.RadialDirection)
        # assert (MathUtil.equals(y, shiftY));
        # assert (MathUtil.equals(z, shiftZ));

        self.fireComponentChangeEvent(ComponentChangeEvent.MASS_CHANGE);
