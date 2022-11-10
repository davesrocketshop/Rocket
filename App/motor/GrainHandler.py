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
from scipy.signal import savgol_filter
from scipy import interpolate

# """Conains the motor class and a supporting configuration property collection."""
# from .grains import grainTypes
# from .nozzle import Nozzle
# from .propellant import Propellant
from . import geometry
from .simResult import SimulationResult, SimAlert, SimAlertLevel, SimAlertType
# from .grains import EndBurningGrain
# from .properties import PropertyCollection, FloatProperty, IntProperty
from abc import abstractmethod

from App.FeatureBase import FeatureBase

from App.Constants import FEATURE_MOTOR_GRAINS, FEATURE_MOTOR_GRAIN
from App.Constants import GRAIN_INHIBITED_NEITHER, GRAIN_INHIBITED_TOP, GRAIN_INHIBITED_BOTTOM, GRAIN_INHIBITED_BOTH


from DraftTools import translate

class GrainHandler:

    def __init__(self, obj):
        self._obj = obj

    def getVolumeSlice(self, regDist, dRegDist):
        """Returns the amount of propellant volume consumed as the grain regresses from a distance of 'regDist' to
        regDist + dRegDist"""
        return self.getVolumeAtRegression(regDist) - self.getVolumeAtRegression(regDist + dRegDist)

    def isWebLeft(self, regDist, burnoutThres=0.00001):
        """Returns True if the grain has propellant left to burn after it has regressed a distance of 'regDist'"""
        return self.getWebLeft(regDist) > burnoutThres

    def getPeakMassFlux(self, massIn, dTime, regDist, dRegDist, density):
        """Uses the grain's mass flux method to return the max. Assumes that it will be at the port of the grain!"""
        return self.getMassFlux(massIn, dTime, regDist, dRegDist, self.getEndPositions(regDist)[1], density)

    def getRegressedLength(self, regDist):
        """Returns the length of the grain when it has regressed a distance of 'regDist', taking any possible
        inhibition into account."""
        endPos = self.getEndPositions(regDist)
        return endPos[1] - endPos[0]

    def getGeometryErrors(self):
        """Returns a list of simAlerts that detail any issues with the geometry of the grain. Errors should be
        used for any condition that prevents simulation of the grain, while warnings can be used to notify the
        user of possible non-fatal mistakes in their entered numbers. Subclasses should still call the superclass
        method, as it performs checks that still apply to its subclasses."""
        errors = []
        if self._obj.Diameter == 0:
            errors.append(SimAlert(SimAlertLevel.ERROR, SimAlertType.GEOMETRY, 'Diameter must not be 0'))
        if self._obj.Length == 0:
            errors.append(SimAlert(SimAlertLevel.ERROR, SimAlertType.GEOMETRY, 'Length must not be 0'))
        return errors

    @abstractmethod
    def getSurfaceAreaAtRegression(self, regDist):
        """Returns the surface area of the grain after it has regressed a linear distance of 'regDist'"""

    @abstractmethod
    def getVolumeAtRegression(self, regDist):
        """Returns the volume of propellant in the grain after it has regressed a linear distance 'regDist'"""

    @abstractmethod
    def getWebLeft(self, regDist):
        """Returns the shortest distance the grain has to regress to burn out"""

    @abstractmethod
    def getMassFlux(self, massIn, dTime, regDist, dRegDist, position, density):
        """Returns the mass flux at a point along the grain. Takes in the mass flow into the grain, a timestep, the
        distance the grain has regressed so far, the additional distance it will regress during the timestep, a
        position along the grain measured from the head end, and the density of the propellant."""

    @abstractmethod
    def getEndPositions(self, regDist):
        """Returns the positions of the grain ends relative to the original (unburned) grain top"""

    @abstractmethod
    def getPortArea(self, regDist):
        """Returns the area of the grain's port when it has regressed a distance of 'regDist'"""

    @abstractmethod
    def simulationSetup(self, config):
        """Do anything needed to prepare this grain for simulation"""

