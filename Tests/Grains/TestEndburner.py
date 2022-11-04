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

from App.motor.grains.endBurner import EndBurningGrain
from App.motor.simResult import SimAlertLevel, SimAlertType

class EndBurningGrainMethods(unittest.TestCase):

    def setUp(self):
        self.Doc = FreeCAD.newDocument("MotorTest")

    def test_getSurfaceAreaAtRegression(self):
        grain = FreeCAD.ActiveDocument.addObject("Part::FeaturePython","Grain")
        EndBurningGrain(grain)

        grain.Diameter = 0.01
        grain.Length = 0.1
        self.assertAlmostEqual(grain.Proxy.getSurfaceAreaAtRegression(0), 7.853981633974483e-05)
        self.assertAlmostEqual(grain.Proxy.getSurfaceAreaAtRegression(0.05), 7.853981633974483e-05)

        grain.Diameter = 0.02
        grain.Length = 0.1
        self.assertAlmostEqual(grain.Proxy.getSurfaceAreaAtRegression(0), 0.0003141592653589793)
        self.assertAlmostEqual(grain.Proxy.getSurfaceAreaAtRegression(0.05), 0.0003141592653589793)

    def test_getVolumeAtRegression(self):
        grain = FreeCAD.ActiveDocument.addObject("Part::FeaturePython","Grain")
        EndBurningGrain(grain)

        grain.Diameter = 0.01
        grain.Length = 0.1
        self.assertAlmostEqual(grain.Proxy.getVolumeAtRegression(0), 7.853981633974484e-06)
        self.assertAlmostEqual(grain.Proxy.getVolumeAtRegression(0.05), 3.926990816987242e-06)

        grain.Diameter = 0.02
        grain.Length = 0.2
        self.assertAlmostEqual(grain.Proxy.getVolumeAtRegression(0), 6.283185307179587e-05)
        self.assertAlmostEqual(grain.Proxy.getVolumeAtRegression(0.05), 4.7123889803846906e-05)

    def test_getWebLeft(self):
        grain = FreeCAD.ActiveDocument.addObject("Part::FeaturePython","Grain")
        EndBurningGrain(grain)

        grain.Diameter = 0.01
        grain.Length = 0.1
        self.assertAlmostEqual(grain.Proxy.getWebLeft(0), 0.1)
        self.assertAlmostEqual(grain.Proxy.getWebLeft(0.05), 0.1 - 0.05)

        grain.Diameter = 0.01
        grain.Length = 0.2
        self.assertAlmostEqual(grain.Proxy.getWebLeft(0), 0.2)
        self.assertAlmostEqual(grain.Proxy.getWebLeft(0.07), 0.2 - 0.07)

    def test_getEndPositions(self):
        grain = FreeCAD.ActiveDocument.addObject("Part::FeaturePython","Grain")
        EndBurningGrain(grain)

        grain.Diameter = 0.01
        grain.Length = 0.1
        self.assertAlmostEqual(grain.Proxy.getEndPositions(0), (0, 0.1))
        self.assertAlmostEqual(grain.Proxy.getEndPositions(0.05), (0, 0.1 - 0.05))

        grain.Diameter = 0.01
        grain.Length = 0.2
        self.assertAlmostEqual(grain.Proxy.getEndPositions(0), (0, 0.2))
        self.assertAlmostEqual(grain.Proxy.getEndPositions(0.07), (0, 0.2 - 0.07))
