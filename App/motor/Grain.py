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

from App.FeatureBase import FeatureBase

from App.motor import geometry
from App.motor.grains import grainTypes

from App.Constants import FEATURE_MOTOR_GRAINS, FEATURE_MOTOR_GRAIN
from App.Constants import GRAIN_INHIBITED_NEITHER, GRAIN_INHIBITED_TOP, GRAIN_INHIBITED_BOTTOM, GRAIN_INHIBITED_BOTH
from App.Constants import GRAIN_GEOMETRY_BATES, GRAIN_GEOMETRY_C, GRAIN_GEOMETRY_CONICAL, GRAIN_GEOMETRY_CUSTOM, GRAIN_GEOMETRY_D, \
        GRAIN_GEOMETRY_END, GRAIN_GEOMETRY_FINOCYL, GRAIN_GEOMETRY_MOONBURNER, GRAIN_GEOMETRY_RODTUBE, GRAIN_GEOMETRY_STAR, GRAIN_GEOMETRY_XCORE


from DraftTools import translate

class Grains(FeatureBase):

    def _initAttributes(self, obj):
        super()._initAttributes(obj)
       
        if not hasattr(obj,"Group"):
            obj.addExtension("App::GroupExtensionPython")

    def _initVars(self, obj):
        super()._initVars(obj)

    def featureType(self):
        return FEATURE_MOTOR_GRAINS