class PerforatedGrain(GrainHandler):
    """A grain with a hole of some shape through the center. Adds abstract methods related to the core to the
    basic grain class """

    def __init__(self, obj):
        super().__init__(obj)
       
        self.wallWeb = 0 # Max distance from the core to the wall

    def getEndPositions(self, regDist):
        if self._obj.InhibitedEnds == GRAIN_INHIBITED_NEITHER: # Neither
            return (regDist, float(self._obj.Length) - regDist)
        if self._obj.InhibitedEnds == GRAIN_INHIBITED_TOP: # Top
            return (0, float(self._obj.Length) - regDist)
        if self._obj.InhibitedEnds == GRAIN_INHIBITED_BOTTOM: # Bottom
            return (regDist, float(self._obj.Length))
        if self._obj.InhibitedEnds == GRAIN_INHIBITED_BOTH:
            return (0, float(self._obj.Length))

        # The enum should prevent this from even being raised, but to cover the case where it somehow gets set wrong
        raise ValueError('Invalid number of faces inhibited')

    @abstractmethod
    def getCorePerimeter(self, regDist):
        """Returns the perimeter of the core after the grain has regressed a distance of 'regDist'."""

    @abstractmethod
    def getFaceArea(self, regDist):
        """Returns the area of the grain face after it has regressed a distance of 'regDist'. This is the
        same as the area of an equal-diameter endburning grain minus the grain's port area."""

    def getCoreSurfaceArea(self, regDist):
        """Returns the surface area of the grain's core after it has regressed a distance of 'regDist'"""
        corePerimeter = self.getCorePerimeter(regDist)
        coreArea = corePerimeter * self.getRegressedLength(regDist)
        return coreArea

    def getWebLeft(self, regDist):
        wallLeft = self.wallWeb - regDist
        if self._obj.InhibitedEnds == GRAIN_INHIBITED_BOTH:
            return wallLeft
        lengthLeft = self.getRegressedLength(regDist)
        return min(lengthLeft, wallLeft)

    def getSurfaceAreaAtRegression(self, regDist):
        faceArea = self.getFaceArea(regDist)
        coreArea = self.getCoreSurfaceArea(regDist)

        exposedFaces = 2
        if self._obj.InhibitedEnds == GRAIN_INHIBITED_TOP or self._obj.InhibitedEnds == GRAIN_INHIBITED_BOTTOM:
            exposedFaces = 1
        if self._obj.InhibitedEnds == GRAIN_INHIBITED_BOTH:
            exposedFaces = 0

        return coreArea + (exposedFaces * faceArea)

    def getVolumeAtRegression(self, regDist):
        faceArea = self.getFaceArea(regDist)
        return faceArea * self.getRegressedLength(regDist)

    def getPortArea(self, regDist):
        faceArea = self.getFaceArea(regDist)
        uncored = geometry.circleArea(self._obj.Diameter)
        return uncored - faceArea

    def getMassFlux(self, massIn, dTime, regDist, dRegDist, position, density):
        diameter = self._obj.Diameter

        endPos = self.getEndPositions(regDist)
        # If a position above the top face is queried, the mass flow is just the input mass and the
        # diameter is the casting tube
        if position < endPos[0]:
            return massIn / geometry.circleArea(diameter)
        # If a position in the grain is queried, the mass flow is the input mass, from the top face,
        # and from the tube up to the point. The diameter is the core.
        if position <= endPos[1]:
            if self._obj.InhibitedEnds in (GRAIN_INHIBITED_TOP, GRAIN_INHIBITED_BOTH):
                top = 0
                countedCoreLength = position
            else:
                top = self.getFaceArea(regDist + dRegDist) * dRegDist * density
                countedCoreLength = position - (endPos[0] + dRegDist)
            # This block gets the mass of propellant the core burns in the step.
            core = ((self.getPortArea(regDist + dRegDist) * countedCoreLength)
                - (self.getPortArea(regDist) * countedCoreLength))
            core *= density

            massFlow = massIn + ((top + core) / dTime)
            return massFlow / self.getPortArea(regDist + dRegDist)
        # A position past the grain end was specified, so the mass flow includes the input mass flow
        # and all mass produced by the grain. Diameter is the casting tube.
        massFlow = massIn + (self.getVolumeSlice(regDist, dRegDist) * density / dTime)
        return massFlow / geometry.circleArea(diameter)

    @abstractmethod
    def getFaceImage(self, mapDim):
        """Returns an image of the grain's cross section, with resolution (mapDim, mapDim)."""

    @abstractmethod
    def getRegressionData(self, mapDim, numContours=15, coreBlack=True):
        """Returns a tuple that includes a grain face image as described in 'getFaceImage', a regression map
        where color maps to regression depth, a list of contours (lists of (x,y) points in image space) of
        equal regression depth, and a list of corresponding contour lengths. The contours are equally spaced
        between 0 regression and burnout."""

