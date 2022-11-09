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

from App.motor.GrainHandler import FmmGrain
from App.motor.simResult import SimAlert, SimAlertLevel, SimAlertType

from DraftTools import translate

class MoonBurner(FmmGrain):
    """A moonburner is very similar to a BATES grain except the core is off center by a specified distance."""
    def __init__(self, obj):
        super().__init__(obj)

    def generateCoreMap(self):
        coreRadius = self.normalize(self._obj.CoreDiameter) / 2
        coreOffset = self.normalize(self._obj.CoreOffset)

        # Open up core
        self.coreMap[(self.mapX - coreOffset)**2 + self.mapY**2 < coreRadius**2] = 0

    def getDetailsString(self, lengthUnit='m'):
        # return 'Length: {}, Core: {}'.format(self.props['length'].dispFormat(lengthUnit),
        #                                      self.props['coreDiameter'].dispFormat(lengthUnit))
        return 'Length: {}, Core: {}'.format(self._obj.Length,
                                             self._obj.CoreDiameter)

    def getGeometryErrors(self):
        errors = super().getGeometryErrors()
        if self._obj.CoreDiameter == 0:
            errors.append(SimAlert(SimAlertLevel.ERROR, SimAlertType.GEOMETRY, 'Core diameter must not be 0'))
        if self._obj.CoreDiameter >= self._obj.Diameter:
            aText = 'Core diameter must be less than or equal to grain diameter'
            errors.append(SimAlert(SimAlertLevel.ERROR, SimAlertType.GEOMETRY, aText))

        if self._obj.CoreOffset * 2 > self._obj.Diameter:
            aText = 'Core offset should be less than or equal to grain radius'
            errors.append(SimAlert(SimAlertLevel.WARNING, SimAlertType.GEOMETRY, aText))

        return errors
