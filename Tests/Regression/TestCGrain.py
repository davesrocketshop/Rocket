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
"""Class for testing motors"""

__title__ = "FreeCAD Motor Tests"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"
    
import FreeCAD
import unittest

from Ui.CmdOpenMotor import makeMotor, makePropellantTab, makeGrain

from App.Constants import GRAIN_INHIBITED_NEITHER
from App.Constants import GRAIN_GEOMETRY_C

class colors:
    OK = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def color(string, name):
    return str(name) + string + str(colors.ENDC)

def formatPercent(percent):
    # if percent < 1 / 100:
    #     c = colors.OK
    # elif percent < 5 / 100:
    #     c = colors.WARNING
    # else:
    #     c = colors.FAIL
    # return color(str(round(percent * 100, 3)) + '%', c)
    return str(round(percent * 100, 3)) + '%'

def compareStat(title, a, b):
    error = abs(a - b) / b
    dispError = formatPercent(error)
    print('\t\t' + title + ': ' + str(round(a, 3)) + ' vs ' + str(round(b, 3)) + ' (' + dispError + ')')
    return error

def compareStats(simRes, stats):
    print('\tBasic stats:')
    thrustError = compareStat('Average Thrust', simRes.getAverageForce(), stats['averageThrust'])
    btError = compareStat('Burn Time', simRes.getBurnTime(), stats['burnTime'])
    ispError = compareStat('ISP', simRes.getISP(), stats['isp'])
    propmassError = compareStat('Propellant Mass', simRes.getPropellantMass(), stats['propMass'])
    score = 1 - ((1 - btError) * (1 - ispError) * (1 - propmassError))
    dispScore = formatPercent(score)
    print('\tOverall error: ' + dispScore)
    return score

class TestCGrain(unittest.TestCase):

    def setUp(self):
        self.Doc = FreeCAD.newDocument("CGrainTest")

        tm = makeMotor('Motor')
        self._motor = tm

        tc = tm.Proxy.getMotorConfig()._obj
        # tc.AmbientPressure = 101324.99674500001
        tc.AmbientPressure = FreeCAD.Units.Quantity("101324.99674500001 Pa").Value
        tc.BurnoutThrustThreshold = 0.1 # %
        tc.BurnoutWebThreshold = FreeCAD.Units.Quantity("0.00025400050800101603 m").Value
        tc.MapDimension = 750
        tc.MaxMassFlux = 1406.4697609001405
        tc.MaxPressure = FreeCAD.Units.Quantity("10342500.000000002 Pa").Value
        tc.MinPortThroat = 2.0 # Ratio
        tc.TimeStep = 0.03

        prop = tm.Proxy.getPropellant()._obj
        prop.PropellantName = "MIT - Ocean Water"
        prop.Density = 1650.0

        tab = makePropellantTab()
        tab.MinPressure = 0.0
        tab.MaxPressure = 6895000.0
        tab.a = 1.467e-05
        tab.n = 0.382
        tab.k = 1.25
        tab.t = 3500.0
        tab.m = 23.67
        prop.Proxy.addTab(tab)
        # prop.addTab(tab)

        nozzle = tm.Proxy.getNozzle()._obj
        nozzle.ConvAngle = 65.0
        nozzle.DivAngle = 15.0
        nozzle.Efficiency = 0.9
        nozzle.Exit = 0.012700025400050802
        nozzle.Throat = 0.00444500889001778
        nozzle.ThroatLength = 0.0025400050800101605
        nozzle.SlagCoeff = 0.0
        nozzle.ErosionCoeff = 0.0

        grain = makeGrain(GRAIN_GEOMETRY_C)
        grain.Diameter = 0.030784861569723144
        grain.Length = 0.10160020320040641
        grain.SlotOffset = 0.0031750063500127004
        grain.SlotWidth = 0.004699009398018796
        grain.InhibitedEnds = GRAIN_INHIBITED_NEITHER

        tm.Proxy.addGrain(grain)

    def test_sim(self):
        simRes = self._motor.Proxy.runSimulation()
        self.assertIsNotNone(simRes)
        self.assertEqual(len(simRes.alerts), 0)

        """
        averageThrust: 56
        isp: 198.251
        burnTime: 3.96
        propMass: 0.1148
        """
        # self.assertAlmostEqual(simRes.getAverageForce(), 56, 2)
        # self.assertAlmostEqual(simRes.getISP(), 198.251, 2)
        # self.assertAlmostEqual(simRes.getBurnTime(), 3.96)
        # self.assertAlmostEqual(simRes.getPropellantMass(), 0.1148, 3)

        stats = {
                    'averageThrust': 56,
                    'isp': 198.251,
                    'burnTime': 3.96,
                    'propMass': 0.1148
        }
        score = compareStats(simRes, stats)