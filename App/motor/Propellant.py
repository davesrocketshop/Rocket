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
import Ui

from App.motor.simResult import SimAlert, SimAlertLevel, SimAlertType
from App.Constants import FEATURE_PROPELLANT, FEATURE_PROPELLANT_TAB, FEATURE_VERSION, GAS_CONSTANT

from DraftTools import translate

class PropellantTab:
    """Contains the combustion properties of a propellant over a specified pressure range."""

    def __init__(self, obj):
        super().__init__()

        if not hasattr(obj, 'MinPressure'):
            obj.addProperty('App::PropertyPressure', 'MinPressure', 'Propellant', translate('App::Property', 'Minimum pressure')).MinPressure = 1.0
        if not hasattr(obj, 'MaxPressure'):
            obj.addProperty('App::PropertyPressure', 'MaxPressure', 'Propellant', translate('App::Property', 'Maximum Pressure')).MaxPressure = 1.0
        if not hasattr(obj, 'a'):
            obj.addProperty('App::PropertyQuantity', 'a', 'Propellant', translate('App::Property', 'Burn rate Coefficient')).a = 3.0
            obj.a = FreeCAD.Units.Unit('m/(s*MPa)')
            # obj.addProperty('App::PropertyLength', 'a', 'Propellant', translate('App::Property', 'Burn rate Coefficient')).a = 3.0
        if not hasattr(obj, 'n'):
            obj.addProperty('App::PropertyLength', 'n', 'Propellant', translate('App::Property', 'Burn rate Exponent')).n = 3.0
        if not hasattr(obj, 'k'):
            obj.addProperty('App::PropertyLength', 'k', 'Propellant', translate('App::Property', 'Specific Heat Ratio')).k = 3.0
        if not hasattr(obj, 't'):
            obj.addProperty('App::PropertyQuantity', 't', 'Propellant', translate('App::Property', 'Combustion Temperature')).t = 3.0
            obj.t = FreeCAD.Units.Unit('K')
        if not hasattr(obj, 'm'):
            obj.addProperty('App::PropertyQuantity', 'm', 'Propellant', translate('App::Property', 'Exhaust Molar Mass')).m = 3.0
            obj.m = FreeCAD.Units.Unit('g/mol')

        self.Type = FEATURE_PROPELLANT_TAB
        self._obj = obj
        obj.Proxy=self
        self.version = FEATURE_VERSION

    def onDocumentRestored(self, obj):
        obj.Proxy=self
        
        # Add any missing attributes
        PropellantTab(obj)

        self._obj = obj

    def __getstate__(self):
        return self.version

    def __setstate__(self, state):
        if state:
            self.version = state

    def applyDict(self, dictionary):
        """Makes the motor copy properties from the dictionary that is passed in, which must be formatted like
        the result passed out by 'getDict'"""
        if "minPressure" in dictionary:
            self._obj.MinPressure = FreeCAD.Units.Quantity(str(dictionary['minPressure']) + " Pa").Value
        if "maxPressure" in dictionary:
            self._obj.MaxPressure = FreeCAD.Units.Quantity(str(dictionary['maxPressure']) + " Pa").Value
        if "a" in dictionary:
            self._obj.a = FreeCAD.Units.Quantity(str(dictionary['a']) + " m/(s*MPa)").Value
            # self._obj.a = FreeCAD.Units.Quantity(str(dictionary['a']) + " m").Value
        if "n" in dictionary:
            self._obj.n = dictionary['n']
        if "k" in dictionary:
            self._obj.k = dictionary['k']
        if "t" in dictionary:
            self._obj.t = FreeCAD.Units.Quantity(str(dictionary['t']) + " K").Value
        if "m" in dictionary:
            self._obj.m = FreeCAD.Units.Quantity(str(dictionary['m']) + " g/mol").Value
 