class FmmGrain(PerforatedGrain):
    """A grain that uses the fast marching method to calculate its regression. All a subclass has to do is
    provide an implementation of generateCoreMap that makes an image of a cross section of the grain."""

    def __init__(self, obj):
        super().__init__(obj)
       
        self.mapDim = 1001
        self.mapX, self.mapY = None, None
        self.mask = None
        self.coreMap = None
        self.regressionMap = None
        self.faceArea = None

    def normalize(self, value):
        """Transforms real unit quantities into self.mapX, self.mapY coordinates. For use in indexing into the
        coremap."""
        return value / (0.5 * self._obj.Diameter)

    def unNormalize(self, value):
        """Transforms self.mapX, self.mapY coordinates to real unit quantities. Used to determine real lengths in
        coremap."""
        return (value / 2) * self._obj.Diameter

    def lengthToMap(self, value):
        """Converts meters to pixels. Used to compare real distances to pixel distances in the regression map."""
        return self.mapDim * (value / self._obj.Diameter)

    def mapToLength(self, value):
        """Converts pixels to meters. Used to extract real distances from pixel distances such as contour lengths"""
        return self._obj.Diameter * (value / self.mapDim)

    def areaToMap(self, value):
        """Used to convert sqm to sq pixels, like on the regression map."""
        return (self.mapDim ** 2) * (value / (self._obj.Diameter ** 2))

    def mapToArea(self, value):
        """Used to convert sq pixels to sqm. For extracting real areas from the regression map."""
        return (self._obj.Diameter ** 2) * (value / (self.mapDim ** 2))

    def initGeometry(self, mapDim):
        """Set up an empty core map and reset the regression map. Takes in the dimension of both maps."""
        if mapDim < 64:
            raise ValueError('Map dimension must be 64 or larger to get good results')
        self.mapDim = mapDim
        self.mapX, self.mapY = np.meshgrid(np.linspace(-1, 1, self.mapDim), np.linspace(-1, 1, self.mapDim))
        self.mask = self.mapX**2 + self.mapY**2 > 1
        self.coreMap = np.ones_like(self.mapX)
        self.regressionMap = None

    @abstractmethod
    def generateCoreMap(self):
        """Use self.mapX and self.mapY to generate an image of the grain cross section in self.coreMap. A 0 in the image
        means propellant, and a 1 means no propellant."""

    def simulationSetup(self, config):
        mapSize = int(config._obj.MapDimension)

        self.initGeometry(mapSize)
        self.generateCoreMap()
        self.generateRegressionMap()

    def generateRegressionMap(self):
        """Uses the fast marching method to generate an image of how the grain regresses from the core map. The map
        is stored under self.regressionMap."""
        masked = np.ma.MaskedArray(self.coreMap, self.mask)
        cellSize = 1 / self.mapDim
        self.regressionMap = skfmm.distance(masked, dx=cellSize) * 2
        maxDist = np.amax(self.regressionMap)
        self.wallWeb = self.unNormalize(maxDist)
        faceArea = []
        polled = []
        valid = np.logical_not(self.mask)
        for i in range(int(maxDist * self.mapDim) + 2):
            polled.append(i / self.mapDim)
            faceArea.append(self.mapToArea(np.count_nonzero(np.logical_and(self.regressionMap > (i / self.mapDim), valid))))
        self.faceArea = savgol_filter(faceArea, 31, 5)
        self.faceAreaFunc = interpolate.interp1d(polled, self.faceArea)

    def getCorePerimeter(self, regDist):
        mapDist = self.normalize(regDist)

        corePerimeter = 0
        contours = measure.find_contours(self.regressionMap, mapDist, fully_connected='low')
        for contour in contours:
            corePerimeter += self.mapToLength(geometry.length(contour, self.mapDim))

        return corePerimeter

    def getFaceArea(self, regDist):
        mapDist = self.normalize(regDist)
        index = int(mapDist * self.mapDim)
        if index >= len(self.faceArea) - 1:
            return 0 # Past burnout
        return self.faceAreaFunc(mapDist)

    def getFaceImage(self, mapDim):
        self.initGeometry(mapDim)
        self.generateCoreMap()
        masked = np.ma.MaskedArray(self.coreMap, self.mask)
        return masked

    def getRegressionData(self, mapDim, numContours=15, coreBlack=True):
        self.initGeometry(mapDim)
        self.generateCoreMap()

        masked = np.ma.MaskedArray(self.coreMap, self.mask)
        regressionMap = None
        contours = []
        contourLengths = {}

        try:
            self.generateRegressionMap()

            regmax = np.amax(self.regressionMap)

            regressionMap = self.regressionMap[:, :].copy()
            if coreBlack:
                regressionMap[np.where(self.coreMap == 0)] = regmax # Make the core black
            regressionMap = np.ma.MaskedArray(regressionMap, self.mask)

            for dist in np.linspace(0, regmax, numContours):
                contours.append([])
                contourLengths[dist] = 0
                layerContours = measure.find_contours(self.regressionMap, dist, fully_connected='low')
                for contour in layerContours:
                    contours[-1].append(geometry.clean(contour, self.mapDim, 3))
                    contourLengths[dist] += geometry.length(contour, self.mapDim)

        except ValueError as exc: # If there aren't any contours, do nothing
            print(exc)

        return (masked, regressionMap, contours, contourLengths)
