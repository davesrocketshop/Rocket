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

from Rocket.util.Coordinate import Coordinate, NUL
from Rocket.RingComponent import RingComponent
from Rocket.Utilities import clamp
from Rocket.interfaces.LineInstanceable import LineInstanceable
from Rocket.interfaces.RadialParent import RadialParent

from Rocket.events.ComponentChangeEvent import ComponentChangeEvent

from DraftTools import translate

class RadiusRingComponent(RingComponent, LineInstanceable):

    def __init__(self, obj):
        super().__init__(obj)

        if not hasattr(obj, 'CenterDiameter'):
            obj.addProperty('App::PropertyLength', 'CenterDiameter', 'RocketComponent', translate('App::Property', 'Diameter of the central hole')).CenterDiameter = 10.0

        if not hasattr(obj, 'InstanceCount'):
            obj.addProperty('App::PropertyInteger', 'InstanceCount', 'RocketComponent', translate('App::Property', 'Instance count')).InstanceCount = 1
        if not hasattr(obj, 'InstanceSeparation'):
            obj.addProperty('App::PropertyDistance', 'InstanceSeparation', 'RocketComponent', translate('App::Property', 'Front to front along the positive rocket axis')).InstanceSeparation = 0.0

    def setDefaults(self):
        super().setDefaults()

    def update(self):
        super().update()

        # Ensure any automatic variables are set
        self.getOuterDiameter(0)

    def getOuterRadius(self, pos):
        return self.getOuterDiameter(pos) / 2.0

    def getOuterDiameter(self, pos):
        if self.hasParent():
            parent = self.getParent()
            if self._obj.AutoDiameter and isinstance(parent, RadialParent):
                pos1 = self.toRelative(NUL, parent)[0]._x
                pos2 = self.toRelative(Coordinate(self.getLength()), parent)[0]._x
                pos1 = clamp(pos1, 0, parent.getLength())
                pos2 = clamp(pos2, 0, parent.getLength())
                self._obj.Diameter = min(parent.getInnerDiameter(pos1), parent.getInnerDiameter(pos2))

        return float(self._obj.Diameter)

    def setOuterRadius(self, r):
        self.setOuterDiameter(r * 2.0)

    def setOuterDiameter(self, d):
        d = max(d,0)

        for listener in self._configListeners:
            if isinstance(listener, RadiusRingComponent):
                listener.setOuterDiameter(d)

        if self._obj.Diameter == d and not self._obj.AutoDiameter:
            return

        self._obj.Diameter = d
        self._obj.AutoDiameter = False
        if self.getInnerRadius(0) > (d / 2.0):
            self._obj.CenterDiameter = d
            self._obj.CenterAutoDiameter = False

        self.clearPreset()
        self.fireComponentChangeEvent(ComponentChangeEvent.MASS_CHANGE)

    def getInnerRadius(self, pos):
        return self.getInnerDiameter(pos) / 2.0

    def getInnerDiameter(self, pos):
        return self._obj.CenterDiameter

    def setInnerRadius(self, r):
        r = max(r,0)

        for listener in self._configListeners:
            if isinstance(listener, RadiusRingComponent):
                listener.setInnerRadius(r)

        if self._obj.CenterDiameter == (2.0 * r):
            return

        self._obj.CenterDiameter = 2.0 * r
        self._obj.CenterAutoDiameter = False
        if self.getOuterRadius(0) < r:
            self._obj.Diameter = 2.0 * r
            self._obj.AutoDiameter = False

        # clearPreset();
        self.fireComponentChangeEvent(ComponentChangeEvent.MASS_CHANGE)

    def getThickness(self):
        return max(self.getOuterRadius(0) - self.getInnerRadius(0), 0)

    def setThickness(self, thickness):
        for listener in self._configListeners:
            if isinstance(listener, RadiusRingComponent):
                listener.setThickness(thickness)

        outer = self.getOuterRadius(0)

        thickness = clamp(thickness, 0, outer)
        self.setInnerRadius(outer - thickness)

    def getInstanceSeparation(self):
        return self._obj.InstanceSeparation

    def setInstanceSeparation(self, separation):
        self._obj.InstanceSeparation = separation

        for listener in self._configListeners:
            if isinstance(listener, RadiusRingComponent):
                listener.setInstanceSeparation(separation)

    def setInstanceCount(self, newCount):
        for listener in self._configListeners:
            if isinstance(listener, RadiusRingComponent):
                listener.setInstanceCount(newCount)

        if 0 < newCount:
            self._obj.InstanceCount = newCount

    def getInstanceOffsets(self):
        toReturn = []
        for index in range(self.getInstanceCount()):
            toReturn.append(Coordinate( index * float(self._obj.InstanceSeparation), 0, 0))

        return toReturn

    def getInstanceCount(self):
        return self._obj.InstanceCount

    def getPatternName(self):
        return str(self.getInstanceCount()) + "-Line"
