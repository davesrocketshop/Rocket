# SPDX-License-Identifier: LGPL-2.1-or-later
# SPDX-FileCopyrightText: 2022 David Carter <dcarter@davidcarter.ca>
# SPDX-File-Notice: Part of the Rocket addon.


"""Class for testing centering rings"""

__title__ = "FreeCAD Centering Ring Tests"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

import FreeCAD
import unittest

from Ui.Commands.CmdCenteringRing import makeCenteringRing

class CenteringRingTests(unittest.TestCase):

    def setUp(self):
        self.Doc = FreeCAD.newDocument("CenteringRingTest")

    def tearDown(self):
        FreeCAD.closeDocument(self.Doc.Name)

    def _checkShape(self, feature, message):
        self.assertTrue(feature._obj.Shape.isValid(), message)
        self.assertIsNone(feature._obj.Shape.check(True), message)

    def testBasic(self):
        feature = makeCenteringRing('CenteringRing')
        self.Doc.recompute()

        self._checkShape(feature, "Basic")

    def testStep(self):
        feature = makeCenteringRing('CenteringRing')
        feature._obj.Step = True
        self.Doc.recompute()

        self._checkShape(feature, "Step")

    def testHoles(self):
        feature = makeCenteringRing('CenteringRing')
        feature._obj.Holes = True
        feature._obj.HoleCount = 4
        self.Doc.recompute()

        self._checkShape(feature, "Holes")
