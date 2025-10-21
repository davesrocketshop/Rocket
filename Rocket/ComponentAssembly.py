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
"""Base class for rocket component assemblies"""

__title__ = "FreeCAD Rocket Components"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

from typing import Any

import FreeCAD

translate = FreeCAD.Qt.translate

from Rocket.position import AxialMethod
from Rocket.position.AxialPositionable import AxialPositionable
from Rocket.util.BoundingBox import BoundingBox
from Rocket.RocketComponentShapeless import RocketComponentShapeless

from Rocket.Constants import FEATURE_ROCKET, FEATURE_STAGE, FEATURE_PARALLEL_STAGE, FEATURE_POD, FEATURE_BODY_TUBE, FEATURE_NOSE_CONE, FEATURE_TRANSITION

class ComponentAssembly(RocketComponentShapeless, AxialPositionable):

    def __init__(self, obj : Any) -> None:
        super().__init__(obj)

        if not obj.hasExtension("App::GeoFeatureGroupExtensionPython"):
            obj.addExtension("App::GeoFeatureGroupExtensionPython")
        # if not obj.hasExtension("App::GroupExtensionPython"):
        #     obj.addExtension("App::GroupExtensionPython")

        super().setAxialMethod(AxialMethod.AFTER)
        self._length = 0

    def setDefaults(self) -> None:
        super().setDefaults()

    def getAxialOffset(self) -> float:
        return self.getAxialOffsetFromMethod(self._obj.AxialMethod)

    def setAxialOffset(self, newAxialOffset : float) -> None:
        self.updateBounds()
        super()._setAxialOffset(self._obj.AxialMethod, newAxialOffset)
        self.notifyComponentChanged()

    def getAxialMethod(self) -> AxialMethod.AxialMethod:
        return self._obj.AxialMethod

    def setAxialMethod(self, newAxialMethod : AxialMethod.AxialMethod) -> None:
        # self._obj.AxialMethod = newMethod

        if not self.hasParent():
            raise Exception(translate("Rocket", "A Stage requires a parent before any positioning!"))

        if self.getType() == FEATURE_PARALLEL_STAGE or self.getType() == FEATURE_POD:
            if newAxialMethod == AxialMethod.AFTER:
                # log.warn("Stages (or Pods) cannot be relative to other stages via AFTER! Ignoring.");
                super().setAxialMethod(AxialMethod.TOP)
            else:
                super().setAxialMethod(newAxialMethod)
        elif self.getType() == FEATURE_STAGE:
            # Centerline stages must be set via AFTER-- regardless of what was requested:
            super().setAxialMethod(AxialMethod.AFTER)
        elif self.getType() == FEATURE_ROCKET:
            # Main rocket must be set via ABSOLUTE-- regardless of what was requested:
            super().setAxialMethod(AxialMethod.ABSOLUTE)
        else:
            raise Exception("Unrecognized subclass of Component Assembly.  Please update this method.")

        self.notifyComponentChanged()

    def getInstanceBoundingBox (self) -> BoundingBox:
        return BoundingBox()

    def getBoundingRadius(self) -> float:
        outerRadius = 0
        for comp in self.getChildren():
            proxy = self.getProxy(comp)
            thisRadius = 0
            if proxy.Type in [FEATURE_BODY_TUBE]:
                thisRadius = proxy.getOuterRadius(0)
            elif proxy.Type in [FEATURE_TRANSITION, FEATURE_NOSE_CONE]:
                thisRadius = max(proxy.getForeRadius(), proxy.getAftRadius())

            outerRadius = max(outerRadius, thisRadius)

        return outerRadius

    def update(self) -> None:
        self.updateBounds()
        if self.isAfter():
            self.setAfter()
        else:
            super().update()

        self.updateChildSequence()

    def updateBounds(self) -> None:
        # currently only updates the length
        self._length = 0
        for  curChild in self.getChildren():
            if curChild.Proxy.isAfter():
                self._length += float(curChild.Proxy.getLength())

    def updateChildSequence(self) -> None:
        for  curChild in self.getChildren():
            if curChild.Proxy.isAfter():
                curChild.Proxy.setAfter()
