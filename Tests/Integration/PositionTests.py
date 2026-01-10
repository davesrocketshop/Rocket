# SPDX-License-Identifier: LGPL-2.1-or-later
# SPDX-FileCopyrightText: 2022 David Carter <dcarter@davidcarter.ca>
# SPDX-File-Notice: Part of the Rocket addon.


"""Class for testing rockets"""

__title__ = "FreeCAD Rocket Tests"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

import FreeCAD
import unittest

from Rocket.util.Coordinate import Coordinate
from Rocket.position import AxialMethod

from Ui.Commands.CmdBodyTube import makeBodyTube
from Ui.Commands.CmdRocket import makeRocket
from Ui.Commands.CmdStage import makeStage
from Ui.Commands.CmdNoseCone import makeNoseCone
from Ui.Commands.CmdFin import makeFin
from Ui.Commands.CmdLaunchGuides import makeLaunchLug
from Ui.Commands.CmdCenteringRing import makeCenteringRing

from Tests.util.TestRockets import TestRockets

from Rocket.Constants import TYPE_OGIVE

class PositionTests(unittest.TestCase):

    def setUp(self):
        self.Doc = FreeCAD.newDocument("PositionTests")

    def tearDown(self):
        FreeCAD.closeDocument(self.Doc.Name)

    def assertCoordinateEqual(self, actual, expected, msg):
        try:
            self.assertEqual(actual, expected)
        except AssertionError:
            msg = "actual %s, expected %s: %s" % (str(actual), str(expected), msg)
            self.fail(msg)

    def testAxialMethod(self):
        rocket = TestRockets.makeEstesAlphaIII()
        stage = rocket.getChild(0).Proxy
        body = stage.getChild(1).Proxy
        lug = body.getChild(1).Proxy

        # verify construction:
        self.assertEqual(200.0, body.getLength(), body.getName() + " incorrect body length:")
        self.assertEqual(50.0, lug.getLength(), lug.getName() + " incorrect lug length:")

        lug._setAxialOffset(AxialMethod.BOTTOM, 0.0)
        # lug.setAxialMethod(AxialMethod.BOTTOM)
        self.assertEqual(lug.getAxialMethod(), AxialMethod.BOTTOM, lug.getName() + " incorrect axial-position-method: ")
        self.assertEqual(lug.getAxialOffset(), 0.0, lug.getName() + " incorrect axial-position-offset: ")
        self.assertEqual(lug.getPosition().x, 220.0, lug.getName() + " incorrect axial-position-value: ")

        lug._setAxialOffset(AxialMethod.BOTTOM, -5.0)
        # lug.setAxialMethod(AxialMethod.BOTTOM)
        self.assertEqual(lug.getAxialMethod(), AxialMethod.BOTTOM, lug.getName() + " incorrect axial-position-method: ")
        self.assertEqual(lug.getAxialOffset(), -5.0, lug.getName() + " incorrect axial-position-offset: ")
        self.assertEqual(lug.getPosition().x, 215.0, lug.getName() + " incorrect axial-position-value: ")

        lug._setAxialOffset(AxialMethod.BOTTOM, 5.0)
        # lug.setAxialMethod(AxialMethod.BOTTOM)
        self.assertEqual(lug.getAxialMethod(), AxialMethod.BOTTOM, lug.getName() + " incorrect axial-position-method: ")
        self.assertEqual(lug.getAxialOffset(), 5.0, lug.getName() + " incorrect axial-position-offset: ")
        self.assertEqual(lug.getPosition().x, 225.0, lug.getName() + " incorrect axial-position-value: ")

        lug._setAxialOffset(AxialMethod.MIDDLE, 0.0)
        # lug.setAxialMethod(AxialMethod.MIDDLE)
        self.assertEqual(lug.getAxialMethod(), AxialMethod.MIDDLE, lug.getName() + " incorrect axial-position-method: ")
        self.assertEqual(lug.getAxialOffset(), 0.0, lug.getName() + " incorrect axial-position-offset: ")
        self.assertEqual(lug.getPosition().x, 145.0, lug.getName() + " incorrect axial-position-value: ")

        lug._setAxialOffset(AxialMethod.MIDDLE, -5.0)
        # lug.setAxialMethod(AxialMethod.MIDDLE)
        self.assertEqual(lug.getAxialMethod(), AxialMethod.MIDDLE, lug.getName() + " incorrect axial-position-method: ")
        self.assertEqual(lug.getAxialOffset(), -5.0, lug.getName() + " incorrect axial-position-offset: ")
        self.assertEqual(lug.getPosition().x, 140.0, lug.getName() + " incorrect axial-position-value: ")

        lug._setAxialOffset(AxialMethod.MIDDLE, 5.0)
        # lug.setAxialMethod(AxialMethod.MIDDLE)
        self.assertEqual(lug.getAxialMethod(), AxialMethod.MIDDLE, lug.getName() + " incorrect axial-position-method: ")
        self.assertEqual(lug.getAxialOffset(), 5.0, lug.getName() + " incorrect axial-position-offset: ")
        self.assertEqual(lug.getPosition().x, 150.0, lug.getName() + " incorrect axial-position-value: ")

        lug._setAxialOffset(AxialMethod.TOP, 0.0)
        # lug.setAxialMethod(AxialMethod.TOP)
        self.assertEqual(lug.getAxialMethod(), AxialMethod.TOP, lug.getName() + " incorrect axial-position-method: ")
        self.assertEqual(lug.getAxialOffset(), 0.0, lug.getName() + " incorrect axial-position-offset: ")
        self.assertEqual(lug.getPosition().x, 70.0, lug.getName() + " incorrect axial-position-value: ")

        lug._setAxialOffset(AxialMethod.TOP, -5.0)
        # lug.setAxialMethod(AxialMethod.TOP)
        self.assertEqual(lug.getAxialMethod(), AxialMethod.TOP, lug.getName() + " incorrect axial-position-method: ")
        self.assertEqual(lug.getAxialOffset(), -5.0, lug.getName() + " incorrect axial-position-offset: ")
        self.assertEqual(lug.getPosition().x, 65.0, lug.getName() + " incorrect axial-position-value: ")

        lug._setAxialOffset(AxialMethod.TOP, 5.0)
        # lug.setAxialMethod(AxialMethod.TOP)
        self.assertEqual(lug.getAxialMethod(), AxialMethod.TOP, lug.getName() + " incorrect axial-position-method: ")
        self.assertEqual(lug.getAxialOffset(), 5.0, lug.getName() + " incorrect axial-position-offset: ")
        self.assertEqual(lug.getPosition().x, 75.0, lug.getName() + " incorrect axial-position-value: ")

    def testChangeAxialMethod(self):
        rocket = TestRockets.makeEstesAlphaIII()
        stage = rocket.getChild(0).Proxy
        body = stage.getChild(1).Proxy
        fins = body.getChild(0).Proxy

        # verify construction:
        self.assertEqual(200.0, body.getLength(), "incorrect body length:")
        self.assertEqual(50.0, fins.getLength(), "incorrect fin length:")
        # fin #1
        # expLoc = Coordinate(0, 0, 0)
        expLoc = Coordinate(220, 0, 0)
        actLocs = fins.getComponentLocations()
        self.assertCoordinateEqual(actLocs[0], expLoc, fins.getName() + " not positioned correctly: ")

        allTestCases = [
            (AxialMethod.BOTTOM, 0.0, AxialMethod.TOP,  220.0, 220.0),
            (AxialMethod.TOP, 0.0, AxialMethod.BOTTOM, 220.0, 70.0),
            (AxialMethod.BOTTOM, -30.0, AxialMethod.TOP, 190.0, 190.0),
            (AxialMethod.BOTTOM, 30.0, AxialMethod.TOP, 250.0, 250.0),
            (AxialMethod.BOTTOM, 30.0, AxialMethod.MIDDLE, 175.0, 250.0),
            (AxialMethod.MIDDLE, 0.0, AxialMethod.TOP, 145.0, 145.0),
            (AxialMethod.MIDDLE, 0.0, AxialMethod.BOTTOM, 295.0, 145.0),
            (AxialMethod.MIDDLE, 5.0, AxialMethod.TOP, 150.0, 150.0)
        ]

        for caseIndex, case in enumerate(allTestCases):
            # test repositioning
            fins._setAxialOffset(case[0], case[1])
            self.assertEqual(fins.getAxialMethod(), case[0], fins.getName() + " Test Case # {0} // incorrect start axial-position-method: ".format(caseIndex))
            self.assertEqual(fins.getAxialOffset(), case[1], fins.getName() + " Test Case # {0} // incorrect start axial-position-value: ".format(caseIndex))

            fins.setAxialMethod(case[2])
            self.assertEqual(case[3], fins.getAxialOffset(), " Test Case # {0} // offset doesn't match!".format(caseIndex))
            self.assertEqual(case[4], fins.getPosition().x, " Test Case # {0} // position doesn't match!".format(caseIndex))
