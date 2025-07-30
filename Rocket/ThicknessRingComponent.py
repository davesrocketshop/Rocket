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

from Rocket.RingComponent import RingComponent
from Rocket.interfaces.RadialParent import RadialParent

from Rocket.util.Coordinate import Coordinate, NUL
from Rocket.Utilities import clamp

from DraftTools import translate

"""
    An inner component that consists of a hollow cylindrical component.  This can be
    an inner tube, tube coupler, centering ring, bulkhead etc.

    The properties include the inner and outer radii, length and radial position.
"""
class ThicknessRingComponent(RingComponent):

    def __init__(self, obj : Any) -> None:
        super().__init__(obj)

        if not hasattr(obj,"Thickness"):
            obj.addProperty('App::PropertyLength', 'Thickness', 'RocketComponent', translate('App::Property', 'Diameter of the inside of the body tube')).Thickness = 0.33

    def setDefaults(self) -> None:
        super().setDefaults()

    def update(self) -> None:
        super().update()

        # Ensure any automatic variables are set
        self.getOuterDiameter(0)
        self.getInnerDiameter(0)

    def getOuterRadius(self, pos : float) -> float:
        return self.getOuterDiameter(pos) / 2.0

    def getOuterDiameter(self, pos : float) -> float:
        if self.hasParent():
            parent = self.getParent()
            if self.isOuterDiameterAutomatic() and isinstance(parent, RadialParent):
                pos1 = self.toRelative(NUL, parent)[0]._x
                pos2 = self.toRelative(Coordinate(self.getLength()), parent)[0]._x
                pos1 = clamp(pos1, 0, parent.getLength())
                pos2 = clamp(pos2, 0, parent.getLength())
                self._obj.Diameter = min(parent.getInnerDiameter(pos1), parent.getInnerDiameter(pos2))

        return float(self._obj.Diameter)

    def setOuterRadius(self, radius : float) -> None:
        self.setOuterDiameter(radius * 2.0)

    def setOuterDiameter(self, diameter : float) -> None:
        diameter = max(diameter,0)
        if self._obj.Diameter == diameter and not self.isOuterDiameterAutomatic():
            return

        self._obj.Diameter = diameter
        self._obj.AutoDiameter = False

        if self._obj.Thickness > (self._obj.Diameter / 2.0):
            self._obj.Thickness = self._obj.Diameter / 2.0

        self.clearPreset()

        self.notifyComponentChanged()

    def getThickness(self) -> float:
        return min(float(self._obj.Thickness), self.getOuterRadius(0))

    def setThickness(self, thickness : float) -> None:
        outer = self.getOuterRadius(0)

        thickness = clamp(thickness, 0, outer)
        if self._obj.Thickness == thickness:
            return

        self._obj.Thickness = thickness

        self.clearPreset()

        self.notifyComponentChanged()

    def getInnerRadius(self, pos : float) -> float:
        return self.getInnerDiameter(pos) / 2.0

    def getInnerDiameter(self, pos : float) -> float:
        return max(self.getOuterDiameter(pos) - float(2.0 * self._obj.Thickness), 0)

    def setInnerRadius(self, radius : float) -> None:
        self.setInnerDiameter(radius * 2.0)

    def setInnerDiameter(self, diameter : float) -> None:
        diameter = max(diameter,0)
        self.setThickness((self.getOuterDiameter(0) - diameter) / 2.0)
