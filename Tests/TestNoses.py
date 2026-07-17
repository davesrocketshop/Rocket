# SPDX-License-Identifier: LGPL-2.1-or-later
# SPDX-File-Notice: Part of the Rocket addon.

################################################################################
#                                                                              #
#   © 2022 David Carter <dcarter@davidcarter.ca>                               #
#                                                                              #
#   This addon is free software: you can redistribute it and/or modify         #
#   it under the terms of the GNU Lesser General Public License as             #
#   published by the Free Software Foundation, either version 2.1              #
#   of the License, or (at your option) any later version.                     #
#                                                                              #
#   This addon is distributed in the hope that it will be useful,              #
#   but WITHOUT ANY WARRANTY; without even the implied warranty                #
#   of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.                    #
#   See the GNU Lesser General Public License for more details.                #
#                                                                              #
#   You should have received a copy of the GNU Lesser General Public           #
#   License along with this addon. If not, see https://www.gnu.org/licenses    #
#                                                                              #
################################################################################


"""Class for testing nose cones"""

__title__ = "FreeCAD Nose Cone Tests"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

import FreeCAD
import unittest
import traceback

from Rocket.Constants import TYPE_CONE, TYPE_BLUNTED_CONE, TYPE_SPHERICAL, TYPE_ELLIPTICAL, TYPE_HAACK, TYPE_OGIVE, TYPE_BLUNTED_OGIVE, TYPE_SECANT_OGIVE, TYPE_VON_KARMAN, TYPE_PARABOLA, TYPE_PARABOLIC, TYPE_POWER
from Rocket.Constants import STYLE_CAPPED, STYLE_HOLLOW, STYLE_SOLID
from Rocket.Constants import STYLE_CAP_SOLID, STYLE_CAP_BAR, STYLE_CAP_CROSS

from Ui.Commands.CmdNoseCone import makeNoseCone

class NoseTests(unittest.TestCase):

    def setUp(self):
        self.Doc = FreeCAD.newDocument("NoseTest")

    def tearDown(self):
        FreeCAD.closeDocument(self.Doc.Name)

    def _checkShape(self, feature, message):
        self.assertTrue(feature._obj.Shape.isValid(), message)
        self.assertIsNone(feature._obj.Shape.check(True), message)

    def _checkRadiusAt(self, feature, message):
        resolution = feature._obj.Resolution
        length = feature._obj.Length
        for i in range(1, resolution): # Start from 1 to avoid a zero result

            x = float(i) * (length / float(resolution))
            radius = feature.getRadius(x)
            # radius = 0
            if not radius > 0:
                print(f"Radius at {x} is {radius}: {message}")
            self.assertGreater(radius, 0, message)

    def testBasic(self):
        feature = makeNoseCone('NoseCone')
        self.Doc.recompute()

        self._checkShape(feature, "Basic")

    def _setType(self, feature, type):
        feature._obj.NoseType = type
        if type == TYPE_POWER:
            feature._obj.Coefficient = 0.5
        elif type == TYPE_SPHERICAL:
            feature._obj.Length = (feature._obj.Diameter / 2.0)

    def _testRadius(self, type, style):
        feature = makeNoseCone('NoseCone')
        self._setType(feature, type)
        feature._obj.NoseStyle = style
        feature._obj.Shoulder = False
        feature._obj.CapStyle = STYLE_CAP_SOLID
        self.Doc.recompute()

        message = type + ": " + style + " Plain"
        message += ", " + STYLE_CAP_SOLID

        self._checkRadiusAt(feature, message)

    def _testPlain(self, type, style, capStyle = STYLE_CAP_SOLID):
        feature = makeNoseCone('NoseCone')
        self._setType(feature, type)
        feature._obj.NoseStyle = style
        feature._obj.Shoulder = False
        feature._obj.CapStyle = capStyle
        self.Doc.recompute()

        message = type + ": " + style + " Plain"
        message += ", " + capStyle

        self._checkShape(feature, message)

    def _testShoulder(self, type, style, capStyle = STYLE_CAP_SOLID):
        feature = makeNoseCone('NoseCone')
        self._setType(feature, type)
        feature._obj.NoseStyle = style
        feature._obj.Shoulder = True
        feature._obj.CapStyle = capStyle
        self.Doc.recompute()

        message = type + ": " + style + " Plain"
        message += ", " + capStyle

        self._checkShape(feature, message)

    def _getTypes(self):
        return [TYPE_CONE, TYPE_BLUNTED_CONE, TYPE_SPHERICAL, TYPE_ELLIPTICAL, TYPE_HAACK, TYPE_OGIVE, TYPE_BLUNTED_OGIVE,
                        TYPE_SECANT_OGIVE, TYPE_VON_KARMAN, TYPE_PARABOLIC, TYPE_PARABOLA, TYPE_POWER]

    def testTypesRadius(self):
        for type in self._getTypes():
            with self.subTest(type=type):
                self._testRadius(type, STYLE_HOLLOW)

    def testTypesSolid(self):
        for type in self._getTypes():
            with self.subTest(type=type):
                self._testPlain(type, STYLE_SOLID)
                self._testShoulder(type, STYLE_SOLID)

    def testTypesHollow(self):
        for type in self._getTypes():
            with self.subTest(type=type):
                self._testPlain(type, STYLE_HOLLOW)
                self._testShoulder(type, STYLE_HOLLOW)

    def testTypesCapped(self):
        for type in self._getTypes():
            with self.subTest(type=type):
                for capStyle in [STYLE_CAP_SOLID, STYLE_CAP_BAR, STYLE_CAP_CROSS]:
                    with self.subTest(capStyle=capStyle):
                        self._testPlain(type, STYLE_CAPPED, capStyle)
                        self._testShoulder(type, STYLE_CAPPED, capStyle)
