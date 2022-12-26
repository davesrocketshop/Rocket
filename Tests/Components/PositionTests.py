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
from App.util.MathUtil import EPSILON
from App.position import AxialMethod

from Tests.util.TestRockets import TestRockets

class PositionTests(unittest.TestCase):

    def setUp(self):
        self.Doc = FreeCAD.newDocument("PositionTests")

    def testChangeAxialMethod(self):
        rocket = TestRockets.makeEstesAlphaIII()
        stage = rocket.getChild(0).Proxy
        body = stage.getChild(1).Proxy
        fins = body.getChild(0).Proxy

        # verify construction:
        self.assertEquals(200.0, body.getLength(), "incorrect body length:")
        self.assertEquals(50.0, fins.getLength(), "incorrect fin length:")
        # fin #1
        # expLoc = Coordinate(220.0, 12.0, 0)
        expLoc = Coordinate(0, 0, 0)
        actLocs = fins.getComponentLocations()
        print("\tActual: " + str(actLocs[0]))
        print("\tExpected: " + str(expLoc))
        self.assertEqual(actLocs[0], expLoc, fins.getName() + " not positioned correctly: ")

        allTestCases = [
            (AxialMethod.BOTTOM, 0.0, AxialMethod.TOP,  150.0, 150.0),
            (AxialMethod.TOP, 0.0, AxialMethod.BOTTOM, -150.0, 0.0),
            (AxialMethod.BOTTOM, -30.0, AxialMethod.TOP, 120.0, 120.0),
            (AxialMethod.BOTTOM, 30.0, AxialMethod.TOP, 180.0, 180.0),
            (AxialMethod.BOTTOM, 30.0, AxialMethod.MIDDLE, 105.0, 180.0),
            (AxialMethod.MIDDLE, 0.0, AxialMethod.TOP, 75.0, 75.0),
            (AxialMethod.MIDDLE, 0.0, AxialMethod.BOTTOM, -75.0, 75.0),
            (AxialMethod.MIDDLE, 5.0, AxialMethod.TOP, 80.0, 80.0)
        ]

        for caseIndex, case in enumerate(allTestCases):
            # test repositioning
            fins._setAxialOffset(case[0], case[1])
            self.assertEquals(fins.getAxialMethod(), case[0], fins.getName() + " incorrect start axial-position-method: ")
            self.assertEquals(fins.getAxialOffset(), case[1], fins.getName() + " incorrect start axial-position-value: ")

            fins.setAxialMethod(case[2])
            self.assertEquals(case[3], fins.getAxialOffset(), " Test Case # {0} // offset doesn't match!".format(caseIndex))
            self.assertEquals(case[4], fins.getPosition().x, " Test Case # {0} // position doesn't match!".format(caseIndex))
