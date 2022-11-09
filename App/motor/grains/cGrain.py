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

import numpy as np

from App.motor.GrainHandler import FmmGrain
from App.motor.simResult import SimAlert, SimAlertLevel, SimAlertType

from DraftTools import translate

class CGrain(FmmGrain):
    """Defines a C grain, which is a cylindrical grain with a single slot taken out. The slot is a rectangular section
    with a certain width that starts at the casting tube and protrudes towards the center of the grain, stopping a
    specified offset away."""

    def __init__(self, obj):
        super().__init__(obj)

    def generateCoreMap(self):
        slotWidth = self.normalize(self._obj.SlotWidth)
        slotOffset = self.normalize(self._obj.SlotOffset)

        self.coreMap[np.logical_and(np.abs(self.mapY) < slotWidth / 2, self.mapX > slotOffset)] = 0

    def getDetailsString(self, lengthUnit='m'):
        return 'Length: {}'.format(self._obj.Length)

    def getGeometryErrors(self):
        errors = super().getGeometryErrors()

        if self._obj.SlotOffset > self._obj.Diameter / 2:
            aText = 'Slot offset should be less than grain radius'
            errors.append(SimAlert(SimAlertLevel.WARNING, SimAlertType.GEOMETRY, aText))
        if self._obj.SlotOffset < -self._obj.Diameter / 2:
            aText = 'Slot offset should be greater than negative grain radius'
            errors.append(SimAlert(SimAlertLevel.WARNING, SimAlertType.GEOMETRY, aText))

        if self._obj.SlotWidth == 0:
            errors.append(SimAlert(SimAlertLevel.WARNING, SimAlertType.GEOMETRY, 'Slot width must not be 0'))
        if self._obj.SlotWidth > self._obj.Diameter:
            aText = 'Slot width should not be greater than grain diameter'
            errors.append(SimAlert(SimAlertLevel.WARNING, SimAlertType.GEOMETRY, aText))

        return errors
