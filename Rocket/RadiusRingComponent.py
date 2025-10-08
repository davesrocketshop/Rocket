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

from typing import Any

import FreeCAD

translate = FreeCAD.Qt.translate

from Rocket.util.Coordinate import Coordinate, NUL
from Rocket.RingComponent import RingComponent
from Rocket.Utilities import clamp
from Rocket.interfaces.LineInstanceable import LineInstanceable
from Rocket.interfaces.RadialParent import RadialParent

class RadiusRingComponent(RingComponent, LineInstanceable):

    def __init__(self, obj : Any) -> None:
        super().__init__(obj)

        if not hasattr(obj, 'CenterDiameter'):
            obj.addProperty('App::PropertyLength', 'CenterDiameter', 'RocketComponent', translate('App::Property', 'Diameter of the central hole')).CenterDiameter = 10.0

        if not hasattr(obj, 'InstanceCount'):
            obj.addProperty('App::PropertyInteger', 'InstanceCount', 'RocketComponent', translate('App::Property', 'Instance count')).InstanceCount = 1
        if not hasattr(obj, 'InstanceSeparation'):
            obj.addProperty('App::PropertyDistance', 'InstanceSeparation', 'RocketComponent', translate('App::Property', 'Front to front along the positive rocket axis')).InstanceSeparation = 0.0

    def setDefaults(self) -> None:
        super().setDefaults()

    def update(self) -> None:
        super().update()

        # Ensure any automatic variables are set
        self.getOuterDiameter(0)

    def getOuterRadius(self, pos : float) -> float:
        return self.getOuterDiameter(pos) / 2.0

    def getOuterDiameter(self, pos : float) -> float:
        if self.hasParent():
            parent = self.getParent()
            if self._obj.AutoDiameter and isinstance(parent, RadialParent):
                pos1 = self.toRelative(NUL, parent)[0]._x
                pos2 = self.toRelative(Coordinate(self.getLength()), parent)[0]._x
                pos1 = clamp(pos1, 0, parent.getLength())
                pos2 = clamp(pos2, 0, parent.getLength())
                self._obj.Diameter = min(parent.getInnerDiameter(pos1), parent.getInnerDiameter(pos2))

        return float(self._obj.Diameter) / self.getDiameterScale()

    def setOuterRadius(self, radius : float) -> None:
        self.setOuterDiameter(radius * 2.0)

    def setOuterDiameter(self, d : float) -> None:
        d = max(d,0)

        if self._obj.Diameter == d and not self._obj.AutoDiameter:
            return

        self._obj.Diameter = d
        self._obj.AutoDiameter = False
        if self.getInnerRadius(0) > (d / 2.0):
            self._obj.CenterDiameter = d
            self._obj.CenterAutoDiameter = False

        self.clearPreset()
        self.notifyComponentChanged()

    def getInnerRadius(self, pos : float) -> float:
        return self.getInnerDiameter(pos) / 2.0

    def getInnerDiameter(self, pos : float) -> float:
        return float(self._obj.CenterDiameter)

    def setInnerRadius(self, radius : float) -> None:
        radius = max(radius,0)

        if self._obj.CenterDiameter == (2.0 * radius):
            return

        self._obj.CenterDiameter = 2.0 * radius
        self._obj.CenterAutoDiameter = False
        if self.getOuterRadius(0) < radius:
            self._obj.Diameter = 2.0 * radius
            self._obj.AutoDiameter = False

        # clearPreset();
        self.notifyComponentChanged()

    def getThickness(self) -> float:
        return max(self.getOuterRadius(0) - self.getInnerRadius(0), 0)

    def setThickness(self, thickness : float) -> None:
        outer = self.getOuterRadius(0)

        thickness = clamp(thickness, 0, outer)
        self.setInnerRadius(outer - thickness)

    def getInstanceSeparation(self) -> float:
        return float(self._obj.InstanceSeparation)

    def setInstanceSeparation(self, separation : float) -> None:
        self._obj.InstanceSeparation = separation

    def setInstanceCount(self, newCount : int) -> None:
        if 0 < newCount:
            self._obj.InstanceCount = newCount

    def getInstanceOffsets(self) -> list:
        toReturn = []
        for index in range(self.getInstanceCount()):
            toReturn.append(Coordinate( index * float(self._obj.InstanceSeparation), 0, 0))

        return toReturn

    def getInstanceCount(self) -> int:
        return self._obj.InstanceCount

    def getPatternName(self) -> str:
        return f"{self.getInstanceCount()}-Line"
