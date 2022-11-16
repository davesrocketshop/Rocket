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

from Ui.CmdOpenMotor import makePropellant, makePropellantTab

class TestPropellantMethods(unittest.TestCase):

    def setUp(self):
        self.Doc = FreeCAD.newDocument("PropellantTest")

    def test_proper_propellant_ranges(self):
        props = makePropellant()

        props.PropellantName = 'TestProp'
        props.Density = FreeCAD.Units.Quantity("1650 kg/(m^3)").Value

        tab = makePropellantTab()
        tab.MinPressure = FreeCAD.Units.Quantity("0 Pa").Value
        tab.MaxPressure = FreeCAD.Units.Quantity("6.895e+06 Pa").Value
        tab.a = FreeCAD.Units.Quantity("1.467e-05 m/(s*MPa)").Value
        tab.n = 0.382
        tab.t = FreeCAD.Units.Quantity("3500 K").Value
        tab.m = FreeCAD.Units.Quantity("23.67 g/mol").Value
        tab.k = 1.25
        props.Proxy.addTab(tab)

        self.assertEqual(len(props.Proxy.getErrors()), 0)

    def test_backwards_pressure_ranges(self):
        props = makePropellant()

        props.PropellantName = 'TestProp'
        props.Density = FreeCAD.Units.Quantity("1650 kg/(m^3)").Value

        tab = makePropellantTab()
        tab.MinPressure = FreeCAD.Units.Quantity("6.895e+06 Pa").Value
        tab.MaxPressure = FreeCAD.Units.Quantity("0 Pa").Value
        tab.a = FreeCAD.Units.Quantity("1.467e-05 m/(s*MPa)").Value
        tab.n = 0.382
        tab.t = FreeCAD.Units.Quantity("3500 K").Value
        tab.m = FreeCAD.Units.Quantity("23.67 g/mol").Value
        tab.k = 1.25
        props.Proxy.addTab(tab)

        tab = makePropellantTab()
        tab.MinPressure = FreeCAD.Units.Quantity("6.895e+06 Pa").Value
        tab.MaxPressure = FreeCAD.Units.Quantity("1.379e+07 Pa").Value
        tab.a = FreeCAD.Units.Quantity("1.467e-05 m/(s*MPa)").Value
        tab.n = 0.382
        tab.t = FreeCAD.Units.Quantity("3500 K").Value
        tab.m = FreeCAD.Units.Quantity("23.67 g/mol").Value
        tab.k = 1.25
        props.Proxy.addTab(tab)

        self.assertIn('Tab #1 has reversed pressure limits.', [err.description for err in props.Proxy.getErrors()])
