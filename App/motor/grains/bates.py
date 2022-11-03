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
import skfmm
from skimage import measure

from App.motor.Grain import PerforatedGrain
from App.motor import geometry
from App.motor.simResult import SimAlert, SimAlertLevel, SimAlertType

from App.Constants import GRAIN_GEOMETRY_BATES

from DraftTools import translate

class BatesGrain(PerforatedGrain):
    """The BATES grain has a simple cylindrical core. This type is not an FMM grain for performance reasons, as the
    calculations are easy enough to do manually."""

    def _initAttributes(self, obj):
        super()._initAttributes(obj)

        self._obj.GeometryName = GRAIN_GEOMETRY_BATES

        if not hasattr(obj, 'CoreDiameter'):
            obj.addProperty('App::PropertyLength', 'CoreDiameter', 'Grain', translate('App::Property', 'Core diameter')).CoreDiameter = 1.0

    def simulationSetup(self, config):
        self.wallWeb = float(self._obj.Diameter - self._obj.CoreDiameter) / 2

    def getCorePerimeter(self, regDist):
        return geometry.circlePerimeter(float(self._obj.CoreDiameter) + (2 * regDist))

    def getFaceArea(self, regDist):
        outer = geometry.circleArea(float(self._obj.Diameter))
        inner = geometry.circleArea(float(self._obj.CoreDiameter) + (2 * regDist))
        return outer - inner

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
            aText = 'Core diameter must be less than grain diameter'
            errors.append(SimAlert(SimAlertLevel.ERROR, SimAlertType.GEOMETRY, aText))
        return errors

    # These two functions have a lot of code reuse, but it is worth it because making BATES an fmmGrain would make it
    # signficantly way slower
    def getFaceImage(self, mapDim):
        mapX, mapY = np.meshgrid(np.linspace(-1, 1, mapDim), np.linspace(-1, 1, mapDim))
        mask = mapX**2 + mapY**2 > 1
        coreMap = np.ones_like(mapX)

        # Normalize core diameter
        coreRadius = (self._obj.CoreDiameter / (0.5 * self._obj.Diameter)) / 2

        # Open up core
        coreMap[mapX**2 + mapY**2 < coreRadius**2] = 0
        maskedMap = np.ma.MaskedArray(coreMap, mask)

        return maskedMap

    def getRegressionData(self, mapDim, numContours=15, coreBlack=True):
        masked = self.getFaceImage(mapDim)
        regressionMap = None
        contours = []
        contourLengths = {}

        try:
            cellSize = 1 / mapDim
            regressionMap = skfmm.distance(masked, dx=cellSize) * 2
            regmax = np.amax(regressionMap)
            regressionMap = regressionMap[:, :].copy()
            if coreBlack:
                regressionMap[np.where(masked == 0)] = regmax # Make the core black

            for dist in np.linspace(0, regmax, numContours):
                contours.append([])
                contourLengths[dist] = 0
                layerContours = measure.find_contours(regressionMap, dist, fully_connected='high')
                for contour in layerContours:
                    contours[-1].append(contour)
                    contourLengths[dist] += geometry.length(contour, mapDim)

        except ValueError as exc: # If there aren't any contours, do nothing
            print(exc)

        return (masked, regressionMap, contours, contourLengths)
