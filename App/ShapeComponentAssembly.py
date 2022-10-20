# ***************************************************************************
# *   Copyright (c) 2021 David Carter <dcarter@davidcarter.ca>              *
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

# import FreeCAD
# import math

from tokenize import Double

from App.position import AxialMethod
from App.position.AxialPositionable import AxialPositionable
from App.ShapeComponent import ShapeComponent
from App.ComponentChangeEvent import ComponentChangeEvent

from App.Constants import FEATURE_STAGE, FEATURE_PARALLEL_STAGE, FEATURE_POD

# from DraftTools import translate

class ShapeComponentAssembly(ShapeComponent, AxialPositionable):

    def __init__(self, obj):
        super().__init__(obj)

        super().setAxialMethod(AxialMethod.AFTER)
        self._length = 0

    def allowsChildren(self):
        return True

    def getAxialOffset(self) -> Double:
        return self.getAxialOffsetFromMethod(self._obj.AxialMethod)
	
    def setAxialOffset(self, newAxialOffset) -> None:
        self._updateBounds()
        self.setAxialOffsetFromMethod(self._obj.AxialMethod, newAxialOffset)
	
    def getAxialMethod(self) -> AxialMethod:
        return self._obj.AxialMethod
	
    def setAxialMethod(self, newMethod) -> None:
        # self._obj.AxialMethod = newMethod
        for listener in self._configListeners:
            if isinstance(listener, ShapeComponentAssembly):
                listener.setAxialMethod(newMethod)

        if self.getParent is None:
            raise Exception(" a Stage requires a parent before any positioning! ")

        if self.getType() == FEATURE_PARALLEL_STAGE or self.getType() == FEATURE_POD:
            if newMethod == AxialMethod.AFTER:
                # log.warn("Stages (or Pods) cannot be relative to other stages via AFTER! Ignoring.");
                super.setAxialMethod(AxialMethod.TOP)
            else:
                super.setAxialMethod(newMethod)
        elif self.getType() == FEATURE_STAGE:
            # Centerline stages must be set via AFTER-- regardless of what was requested:
            super.setAxialMethod(AxialMethod.AFTER)
        else:
            raise Exception("Unrecognized subclass of Component Assembly.  Please update this method.")

        self.fireComponentChangeEvent(ComponentChangeEvent.NONFUNCTIONAL_CHANGE);

    # Components have no aerodynamic effect, so return false.
    def isAerodynamic(self):
        return False

    # Component have no effect on mass, so return false (even though the override values
    # may have an effect).
    def isMassive(self):
        return False

    def isAxisymmetric(self):
        # return !(2 == this.getInstanceCount())
        return False

    def update(self):
        self.updateBounds()
        if self.isAfter():
            self.setAfter()
        else:
            super.update()

        self.updateChildSequence()

    def updateBounds(self):
        # currently only updates the length 
        self._length = 0
        for  curChild in self.getChildren():
            if curChild.Proxy.isAfter():
                self._length += curChild.Proxy.getLength()

    def updateChildSequence(self):
        for  curChild in self.getChildren():
            if curChild.Proxy.getAxialMethod() == AxialMethod.AFTER:
                curChild.Proxy.setAfter()
