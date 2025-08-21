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

class RocketTest(unittest.TestCase):

    def setUp(self):
        self.Doc = FreeCAD.newDocument("RocketTest")

    def tearDown(self):
        # FreeCAD.closeDocument(self.Doc.Name)
        ...

    def assertCoordinateEqual(self, actual, expected, msg):
        try:
            self.assertEqual(actual, expected)
        except AssertionError:
            msg = "actual %s, expected %s: %s" % (str(actual), str(expected), msg)
            self.fail(msg)


    def testEstesAlphaIII(self):
        rocket = TestRockets.makeEstesAlphaIII()
        stage = rocket.getChild(0).Proxy

        nose = stage.getChild(0).Proxy
        expected = Coordinate(0.0,0,0)
        actual = nose.getPositionAsCoordinate()
        self.assertCoordinateEqual(actual, expected, nose.getName() + " not positioned correctly")

        body = stage.getChild(1).Proxy
        expected = Coordinate(70.0,0,0)
        actual = body.getPositionAsCoordinate()
        self.assertCoordinateEqual(actual, expected, body.getName() + " not positioned correctly")

        fins = body.getChild(0).Proxy
        self.assertTrue(fins.isFinSet(), fins.getName()+" is not a fin set")
        self.assertEqual(fins.getFinCount(), 3, fins.getName()+" have incorrect count")
        expected = Coordinate(220.0,0,0)
        actual = fins.getPositionAsCoordinate()
        self.assertCoordinateEqual(actual, expected, fins.getName()+" not positioned correctly")

        lugs = body.getChild(1).Proxy
        self.assertEqual(lugs.getInstanceCount(), 1, lugs.getName()+" have incorrect count")
        # actLocs = lugs.getComponentLocations()
        expected = Coordinate(181.0, 0.0, 14.2)
        actual = lugs.getPositionAsCoordinate()
        self.assertCoordinateEqual(actual, expected, lugs.getName()+" not positioned correctly")

        mmt = body.getChild(2).Proxy
        # expLoc = Coordinate(203.0,0,0)
        expected = Coordinate(203.0,0,0)
        actual = mmt.getPositionAsCoordinate()
        self.assertCoordinateEqual(actual, expected, mmt.getName()+" not positioned correctly")

        block = mmt.getChild(0).Proxy
        expected = Coordinate(203.0,0,0)
        actual = block.getPositionAsCoordinate()
        self.assertCoordinateEqual(actual, expected, block.getName()+" not positioned correctly")

        ring = body.getChild(3).Proxy
        self.assertEqual(ring.getInstanceCount(), 2, ring.getName()+" have incorrect count")

        # singleton instances follow different code paths
        ring.setInstanceCount(1)
        self.assertEqual(ring.getInstanceCount(), 1, ring.getName()+" have incorrect count")
        # expLoc = Coordinate(210.0,0,0)
        expected = Coordinate(210.0,0,0)
        actual = ring.getPositionAsCoordinate()
        self.assertCoordinateEqual(actual, expected, ring.getName()+" not positioned correctly")

        ring.setInstanceCount(2)
        actLocs = ring.getComponentLocations()
        # first instance
        expected = Coordinate(210.0, 0, 0)
        # expected = Coordinate(0.0, 0, 0)
        actual = actLocs[0]
        self.assertCoordinateEqual(actual, expected, ring.getName()+" not positioned correctly")
        # second instance
        self.assertEqual(ring.getInstanceCount(), 2, ring.getName()+" have incorrect count")
        expected = Coordinate(245.0, 0, 0)
        # expected = Coordinate(35.0, 0, 0)
        actual = actLocs[1]
        self.assertCoordinateEqual(actual, expected, ring.getName()+" not positioned correctly")

        bounds = rocket.getBoundingBox()
        # self.assertEqual(bounds._min._x, 0.0)
        # self.assertEqual(bounds._max._x, 270.0)

        # self.assertEqual(bounds._min._y, -32.385640)
        # self.assertEqual(bounds._min._z, -54.493575)
        # self.assertEqual(bounds._max._y,  62.000000)
        # self.assertEqual(bounds._max._z,  52.893575)

    def verify3StagePositioning(self, rocket, coordinates):
        self.assertEqual(rocket.getChildCount(), 3)

        stage1 = rocket.getChild(0).Proxy
        stage2 = rocket.getChild(1).Proxy
        stage3 = rocket.getChild(2).Proxy

        expected = coordinates[0]
        actual = stage1.getPositionAsCoordinate()
        self.assertCoordinateEqual(actual, expected, stage1.getName() + " not positioned correctly")

        nose = stage1.getChild(0).Proxy
        expected = coordinates[1]
        actual = nose.getPositionAsCoordinate()
        self.assertCoordinateEqual(actual, expected, nose.getName() + " not positioned correctly")

        body = stage1.getChild(1).Proxy
        expected = coordinates[2]
        actual = body.getPositionAsCoordinate()
        self.assertCoordinateEqual(actual, expected, body.getName() + " not positioned correctly")

        fins = body.getChild(0).Proxy
        self.assertTrue(fins.isFinSet(), fins.getName()+" is not a fin set")
        self.assertEqual(fins.getFinCount(), 3, fins.getName()+" have incorrect count")
        expected = coordinates[3]
        actual = fins.getPositionAsCoordinate()
        self.assertCoordinateEqual(actual, expected, fins.getName()+" not positioned correctly")

        lugs = body.getChild(1).Proxy
        self.assertEqual(lugs.getInstanceCount(), 1, lugs.getName()+" have incorrect count")
        # actLocs = lugs.getComponentLocations()
        expected = coordinates[4]
        actual = lugs.getPositionAsCoordinate()
        self.assertCoordinateEqual(actual, expected, lugs.getName()+" not positioned correctly")

        innerTube = body.getChild(2).Proxy
        expected = coordinates[5]
        actual = innerTube.getPositionAsCoordinate()
        self.assertCoordinateEqual(actual, expected, innerTube.getName()+" not positioned correctly")

        block = innerTube.getChild(0).Proxy
        expected = coordinates[6]
        actual = block.getPositionAsCoordinate()
        self.assertCoordinateEqual(actual, expected, block.getName()+" not positioned correctly")

        rings = body.getChild(3).Proxy
        self.assertEqual(rings.getInstanceCount(), 2, rings.getName()+" have incorrect count")
        expected = coordinates[7]
        actual = rings.getPositionAsCoordinate()
        self.assertCoordinateEqual(actual, expected, rings.getName()+" not positioned correctly")

        expected = coordinates[8]
        actual = stage2.getPositionAsCoordinate()
        self.assertCoordinateEqual(actual, expected, stage2.getName() + " not positioned correctly")

        body = stage2.getChild(0).Proxy
        expected = coordinates[9]
        actual = body.getPositionAsCoordinate()
        self.assertCoordinateEqual(actual, expected, body.getName() + " not positioned correctly")

        fins = body.getChild(0).Proxy
        self.assertTrue(fins.isFinSet(), fins.getName()+" is not a fin set")
        self.assertEqual(fins.getFinCount(), 3, fins.getName()+" have incorrect count")
        expected = coordinates[10]
        actual = fins.getPositionAsCoordinate()
        self.assertCoordinateEqual(actual, expected, fins.getName()+" not positioned correctly")

        expected = coordinates[11]
        actual = stage3.getPositionAsCoordinate()
        self.assertCoordinateEqual(actual, expected, stage3.getName() + " not positioned correctly")

        fincan = stage3.getChild(0).Proxy
        self.assertTrue(fincan.isFinSet(), fincan.getName()+" is not a fin set")
        self.assertEqual(fincan.getFinCount(), 3, fincan.getName()+" has incorrect fin count")
        expected = coordinates[12]
        actual = fincan.getPositionAsCoordinate()
        self.assertCoordinateEqual(actual, expected, fincan.getName()+" not positioned correctly")

    def test3Stage(self):
        rocket = TestRockets.make3stage()
        coordinates = []

        coordinates.append(Coordinate(0,0,0)) # Stage 1
        coordinates.append(Coordinate(0.0,0,0)) # Node
        coordinates.append(Coordinate(100.0,0,0)) # Body
        coordinates.append(Coordinate(499.85,0,0)) # Fins
        coordinates.append(Coordinate(303.5,-12.63964076823388,7.297500000000001)) # Lug
        coordinates.append(Coordinate(492.0,0,0)) # Engine mount
        coordinates.append(Coordinate(492.0,0,0)) # Engine block
        coordinates.append(Coordinate(501.0,0,0)) # Centering rings
        coordinates.append(Coordinate(557.0,0,0)) # Stage 2
        coordinates.append(Coordinate(557.0,0,0)) # Body
        coordinates.append(Coordinate(569.85,0,0)) # Fins
        coordinates.append(Coordinate(627.0,0,0)) # Stage 3
        coordinates.append(Coordinate(627.0,0,0)) # Fin can

        self.verify3StagePositioning(rocket, coordinates)


