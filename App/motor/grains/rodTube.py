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

from App.motor.GrainHandler import PerforatedGrain
from App.motor import geometry
from App.motor.simResult import SimAlert, SimAlertLevel, SimAlertType

from App.Constants import GRAIN_GEOMETRY_RODTUBE

from DraftTools import translate

class RodTubeGrain(PerforatedGrain):
    """Tbe rod and tube grain resembles a BATES grain except that it features a fully-uninhibited rod of propellant in
    the center of the core."""

    def __init__(self, obj):
        super().__init__(obj)

        self.tubeWeb = None
        self.rodWeb = None

    def simulationSetup(self, config):
        self.tubeWeb = (self._obj.Diameter - self._obj.CoreDiameter) / 2
        self.rodWeb = (self._obj.RodDiameter - self._obj.SupportDiameter) / 2
        self.wallWeb = max(self.tubeWeb, self.rodWeb)

    def getCorePerimeter(self, regDist):
        if regDist < self.tubeWeb:
            tubePerimeter = geometry.circlePerimeter(self._obj.CoreDiameter + (2 * regDist))
        else:
            tubePerimeter = 0
        if regDist < self.rodWeb:
            rodPerimeter = geometry.circlePerimeter(self._obj.RodDiameter - (2 * regDist))
        else:
            rodPerimeter = 0
        return tubePerimeter + rodPerimeter

    def getFaceArea(self, regDist):
        if regDist < self.tubeWeb:
            outer = geometry.circleArea(self._obj.Diameter)
            inner = geometry.circleArea(self._obj.CoreDiameter + (2 * regDist))
            tubeArea = outer - inner
        else:
            tubeArea = 0
        if regDist < self.rodWeb:
            outer = geometry.circleArea(self._obj.RodDiameter - (2 * regDist))
            inner = geometry.circleArea(self._obj.SupportDiameter)
            rodArea = outer - inner
        else:
            rodArea = 0
        return tubeArea + rodArea

    def getDetailsString(self, lengthUnit='m'):
        # return 'Length: {}, Core: {}, Rod: {}'.format(self.props['length'].dispFormat(lengthUnit),
        #                                               self.props['coreDiameter'].dispFormat(lengthUnit),
        #                                               self.props['rodDiameter'].dispFormat(lengthUnit))
        return 'Length: {}, Core: {}, Rod: {}'.format(self._obj.Length,
                                                      self._obj.CoreDiameter,
                                                      self._obj.RodDiameter)

    def getGeometryErrors(self):
        errors = super().getGeometryErrors()
        if self._obj.CoreDiameter == 0:
            errors.append(SimAlert(SimAlertLevel.ERROR, SimAlertType.GEOMETRY, 'Core diameter must not be 0'))
        if self._obj.CoreDiameter >= self._obj.Diameter:
            aText = 'Core diameter must be less than grain diameter'
            errors.append(SimAlert(SimAlertLevel.ERROR, SimAlertType.GEOMETRY, aText))
        if self._obj.RodDiameter >= self._obj.CoreDiameter:
            aText = 'Rod diameter must be less than core diameter'
            errors.append(SimAlert(SimAlertLevel.ERROR, SimAlertType.GEOMETRY, aText))
        return errors

    # These two functions have a lot of code reuse, but it is worth it because making this an fmmGrain would make it
    # signficantly slower
    def getFaceImage(self, mapDim):
        # Normalize core and rod diameters
        coreRadius = (self._obj.CoreDiameter / (0.5 * self._obj.Diameter)) / 2
        rodRadius = (self._obj.RodDiameter / (0.5 * self._obj.Diameter)) / 2
        supportRadius = (self._obj.SupportDiameter / (0.5 * self._obj.Diameter)) / 2

        mapX, mapY = np.meshgrid(np.linspace(-1, 1, mapDim), np.linspace(-1, 1, mapDim))
        mask = np.logical_or(mapX**2 + mapY**2 > 1, mapX**2 + mapY**2 < supportRadius ** 2)
        coreMap = np.ones_like(mapX)

        # Open up core
        coreMap[mapX ** 2 + mapY ** 2 < coreRadius ** 2] = 0
        coreMap[mapX ** 2 + mapY ** 2 < rodRadius ** 2] = 1
        coreMap[mapX ** 2 + mapY ** 2 < supportRadius ** 2] = 0

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
