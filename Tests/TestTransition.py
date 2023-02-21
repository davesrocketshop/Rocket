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
"""Class for testing transitions"""

__title__ = "FreeCAD Transition Tests"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"
    
import FreeCAD
import unittest

from App.Constants import TYPE_CONE, TYPE_ELLIPTICAL, TYPE_HAACK, TYPE_OGIVE, TYPE_VON_KARMAN, TYPE_PARABOLA, TYPE_PARABOLIC, TYPE_POWER
from App.Constants import STYLE_CAPPED, STYLE_HOLLOW, STYLE_SOLID, STYLE_SOLID_CORE
from App.Constants import STYLE_CAP_SOLID, STYLE_CAP_BAR, STYLE_CAP_CROSS

from Ui.CmdTransition import makeTransition

class TransitionTests(unittest.TestCase):

    def setUp(self):
        self.Doc = FreeCAD.newDocument("TransitionTest")

    def testBasic(self):
        feature = makeTransition('Transition')
        self.Doc.recompute()

        self.assertTrue(feature.Shape.isValid())
        self.assertIsNone(feature.Shape.check(True))

    def _checkStyle(self, feature, message):
        self.assertTrue(feature.Shape.isValid(), message)
        self.assertIsNone(feature.Shape.check(True), message)

    def _reverse(self, feature):
        temp = feature.ForeDiameter
        feature.ForeDiameter = feature.AftDiameter
        feature.AftDiameter = temp

        temp = feature.ForeShoulderDiameter
        feature.ForeShoulderDiameter = feature.AftShoulderDiameter
        feature.AftShoulderDiameter = temp

    def _testPlain(self, type, style, clipped, capStyle = STYLE_CAP_SOLID):
        feature = makeTransition('Transition')
        feature.TransitionType = type
        if type == TYPE_POWER:
            feature.Coefficient = 0.5
        feature.Clipped = clipped
        feature.TransitionStyle = style
        feature.ForeShoulder = False
        feature.AftShoulder = False
        feature.ForeCapStyle = capStyle
        feature.AftCapStyle = capStyle
        self.Doc.recompute()
        
        message = type + ": " + style + " Plain"
        message += ", " + capStyle
        if clipped:
            message += ", clipped"

        self._checkStyle(feature, message)

        self._reverse(feature)
        message += ", reversed"
        self._checkStyle(feature, message)

    def _testForeShoulder(self, type, style, clipped, capStyle = STYLE_CAP_SOLID):
        feature = makeTransition('Transition')
        feature.TransitionType = type
        if type == TYPE_POWER:
            feature.Coefficient = 0.5
        feature.Clipped = clipped
        feature.TransitionStyle = style
        feature.ForeShoulder = True
        feature.AftShoulder = False
        feature.ForeCapStyle = capStyle
        feature.AftCapStyle = capStyle
        self.Doc.recompute()

        message = type + ": " + style + " Fore Shoulder"
        message += ", " + capStyle
        if clipped:
            message += ", clipped"

        self._checkStyle(feature, message)

        self._reverse(feature)
        message += ", reversed"
        self._checkStyle(feature, message)

    def _testForeShoulderNoStep(self, type, style, clipped, capStyle = STYLE_CAP_SOLID):
        feature = makeTransition('Transition')
        feature.TransitionType = type
        if type == TYPE_POWER:
            feature.Coefficient = 0.5
        feature.Clipped = clipped
        feature.TransitionStyle = style
        feature.ForeShoulder = True
        feature.AftShoulder = False
        feature.ForeCapStyle = capStyle
        feature.AftCapStyle = capStyle
        feature.ForeShoulderDiameter = feature.ForeDiameter
        self.Doc.recompute()

        message = type + ": " + style + " Fore Shoulder No Step"
        message += ", " + capStyle
        if clipped:
            message += ", clipped"

        self._checkStyle(feature, message)

        self._reverse(feature)
        message += ", reversed"
        self._checkStyle(feature, message)

    def _testAftShoulder(self, type, style, clipped, capStyle = STYLE_CAP_SOLID):
        feature = makeTransition('Transition')
        feature.TransitionType = type
        if type == TYPE_POWER:
            feature.Coefficient = 0.5
        feature.Clipped = clipped
        feature.TransitionStyle = style
        feature.ForeShoulder = False
        feature.AftShoulder = True
        feature.ForeCapStyle = capStyle
        feature.AftCapStyle = capStyle
        self.Doc.recompute()

        message = type + ": " + style + " Aft Shoulder"
        message += ", " + capStyle
        if clipped:
            message += ", clipped"

        self._checkStyle(feature, message)

        self._reverse(feature)
        message += ", reversed"
        self._checkStyle(feature, message)

    def _testAftShoulderNoStep(self, type, style, clipped, capStyle = STYLE_CAP_SOLID):
        feature = makeTransition('Transition')
        feature.TransitionType = type
        if type == TYPE_POWER:
            feature.Coefficient = 0.5
        feature.Clipped = clipped
        feature.TransitionStyle = style
        feature.ForeShoulder = False
        feature.AftShoulder = True
        feature.ForeCapStyle = capStyle
        feature.AftCapStyle = capStyle
        feature.AftShoulderDiameter = feature.AftDiameter
        self.Doc.recompute()

        message = type + ": " + style + " Aft Shoulder No Step"
        message += ", " + capStyle
        if clipped:
            message += ", clipped"

        self._checkStyle(feature, message)

        self._reverse(feature)
        message += ", reversed"
        self._checkStyle(feature, message)

    def _testBothShoulder(self, type, style, clipped, capStyle = STYLE_CAP_SOLID):
        feature = makeTransition('Transition')
        feature.TransitionType = type
        if type == TYPE_POWER:
            feature.Coefficient = 0.5
        feature.Clipped = clipped
        feature.TransitionStyle = style
        feature.ForeShoulder = True
        feature.AftShoulder = True
        feature.ForeCapStyle = capStyle
        feature.AftCapStyle = capStyle
        self.Doc.recompute()

        message = type + ": " + style + " Both Shoulder"
        message += ", " + capStyle
        if clipped:
            message += ", clipped"

        self._checkStyle(feature, message)

        self._reverse(feature)
        message += ", reversed"
        self._checkStyle(feature, message)

    def _testBothShoulderNoStep(self, type, style, clipped, capStyle = STYLE_CAP_SOLID):
        feature = makeTransition('Transition')
        feature.TransitionType = type
        if type == TYPE_POWER:
            feature.Coefficient = 0.5
        feature.Clipped = clipped
        feature.TransitionStyle = style
        feature.ForeShoulder = True
        feature.AftShoulder = True
        feature.ForeCapStyle = capStyle
        feature.AftCapStyle = capStyle
        feature.ForeShoulderDiameter = feature.ForeDiameter
        feature.AftShoulderDiameter = feature.AftDiameter
        self.Doc.recompute()

        message = type + ": " + style + " Both Shoulder No Step"
        message += ", " + capStyle
        if clipped:
            message += ", clipped"

        self._checkStyle(feature, message)

        self._reverse(feature)
        message += ", reversed"
        self._checkStyle(feature, message)

    def testTypesSolid(self):
        for type in [TYPE_CONE, TYPE_ELLIPTICAL, TYPE_HAACK, TYPE_OGIVE, TYPE_VON_KARMAN, TYPE_PARABOLA, TYPE_PARABOLIC, TYPE_POWER]:
            with self.subTest(t=type):
                for clipped in [True, False]:
                    with self.subTest(clipped=clipped):
                        self._testPlain(type, STYLE_SOLID, clipped)
                        self._testForeShoulder(type, STYLE_SOLID, clipped)
                        self._testAftShoulder(type, STYLE_SOLID, clipped)
                        self._testBothShoulder(type, STYLE_SOLID, clipped)
                        self._testForeShoulderNoStep(type, STYLE_SOLID, clipped)
                        self._testAftShoulderNoStep(type, STYLE_SOLID, clipped)
                        self._testBothShoulderNoStep(type, STYLE_SOLID, clipped)

    def testTypesSolidCore(self):
        for type in [TYPE_CONE, TYPE_ELLIPTICAL, TYPE_HAACK, TYPE_OGIVE, TYPE_VON_KARMAN, TYPE_PARABOLA, TYPE_PARABOLIC, TYPE_POWER]:
            with self.subTest(t=type):
                for clipped in [True, False]:
                    with self.subTest(clipped=clipped):
                        self._testPlain(type, STYLE_SOLID_CORE, clipped)
                        self._testForeShoulder(type, STYLE_SOLID_CORE, clipped)
                        self._testAftShoulder(type, STYLE_SOLID_CORE, clipped)
                        self._testBothShoulder(type, STYLE_SOLID_CORE, clipped)
                        self._testForeShoulderNoStep(type, STYLE_SOLID_CORE, clipped)
                        self._testAftShoulderNoStep(type, STYLE_SOLID_CORE, clipped)
                        self._testBothShoulderNoStep(type, STYLE_SOLID_CORE, clipped)

    def testTypesHollow(self):
        for type in [TYPE_CONE, TYPE_ELLIPTICAL, TYPE_HAACK, TYPE_OGIVE, TYPE_VON_KARMAN, TYPE_PARABOLA, TYPE_PARABOLIC, TYPE_POWER]:
            with self.subTest(t=type):
                for clipped in [True, False]:
                    with self.subTest(clipped=clipped):
                        self._testPlain(type, STYLE_HOLLOW, clipped)
                        self._testForeShoulder(type, STYLE_HOLLOW, clipped)
                        self._testAftShoulder(type, STYLE_HOLLOW, clipped)
                        self._testBothShoulder(type, STYLE_HOLLOW, clipped)
                        self._testForeShoulderNoStep(type, STYLE_HOLLOW, clipped)
                        self._testAftShoulderNoStep(type, STYLE_HOLLOW, clipped)
                        self._testBothShoulderNoStep(type, STYLE_HOLLOW, clipped)

    def testTypesCapped(self):
        for type in [TYPE_CONE, TYPE_ELLIPTICAL, TYPE_HAACK, TYPE_OGIVE, TYPE_VON_KARMAN, TYPE_PARABOLA, TYPE_PARABOLIC, TYPE_POWER]:
            with self.subTest(t=type):
                for capStyle in [STYLE_CAP_SOLID, STYLE_CAP_BAR, STYLE_CAP_CROSS]:
                    with self.subTest(capStyle=capStyle):
                        for clipped in [True, False]:
                            with self.subTest(clipped=clipped):
                                self._testPlain(type, STYLE_CAPPED, clipped, capStyle)
                                self._testForeShoulder(type, STYLE_CAPPED, clipped, capStyle)
                                self._testAftShoulder(type, STYLE_CAPPED, clipped, capStyle)
                                self._testBothShoulder(type, STYLE_CAPPED, clipped, capStyle)
                                self._testForeShoulderNoStep(type, STYLE_CAPPED, clipped, capStyle)
                                self._testAftShoulderNoStep(type, STYLE_CAPPED, clipped, capStyle)
                                self._testBothShoulderNoStep(type, STYLE_CAPPED, clipped, capStyle)
