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
"""Class for testing rockets"""

__title__ = "FreeCAD Rocket Tests"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"
    
import FreeCAD
import unittest

from App.util.Coordinate import Coordinate

from Tests.util.TestRockets import TestRockets

class RocketTest(unittest.TestCase):

    def setUp(self):
        self.Doc = FreeCAD.newDocument("RocketTest")

    def testEstesAlphaIII(self):
        rocket = TestRockets.makeEstesAlphaIII()
        stage = rocket.getChild(0).Proxy

        nose = stage.getChild(0).Proxy
        expected = Coordinate(0,0,0)
        actual = nose.getComponentLocations()[0]
        print(str(actual))
        print(str(expected))
        self.assertTrue(actual == expected, nose.getName() + " not positioned correctly")

        body = stage.getChild(1).Proxy
        expected = Coordinate(70.0,0,0)
        actual = body.getComponentLocations()[0]
        for i, coord in enumerate(body.getComponentLocations()):
            print("%d, %s" % (i, str(coord)))
        print(str(actual))
        print(str(expected))
        self.assertEqual(actual, expected, body.getName() + " not positioned correctly")
