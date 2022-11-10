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
from App.Constants import GRAIN_INHIBITED_BOTH
from App.Constants import GRAIN_GEOMETRY_CONICAL

class ConicalGrainMethods(unittest.TestCase):

    def setUp(self):
        self.Doc = FreeCAD.newDocument("MotorTest")

    def test_isCoreInverted(self):
        inverted = FreeCAD.ActiveDocument.addObject("Part::FeaturePython","Grain")
        Grain(inverted)
        inverted.GeometryName = GRAIN_GEOMETRY_CONICAL
        inverted.Diameter = FreeCAD.Units.Quantity("0.01 m").Value
        inverted.Length = FreeCAD.Units.Quantity("0.1 m").Value
        inverted.ForwardCoreDiameter = FreeCAD.Units.Quantity("0.0025 m").Value
        inverted.AftCoreDiameter = FreeCAD.Units.Quantity("0.002 m").Value

        regular = FreeCAD.ActiveDocument.addObject("Part::FeaturePython","Grain")
        Grain(regular)
        regular.GeometryName = GRAIN_GEOMETRY_CONICAL
        regular.Diameter = FreeCAD.Units.Quantity("0.01 m").Value
        regular.Length = FreeCAD.Units.Quantity("0.1 m").Value
        regular.ForwardCoreDiameter = FreeCAD.Units.Quantity("0.003 m").Value
        regular.AftCoreDiameter = FreeCAD.Units.Quantity("0.004 m").Value

        self.assertEqual(inverted.Proxy._getHandler().isCoreInverted(), True)
        self.assertEqual(regular.Proxy._getHandler().isCoreInverted(), False)

    def test_getFrustumInfo(self):
        properties = {
            'length': 0.1,
            'diameter': 0.01,
            'forwardCoreDiameter': 0.0025,
            'aftCoreDiameter': 0.002,
            'inhibitedEnds': 'Both'
        }

        testGrain = FreeCAD.ActiveDocument.addObject("Part::FeaturePython","Grain")
        Grain(testGrain)
        testGrain.GeometryName = GRAIN_GEOMETRY_CONICAL
        testGrain.Diameter = FreeCAD.Units.Quantity("{} m".format(properties['diameter'])).Value
        testGrain.Length = FreeCAD.Units.Quantity("{} m".format(properties['length'])).Value
        testGrain.ForwardCoreDiameter = FreeCAD.Units.Quantity("{} m".format(properties['forwardCoreDiameter'])).Value
        testGrain.AftCoreDiameter = FreeCAD.Units.Quantity("{} m".format(properties['aftCoreDiameter'])).Value
        testGrain.InhibitedEnds = GRAIN_INHIBITED_BOTH

        unregressed = testGrain.Proxy._getHandler().getFrustumInfo(0)
        self.assertAlmostEqual(unregressed[0], 1000.0 * properties['aftCoreDiameter'])
        self.assertAlmostEqual(unregressed[1], 1000.0 * properties['forwardCoreDiameter'])
        self.assertAlmostEqual(unregressed[2], 1000.0 * properties['length'])

        # beforeHittingWall = testGrain.Proxy._getHandler().getFrustumInfo(0.001)
        beforeHittingWall = testGrain.Proxy._getHandler().getFrustumInfo(1)
        self.assertAlmostEqual(beforeHittingWall[0], 3.999993750029297)
        self.assertAlmostEqual(beforeHittingWall[1], 4.499993750029296)
        self.assertAlmostEqual(beforeHittingWall[2], 1000.0 * properties['length']) # Length hasn't changed yet

        hitWall = testGrain.Proxy._getHandler().getFrustumInfo(3.8)
        self.assertAlmostEqual(hitWall[0], 9.599976250111327)
        self.assertAlmostEqual(hitWall[1], 1000.0 * properties['diameter']) # This end has burned all the way to the wall
        self.assertAlmostEqual(hitWall[2], 80.00468749267584)

    def test_getSurfaceAreaAtRegression(self):
        properties = {
            'length': 0.1,
            'diameter': 0.01,
            'forwardCoreDiameter': 0.0025,
            'aftCoreDiameter': 0.002,
            'inhibitedEnds': 'Both'
        }

        forwardFaceArea = 7.36310778e-05
        aftFaceArea = 7.53982236e-05
        lateralArea = 706.86055598659

        testGrain = FreeCAD.ActiveDocument.addObject("Part::FeaturePython","Grain")
        Grain(testGrain)
        testGrain.GeometryName = GRAIN_GEOMETRY_CONICAL
        testGrain.Diameter = FreeCAD.Units.Quantity("{} m".format(properties['diameter'])).Value
        testGrain.Length = FreeCAD.Units.Quantity("{} m".format(properties['length'])).Value
        testGrain.ForwardCoreDiameter = FreeCAD.Units.Quantity("{} m".format(properties['forwardCoreDiameter'])).Value
        testGrain.AftCoreDiameter = FreeCAD.Units.Quantity("{} m".format(properties['aftCoreDiameter'])).Value
        testGrain.InhibitedEnds = GRAIN_INHIBITED_BOTH

        self.assertAlmostEqual(testGrain.Proxy.getSurfaceAreaAtRegression(0), lateralArea)
        self.assertAlmostEqual(testGrain.Proxy.getSurfaceAreaAtRegression(1), 1335.1790867045452)

        # For when uninibited conical grains work:
        """testGrain.setProperty('inhibitedEnds', 'Top')
        self.assertAlmostEqual(testGrain.getSurfaceAreaAtRegression(0), lateralArea + aftFaceArea)

        testGrain.setProperty('inhibitedEnds', 'Bottom')
        self.assertAlmostEqual(testGrain.getSurfaceAreaAtRegression(0), lateralArea + forwardFaceArea)

        testGrain.setProperty('inhibitedEnds', 'Neither')
        self.assertAlmostEqual(testGrain.getSurfaceAreaAtRegression(0), lateralArea + forwardFaceArea + aftFaceArea)"""

    def test_getVolumeAtRegression(self):
        properties = {
            'length': 0.1,
            'diameter': 0.01,
            'forwardCoreDiameter': 0.0025,
            'aftCoreDiameter': 0.002,
            'inhibitedEnds': 'Both'
        }

        testGrain = FreeCAD.ActiveDocument.addObject("Part::FeaturePython","Grain")
        Grain(testGrain)
        testGrain.GeometryName = GRAIN_GEOMETRY_CONICAL
        testGrain.Diameter = FreeCAD.Units.Quantity("{} m".format(properties['diameter'])).Value
        testGrain.Length = FreeCAD.Units.Quantity("{} m".format(properties['length'])).Value
        testGrain.ForwardCoreDiameter = FreeCAD.Units.Quantity("{} m".format(properties['forwardCoreDiameter'])).Value
        testGrain.AftCoreDiameter = FreeCAD.Units.Quantity("{} m".format(properties['aftCoreDiameter'])).Value
        testGrain.InhibitedEnds = GRAIN_INHIBITED_BOTH

        self.assertAlmostEqual(testGrain.Proxy.getVolumeAtRegression(0), 7.454737567580781e3)
        self.assertAlmostEqual(testGrain.Proxy.getVolumeAtRegression(1), 6.433724127569215e3)
        self.assertAlmostEqual(testGrain.Proxy.getVolumeAtRegression(3.8), 2.480054353678591e2)

    def test_getWebLeft(self):
        properties = {
            'length': 0.1,
            'diameter': 0.01,
            'forwardCoreDiameter': 0.0025,
            'aftCoreDiameter': 0.002,
            'inhibitedEnds': 'Both'
        }

        testGrain = FreeCAD.ActiveDocument.addObject("Part::FeaturePython","Grain")
        Grain(testGrain)
        testGrain.GeometryName = GRAIN_GEOMETRY_CONICAL
        testGrain.Diameter = FreeCAD.Units.Quantity("{} m".format(properties['diameter'])).Value
        testGrain.Length = FreeCAD.Units.Quantity("{} m".format(properties['length'])).Value
        testGrain.ForwardCoreDiameter = FreeCAD.Units.Quantity("{} m".format(properties['forwardCoreDiameter'])).Value
        testGrain.AftCoreDiameter = FreeCAD.Units.Quantity("{} m".format(properties['aftCoreDiameter'])).Value
        testGrain.InhibitedEnds = GRAIN_INHIBITED_BOTH

        self.assertAlmostEqual(testGrain.Proxy.getWebLeft(0), 4.0)
        self.assertAlmostEqual(testGrain.Proxy.getWebLeft(1), 3.0, 4)
        self.assertAlmostEqual(testGrain.Proxy.getWebLeft(3.8), 0.2, 4)

        testGrain.ForwardCoreDiameter = FreeCAD.Units.Quantity("0.002 m").Value
        testGrain.AftCoreDiameter = FreeCAD.Units.Quantity("0.0025 m").Value
        self.assertAlmostEqual(testGrain.Proxy.getWebLeft(0), 4.0)
        self.assertAlmostEqual(testGrain.Proxy.getWebLeft(1), 3.0, 4)
        self.assertAlmostEqual(testGrain.Proxy.getWebLeft(3.8), 0.2, 4)
