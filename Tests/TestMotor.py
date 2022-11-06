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

# from App.motor.Motor import Motor, makeMotor
from Ui.CmdOpenMotor import makeMotor, makePropellant, makePropellantTab, makeBatesGrain
from App.motor.MotorConfig import MotorConfig
from App.motor.grains.bates import BatesGrain
from App.motor.Propellant import Propellant, PropellantTab

from App.Constants import GRAIN_INHIBITED_NEITHER

class TestMotorMethods(unittest.TestCase):

    def setUp(self):
        self.Doc = FreeCAD.newDocument("MotorTest")

    def test_calcKN(self):
        tm = makeMotor('Motor')
        tc = tm.Proxy.getMotorConfig()
        self.assertIsNotNone(tc)
        self.assertIsNotNone(tm.Proxy.getNozzle())
        self.assertIsNotNone(tm.Proxy.getGrains())

        bg = makeBatesGrain()
        bg.Diameter = 0.083058
        bg.Length = 0.1397
        bg.CoreDiameter = 0.05
        bg.InhibitedEnds = GRAIN_INHIBITED_NEITHER

        tm.Proxy.addGrain(bg)
        bg.Proxy.simulationSetup(tc)
        tm.Proxy.getNozzle()._obj.Throat = 0.01428

        self.assertAlmostEqual(tm.Proxy.calcKN([0], 0), 180, 0)
        self.assertAlmostEqual(tm.Proxy.calcKN([0.0025], 0), 183, 0)
        self.assertAlmostEqual(tm.Proxy.calcKN([0.005], 0), 185, 0)

    def test_calcPressure(self):
        tm = makeMotor('Motor')
        tc = tm.Proxy.getMotorConfig()
        self.assertIsNotNone(tc)
        self.assertIsNotNone(tm.Proxy.getNozzle())
        self.assertIsNotNone(tm.Proxy.getGrains())

        bg = makeBatesGrain()
        bg.Diameter = 0.083058
        bg.Length = 0.1397
        bg.CoreDiameter = 0.05
        bg.InhibitedEnds = GRAIN_INHIBITED_NEITHER

        tm.Proxy.addGrain(bg)
        bg.Proxy.simulationSetup(tc)

        tm.Proxy.getNozzle()._obj.Throat = 0.01428

        propellant = makePropellant()
        # propellant.Name = 'KNSU'
        propellant.Density = 1890
        # tm.addObject(propellant)
        tm.Proxy.setPropellant(propellant.Proxy)
        self.assertIsNotNone(tm.Proxy.getPropellant())
        self.assertEqual(tm.Proxy.getPropellant(), propellant.Proxy)

        tab = makePropellantTab()
        tab.a = 0.000101
        tab.n = 0.319
        tab.t = 1720
        tab.m = 41.98
        tab.k = 1.133
        tm.Proxy.getPropellant()._obj.addObject(tab)

        self.assertAlmostEqual(tm.Proxy.calcIdealPressure([0], 0), 4050196, 0)
