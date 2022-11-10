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

from Ui.CmdOpenMotor import makeMotor, makePropellant, makePropellantTab, makeGrain

from App.Constants import GRAIN_INHIBITED_NEITHER
from App.Constants import GRAIN_GEOMETRY_BATES

class TestMotorMethods(unittest.TestCase):

    def setUp(self):
        self.Doc = FreeCAD.newDocument("MotorTest")

    def test_calcKN(self):
        tm = makeMotor('Motor')
        tc = tm.Proxy.getMotorConfig()
        self.assertIsNotNone(tc)
        self.assertIsNotNone(tm.Proxy.getNozzle())
        self.assertIsNotNone(tm.Proxy.getGrains())

        bg = makeGrain(GRAIN_GEOMETRY_BATES)
        bg.Diameter = FreeCAD.Units.Quantity("0.083058 m").Value
        bg.Length = FreeCAD.Units.Quantity("0.1397 m").Value
        bg.CoreDiameter = FreeCAD.Units.Quantity("0.05 m").Value
        bg.InhibitedEnds = GRAIN_INHIBITED_NEITHER

        tm.Proxy.addGrain(bg)
        bg.Proxy.simulationSetup(tc)
        tm.Proxy.getNozzle()._obj.Throat = FreeCAD.Units.Quantity("0.01428 m").Value 

        self.assertAlmostEqual(tm.Proxy.calcKN([0], 0), 180, 0)
        self.assertAlmostEqual(tm.Proxy.calcKN([2.5], 0), 183, 0)
        self.assertAlmostEqual(tm.Proxy.calcKN([5], 0), 185, 0)

    def test_calcPressure(self):
        tm = makeMotor('Motor')
        tc = tm.Proxy.getMotorConfig()
        self.assertIsNotNone(tc)
        self.assertIsNotNone(tm.Proxy.getNozzle())
        self.assertIsNotNone(tm.Proxy.getGrains())

        bg = makeGrain(GRAIN_GEOMETRY_BATES)
        bg.Diameter = FreeCAD.Units.Quantity("0.083058 m").Value
        bg.Length = FreeCAD.Units.Quantity("0.1397 m").Value
        bg.CoreDiameter = FreeCAD.Units.Quantity("0.05 m").Value
        bg.InhibitedEnds = GRAIN_INHIBITED_NEITHER

        tm.Proxy.addGrain(bg)
        bg.Proxy.simulationSetup(tc)

        tm.Proxy.getNozzle()._obj.Throat = FreeCAD.Units.Quantity("0.01428 m").Value 

        propellant = makePropellant()
        propellant.PropellantName = 'KNSU'
        propellant.Density = 1890
        tm.Proxy.setPropellant(propellant.Proxy)
        self.assertIsNotNone(tm.Proxy.getPropellant())
        self.assertEqual(tm.Proxy.getPropellant(), propellant.Proxy)

        tab = makePropellantTab()
        tab.a = 0.000101
        tab.n = 0.319
        tab.t = 1720
        tab.m = 41.98
        tab.k = 1.133
        tm.Proxy.getPropellant().addTab(tab)

        self.assertAlmostEqual(tm.Proxy.calcIdealPressure([0], 0), 4050196, 0)
