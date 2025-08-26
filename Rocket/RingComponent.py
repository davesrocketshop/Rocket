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
from typing import Any

from Rocket.InternalComponent import InternalComponent
from Rocket.interfaces.BoxBounded import BoxBounded
from Rocket.interfaces.Coaxial import Coaxial

from Rocket.Utilities import reducePi
from Rocket.util.BoundingBox import BoundingBox
from Rocket.util.Coordinate import Coordinate

from Rocket.Utilities import translate

"""
    An inner component that consists of a hollow cylindrical component.  This can be
    an inner tube, tube coupler, centering ring, bulkhead etc.

    The properties include the inner and outer radii, length and radial position.
"""
class RingComponent(InternalComponent, BoxBounded, Coaxial):

    def __init__(self, obj : Any) -> None:
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

    def setDefaults(self) -> None:
        super().setDefaults()

    def _isDiameterScaled(self) -> bool:
        if self._obj.AutoDiameter:
            return False
        return self.isScaled()

    def getDiameterScale(self) -> float:
        if self._isDiameterScaled():
            return self.getScale()
        return 1.0

    def _isCenterDiameterScaled(self) -> bool:
        if self._obj.Proxy.hasParent():
            return self._obj.Proxy.getParent().isScaled()
        return not self._obj.CenterAutoDiameter

    def getCenterDiameterScale(self) -> float:
        if self._isCenterDiameterScaled():
            return self.getScale()
        return 1.0

    @abstractmethod
    def getOuterRadius(self, pos : float) -> float:
        pass

    @abstractmethod
    def setOuterRadius(self, radius : float) -> None:
        pass

    @abstractmethod
    def getInnerRadius(self, pos : float) -> float:
        pass

    @abstractmethod
    def setInnerRadius(self, radius : float) -> None:
        pass

    @abstractmethod
    def getThickness(self) -> float:
        pass

    @abstractmethod
    def setThickness(self, thickness : float) -> None:
        pass

    def isOuterRadiusAutomatic(self) -> bool:
        return self._obj.AutoDiameter

    def isOuterDiameterAutomatic(self) -> bool:
        return self._obj.AutoDiameter

    def setOuterRadiusAutomatic(self, auto : bool) -> None:
        self.setOuterDiameterAutomatic(auto)

    def setOuterDiameterAutomatic(self, auto : bool) -> None:
        if self._obj.AutoDiameter == auto:
            return
        self._obj.AutoDiameter = auto
        self.notifyComponentChanged()

    def isInnerRadiusAutomatic(self) -> bool:
        return self._obj.CenterAutoDiameter

    def isInnerDiameterAutomatic(self) -> bool:
        return self._obj.CenterAutoDiameter

    def setInnerRadiusAutomatic(self, auto : bool) -> None:
        self.setInnerDiameterAutomatic(auto)

    def setInnerDiameterAutomatic(self, auto : bool) -> None:
        if self._obj.CenterAutoDiameter == auto:
            return
        self._obj.CenterAutoDiameter = auto
        self.notifyComponentChanged()

    def setLength(self, length : float) -> None:
        l = max(length, 0)
        if self._obj.Length == l:
            return

        self._obj.Length = l
        # clearPreset();
        self.notifyComponentChanged()

    """
        Return the radial direction of displacement of the component.  Direction 0
        is equivalent to the Y-direction.
    """
    def getRadialDirection(self) -> float:
        return float(self._obj.RadialDirection)

    """
        Set the radial direction of displacement of the component.  Direction 0
        is equivalent to the Y-direction.
    """
    def setRadialDirection(self, dir : float) -> None:
        dir = reducePi(dir)
        if self._obj.RadialDirection == dir:
            return
        self._obj.RadialDirection = dir
        self._obj.ShiftY = self._obj.RadialPosition * math.cos(self._obj.RadialDirection)
        self._obj.ShiftZ = self._obj.RadialPosition * math.sin(self._obj.RadialDirection)
        self.notifyComponentChanged()

    def getInstanceBoundingBox(self) -> BoundingBox:
        instanceBounds = BoundingBox()

        instanceBounds.update(Coordinate(self.getLength(), 0,0))

        r = self.getOuterRadius(0)
        instanceBounds.update(Coordinate(0,r,r))
        instanceBounds.update(Coordinate(0,-r,-r))

        return instanceBounds

    """
        Return the radial position of the component.  The position is the distance
        of the center of the component from the center of the parent component.
    """
    def getRadialPosition(self) -> float:
        return float(self._obj.RadialPosition)

    """
        Set the radial position of the component.  The position is the distance
        of the center of the component from the center of the parent component.
    """
    def setRadialPosition(self, pos : float) -> None:
        pos = max(pos, 0);

        if self._obj.RadialPosition == pos:
            return
        self._obj.RadialPosition = pos
        self._obj.ShiftY = self._obj.RadialPosition * math.cos(self._obj.RadialDirection)
        self._obj.ShiftZ = self._obj.RadialPosition * math.sin(self._obj.RadialDirection)
        self.notifyComponentChanged()

    def getRadialShiftY(self) -> float:
        return float(self._obj.ShiftY)

    def getRadialShiftZ(self) -> float:
        return float(self._obj.ShiftZ)

    def setRadialShift(self, y : float, z : float) -> None:
        self._obj.RadialPosition = math.hypot(y, z);
        self._obj.RadialDirection = math.atan2(z, y);

        # Re-calculate to ensure consistency
        self._obj.ShiftY = self._obj.RadialPosition * math.cos(self._obj.RadialDirection)
        self._obj.ShiftZ = self._obj.RadialPosition * math.sin(self._obj.RadialDirection)
        # assert (MathUtil.equals(y, shiftY));
        # assert (MathUtil.equals(z, shiftZ));

        self.notifyComponentChanged()
