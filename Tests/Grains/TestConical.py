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
        inverted.Diameter = 0.01
        inverted.Length = 0.1
        inverted.ForwardCoreDiameter = 0.0025
        inverted.AftCoreDiameter = 0.002

        regular = FreeCAD.ActiveDocument.addObject("Part::FeaturePython","Grain")
        Grain(regular)
        regular.GeometryName = GRAIN_GEOMETRY_CONICAL
        regular.Diameter = 0.01
        regular.Length = 0.1
        regular.ForwardCoreDiameter = 0.003
        regular.AftCoreDiameter = 0.004

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
        testGrain.Diameter = properties['diameter']
        testGrain.Length = properties['length']
        testGrain.ForwardCoreDiameter = properties['forwardCoreDiameter']
        testGrain.AftCoreDiameter = properties['aftCoreDiameter']
        testGrain.InhibitedEnds = GRAIN_INHIBITED_BOTH

        unregressed = testGrain.Proxy._getHandler().getFrustumInfo(0)
        self.assertAlmostEqual(unregressed[0], properties['aftCoreDiameter'])
        self.assertAlmostEqual(unregressed[1], properties['forwardCoreDiameter'])
        self.assertAlmostEqual(unregressed[2], properties['length'])

        beforeHittingWall = testGrain.Proxy._getHandler().getFrustumInfo(0.001)
        self.assertAlmostEqual(beforeHittingWall[0], 0.003999993750029297)
        self.assertAlmostEqual(beforeHittingWall[1], 0.004499993750029296)
        self.assertAlmostEqual(beforeHittingWall[2], properties['length']) # Length hasn't changed yet

        hitWall = testGrain.Proxy._getHandler().getFrustumInfo(0.0038)
        self.assertAlmostEqual(hitWall[0], 0.009599976250111327)
        self.assertAlmostEqual(hitWall[1], properties['diameter']) # This end has burned all the way to the wall
        self.assertAlmostEqual(hitWall[2], 0.08000468749267584)

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
        lateralArea = 0.00070686055598659

        testGrain = FreeCAD.ActiveDocument.addObject("Part::FeaturePython","Grain")
        Grain(testGrain)
        testGrain.GeometryName = GRAIN_GEOMETRY_CONICAL
        testGrain.Diameter = properties['diameter']
        testGrain.Length = properties['length']
        testGrain.ForwardCoreDiameter = properties['forwardCoreDiameter']
        testGrain.AftCoreDiameter = properties['aftCoreDiameter']
        testGrain.InhibitedEnds = GRAIN_INHIBITED_BOTH

        self.assertAlmostEqual(testGrain.Proxy.getSurfaceAreaAtRegression(0), lateralArea)
        self.assertAlmostEqual(testGrain.Proxy.getSurfaceAreaAtRegression(0.001), 0.0013351790867045452)

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
        testGrain.Diameter = properties['diameter']
        testGrain.Length = properties['length']
        testGrain.ForwardCoreDiameter = properties['forwardCoreDiameter']
        testGrain.AftCoreDiameter = properties['aftCoreDiameter']
        testGrain.InhibitedEnds = GRAIN_INHIBITED_BOTH

        self.assertAlmostEqual(testGrain.Proxy.getVolumeAtRegression(0), 7.454737567580781e-06)
        self.assertAlmostEqual(testGrain.Proxy.getVolumeAtRegression(0.001), 6.433724127569215e-06)
        self.assertAlmostEqual(testGrain.Proxy.getVolumeAtRegression(0.0038), 2.480054353678591e-07)

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
        testGrain.Diameter = properties['diameter']
        testGrain.Length = properties['length']
        testGrain.ForwardCoreDiameter = properties['forwardCoreDiameter']
        testGrain.AftCoreDiameter = properties['aftCoreDiameter']
        testGrain.InhibitedEnds = GRAIN_INHIBITED_BOTH

        self.assertAlmostEqual(testGrain.Proxy.getWebLeft(0), 0.004)
        self.assertAlmostEqual(testGrain.Proxy.getWebLeft(0.001), 0.003)
        self.assertAlmostEqual(testGrain.Proxy.getWebLeft(0.0038), 0.0002)

        testGrain.ForwardCoreDiameter = 0.002
        testGrain.AftCoreDiameter = 0.0025
        self.assertAlmostEqual(testGrain.Proxy.getWebLeft(0), 0.004)
        self.assertAlmostEqual(testGrain.Proxy.getWebLeft(0.001), 0.003)
        self.assertAlmostEqual(testGrain.Proxy.getWebLeft(0.0038), 0.0002)