class Propellant:
    """Contains the physical and thermodynamic properties of a propellant formula."""

    def __init__(self, obj):
        super().__init__()

        if not hasattr(obj, 'PropellantName'):
            obj.addProperty('App::PropertyString', 'PropellantName', 'Propellant', translate('App::Property', 'Name')).PropellantName = ""
        if not hasattr(obj, 'Density'):
            obj.addProperty('App::PropertyQuantity', 'Density', 'Propellant', translate('App::Property', 'Density')).Density = 1.0
            obj.Density = FreeCAD.Units.Density
       
        if not hasattr(obj,"Group"):
            obj.addExtension("App::GroupExtensionPython")

        self.Type = FEATURE_PROPELLANT
        self._obj = obj
        obj.Proxy=self
        self.version = FEATURE_VERSION

    def onDocumentRestored(self, obj):
        obj.Proxy=self
        
        # Add any missing attributes
        PropellantTab(obj)

        self._obj = obj

    def getTabs(self):
        return self._obj.Group

    def addTab(self, tab):
        """Adds a set of combustion properties to the propellant"""
        self._obj.addObject(tab)

    def clearTabs(self):
        for tab in self._obj.Group:
            FreeCAD.ActiveDocument.removeObject(tab.Label)

        self._obj.Group = []

    def __getstate__(self):
        return self.version

    def __setstate__(self, state):
        if state:
            self.version = state

    def applyDict(self, dictionary):
        """Makes the motor copy properties from the dictionary that is passed in, which must be formatted like
        the result passed out by 'getDict'"""
        if "name" in dictionary:
            self._obj.PropellantName = dictionary['name']
        if "density" in dictionary:
            self._obj.Density = FreeCAD.Units.Quantity(str(dictionary['density']) + " kg/m^3").Value

        if "tabs" in dictionary:
            tabs = dictionary['tabs']
            for tab in tabs:
                propTab = Ui.CmdOpenMotor.makePropellantTab()
                propTab.Proxy.applyDict(tab)
                self.addTab(propTab)

    def getCStar(self, pressure):
        """Returns the propellant's characteristic velocity."""
        _, _, gamma, temp, molarMass = self.getCombustionProperties(pressure)
        num = (gamma * GAS_CONSTANT / molarMass * temp)**0.5
        denom = gamma * ((2 / (gamma + 1))**((gamma + 1) / (gamma - 1)))**0.5
        return num / denom

    def getBurnRate(self, pressure):
        """Returns the propellant's burn rate for the given pressure"""
        ballA, ballN, _, _, _ = self.getCombustionProperties(pressure)
        print("getBurnRate: a %g, n %g, p %g" % (ballA, ballN, pressure))
        print("getBurnRate: burn rate %g" % (ballA * (pressure ** ballN)))
        return ballA * (pressure ** ballN)

    def getCombustionProperties(self, pressure):
        """Returns the propellant's a, n, gamma, combustion temp and molar mass for a given pressure"""
        closest = {}
        closestPressure = 1e100
        for tab in self._obj.Group:
            if float(tab.MinPressure) < float(pressure) < float(tab.MaxPressure):
                return float(tab.a), float(tab.n), float(tab.k), float(tab.t), float(tab.m)
            if abs(float(pressure) - float(tab.MinPressure)) < closestPressure:
                closest = tab
                closestPressure = abs(float(pressure) - float(tab.MinPressure))
            if abs(float(pressure) - float(tab.MaxPressure)) < closestPressure:
                closest = tab
                closestPressure = abs(float(pressure) - float(tab.MaxPressure))

        return float(closest.a), float(closest.n), float(closest.k), float(closest.t), float(closest.m)

    def getMinimumValidPressure(self):
        """Returns the lowest pressure value with associated combustion properties"""
        return min([tab.MinPressure for tab in self._obj.Group])

    def getMaximumValidPressure(self):
        """Returns the highest pressure value with associated combustion properties"""
        return max([tab.MaxPressure for tab in self._obj.Group])

    def getErrors(self):
        """Checks that all tabs have smaller start pressures than their end pressures, and verifies that no ranges
        overlap."""
        errors = []
        for tabId, tab in enumerate(self._obj.Group):
            if tab.MaxPressure == tab.MinPressure:
                errText = 'Tab #{} has the same minimum and maximum pressures.'.format(tabId + 1)
                errors.append(SimAlert(SimAlertLevel.ERROR, SimAlertType.VALUE, errText, 'Propellant'))
            if tab.MaxPressure < tab.MinPressure:
                errText = 'Tab #{} has reversed pressure limits.'.format(tabId + 1)
                errors.append(SimAlert(SimAlertLevel.ERROR, SimAlertType.VALUE, errText, 'Propellant'))
            for otherTabId, otherTab in enumerate(self._obj.Group):
                if tabId != otherTabId:
                    if otherTab.MinPressure < tab.MaxPressure < otherTab.MaxPressure:
                        err = 'Tabs #{} and #{} have overlapping ranges.'.format(tabId + 1, otherTabId + 1)
                        errors.append(SimAlert(SimAlertLevel.ERROR, SimAlertType.VALUE, err, 'Propellant'))
        return errors

    def getPressureErrors(self, pressure):
        """Returns if the propellant has any errors associated with the supplied pressure such as not having set
        combustion properties"""
        errors = []
        for tab in self._obj.Group:
            if tab.MinPressure < pressure < tab.MaxPressure:
                return errors
        aText = "Chamber pressure deviated from propellant's entered ranges. Results may not be accurate."
        errors.append(SimAlert(SimAlertLevel.WARNING, SimAlertType.VALUE, aText, 'Propellant'))
        return errors
