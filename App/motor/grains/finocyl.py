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

from App.motor.Grain import FmmGrain
from App.motor.simResult import SimAlert, SimAlertLevel, SimAlertType

from App.Constants import GRAIN_GEOMETRY_FINOCYL

from DraftTools import translate

class Finocyl(FmmGrain):
    """A finocyl (fins on cylinder) grain has a circular core with a number of rectangular extensions that start at the
    circle's edge and protude along its normals."""

    def __init__(self, obj):
        super().__init__(obj)

        self._obj.GeometryName = GRAIN_GEOMETRY_FINOCYL

        if not hasattr(obj, 'NumFins'):
            obj.addProperty('App::PropertyQuantity', 'NumFins', 'Grain', translate('App::Property', 'Number of fins')).NumFins = 4
        if not hasattr(obj, 'FinWidth'):
            obj.addProperty('App::PropertyLength', 'FinWidth', 'Grain', translate('App::Property', 'Fin width')).FinWidth = 0.25
        if not hasattr(obj, 'FinLength'):
            obj.addProperty('App::PropertyLength', 'FinLength', 'Grain', translate('App::Property', 'Fin length')).v = 0.5
        if not hasattr(obj, 'CoreDiameter'):
            obj.addProperty('App::PropertyLength', 'CoreDiameter', 'Grain', translate('App::Property', 'Core diameter')).CoreDiameter = 1.0

    def onDocumentRestored(self, obj):
        super().onDocumentRestored(obj)
        
        # Add any missing attributes
        Finocyl(obj)

    def generateCoreMap(self):
        coreRadius = self.normalize(self._obj.CoreDiameter) / 2
        numFins = self._obj.NumFins
        finWidth = self.normalize(self._obj.FinWidth)
        # The user enters the length that the fin protrudes from the core, so we add the radius on
        finLength = self.normalize(self._obj.FinLength) + coreRadius

        # Open up core
        self.coreMap[self.mapX**2 + self.mapY**2 < coreRadius**2] = 0

        # Add fins
        for i in range(0, numFins):
            theta = 2 * np.pi / numFins * i
            # Initialize a vector pointing along the fin
            vect0 = np.cos(theta)
            vect1 = np.sin(theta)
            # Select all points within half the width of the vector
            vect = abs(vect0*self.mapX + vect1*self.mapY) < finWidth / 2
            # Set up two perpendicular vectors to cap off the ends
            near = (vect1 * self.mapX) - (vect0 * self.mapY) > 0 # Inside of the core
            far = (vect1 * self.mapX) - (vect0 * self.mapY) < finLength # At the casting tube end of the vector
            ends = np.logical_and(far, near)
            # Open up the fin
            self.coreMap[np.logical_and(vect, ends)] = 0

    def getDetailsString(self, lengthUnit='m'):
        # return 'Length: {}, Core: {}, Fins: {}'.format(self.props['length'].dispFormat(lengthUnit),
        #                                                self.props['coreDiameter'].dispFormat(lengthUnit),
        #                                                self._obj.NumFins)
        return 'Length: {}, Core: {}, Fins: {}'.format(self._obj.Length,
                                                       self._obj.CoreDiameter,
                                                       self._obj.NumFins)

    def getGeometryErrors(self):
        errors = super().getGeometryErrors()
        if self._obj.CoreDiameter == 0:
            errors.append(SimAlert(SimAlertLevel.ERROR, SimAlertType.GEOMETRY, 'Core diameter must not be 0'))
        if self._obj.CoreDiameter >= self._obj.Diameter:
            aText = 'Core diameter must be less than or equal to grain diameter'
            errors.append(SimAlert(SimAlertLevel.ERROR, SimAlertType.GEOMETRY, aText))

        if self._obj.FinLength == 0:
            errors.append(SimAlert(SimAlertLevel.ERROR, SimAlertType.GEOMETRY, 'Fin length must not be 0'))
        if self._obj.FinLength * 2 > self._obj.Diameter:
            aText = 'Fin length should be less than or equal to grain radius'
            errors.append(SimAlert(SimAlertLevel.WARNING, SimAlertType.GEOMETRY, aText))
        coreWidth = self._obj.CoreDiameter + (2 * self._obj.FinLength)
        if coreWidth > self._obj.Diameter:
            aText = 'Core radius plus fin length should be less than or equal to grain radius'
            errors.append(SimAlert(SimAlertLevel.WARNING, SimAlertType.GEOMETRY, aText))

        if self._obj.FinWidth == 0:
            errors.append(SimAlert(SimAlertLevel.ERROR, SimAlertType.GEOMETRY, 'Fin width must not be 0'))
        if self._obj.NumFins > 1:
            radius = self._obj.CoreDiameter / 2
            apothem = radius + self._obj.FinLength
            sideLength = 2 * apothem * np.tan(np.pi / self._obj.NumFins)
            if sideLength < self._obj.FinWidth:
                errors.append(SimAlert(SimAlertLevel.WARNING, SimAlertType.GEOMETRY, 'Fin tips intersect'))

        return errors
