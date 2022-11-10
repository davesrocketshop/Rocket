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
from App.Constants import GRAIN_GEOMETRY_END

class EndBurningGrainMethods(unittest.TestCase):

    def setUp(self):
        self.Doc = FreeCAD.newDocument("MotorTest")

    def test_getSurfaceAreaAtRegression(self):
        grain = FreeCAD.ActiveDocument.addObject("Part::FeaturePython","Grain")
        Grain(grain)
        grain.GeometryName = GRAIN_GEOMETRY_END

        grain.Diameter = FreeCAD.Units.Quantity("0.01 m").Value
        grain.Length = FreeCAD.Units.Quantity("0.1 m").Value
        self.assertAlmostEqual(grain.Proxy.getSurfaceAreaAtRegression(0), 78.53981633974483)
        self.assertAlmostEqual(grain.Proxy.getSurfaceAreaAtRegression(50), 78.53981633974483)

        grain.Diameter = FreeCAD.Units.Quantity("0.02 m").Value
        grain.Length = FreeCAD.Units.Quantity("0.1 m").Value
        self.assertAlmostEqual(grain.Proxy.getSurfaceAreaAtRegression(0), 314.1592653589793)
        self.assertAlmostEqual(grain.Proxy.getSurfaceAreaAtRegression(50), 314.1592653589793)

    def test_getVolumeAtRegression(self):
        grain = FreeCAD.ActiveDocument.addObject("Part::FeaturePython","Grain")
        Grain(grain)
        grain.GeometryName = GRAIN_GEOMETRY_END

        grain.Diameter = FreeCAD.Units.Quantity("0.01 m").Value
        grain.Length = FreeCAD.Units.Quantity("0.1 m").Value
        self.assertAlmostEqual(grain.Proxy.getVolumeAtRegression(0), 7853.981633974484)
        self.assertAlmostEqual(grain.Proxy.getVolumeAtRegression(50), 3926.990816987242)

        grain.Diameter = FreeCAD.Units.Quantity("0.02 m").Value
        grain.Length = FreeCAD.Units.Quantity("0.2 m").Value
        self.assertAlmostEqual(grain.Proxy.getVolumeAtRegression(0), 62831.85307179587)
        self.assertAlmostEqual(grain.Proxy.getVolumeAtRegression(50), 47123.889803846906)

    def test_getWebLeft(self):
        grain = FreeCAD.ActiveDocument.addObject("Part::FeaturePython","Grain")
        Grain(grain)
        grain.GeometryName = GRAIN_GEOMETRY_END

        grain.Diameter = FreeCAD.Units.Quantity("0.01 m").Value
        grain.Length = FreeCAD.Units.Quantity("0.1 m").Value
        self.assertAlmostEqual(grain.Proxy.getWebLeft(0), 100)
        self.assertAlmostEqual(grain.Proxy.getWebLeft(50), 100 - 50)

        grain.Diameter = FreeCAD.Units.Quantity("0.01 m").Value
        grain.Length = FreeCAD.Units.Quantity("0.2 m").Value
        self.assertAlmostEqual(grain.Proxy.getWebLeft(0), 200)
        self.assertAlmostEqual(grain.Proxy.getWebLeft(70), 200 - 70)

    def test_getEndPositions(self):
        grain = FreeCAD.ActiveDocument.addObject("Part::FeaturePython","Grain")
        Grain(grain)
        grain.GeometryName = GRAIN_GEOMETRY_END

        grain.Diameter = FreeCAD.Units.Quantity("0.01 m").Value
        grain.Length = FreeCAD.Units.Quantity("0.1 m").Value
        self.assertAlmostEqual(grain.Proxy.getEndPositions(0)[0], 0)
        self.assertAlmostEqual(grain.Proxy.getEndPositions(0)[1], 100)
        self.assertAlmostEqual(grain.Proxy.getEndPositions(50)[0], 0)
        self.assertAlmostEqual(grain.Proxy.getEndPositions(50)[1], 100 - 50)

        grain.Diameter = FreeCAD.Units.Quantity("0.01 m").Value
        grain.Length = FreeCAD.Units.Quantity("0.2 m").Value
        self.assertAlmostEqual(grain.Proxy.getEndPositions(0)[0], 0)
        self.assertAlmostEqual(grain.Proxy.getEndPositions(0)[1], 200)
        self.assertAlmostEqual(grain.Proxy.getEndPositions(70)[0], 0)
        self.assertAlmostEqual(grain.Proxy.getEndPositions(70)[1], 200 - 70)
