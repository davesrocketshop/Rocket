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
"""Class for rocket components"""

__title__ = "FreeCAD Rocket Components"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

from abc import abstractmethod
import math

from App.RingComponent import RingComponent
from App.interfaces.RadialParent import RadialParent

from App.events.ComponentChangeEvent import ComponentChangeEvent

from App.util.Coordinate import Coordinate, NUL
from App.util.MathUtil import MathUtil

from DraftTools import translate

"""
    An inner component that consists of a hollow cylindrical component.  This can be
    an inner tube, tube coupler, centering ring, bulkhead etc.
    
    The properties include the inner and outer radii, length and radial position.
"""
class ThicknessRingComponent(RingComponent):
	
    def __init__(self, obj):
        super().__init__(obj)

        if not hasattr(obj,"OuterDiameter"):
            obj.addProperty('App::PropertyLength', 'OuterDiameter', 'BodyTube', translate('App::Property', 'Diameter of the outside of the body tube')).OuterDiameter = 24.79
        if not hasattr(obj,"Thickness"):
            obj.addProperty('App::PropertyLength', 'Thickness', 'BodyTube', translate('App::Property', 'Diameter of the inside of the body tube')).Thickness = 0.33

    def setDefaults(self):
        super().setDefaults()

    def getOuterRadius(self):
        return self.getOuterDiameter() / 2.0

    def getOuterDiameter(self):
        if self.isOuterDiameterAutomatic() and isinstance(self.getParent(), RadialParent):
            pos1 = self.toRelative(NUL, self.getParent())[0]._x
            pos2 = self.toRelative(Coordinate(self.getLength()), self.getParent())[0]._x
            pos1 = MathUtil.clamp(pos1, 0, self.getParent().getLength())
            pos2 = MathUtil.clamp(pos2, 0, self.getParent().getLength())
            self._obj.OuterDiameter = min(self.getParent().getInnerDiameter(pos1), self.getParent().getInnerDiameter(pos2))
                
        return self._obj.OuterDiameter

    def setOuterRadius(self, radius):
        self.setOuterDiameter(radius * 2.0)

    def setOuterDiameter(self, diameter):
        for listener in self._configListeners:
            if isinstance(listener, ThicknessRingComponent):
                listener.setOuterDiameter(diameter)

        diameter = max(diameter,0)
        if self._obj.OuterDiameter == diameter and not self.isOuterDiameterAutomatic():
            return
        
        self._obj.OuterDiameter = diameter
        self._obj.AutoDiameter = False

        if self._obj.Thickness > (self._obj.OuterDiameter / 2.0):
            self._obj.Thickness = self._obj.OuterDiameter / 2.0
        
        self.clearPreset()
        
        self.fireComponentChangeEvent(ComponentChangeEvent.MASS_CHANGE)

    def getThickness(self):
        return min(self._obj.Thickness, self.getOuterRadius())

    def setThickness(self, thickness):
        for listener in self._configListeners:
            if isinstance(listener, ThicknessRingComponent):
                listener.setThickness(thickness)

        outer = self.getOuterRadius()
        
        thickness = MathUtil.clamp(thickness, 0, outer)
        if self._obj.Thickness == thickness:
            return
        
        self._obj.Thickness = thickness
        
        self.clearPreset()

        self.fireComponentChangeEvent(ComponentChangeEvent.MASS_CHANGE)

    def getInnerRadius(self, pos=0):
        return self.getInnerDiameter() / 2.0

    def getInnerDiameter(self, pos=0):
        return max(self.getOuterDiameter() - (2.0 * self._obj.Thickness), 0)

    def setInnerRadius(self, radius):
        self.setInnerDiameter(radius * 2.0)

    def setInnerRadius(self, diameter):
        for listener in self._configListeners:
            if isinstance(listener, ThicknessRingComponent):
                listener.setInnerRadius(diameter)

        diameter = max(diameter,0)
        self.setThickness((self.getOuterDiameter() - diameter) / 2.0)
