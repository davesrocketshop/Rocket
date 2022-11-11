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

import math

from scipy.optimize import fsolve

from App.FeatureBase import FeatureBase

from App.Constants import FEATURE_MOTOR_NOZZLE

from App.motor import geometry
from App.motor.simResult import SimAlert, SimAlertLevel, SimAlertType

from DraftTools import translate

def eRatioFromPRatio(k, pRatio):
    """Returns the expansion ratio of a nozzle given the pressure ratio it causes."""
    return (((k+1)/2)**(1/(k-1))) * (pRatio ** (1/k)) * ((((k+1)/(k-1))*(1-(pRatio**((k-1)/k))))**0.5)

class Nozzle(FeatureBase):
    """An object that contains the details about a motor's nozzle."""

    def _initAttributes(self, obj):
        super()._initAttributes(obj)
       
        if not hasattr(obj, 'Throat'):
            obj.addProperty('App::PropertyLength', 'Throat', 'Nozzle', translate('App::Property', 'Throat Diameter')).Throat = 12.7
        if not hasattr(obj, 'Exit'):
            obj.addProperty('App::PropertyLength', 'Exit', 'Nozzle', translate('App::Property', 'Exit Diameter')).Exit = 25.4
        if not hasattr(obj, 'Efficiency'):
            obj.addProperty('App::PropertyFloat', 'Efficiency', 'Nozzle', translate('App::Property', 'Efficiency')).Efficiency = 1.0
        if not hasattr(obj, 'DivAngle'):
            obj.addProperty('App::PropertyAngle', 'DivAngle', 'Nozzle', translate('App::Property', 'Divergence Half Angle')).DivAngle = 15.0
        if not hasattr(obj, 'ConvAngle'):
            obj.addProperty('App::PropertyAngle', 'ConvAngle', 'Nozzle', translate('App::Property', 'Convergence Half Angle')).ConvAngle = 30.0
        if not hasattr(obj, 'ThroatLength'):
            obj.addProperty('App::PropertyLength', 'ThroatLength', 'Nozzle', translate('App::Property', 'Throat Length')).ThroatLength = 0.5
        if not hasattr(obj, 'SlagCoeff'):
            obj.addProperty('App::PropertyFloat', 'SlagCoeff', 'Nozzle', translate('App::Property', 'Slag Buildup Coefficient')).SlagCoeff = 1.0
        if not hasattr(obj, 'ErosionCoeff'):
            obj.addProperty('App::PropertyFloat', 'ErosionCoeff', 'Nozzle', translate('App::Property', 'Throat Erosion Coefficient')).ErosionCoeff = 1.0

    def _initVars(self, obj):
        super()._initVars(obj)

    def featureType(self):
        return FEATURE_MOTOR_NOZZLE

    def getDetailsString(self, lengthUnit='m'):
        """Returns a human-readable string containing some details about the nozzle."""
        return 'Throat: {}'.format(self._obj.Throat)

    def calcExpansion(self):
        """Returns the nozzle's expansion ratio."""
        return float(self._obj.Exit / self._obj.Throat) ** 2

    def getThroatArea(self, dThroat=0):
        """Returns the area of the nozzle's throat. The optional parameter is added on to the nozzle throat diameter
        allow erosion or slag buildup during a burn."""
        return geometry.circleArea(float(self._obj.Throat) + dThroat)

    def getExitArea(self):
        """Return the area of the nozzle's exit."""
        return geometry.circleArea(float(self._obj.Exit))

    def getExitPressure(self, k, inputPressure):
        """Solves for the nozzle's exit pressure, given an input pressure and the gas's specific heat ratio."""
        return fsolve(lambda x: (1/self.calcExpansion()) - eRatioFromPRatio(k, x / inputPressure), 0)[0]

    def getDivergenceLosses(self):
        """Returns nozzle efficiency losses due to divergence angle"""
        divAngleRad = math.radians(float(self._obj.DivAngle))
        return (1 + math.cos(divAngleRad)) / 2

    def getThroatLosses(self, dThroat=0):
        """Returns the losses caused by the throat aspect ratio as described in this document:
        http://rasaero.com/dloads/Departures%20from%20Ideal%20Performance.pdf"""
        throatAspect = float(self._obj.ThroatLength) / (float(self._obj.Throat) + dThroat)
        if throatAspect > 0.45:
            return 0.95
        return 0.99 - (0.0333 * throatAspect)

    def getSkinLosses(self):
        """Returns the losses due to drag on the nozzle surface as described here:
        https://apps.dtic.mil/dtic/tr/fulltext/u2/a099791.pdf. This is a constant for now, as people likely don't have
        a way to measure this themselves."""
        return 0.99

    def getIdealThrustCoeff(self, chamberPres, ambPres, gamma, dThroat, exitPres=None):
        """Calculates C_f, the ideal thrust coefficient for the nozzle, given the propellant's specific heat ratio, the
        ambient and chamber pressures. If nozzle exit presure isn't provided, it will be calculated. dThroat is the 
        change in throat diameter due to erosion or slag accumulation."""
        if chamberPres == 0:
            return 0

        if exitPres is None:
            exitPres = self.getExitPressure(gamma, chamberPres)
        # print("getIdealThrustCoeff: exitPres %g" % (exitPres))
        exitArea = self.getExitArea()
        # print("getIdealThrustCoeff: exitArea %g" % (exitArea))
        throatArea = self.getThroatArea(dThroat)
        # print("getIdealThrustCoeff: throatArea %g" % (throatArea))

        term1 = (2 * (gamma ** 2)) / (gamma - 1)
        term2 = (2 / (gamma + 1)) ** ((gamma + 1) / (gamma - 1))
        term3 = 1 - ((exitPres / chamberPres) ** ((gamma - 1) / gamma))

        momentumThrust = (term1 * term2 * term3) ** 0.5
        # print("getIdealThrustCoeff: momentumThrust %g" % (momentumThrust))
        pressureThrust = ((exitPres - ambPres) * exitArea) / (throatArea * chamberPres)
        # print("getIdealThrustCoeff: pressureThrust %g" % (pressureThrust))

        # print("getIdealThrustCoeff: thrust %g" % (momentumThrust + pressureThrust))
        return momentumThrust + pressureThrust

    def getAdjustedThrustCoeff(self, chamberPres, ambPres, gamma, dThroat, exitPres=None):
        """Calculates adjusted thrust coefficient for the nozzle, given the propellant's specific heat ratio, the
        ambient and chamber pressures. If nozzle exit presure isn't provided, it will be calculated. dThroat is the 
        change in throat diameter due to erosion or slag accumulation. This method uses a combination of the techniques
        described in these resources to adjust the thrust coefficient:
        https://apps.dtic.mil/dtic/tr/fulltext/u2/a099791.pdf
        http://rasaero.com/dloads/Departures%20from%20Ideal%20Performance.pdf"""
        thrustCoeffIdeal = self.getIdealThrustCoeff(chamberPres, ambPres, gamma, dThroat, exitPres)
        divLoss = self.getDivergenceLosses()
        throatLoss = self.getThroatLosses(dThroat)
        skinLoss = self.getSkinLosses()
        efficiency = float(self._obj.Efficiency)
        return divLoss * throatLoss * efficiency * (skinLoss * thrustCoeffIdeal + (1 - skinLoss))

    def getGeometryErrors(self):
        """Returns a list containing any errors with the nozzle's properties."""
        errors = []
        if self._obj.Throat == 0:
            aText = 'Throat diameter must not be 0'
            errors.append(SimAlert(SimAlertLevel.ERROR, SimAlertType.GEOMETRY, aText, 'Nozzle'))
        if self._obj.Exit < self._obj.Throat:
            aText = 'Exit diameter must not be smaller than throat diameter'
            errors.append(SimAlert(SimAlertLevel.ERROR, SimAlertType.GEOMETRY, aText, 'Nozzle'))
        if self._obj.Efficiency == 0:
            aText = 'Efficiency must not be 0'
            errors.append(SimAlert(SimAlertLevel.ERROR, SimAlertType.CONSTRAINT, aText, 'Nozzle'))
        return errors
