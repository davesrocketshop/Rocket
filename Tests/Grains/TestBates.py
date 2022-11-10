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
"""Class for testing motor grains"""

__title__ = "FreeCAD Motor Tests"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"
    
import FreeCAD
import unittest

from App.motor.Grain import Grain
from App.motor.simResult import SimAlertLevel, SimAlertType
from App.Constants import GRAIN_GEOMETRY_BATES

class BatesGrainMethods(unittest.TestCase):

    def setUp(self):
        self.Doc = FreeCAD.newDocument("MotorTest")

    def test_getDetailsString(self):
        grain = FreeCAD.ActiveDocument.addObject("Part::FeaturePython","Grain")
        Grain(grain)
        grain.GeometryName = GRAIN_GEOMETRY_BATES
        grain.Diameter = FreeCAD.Units.Quantity("0.05 m").Value
        grain.Length = FreeCAD.Units.Quantity("0.1 m").Value
        grain.CoreDiameter = FreeCAD.Units.Quantity("0.02 m").Value

        self.assertEqual(grain.Proxy.getDetailsString(), 'Length: 0.1 m, Core: 0.02 m')
        self.assertEqual(grain.Proxy.getDetailsString('cm'), 'Length: 10 cm, Core: 2 cm')

    def test_getGeometryErrors(self):
        grain = FreeCAD.ActiveDocument.addObject("Part::FeaturePython","Grain")
        Grain(grain)
        grain.GeometryName = GRAIN_GEOMETRY_BATES
        grain.Diameter = FreeCAD.Units.Quantity("0.05 m").Value
        grain.Length = FreeCAD.Units.Quantity("0.1 m").Value
        grain.CoreDiameter = FreeCAD.Units.Quantity("0.02 m").Value
        self.assertEqual(grain.Proxy.getGeometryErrors(), [])

        grain.Diameter = FreeCAD.Units.Quantity("0.05 m").Value
        grain.Length = FreeCAD.Units.Quantity("0.1 m").Value
        grain.CoreDiameter = FreeCAD.Units.Quantity("0.0 m").Value
        errors = grain.Proxy.getGeometryErrors()
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0].level, SimAlertLevel.ERROR)
        self.assertEqual(errors[0].type, SimAlertType.GEOMETRY)
        self.assertEqual(errors[0].description, 'Core diameter must not be 0')

        grain.Diameter = FreeCAD.Units.Quantity("0.05 m").Value
        grain.Length = FreeCAD.Units.Quantity("0.1 m").Value
        grain.CoreDiameter = FreeCAD.Units.Quantity("0.7 m").Value
        errors = grain.Proxy.getGeometryErrors()
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0].level, SimAlertLevel.ERROR)
        self.assertEqual(errors[0].type, SimAlertType.GEOMETRY)
        self.assertEqual(errors[0].description, 'Core diameter must be less than grain diameter')
