# ***************************************************************************
# *   Copyright (c) 2022 David Carter <dcarter@davidcarter.ca>              *
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
"""Class for rocket motors"""

__title__ = "FreeCAD Rocket Motors"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

from App.motor.Grain import FmmGrain
from App.motor.simResult import SimAlert, SimAlertLevel, SimAlertType

from App.Constants import GRAIN_GEOMETRY_D

from DraftTools import translate

class DGrain(FmmGrain):
    """Defines a D grain, which is a grain that has no propellant past a chord that is a user-specified distance from
    the diameter."""

    def __init__(self, obj):
        super().__init__(obj)

        self._obj.GeometryName = GRAIN_GEOMETRY_D

        if not hasattr(obj, 'SlotOffset'):
            obj.addProperty('App::PropertyLength', 'SlotOffset', 'Grain', translate('App::Property', 'Slot offset')).SlotOffset = 0.0

    def onDocumentRestored(self, obj):
        super().onDocumentRestored(obj)
        
        # Add any missing attributes
        DGrain(obj)

    def generateCoreMap(self):
        slotOffset = self.normalize(self._obj.SlotOffset)

        self.coreMap[self.mapX > slotOffset] = 0

    def getDetailsString(self, lengthUnit='m'):
        # return 'Length: {}, Slot offset: {}'.format(self.props['length'].dispFormat(lengthUnit),
        #                                             self.props['slotOffset'].dispFormat(lengthUnit))
        return 'Length: {}, Slot offset: {}'.format(self._obj.Length,
                                                    self._obj.SlotOffset)

    def getGeometryErrors(self):
        errors = super().getGeometryErrors()

        if self._obj.SlotOffset > self._obj.Diameter / 2:
            aText = 'Core offset must not be greater than grain radius'
            errors.append(SimAlert(SimAlertLevel.ERROR, SimAlertType.GEOMETRY, aText))
        if self._obj.SlotOffset < -self._obj.Diameter / 2:
            aText = 'Core offset must be greater than negative grain radius'
            errors.append(SimAlert(SimAlertLevel.ERROR, SimAlertType.GEOMETRY, aText))

        return errors
