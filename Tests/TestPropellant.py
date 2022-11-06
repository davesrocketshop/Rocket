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

from App.motor.Propellant import Propellant, PropellantTab

from Ui.CmdOpenMotor import makePropellant, makePropellantTab

class TestPropellantMethods(unittest.TestCase):

    def setUp(self):
        self.Doc = FreeCAD.newDocument("PropellantTest")

    def test_proper_propellant_ranges(self):
        props = makePropellant()

        # props.Name = 'TestProp'
        props.Density = 1650

        tab = makePropellantTab()
        tab.MinPressure = 0
        tab.MaxPressure = 6.895e+06
        tab.a = 1.467e-05
        tab.n = 0.382
        tab.t = 3500
        tab.m = 23.67
        tab.k = 1.25
        props.addObject(tab)

        self.assertEqual(len(props.Proxy.getErrors()), 0)

    def test_backwards_pressure_ranges(self):
        props = makePropellant()

        # props.Name = 'TestProp'
        props.Density = 1650

        tab = makePropellantTab()
        tab.MinPressure = 6.895e+06
        tab.MaxPressure = 0
        tab.a = 1.467e-05
        tab.n = 0.382
        tab.t = 3500
        tab.m = 23.67
        tab.k = 1.25
        props.addObject(tab)

        tab = makePropellantTab()
        tab.MinPressure = 6.895e+06
        tab.MaxPressure = 1.379e+07
        tab.a = 1.467e-05
        tab.n = 0.382
        tab.t = 3500
        tab.m = 23.67
        tab.k = 1.25
        props.addObject(tab)

        self.assertIn('Tab #1 has reversed pressure limits.', [err.description for err in props.Proxy.getErrors()])
