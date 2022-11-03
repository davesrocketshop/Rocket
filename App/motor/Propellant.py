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
            obj.addProperty('App::PropertyLength', 'a', 'Propellant', translate('App::Property', 'Burn rate Coefficient')).a = 3.0
        if not hasattr(obj, 'n'):
            obj.addProperty('App::PropertyLength', 'n', 'Propellant', translate('App::Property', 'Burn rate Exponent')).n = 3.0
        if not hasattr(obj, 'k'):
            obj.addProperty('App::PropertyLength', 'k', 'Propellant', translate('App::Property', 'Specific Heat Ratio')).k = 3.0
        if not hasattr(obj, 't'):
            obj.addProperty('App::PropertyLength', 't', 'Propellant', translate('App::Property', 'Combustion Temperature')).t = 3.0
        if not hasattr(obj, 'm'):
            obj.addProperty('App::PropertyLength', 'm', 'Propellant', translate('App::Property', 'Exhaust Molar Mass')).m = 3.0

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
 

class Propellant:
    """Contains the physical and thermodynamic properties of a propellant formula."""

    def __init__(self, obj):
        super().__init__()

        if not hasattr(obj, 'Name'):
            obj.addProperty('App::PropertyString', 'Name', 'Propellant', translate('App::Property', 'Name')).Name = ""
        if not hasattr(obj, 'Density'):
            obj.addProperty('App::PropertyFloat', 'Density', 'Propellant', translate('App::Property', 'Density')).Density = 1.0
       
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

    def __getstate__(self):
        return self.version

    def __setstate__(self, state):
        if state:
            self.version = state

    def getCStar(self, pressure):
        """Returns the propellant's characteristic velocity."""
        _, _, gamma, temp, molarMass = self.getCombustionProperties(pressure)
        num = (gamma * GAS_CONSTANT / molarMass * temp)**0.5
        denom = gamma * ((2 / (gamma + 1))**((gamma + 1) / (gamma - 1)))**0.5
        return num / denom

    def getBurnRate(self, pressure):
        """Returns the propellant's burn rate for the given pressure"""
        ballA, ballN, _, _, _ = self.getCombustionProperties(pressure)
        return ballA * (pressure ** ballN)

    def getCombustionProperties(self, pressure):
        """Returns the propellant's a, n, gamma, combustion temp and molar mass for a given pressure"""
        closest = {}
        closestPressure = 1e100
        for tab in self._obj.Group:
            if tab.MinPressure < pressure < tab.MaxPressure:
                return tab.a, tab.n, tab.k, tab.t, tab.m
            if abs(pressure - tab.MinPressure) < closestPressure:
                closest = tab
                closestPressure = abs(pressure - tab.MinPressure)
            if abs(pressure - tab.MaxPressure) < closestPressure:
                closest = tab
                closestPressure = abs(pressure - tab.MaxPressure)

        return closest.a, closest.n, closest.k, closest.t, closest.m

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
        for tabId, tab in enumerate(self.getProperty('tabs')):
            if tab.MaxPressure == tab.MinPressure:
                errText = 'Tab #{} has the same minimum and maximum pressures.'.format(tabId + 1)
                errors.append(SimAlert(SimAlertLevel.ERROR, SimAlertType.VALUE, errText, 'Propellant'))
            if tab.MaxPressure < tab.MinPressure:
                errText = 'Tab #{} has reversed pressure limits.'.format(tabId + 1)
                errors.append(SimAlert(SimAlertLevel.ERROR, SimAlertType.VALUE, errText, 'Propellant'))
            for otherTabId, otherTab in enumerate(self.getProperty('tabs')):
                if tabId != otherTabId:
                    if othertab.MinPressure < tab.MaxPressure < othertab.MaxPressure:
                        err = 'Tabs #{} and #{} have overlapping ranges.'.format(tabId + 1, otherTabId + 1)
                        errors.append(SimAlert(SimAlertLevel.ERROR, SimAlertType.VALUE, err, 'Propellant'))
        return errors

    def getPressureErrors(self, pressure):
        """Returns if the propellant has any errors associated with the supplied pressure such as not having set
        combustion properties"""
        errors = []
        for tab in self.getProperty('tabs'):
            if tab.MinPressure < pressure < tab.MaxPressure:
                return errors
        aText = "Chamber pressure deviated from propellant's entered ranges. Results may not be accurate."
        errors.append(SimAlert(SimAlertLevel.WARNING, SimAlertType.VALUE, aText, 'Propellant'))
        return errors

    def addTab(self, tab):
        """Adds a set of combustion properties to the propellant"""
        self.props['tabs'].addTab(tab)
