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
"""Class for rocket components"""

__title__ = "FreeCAD Rocket Components"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

import FreeCAD

from App.util.Coordinate import Coordinate
from App.RingComponent import RingComponent
from App.Utilities import clamp
from App.interfaces.LineInstanceable import LineInstanceable
from App.interfaces.RadialParent import RadialParent

from App.events.ComponentChangeEvent import ComponentChangeEvent

from DraftTools import translate

class RadiusRingComponent(RingComponent, LineInstanceable):
	
    def __init__(self, obj):
        super().__init__(obj)

        if not hasattr(obj, 'Diameter'):
            obj.addProperty('App::PropertyLength', 'Diameter', 'Bulkhead', translate('App::Property', 'Outer diameter of the object')).Diameter = 25.0
        if not hasattr(obj, 'CenterDiameter'):
            obj.addProperty('App::PropertyLength', 'CenterDiameter', 'Bulkhead', translate('App::Property', 'Diameter of the central hole')).CenterDiameter = 10.0

        if not hasattr(obj, 'InstanceCount'):
            obj.addProperty('App::PropertyInteger', 'InstanceCount', 'Bulkhead', translate('App::Property', 'Instance count')).InstanceCount = 1
        if not hasattr(obj, 'InstanceSeparation'):
            obj.addProperty('App::PropertyVector', 'InstanceSeparation', 'Bulkhead', translate('App::Property', 'front-front along the positive rocket axis')).InstanceSeparation = FreeCAD.Vector(0, 0, 0)

    def getOuterRadius(self):
        if self.AutoDiameter and isinstance(self.getParent(), RadialParent):
            pos1 = self.toRelative(Coordinate.NUL, self.getParent())[0].x;
            pos2 = self.toRelative(Coordinate(self.getLength()), self.getParent())[0].x;
            pos1 = clamp(pos1, 0, self.getParent().getLength())
            pos2 = clamp(pos2, 0, self.getParent().getLength())
            outerRadius = min(self.getParent().getInnerRadius(pos1), self.getParent().getInnerRadius(pos2))

        return outerRadius

    def setOuterRadius(self, r):
        r = max(r,0)

        for listener in self._configListeners:
            if isinstance(listener, RadiusRingComponent):
                listener.setOuterRadius(r)

        if self._obj.Diameter == (2.0 * r) and not self._obj.AutoDiameter:
            return

        self._obj.Diameter = 2.0 * r
        self._obj.AutoDiameter = False
        if self.getInnerRadius() > r:
            self._obj.CenterDiameter = 2.0 * r
            self._obj.CenterAutoDiameter = False

        # self.clearPreset()
        self.fireComponentChangeEvent(ComponentChangeEvent.MASS_CHANGE)


    def getInnerRadius(self):
        return self._obj.CenterDiameter / 2.0

    def setInnerRadius(self, r):
        r = max(r,0)

        for listener in self._configListeners:
            if isinstance(listener, RadiusRingComponent):
                listener.setInnerRadius(r)

        if self._obj.CenterDiameter == (2.0 * r):
            return

        self._obj.CenterDiameter = 2.0 * r
        self._obj.CenterAutoDiameter = False
        if self.getOuterRadius() < r:
            self._obj.Diameter = 2.0 * r
            self._obj.AutoDiameter = False

        # clearPreset();
        self.fireComponentChangeEvent(ComponentChangeEvent.MASS_CHANGE)

    def getThickness(self):
        return max(self.getOuterRadius() - self.getInnerRadius(), 0)

    def setThickness(self, thickness):
        for listener in self._configListeners:
            if isinstance(listener, RadiusRingComponent):
                listener.setThickness(thickness)

        outer = self.getOuterRadius()

        thickness = clamp(thickness, 0, outer)
        self.setInnerRadius(outer - thickness)

    def getInstanceSeparation(self):
        return self._obj.InstanceSeparation

    def setInstanceSeparation(self, _separation):
        self._obj.InstanceSeparation = _separation

        for listener in self._configListeners:
            if isinstance(listener, RadiusRingComponent):
                listener.setInstanceSeparation(_separation)

    def setInstanceCount(self, newCount):
        for listener in self._configListeners:
            if isinstance(listener, RadiusRingComponent):
                listener.setInstanceCount(newCount)

        if 0 < newCount:
            self._obj.InstanceCount = newCount

    def getInstanceOffsets(self):
        toReturn = []
        for index in range(self.getInstanceCount()):
            toReturn.append(Coordinate( index * self._obj.InstanceSeparation, 0, 0))
        
        return toReturn

    def getInstanceCount(self):
        return self._obj.InstanceCount

    def getPatternName(self):
        return str(self.getInstanceCount()) + "-Line"
