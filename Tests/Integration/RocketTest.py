# ***************************************************************************
# *   Copyright (c) 2022-2025 David Carter <dcarter@davidcarter.ca>         *
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
"""Class for testing rockets"""

__title__ = "FreeCAD Rocket Tests"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

import FreeCAD
import unittest

from Rocket.util.Coordinate import Coordinate

from Tests.util.TestRockets import TestRockets
from Tests.util.Utilities import assertCoordinateEqual

# Component indexes
STAGE1 = 0
STAGE1_NOSE = 1
STAGE1_BODY = 2
STAGE1_FINS = 3
STAGE1_LUG = 4
STAGE1_ENGINE_MOUNT = 5
STAGE1_ENGINE_BLOCK = 6
STAGE1_CR = 7
STAGE2 = 8
STAGE2_BODY = 9
STAGE2_FINS = 10
STAGE3 = 11
STAGE3_FINCAN = 12

class RocketTest(unittest.TestCase):

    def setUp(self):
        self.Doc = FreeCAD.newDocument("RocketTest")

    def tearDown(self):
        # FreeCAD.closeDocument(self.Doc.Name)
        ...

    def getStage(self, rocket, stageNumber):
        return rocket.getChild(stageNumber).Proxy

    def testEstesAlphaIII(self):
        rocket = TestRockets.makeEstesAlphaIII()
        stage = self.getStage(rocket, 0)

        nose = stage.getChild(0).Proxy
        expected = Coordinate(0.0,0,0)
        actual = nose.getPositionAsCoordinate()
        assertCoordinateEqual(self, actual, expected, nose.getName() + " not positioned correctly")

        body = stage.getChild(1).Proxy
        expected = Coordinate(70.0,0,0)
        actual = body.getPositionAsCoordinate()
        assertCoordinateEqual(self, actual, expected, body.getName() + " not positioned correctly")

        fins = body.getChild(0).Proxy
        self.assertTrue(fins.isFinSet(), fins.getName()+" is not a fin set")
        self.assertEqual(fins.getFinCount(), 3, fins.getName()+" have incorrect count")
        expected = Coordinate(220.0,0,0)
        actual = fins.getPositionAsCoordinate()
        assertCoordinateEqual(self, actual, expected, fins.getName()+" not positioned correctly")

        lugs = body.getChild(1).Proxy
        self.assertEqual(lugs.getInstanceCount(), 1, lugs.getName()+" have incorrect count")
        # actLocs = lugs.getComponentLocations()
        expected = Coordinate(181.0, 0.0, 14.2)
        actual = lugs.getPositionAsCoordinate()
        assertCoordinateEqual(self, actual, expected, lugs.getName()+" not positioned correctly")

        mmt = body.getChild(2).Proxy
        # expLoc = Coordinate(203.0,0,0)
        expected = Coordinate(203.0,0,0)
        actual = mmt.getPositionAsCoordinate()
        assertCoordinateEqual(self, actual, expected, mmt.getName()+" not positioned correctly")

        block = mmt.getChild(0).Proxy
        expected = Coordinate(203.0,0,0)
        actual = block.getPositionAsCoordinate()
        assertCoordinateEqual(self, actual, expected, block.getName()+" not positioned correctly")

        ring = body.getChild(3).Proxy
        self.assertEqual(ring.getInstanceCount(), 2, ring.getName()+" have incorrect count")

        # singleton instances follow different code paths
        ring.setInstanceCount(1)
        self.assertEqual(ring.getInstanceCount(), 1, ring.getName()+" have incorrect count")
        # expLoc = Coordinate(210.0,0,0)
        expected = Coordinate(210.0,0,0)
        actual = ring.getPositionAsCoordinate()
        assertCoordinateEqual(self, actual, expected, ring.getName()+" not positioned correctly")

        ring.setInstanceCount(2)
        actLocs = ring.getComponentLocations()
        # first instance
        expected = Coordinate(210.0, 0, 0)
        # expected = Coordinate(0.0, 0, 0)
        actual = actLocs[0]
        assertCoordinateEqual(self, actual, expected, ring.getName()+" not positioned correctly")
        # second instance
        self.assertEqual(ring.getInstanceCount(), 2, ring.getName()+" have incorrect count")
        expected = Coordinate(245.0, 0, 0)
        # expected = Coordinate(35.0, 0, 0)
        actual = actLocs[1]
        assertCoordinateEqual(self, actual, expected, ring.getName()+" not positioned correctly")

        bounds = rocket.getBoundingBox()
        # self.assertEqual(bounds._min._x, 0.0)
        # self.assertEqual(bounds._max._x, 270.0)

        # self.assertEqual(bounds._min._y, -32.385640)
        # self.assertEqual(bounds._min._z, -54.493575)
        # self.assertEqual(bounds._max._y,  62.000000)
        # self.assertEqual(bounds._max._z,  52.893575)

    def verify3StagePositioning(self, rocket, coordinates):
        self.assertEqual(rocket.getChildCount(), 3)

        stage1 = self.getStage(rocket, 0)
        stage2 = self.getStage(rocket, 1)
        stage3 = self.getStage(rocket, 2)

        expected = coordinates[STAGE1]
        actual = stage1.getPositionAsCoordinate()
        assertCoordinateEqual(self, actual, expected, stage1.getName() + " not positioned correctly")

        nose = stage1.getChild(0).Proxy
        expected = coordinates[STAGE1_NOSE]
        actual = nose.getPositionAsCoordinate()
        assertCoordinateEqual(self, actual, expected, nose.getName() + " not positioned correctly")

        body = stage1.getChild(1).Proxy
        expected = coordinates[STAGE1_BODY]
        actual = body.getPositionAsCoordinate()
        assertCoordinateEqual(self, actual, expected, body.getName() + " not positioned correctly")

        fins = body.getChild(0).Proxy
        self.assertTrue(fins.isFinSet(), fins.getName()+" is not a fin set")
        self.assertEqual(fins.getFinCount(), 3, fins.getName()+" have incorrect count")
        expected = coordinates[STAGE1_FINS]
        actual = fins.getPositionAsCoordinate()
        assertCoordinateEqual(self, actual, expected, fins.getName()+" not positioned correctly")

        lugs = body.getChild(1).Proxy
        self.assertEqual(lugs.getInstanceCount(), 1, lugs.getName()+" have incorrect count")
        # actLocs = lugs.getComponentLocations()
        expected = coordinates[STAGE1_LUG]
        actual = lugs.getPositionAsCoordinate()
        assertCoordinateEqual(self, actual, expected, lugs.getName()+" not positioned correctly")

        innerTube = body.getChild(2).Proxy
        expected = coordinates[STAGE1_ENGINE_MOUNT]
        actual = innerTube.getPositionAsCoordinate()
        assertCoordinateEqual(self, actual, expected, innerTube.getName()+" not positioned correctly")

        block = innerTube.getChild(0).Proxy
        expected = coordinates[STAGE1_ENGINE_BLOCK]
        actual = block.getPositionAsCoordinate()
        assertCoordinateEqual(self, actual, expected, block.getName()+" not positioned correctly")

        rings = body.getChild(3).Proxy
        self.assertEqual(rings.getInstanceCount(), 2, rings.getName()+" have incorrect count")
        expected = coordinates[STAGE1_CR]
        actual = rings.getPositionAsCoordinate()
        assertCoordinateEqual(self, actual, expected, rings.getName()+" not positioned correctly")

        expected = coordinates[STAGE2]
        actual = stage2.getPositionAsCoordinate()
        assertCoordinateEqual(self, actual, expected, stage2.getName() + " not positioned correctly")

        body = stage2.getChild(0).Proxy
        expected = coordinates[STAGE2_BODY]
        actual = body.getPositionAsCoordinate()
        assertCoordinateEqual(self, actual, expected, body.getName() + " not positioned correctly")

        fins = body.getChild(0).Proxy
        self.assertTrue(fins.isFinSet(), fins.getName()+" is not a fin set")
        self.assertEqual(fins.getFinCount(), 3, fins.getName()+" have incorrect count")
        expected = coordinates[STAGE2_FINS]
        actual = fins.getPositionAsCoordinate()
        assertCoordinateEqual(self, actual, expected, fins.getName()+" not positioned correctly")

        expected = coordinates[STAGE3]
        actual = stage3.getPositionAsCoordinate()
        assertCoordinateEqual(self, actual, expected, stage3.getName() + " not positioned correctly")

        fincan = stage3.getChild(0).Proxy
        self.assertTrue(fincan.isFinSet(), fincan.getName()+" is not a fin set")
        self.assertEqual(fincan.getFinCount(), 3, fincan.getName()+" has incorrect fin count")
        expected = coordinates[STAGE3_FINCAN]
        actual = fincan.getPositionAsCoordinate()
        assertCoordinateEqual(self, actual, expected, fincan.getName()+" not positioned correctly")

    def verifyBody(self, body, scale, length, radius, thickness, referenceRadius):
        self.assertEqual(body.getLength(), length / scale)
        if body.isAftRadiusAutomatic():
            self.assertFalse(body._isDiameterScaled())
            self.assertEqual(body.getDiameterScale(), 1.0)
            self.assertEqual(body.getOuterRadius(0), referenceRadius)
            self.assertEqual(body.getInnerRadius(0), referenceRadius - thickness)
        else:
            # self.assertTrue(body._isDiameterScaled()) - this may not be true
            self.assertEqual(body.getDiameterScale(), scale)
            self.assertEqual(body.getOuterRadius(0), radius / scale)
            self.assertEqual(body.getInnerRadius(0), radius / scale - thickness)

    def verifyFins(self, fins, scale, count, rootChord, tipChord, sweep, height):
        self.assertTrue(fins.isFinSet())
        self.assertEqual(fins.getFinCount(), count)
        self.assertEqual(fins.getRootChord(), rootChord / scale)
        self.assertEqual(fins.getTipChord(), tipChord / scale)
        self.assertEqual(fins.getSweepLength(), sweep / scale)
        self.assertEqual(fins.getHeight(), height / scale)

    def verifyStage1Nose(self, nose, scale):
        length = 100.0
        radius = 24.79 / 2.0
        self.assertEqual(nose.getLength(), length / scale)
        self.assertEqual(nose.getAftRadius(), radius / scale)

    def verifyStage1Body(self, rocket, body, scale):
        length = 457.0
        radius = 24.79 / 2.0
        thickness = 0.33
        nose = self.getStage(rocket, 0).getChild(0).Proxy
        self.verifyBody(body, scale, length, radius, thickness, nose.getAftRadius())

    def verifyStage1Fins(self, fins, scale):
        count = 3
        rootChord = 57.15
        tipChord = 30.48
        sweep = 69.86
        height = 40.64
        self.verifyFins(fins, scale, count, rootChord, tipChord, sweep, height)

    def verifyStage1(self, rocket, stage1, scale):
        nose = stage1.getChild(0).Proxy
        body = stage1.getChild(1).Proxy
        fins = body.getChild(0).Proxy
        lugs = body.getChild(1).Proxy
        innerTube = body.getChild(2).Proxy
        block = innerTube.getChild(0).Proxy
        rings = body.getChild(3).Proxy

        self.verifyStage1Nose(nose, scale)
        self.verifyStage1Body(rocket, body, scale)
        self.verifyStage1Fins(fins, scale)

    def verifyStage2Body(self, rocket, body, scale):
        length = 70.0
        radius = 24.79 / 2.0
        thickness = 0.33
        nose = self.getStage(rocket, 0).getChild(0).Proxy
        self.verifyBody(body, scale, length, radius, thickness, nose.getAftRadius())

    def verifyStage2Fins(self, fins, scale):
        count = 3
        rootChord = 57.15
        tipChord = 30.48
        sweep = 69.86
        height = 40.64
        self.verifyFins(fins, scale, count, rootChord, tipChord, sweep, height)

    def verifyStage2(self, rocket, stage2, scale):
        body = stage2.getChild(0).Proxy
        fins = body.getChild(0).Proxy

        self.verifyStage2Body(rocket, body, scale)
        self.verifyStage2Fins(fins, scale)

    def verifyStage3Fincan(self, rocket, fincan, scale):
        count = 3
        rootChord = 57.15
        tipChord = 30.48
        sweep = 69.86
        height = 40.64
        self.verifyFins(fincan, scale, count, rootChord, tipChord, sweep, height)

        length = 60.0
        radius = 24.79 / 2.0
        thickness = 1.5
        body = self.getStage(rocket, 1).getChild(0).Proxy # Reference is Stage 2 body
        self.verifyBody(fincan, scale, length, radius, thickness, body.getAftRadius())

    def verifyStage3(self, rocket, stage3, scale):
        fincan = stage3.getChild(0).Proxy

        self.verifyStage3Fincan(rocket, fincan, scale)

    def verifyRocket(self, rocket, scale):
        self.verifyStage1(rocket, self.getStage(rocket, 0), scale)
        self.verifyStage2(rocket, self.getStage(rocket, 1), scale)
        self.verifyStage3(rocket, self.getStage(rocket, 2), scale)

    def referenceCoordinates(self):
        coordinates = []

        # Added in the same sequence as our reference constants
        coordinates.append(Coordinate(0,0,0)) # Stage 1
        coordinates.append(Coordinate(0.0,0,0)) # Nose
        coordinates.append(Coordinate(100.0,0,0)) # Body
        coordinates.append(Coordinate(499.85,0,0)) # Fins
        coordinates.append(Coordinate(303.5,-12.63964076,7.2975)) # Lug
        coordinates.append(Coordinate(492.0,0,0)) # Engine mount
        coordinates.append(Coordinate(492.0,0,0)) # Engine block
        coordinates.append(Coordinate(501.0,0,0)) # Centering rings
        coordinates.append(Coordinate(557.0,0,0)) # Stage 2
        coordinates.append(Coordinate(557.0,0,0)) # Body
        coordinates.append(Coordinate(569.85,0,0)) # Fins
        coordinates.append(Coordinate(627.0,0,0)) # Stage 3
        coordinates.append(Coordinate(627.0,0,0)) # Fin can
        return coordinates

    def test3Stage(self):
        rocket = TestRockets.make3stage('test3Stage')
        coordinates = self.referenceCoordinates()

        self.verify3StagePositioning(rocket, coordinates)
        self.verifyRocket(rocket, 1.0)

    def testNullScalefinCan(self):
        rocket = TestRockets.make3stage('testNullScalefinCan')
        coordinates = self.referenceCoordinates()

        self.verify3StagePositioning(rocket, coordinates)

        stage3 = rocket.getChild(2).Proxy
        fincan = stage3.getChild(0).Proxy

        fincan.setScale(1.0)
        FreeCAD.activeDocument().recompute(None,True,True)
        self.verify3StagePositioning(rocket, coordinates)

    def testHalfScalefinCan(self):
        rocket = TestRockets.make3stage('testHalfScalefinCan')
        coordinates = self.referenceCoordinates()

        self.verify3StagePositioning(rocket, coordinates)

        stage3 = rocket.getChild(2).Proxy
        fincan = stage3.getChild(0).Proxy

        fincan.setScale(0.5)
        FreeCAD.activeDocument().recompute(None,True,True)
        self.verify3StagePositioning(rocket, coordinates)

    def testTwoScalefinCan(self):
        rocket = TestRockets.make3stage('testTwoScalefinCan')
        coordinates = self.referenceCoordinates()

        self.verify3StagePositioning(rocket, coordinates)

        stage3 = rocket.getChild(2).Proxy
        fincan = stage3.getChild(0).Proxy

        fincan.setScale(2.0)
        FreeCAD.activeDocument().recompute(None,True,True)
        self.verify3StagePositioning(rocket, coordinates)

    def testNullScaleStage3(self):
        rocket = TestRockets.make3stage('testNullScaleStage3')
        coordinates = self.referenceCoordinates()

        self.verify3StagePositioning(rocket, coordinates)

        stage3 = rocket.getChild(2).Proxy
        fincan = stage3.getChild(0).Proxy

        stage3.setScale(1.0)
        FreeCAD.activeDocument().recompute(None,True,True)
        self.verify3StagePositioning(rocket, coordinates)

    def testHalfScaleStage3(self):
        rocket = TestRockets.make3stage('testHalfScaleStage3')
        coordinates = self.referenceCoordinates()

        self.verify3StagePositioning(rocket, coordinates)

        stage3 = rocket.getChild(2).Proxy
        fincan = stage3.getChild(0).Proxy

        stage3.setScale(0.5)
        FreeCAD.activeDocument().recompute(None,True,True)
        self.verify3StagePositioning(rocket, coordinates)
        self.verifyStage1(rocket, self.getStage(rocket, 0), 1.0)
        self.verifyStage2(rocket, self.getStage(rocket, 1), 1.0)
        self.verifyStage3(rocket, self.getStage(rocket, 2), 0.5)

        # Turn the scaling off
        stage3.setScaled(False)
        FreeCAD.activeDocument().recompute(None,True,True)
        self.verify3StagePositioning(rocket, coordinates)
        self.verifyRocket(rocket, 1.0)

        # And back on
        stage3.setScaled(True)
        FreeCAD.activeDocument().recompute(None,True,True)
        self.verify3StagePositioning(rocket, coordinates)
        self.verifyStage1(rocket, self.getStage(rocket, 0), 1.0)
        self.verifyStage2(rocket, self.getStage(rocket, 1), 1.0)
        self.verifyStage3(rocket, self.getStage(rocket, 2), 0.5)

    def testTwoScaleStage3(self):
        rocket = TestRockets.make3stage('testTwoScaleStage3')
        coordinates = self.referenceCoordinates()

        self.verify3StagePositioning(rocket, coordinates)

        stage3 = rocket.getChild(2).Proxy
        self.verifyRocket(rocket, 1.0)

        stage3.setScale(2.0)
        FreeCAD.activeDocument().recompute(None,True,True)
        self.verify3StagePositioning(rocket, coordinates)
        self.verifyStage1(rocket, self.getStage(rocket, 0), 1.0)
        self.verifyStage2(rocket, self.getStage(rocket, 1), 1.0)
        self.verifyStage3(rocket, self.getStage(rocket, 2), 2.0)

        # Turn the scaling off
        stage3.setScaled(False)
        FreeCAD.activeDocument().recompute(None,True,True)
        self.verify3StagePositioning(rocket, coordinates)
        self.verifyRocket(rocket, 1.0)

        # And back on
        stage3.setScaled(True)
        FreeCAD.activeDocument().recompute(None,True,True)
        self.verify3StagePositioning(rocket, coordinates)
        self.verifyStage1(rocket, self.getStage(rocket, 0), 1.0)
        self.verifyStage2(rocket, self.getStage(rocket, 1), 1.0)
        self.verifyStage3(rocket, self.getStage(rocket, 2), 2.0)

    def testNullScaleStage2(self):
        rocket = TestRockets.make3stage('testNullScaleStage2')
        coordinates = self.referenceCoordinates()

        self.verify3StagePositioning(rocket, coordinates)
        self.verifyRocket(rocket, 1.0)

        stage2 = self.getStage(rocket, 1)

        stage2.setScale(1.0)
        FreeCAD.activeDocument().recompute(None,True,True)
        self.verify3StagePositioning(rocket, coordinates)
        self.verifyRocket(rocket, 1.0)

        # Turn the scaling off
        stage2.setScaled(False)
        FreeCAD.activeDocument().recompute(None,True,True)
        self.verify3StagePositioning(rocket, coordinates)
        self.verifyRocket(rocket, 1.0)

        # And back on
        stage2.setScaled(True)
        FreeCAD.activeDocument().recompute(None,True,True)
        self.verify3StagePositioning(rocket, coordinates)
        self.verifyRocket(rocket, 1.0)

    def testHalfScaleStage2(self):
        rocket = TestRockets.make3stage('testHalfScaleStage2')
        coordinates = self.referenceCoordinates()
        coordinates_scaled = self.referenceCoordinates()
        coordinates_scaled[STAGE2_FINS] = Coordinate(582.7,0,0)
        coordinates_scaled[STAGE3] = Coordinate(697.0,0,0)
        coordinates_scaled[STAGE3_FINCAN] = Coordinate(697.0,0,0)

        self.verify3StagePositioning(rocket, coordinates)
        self.verifyRocket(rocket, 1.0)

        stage2 = self.getStage(rocket, 1)

        stage2.setScale(0.5)
        FreeCAD.activeDocument().recompute(None,True,True)
        self.verify3StagePositioning(rocket, coordinates_scaled)
        self.verifyStage1(rocket, self.getStage(rocket, 0), 1.0)
        self.verifyStage2(rocket, self.getStage(rocket, 1), 0.5)
        self.verifyStage3(rocket, self.getStage(rocket, 2), 1.0)

        # Turn the scaling off
        stage2.setScaled(False)
        FreeCAD.activeDocument().recompute(None,True,True)
        coordinates = self.referenceCoordinates()
        self.verify3StagePositioning(rocket, coordinates)
        self.verifyRocket(rocket, 1.0)

        # And back on
        stage2.setScaled(True)
        FreeCAD.activeDocument().recompute(None,True,True)
        self.verify3StagePositioning(rocket, coordinates_scaled)
        self.verifyStage1(rocket, self.getStage(rocket, 0), 1.0)
        self.verifyStage2(rocket, self.getStage(rocket, 1), 0.5)
        self.verifyStage3(rocket, self.getStage(rocket, 2), 1.0)

    def testTwoScaleStage2(self):
        rocket = TestRockets.make3stage('testTwoScaleStage2')
        coordinates = self.referenceCoordinates()
        coordinates_scaled = self.referenceCoordinates()
        coordinates_scaled[STAGE2_FINS] = Coordinate(563.425,0,0)
        coordinates_scaled[STAGE3] = Coordinate(592,0,0)
        coordinates_scaled[STAGE3_FINCAN] = Coordinate(592.0,0,0)

        self.verify3StagePositioning(rocket, coordinates)
        self.verifyRocket(rocket, 1.0)

        stage2 = self.getStage(rocket, 1)

        stage2.setScale(2.0)
        FreeCAD.activeDocument().recompute(None,True,True)
        self.verify3StagePositioning(rocket, coordinates_scaled)
        self.verifyStage1(rocket, self.getStage(rocket, 0), 1.0)
        self.verifyStage2(rocket, self.getStage(rocket, 1), 2.0)
        self.verifyStage3(rocket, self.getStage(rocket, 2), 1.0)

        # Turn the scaling off
        stage2.setScaled(False)
        FreeCAD.activeDocument().recompute(None,True,True)
        coordinates = self.referenceCoordinates()
        self.verify3StagePositioning(rocket, coordinates)
        self.verifyRocket(rocket, 1.0)

        # And back on
        stage2.setScaled(True)
        FreeCAD.activeDocument().recompute(None,True,True)
        self.verify3StagePositioning(rocket, coordinates_scaled)
        self.verifyStage1(rocket, self.getStage(rocket, 0), 1.0)
        self.verifyStage2(rocket, self.getStage(rocket, 1), 2.0)
        self.verifyStage3(rocket, self.getStage(rocket, 2), 1.0)

        # set auto diameter
        body = stage2.getChild(0).Proxy
        body.setOuterRadiusAutomatic(True)
        FreeCAD.activeDocument().recompute(None,True,True)
        self.verify3StagePositioning(rocket, coordinates_scaled)
        self.verifyStage1(rocket, self.getStage(rocket, 0), 1.0)
        self.verifyStage2(rocket, self.getStage(rocket, 1), 2.0)
        self.verifyStage3(rocket, self.getStage(rocket, 2), 1.0)
