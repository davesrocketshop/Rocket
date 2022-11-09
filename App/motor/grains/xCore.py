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

class XCore(FmmGrain):
    """An X Core grain has a core shaped like a plus sign or an X."""

    def __init__(self, obj):
        super().__init__(obj)

    def generateCoreMap(self):
        slotWidth = self.normalize(self._obj.SlotWidth)
        slotLength = self.normalize(self._obj.SlotLength)

        self.coreMap[np.logical_and(np.abs(self.mapY) < slotWidth/2, np.abs(self.mapX) < slotLength)] = 0
        self.coreMap[np.logical_and(np.abs(self.mapX) < slotWidth/2, np.abs(self.mapY) < slotLength)] = 0

    def getDetailsString(self, lengthUnit='m'):
        # return 'Length: {}, Slots: {} by {}'.format(self.props['length'].dispFormat(lengthUnit),
        #                                             self.props['slotWidth'].dispFormat(lengthUnit),
        #                                             self.props['slotLength'].dispFormat(lengthUnit))
        return 'Length: {}, Slots: {} by {}'.format(self._obj.Length,
                                                    self._obj.SlotWidth,
                                                    self._obj.SlotLength)

    def getGeometryErrors(self):
        errors = super().getGeometryErrors()
        if self._obj.SlotWidth == 0:
            errors.append(SimAlert(SimAlertLevel.ERROR, SimAlertType.GEOMETRY, 'Slot width must not be 0'))
        if self._obj.SlotWidth > self._obj.Diameter:
            aText = 'Slot width should be less than or equal to grain diameter'
            errors.append(SimAlert(SimAlertLevel.WARNING, SimAlertType.GEOMETRY, aText))

        if self._obj.SlotLength == 0:
            errors.append(SimAlert(SimAlertLevel.ERROR, SimAlertType.GEOMETRY, 'Slot length must not be 0'))
        if self._obj.SlotLength * 2 > self._obj.Diameter:
            aText = 'Slot length should be less than or equal to grain radius'
            errors.append(SimAlert(SimAlertLevel.WARNING, SimAlertType.GEOMETRY, aText))

        return errors
