#***************************************************************************
# *   Copyright (c) 2022-2025 David Carter <dcarter@davidcarter.ca>         *
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

from Rocket.util.MathUtil import MathUtil
from Rocket.interfaces.BoxBounded import BoxBounded
from Rocket.interfaces.RadialParent import RadialParent
from Rocket.events.ComponentChangeEvent import ComponentChangeEvent

from Rocket.RocketComponent import RocketComponent
from Rocket.ComponentAssembly import ComponentAssembly
from Rocket.util.BoundingBox import BoundingBox
from Rocket.util.Coordinate import Coordinate

# Class for an axially symmetric rocket component generated by rotating
# a function y=f(x) >= 0 around the x-axis (eg. tube, cone, etc.)

class SymmetricComponent(RocketComponent, BoxBounded, RadialParent):

    DEFAULT_RADIUS = (24.79 / 2.0)
    DEFAULT_THICKNESS = 0.33

    def __init__(self, obj):
        super().__init__(obj)

    def setDefaults(self):
        super().setDefaults()

    def getInstanceBoundingBox(self):
        instanceBounds = BoundingBox()

        instanceBounds.update(Coordinate(self.getLength(), 0,0))

        r = max(self.getForeRadius(), self.getAftRadius())
        instanceBounds.update(Coordinate(0,r,r))
        instanceBounds.update(Coordinate(0,-r,-r))

        return instanceBounds

    """
        Return the component radius at position x.
    """
    @abstractmethod
    def getRadius(self, x):
        pass

    @abstractmethod
    def getForeRadius(self):
        pass

    @abstractmethod
    def isForeRadiusAutomatic(self):
        pass

    @abstractmethod
    def getAftRadius(self):
        pass

    @abstractmethod
    def isAftRadiusAutomatic(self):
        pass

    def getOuterRadius(self, x):
        self.getRadius(x)

    def getInnerRadius(self, x):
        # self.getRadius(x)
        pass

    """
        Returns the largest radius of the component (either the aft radius, or the fore radius).
    """
    def getMaxRadius(self):
        return max(self.getForeRadius(), self.getAftRadius())


    """
        Return the component wall thickness.
    """
    def getThickness(self):
        if self.isFilled():
            return max(self.getForeRadius(), self.getAftRadius())
        return self._obj.Thickness

    """
        Set the component wall thickness.  If <code>doClamping</code> is true, values greater than
        the maximum radius will be clamped the thickness to the maximum radius.
        @param doClamping If true, the thickness will be clamped to the maximum radius.
    """
    def setThickness(self, thickness, doClamping = True):
        for listener in self._configListeners:
            if isinstance(listener, SymmetricComponent):
                listener.setThickness(thickness)

        if (self._obj.Thickness == thickness) and not self.isFilled():
            return
        if doClamping:
            self._obj.Thickness = MathUtil.clamp(thickness, 0, self.getMaxRadius())
        else:
            self._obj.Thickness = thickness
        self.setFilled(False)

        self.fireComponentChangeEvent(ComponentChangeEvent.MASS_CHANGE)
        self.clearPreset()

    def isAfter(self):
        return True

    """
        Returns whether the component is set as filled.  If it is set filled, then the
        wall thickness will have no effect.
    """
    def isFilled(self):
        return self._obj.Filled

    """
        Sets whether the component is set as filled.  If the component is filled, then
        the wall thickness will have no effect.
    """
    def setFilled(self, filled):
        for listener in self._configListeners:
            if isinstance(listener, SymmetricComponent):
                listener.setFilled(filled)

        if self.isFilled():
            return

        self._obj.Filled = filled
        self.fireComponentChangeEvent(ComponentChangeEvent.MASS_CHANGE)
        self.clearPreset()

    """
        Returns the automatic radius for this component towards the
        front of the rocket.  The automatics will not search towards the
        rear of the rocket for a suitable radius.  A positive return value
        indicates a preferred radius, a negative value indicates that a
        match was not found.
    """
    @abstractmethod
    def getFrontAutoRadius(self):
        pass

    @abstractmethod
    def getFrontAutoDiameter(self):
        pass

    @abstractmethod
    def getFrontAutoInnerDiameter(self):
        pass

    """
        Returns the automatic radius for this component towards the
        end of the rocket.  The automatics will not search towards the
        front of the rocket for a suitable radius.  A positive return value
        indicates a preferred radius, a negative value indicates that a
        match was not found.
    """
    @abstractmethod
    def getRearAutoRadius(self):
        pass

    @abstractmethod
    def getRearAutoDiameter(self):
        pass

    @abstractmethod
    def getRearAutoInnerDiameter(self):
        pass

    """
        Return the previous symmetric component, or null if none exists.
    """
    def getPreviousSymmetricComponent(self):
        if self.getParent() is None or self.getParent().getParent() is None:
            return None

        # might be: (a) Rocket -- for Centerline/Axial stages
        #           (b) BodyTube -- for Parallel Stages & PodSets
        grandParent = self.getParent().getParent()
        parent = self.getParent()

        searchParentIndex = grandParent.getChildPosition(parent)       # position of stage w/in parent
        searchSiblingIndex = parent.getChildPosition(self)-1           # guess at index of previous stage

        while 0 <= searchParentIndex:
            searchParent = grandParent.getChild(searchParentIndex).Proxy

            if isinstance(searchParent, ComponentAssembly):
                while 0 <= searchSiblingIndex:
                    searchSibling = searchParent.getChild(searchSiblingIndex).Proxy
                    if isinstance(searchSibling, SymmetricComponent):
                        return searchSibling
                    searchSiblingIndex -= 1

            searchParentIndex -= 1
            if 0 <= searchParentIndex:
                searchSiblingIndex = grandParent.getChild(searchParentIndex).Proxy.getChildCount() - 1

        return None

    """
         Return the next symmetric component, or null if none exists.
    """
    def getNextSymmetricComponent(self):
        if self.getParent() is None or self.getParent().getParent() is None:
            return None

        # might be: (a) Rocket -- for centerline stages
        #           (b) BodyTube -- for Parallel Stages
        grandParent = self.getParent().getParent()
        parent = self.getParent()

        # note:  this is not guaranteed to _contain_ a stage... but that we're _searching_ for one.
        searchParentIndex = grandParent.getChildPosition(parent)
        searchSiblingIndex = parent.getChildPosition(self) + 1

        while searchParentIndex < grandParent.getChildCount():
            searchParent = grandParent.getChild(searchParentIndex).Proxy

            if isinstance(searchParent, ComponentAssembly):
                while searchSiblingIndex < searchParent.getChildCount():
                    searchSibling = searchParent.getChild(searchSiblingIndex).Proxy

                    if isinstance(searchSibling, SymmetricComponent):
                        return searchSibling
                    searchSiblingIndex += 1

            searchParentIndex += 1
            searchSiblingIndex = 0

        return None

    """
        Checks whether the component uses the previous symmetric component for its auto diameter.
    """
    @abstractmethod
    def usesPreviousCompAutomatic(self):
        pass

    """
        Checks whether the component uses the next symmetric component for its auto diameter.
    """
    @abstractmethod
    def usesNextCompAutomatic(self):
        pass