class Grain(FeatureBase):

    def _initAttributes(self, obj):
        super()._initAttributes(obj)
       
        if not hasattr(obj, 'GeometryName'):
            obj.addProperty('App::PropertyEnumeration', 'GeometryName', 'Grain', translate('App::Property', 'Geometry Name')).GeometryName
            obj.GeometryName = [GRAIN_GEOMETRY_BATES, GRAIN_GEOMETRY_C, GRAIN_GEOMETRY_CONICAL, GRAIN_GEOMETRY_CUSTOM, GRAIN_GEOMETRY_D, 
                GRAIN_GEOMETRY_END, GRAIN_GEOMETRY_FINOCYL, GRAIN_GEOMETRY_MOONBURNER, GRAIN_GEOMETRY_RODTUBE, GRAIN_GEOMETRY_STAR, GRAIN_GEOMETRY_XCORE]
            obj.GeometryName = GRAIN_GEOMETRY_BATES
        if not hasattr(obj, 'Length'):
            obj.addProperty('App::PropertyLength', 'Length', 'Grain', translate('App::Property', 'Length of the grain')).Length = 1.0
        if not hasattr(obj, 'Diameter'):
            obj.addProperty('App::PropertyLength', 'Diameter', 'Grain', translate('App::Property', 'Diameter of the grain')).Diameter = 3.0
        if not hasattr(obj, 'InhibitedEnds'):
            obj.addProperty('App::PropertyEnumeration', 'InhibitedEnds', 'Grain', translate('App::Property', 'Inhibited ends'))
            obj.InhibitedEnds = [GRAIN_INHIBITED_NEITHER, GRAIN_INHIBITED_TOP, GRAIN_INHIBITED_BOTTOM, GRAIN_INHIBITED_BOTH]
            obj.InhibitedEnds = GRAIN_INHIBITED_NEITHER
        if not hasattr(obj, 'CoreDiameter'):
            obj.addProperty('App::PropertyLength', 'CoreDiameter', 'Grain', translate('App::Property', 'Core diameter')).CoreDiameter = 1.0
        if not hasattr(obj, 'CoreOffset'):
            obj.addProperty('App::PropertyLength', 'CoreOffset', 'Grain', translate('App::Property', 'Core offset')).CoreOffset = 1.0
        if not hasattr(obj, 'SlotWidth'):
            obj.addProperty('App::PropertyLength', 'SlotWidth', 'Grain', translate('App::Property', 'Slot width')).SlotWidth = 1.0
        if not hasattr(obj, 'SlotLength'):
            obj.addProperty('App::PropertyLength', 'SlotLength', 'Grain', translate('App::Property', 'Slot length')).SlotLength = 1.0
        if not hasattr(obj, 'SlotOffset'):
            obj.addProperty('App::PropertyLength', 'SlotOffset', 'Grain', translate('App::Property', 'Slot offset')).SlotOffset = 0.0
        if not hasattr(obj, 'ForwardCoreDiameter'):
            obj.addProperty('App::PropertyLength', 'ForwardCoreDiameter', 'Grain', translate('App::Property', 'Foreward core diameter')).ForwardCoreDiameter = 1.0
        if not hasattr(obj, 'AftCoreDiameter'):
            obj.addProperty('App::PropertyLength', 'AftCoreDiameter', 'Grain', translate('App::Property', 'Aft core diameter')).AftCoreDiameter = 1.0
        if not hasattr(obj, 'Points'):
            obj.addProperty('App::PropertyVectorList', 'Points', 'Grain', translate('App::Property', 'Core geometry')).Points = []
        if not hasattr(obj, 'DfxUnit'):
            obj.addProperty('App::PropertyEnumeration', 'DfxUnit', 'Grain', translate('App::Property', 'DXF Unit'))
            # obj.DfxUnit = getAllConversions('m')
            obj.DfxUnit = ['m', 'ft']
            obj.DfxUnit = 'm'
        if not hasattr(obj, 'NumFins'):
            obj.addProperty('App::PropertyQuantity', 'NumFins', 'Grain', translate('App::Property', 'Number of fins')).NumFins = 4
        if not hasattr(obj, 'FinWidth'):
            obj.addProperty('App::PropertyLength', 'FinWidth', 'Grain', translate('App::Property', 'Fin width')).FinWidth = 0.25
        if not hasattr(obj, 'FinLength'):
            obj.addProperty('App::PropertyLength', 'FinLength', 'Grain', translate('App::Property', 'Fin length')).FinLength = 0.5
        if not hasattr(obj, 'RodDiameter'):
            obj.addProperty('App::PropertyLength', 'RodDiameter', 'Grain', translate('App::Property', 'Rod diameter')).RodDiameter = 1.0
        if not hasattr(obj, 'SupportDiameter'):
            obj.addProperty('App::PropertyLength', 'SupportDiameter', 'Grain', translate('App::Property', 'Support diameter')).SupportDiameter = 1.0
        if not hasattr(obj, 'NumPoints'):
            obj.addProperty('App::PropertyQuantity', 'NumPoints', 'Grain', translate('App::Property', 'Number of points')).NumPoints = 5
        if not hasattr(obj, 'PointLength'):
            obj.addProperty('App::PropertyLength', 'PointLength', 'Grain', translate('App::Property', 'Point length')).PointLength = 1.0
        if not hasattr(obj, 'PointWidth'):
            obj.addProperty('App::PropertyLength', 'PointWidth', 'Grain', translate('App::Property', 'Point base width')).PointWidth = 1.0

    def _initVars(self, obj):
        super()._initVars(obj)

        self._handler = None

    def onChanged(self, fp, prop):
        '''Reset the handler when the geometry changes'''
        if str(prop) == 'GeometryName':
            self._handler = None

    def _getHandler(self):
        if self._handler is None:
            if self._obj.GeometryName not in grainTypes:
                raise Exception("Unknown grain type " + self._obj.GeometryName)

            constructor = grainTypes[self._obj.GeometryName]
            self._handler = constructor(self._obj)

        return self._handler

    def featureType(self):
        return FEATURE_MOTOR_GRAIN

    def getVolumeSlice(self, regDist, dRegDist):
        """Returns the amount of propellant volume consumed as the grain regresses from a distance of 'regDist' to
        regDist + dRegDist"""
        return self._getHandler().getVolumeSlice(regDist, dRegDist)

    def isWebLeft(self, regDist, burnoutThres=0.00001):
        """Returns True if the grain has propellant left to burn after it has regressed a distance of 'regDist'"""
        return self._getHandler().isWebLeft(regDist, burnoutThres)

    def getPeakMassFlux(self, massIn, dTime, regDist, dRegDist, density):
        """Uses the grain's mass flux method to return the max. Assumes that it will be at the port of the grain!"""
        return self._getHandler().getPeakMassFlux(massIn, dTime, regDist, dRegDist, density)

    def getRegressedLength(self, regDist):
        """Returns the length of the grain when it has regressed a distance of 'regDist', taking any possible
        inhibition into account."""
        return self._getHandler().getRegressedLength(regDist)

    def getGeometryErrors(self):
        """Returns a list of simAlerts that detail any issues with the geometry of the grain. Errors should be
        used for any condition that prevents simulation of the grain, while warnings can be used to notify the
        user of possible non-fatal mistakes in their entered numbers. Subclasses should still call the superclass
        method, as it performs checks that still apply to its subclasses."""
        return self._getHandler().getGeometryErrors()
        # errors = []
        # if self._obj.Diameter == 0:
        #     errors.append(SimAlert(SimAlertLevel.ERROR, SimAlertType.GEOMETRY, 'Diameter must not be 0'))
        # if self._obj.Length == 0:
        #     errors.append(SimAlert(SimAlertLevel.ERROR, SimAlertType.GEOMETRY, 'Length must not be 0'))
        # return errors

    def getDetailsString(self, lengthUnit='m'):
        """Returns a short string describing the grain, formatted using the units that is passed in"""
        return self._getHandler().getDetailsString(lengthUnit)
        # return 'Length: {}'.format(self._obj.Length)

    def getGrainBoundingVolume(self):
        """Returns the volume of the bounding cylinder around the grain"""
        return geometry.cylinderVolume(self._obj.Diameter, self._obj.Length)

    def getFreeVolume(self, regDist):
        """Returns the amount of empty (non-propellant) volume in bounding cylinder of the grain for a given regression
        depth."""
        return float(self.getGrainBoundingVolume() - self.getVolumeAtRegression(regDist))

    def getSurfaceAreaAtRegression(self, regDist):
        """Returns the surface area of the grain after it has regressed a linear distance of 'regDist'"""
        return self._getHandler().getSurfaceAreaAtRegression(regDist)

    def getVolumeAtRegression(self, regDist):
        """Returns the volume of propellant in the grain after it has regressed a linear distance 'regDist'"""
        return self._getHandler().getVolumeAtRegression(regDist)

    def getWebLeft(self, regDist):
        """Returns the shortest distance the grain has to regress to burn out"""
        return self._getHandler().getWebLeft(regDist)

    def getMassFlux(self, massIn, dTime, regDist, dRegDist, position, density):
        """Returns the mass flux at a point along the grain. Takes in the mass flow into the grain, a timestep, the
        distance the grain has regressed so far, the additional distance it will regress during the timestep, a
        position along the grain measured from the head end, and the density of the propellant."""
        return self._getHandler().getMassFlux(massIn, dTime, regDist, dRegDist, position, density)

    def getEndPositions(self, regDist):
        """Returns the positions of the grain ends relative to the original (unburned) grain top"""
        return self._getHandler().getEndPositions(regDist)

    def getPortArea(self, regDist):
        """Returns the area of the grain's port when it has regressed a distance of 'regDist'"""
        return self._getHandler().getPortArea(regDist)

    def simulationSetup(self, config):
        """Do anything needed to prepare this grain for simulation"""
        return self._getHandler().simulationSetup(config)
