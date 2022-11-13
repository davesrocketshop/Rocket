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

import FreeCAD

from App.Constants import FEATURE_VERSION, FEATURE_MOTOR_CONFIG

from DraftTools import translate

class MotorConfig(object):

    def __init__(self, obj):
        super().__init__()
       
        # Limits
        if not hasattr(obj, 'MaxPressure'):
            obj.addProperty('App::PropertyPressure', 'MaxPressure', 'MotorConfig', translate('App::Property', 'Maximum Allowed Pressure')).MaxPressure = 0 #(0, 0, 7e7, 0)
        if not hasattr(obj, 'MaxMassFlux'):
            obj.addProperty('App::PropertyFloat', 'MaxMassFlux', 'MotorConfig', translate('App::Property', 'Maximum Allowed Mass Flux')).MaxMassFlux = 0 #(0, 0, 1e4, 0)
        if not hasattr(obj, 'MinPortThroat'):
            obj.addProperty('App::PropertyLength', 'MinPortThroat', 'MotorConfig', translate('App::Property', 'Minimum Allowed Port/Throat Ratio')).MinPortThroat = 1 #(1, 1, 4, 0)

        # Simulation
        if not hasattr(obj, 'BurnoutWebThreshold'):
            obj.addProperty('App::PropertyFloat', 'BurnoutWebThreshold', 'MotorConfig', translate('App::Property', 'Web Burnout Threshold')).BurnoutWebThreshold = 2.54e-5 #(2.54e-5, 2.54e-5, 3.175e-3, 0)
        if not hasattr(obj, 'BurnoutThrustThreshold'):
            obj.addProperty('App::PropertyFloat', 'BurnoutThrustThreshold', 'MotorConfig', translate('App::Property', 'Thrust Burnout Threshold')).BurnoutThrustThreshold = 0.01 #(0.01, 0.01, 10, 0)
        if not hasattr(obj, 'TimeStep'):
            obj.addProperty('App::PropertyFloat', 'TimeStep', 'MotorConfig', translate('App::Property', 'Simulation Timestep')).TimeStep = 0.0001 #(0.0001, 0.0001, 0.1, 0)
        if not hasattr(obj, 'AmbientPressure'):
            obj.addProperty('App::PropertyPressure', 'AmbientPressure', 'MotorConfig', translate('App::Property', 'Ambient Pressure')).AmbientPressure = 0.0001 # (0.0001, 0.0001, 10200, 0)
        if not hasattr(obj, 'MapDimension'):
            obj.addProperty('App::PropertyInteger', 'MapDimension', 'MotorConfig', translate('App::Property', 'Grain Map Dimension')).MapDimension = 250 #(250, 250, 2000, 1)

        self.Type = FEATURE_MOTOR_CONFIG
        self._obj = obj
        obj.Proxy=self
        self.version = FEATURE_VERSION

    def onDocumentRestored(self, obj):
        obj.Proxy=self
        
        # Add any missing attributes
        MotorConfig(obj)

        self._obj = obj
        self._parent = None

    def __getstate__(self):
        return self.version

    def __setstate__(self, state):
        if state:
            self.version = state

    def applyDict(self, dictionary):
        """Makes the motor copy properties from the dictionary that is passed in, which must be formatted like
        the result passed out by 'getDict'"""
        if "maxPressure" in dictionary:
            self._obj.MaxPressure = FreeCAD.Units.Quantity(str(dictionary['maxPressure']) + " Pa").Value
        if "maxMassFlux" in dictionary:
            self._obj.MaxMassFlux = dictionary['maxMassFlux']
        if "minPortThroat" in dictionary:
            self._obj.MinPortThroat = dictionary['minPortThroat']
        if "burnoutWebThres" in dictionary:
            self._obj.BurnoutWebThreshold = FreeCAD.Units.Quantity(str(dictionary['burnoutWebThres']) + " m").Value
        if "burnoutThrustThres" in dictionary:
            self._obj.BurnoutThrustThreshold = dictionary['burnoutThrustThres']
        if "timestep" in dictionary:
            self._obj.TimeStep = dictionary['timestep']
        if "ambPressure" in dictionary:
            self._obj.AmbientPressure = FreeCAD.Units.Quantity(str(dictionary['ambPressure']) + " Pa").Value
        if "mapDim" in dictionary:
            self._obj.MapDimension = dictionary['mapDim']

    def getMaxPressure(self):
        return self._obj.MaxPressure

    def getMaxMassFlux(self):
        return self._obj.MaxMassFlux

    def getMinPortThroat(self):
        return self._obj.MinPortThroat

    def getBurnoutWebThreshold(self):
        return self._obj.BurnoutWebThreshold

    def getBurnoutThrustThreshold(self):
        return self._obj.BurnoutThrustThreshold

    def getTimeStep(self):
        return self._obj.TimeStep

    def getAmbientPressure(self):
        return self._obj.AmbientPressure

    def getMapDimension(self):
        return self._obj.MapDimension
