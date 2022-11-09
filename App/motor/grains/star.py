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

class StarGrain(FmmGrain):
    """A star grain has a core shaped like a star."""

    def __init__(self, obj):
        super().__init__(obj)

    def generateCoreMap(self):
        numPoints = self._obj.NumPoints
        pointWidth = self.normalize(self._obj.PointWidth)
        pointLength = self.normalize(self._obj.PointLength)

        for i in range(0, numPoints):
            theta = 2 * np.pi / numPoints * i
            comp0 = np.cos(theta)
            comp1 = np.sin(theta)

            rect = abs(comp0 * self.mapX + comp1 * self.mapY)
            width = pointWidth / 2 * (1 - (((self.mapX ** 2 + self.mapY ** 2) ** 0.5) / pointLength))
            vect = rect < width
            near = comp1*self.mapX - comp0*self.mapY > -0.025
            self.coreMap[np.logical_and(vect, near)] = 0

    def getDetailsString(self, lengthUnit='m'):
        # return 'Length: {}, Points: {}'.format(self.props['length'].dispFormat(lengthUnit),
        #                                        self._obj.NumPoints)
        return 'Length: {}, Points: {}'.format(self._obj.Length,
                                               self._obj.NumPoints)

    def getGeometryErrors(self):
        errors = super().getGeometryErrors()
        if self._obj.NumPoints == 0:
            errors.append(SimAlert(SimAlertLevel.ERROR, SimAlertType.GEOMETRY, 'Star grain has 0 points'))

        if self._obj.PointLength == 0:
            errors.append(SimAlert(SimAlertLevel.ERROR, SimAlertType.GEOMETRY, 'Point length must not be 0'))
        if self._obj.PointLength * 2 > self._obj.Diameter:
            aText = 'Point length should be less than or equal to grain radius'
            errors.append(SimAlert(SimAlertLevel.WARNING, SimAlertType.GEOMETRY, aText))

        if self._obj.PointWidth == 0:
            errors.append(SimAlert(SimAlertLevel.ERROR, SimAlertType.GEOMETRY, 'Point width must not be 0'))

        return errors
