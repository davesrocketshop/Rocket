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

from Ui.Commands.CmdTransition import makeTransition

class TransitionTests(unittest.TestCase):

    def setUp(self):
        self.Doc = FreeCAD.newDocument("TransitionTest")

    def testBasic(self):
        feature = makeTransition('Transition')
        self.Doc.recompute()

        self.assertTrue(feature._obj.Shape.isValid())
        self.assertIsNone(feature._obj.Shape.check(True))

    def _checkStyle(self, feature, message):
        self.assertTrue(feature._obj.Shape.isValid(), message)
        self.assertIsNone(feature._obj.Shape.check(True), message)

    def _reverse(self, feature):
        temp = feature._obj.ForeDiameter
        feature._obj.ForeDiameter = feature._obj.AftDiameter
        feature._obj.AftDiameter = temp

        temp = feature._obj.ForeShoulderDiameter
        feature._obj.ForeShoulderDiameter = feature._obj.AftShoulderDiameter
        feature._obj.AftShoulderDiameter = temp

    def _testPlain(self, type, style, clipped, capStyle = STYLE_CAP_SOLID):
        feature = makeTransition('Transition')
        feature._obj.TransitionType = type
        if type == TYPE_POWER:
            feature._obj.Coefficient = 0.5
        feature._obj.Clipped = clipped
        feature._obj.TransitionStyle = style
        feature._obj.ForeShoulder = False
        feature._obj.AftShoulder = False
        feature._obj.ForeCapStyle = capStyle
        feature._obj.AftCapStyle = capStyle
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
        feature._obj.TransitionType = type
        if type == TYPE_POWER:
            feature._obj.Coefficient = 0.5
        feature._obj.Clipped = clipped
        feature._obj.TransitionStyle = style
        feature._obj.ForeShoulder = True
        feature._obj.AftShoulder = False
        feature._obj.ForeCapStyle = capStyle
        feature._obj.AftCapStyle = capStyle
        self.Doc.recompute()

        message = type + ": " + style + " Fore Shoulder"
        message += ", " + capStyle
        if clipped:
            message += ", clipped"

        self._checkStyle(feature, message)

        self._reverse(feature)
        message += ", reversed"
        self._checkStyle(feature, message)

    def _testAftShoulder(self, type, style, clipped, capStyle = STYLE_CAP_SOLID):
        feature = makeTransition('Transition')
        feature._obj.TransitionType = type
        if type == TYPE_POWER:
            feature._obj.Coefficient = 0.5
        feature._obj.Clipped = clipped
        feature._obj.TransitionStyle = style
        feature._obj.ForeShoulder = False
        feature._obj.AftShoulder = True
        feature._obj.ForeCapStyle = capStyle
        feature._obj.AftCapStyle = capStyle
        self.Doc.recompute()

        message = type + ": " + style + " Aft Shoulder"
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
            feature._obj.Coefficient = 0.5
        feature._obj.Clipped = clipped
        feature._obj.TransitionStyle = style
        feature._obj.ForeShoulder = True
        feature._obj.AftShoulder = True
        feature._obj.ForeCapStyle = capStyle
        feature._obj.AftCapStyle = capStyle
        self.Doc.recompute()

        message = type + ": " + style + " Both Shoulder"
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
                self._testPlain(type, STYLE_SOLID, False)
                self._testForeShoulder(type, STYLE_SOLID, False)
                self._testAftShoulder(type, STYLE_SOLID, False)
                self._testBothShoulder(type, STYLE_SOLID, False)
                self._testPlain(type, STYLE_SOLID, True)
                self._testForeShoulder(type, STYLE_SOLID, True)
                self._testAftShoulder(type, STYLE_SOLID, True)
                self._testBothShoulder(type, STYLE_SOLID, True)

    def testTypesSolidCore(self):
        for type in [TYPE_CONE, TYPE_ELLIPTICAL, TYPE_HAACK, TYPE_OGIVE, TYPE_VON_KARMAN, TYPE_PARABOLA, TYPE_PARABOLIC, TYPE_POWER]:
            with self.subTest(t=type):
                self._testPlain(type, STYLE_SOLID_CORE, False)
                self._testForeShoulder(type, STYLE_SOLID_CORE, False)
                self._testAftShoulder(type, STYLE_SOLID_CORE, False)
                self._testBothShoulder(type, STYLE_SOLID_CORE, False)
                self._testPlain(type, STYLE_SOLID_CORE, True)
                self._testForeShoulder(type, STYLE_SOLID_CORE, True)
                self._testAftShoulder(type, STYLE_SOLID_CORE, True)
                self._testBothShoulder(type, STYLE_SOLID_CORE, True)

    def testTypesHollow(self):
        for type in [TYPE_CONE, TYPE_ELLIPTICAL, TYPE_HAACK, TYPE_OGIVE, TYPE_VON_KARMAN, TYPE_PARABOLA, TYPE_PARABOLIC, TYPE_POWER]:
            with self.subTest(t=type):
                self._testPlain(type, STYLE_HOLLOW, False)
                self._testForeShoulder(type, STYLE_HOLLOW, False)
                self._testAftShoulder(type, STYLE_HOLLOW, False)
                self._testBothShoulder(type, STYLE_HOLLOW, False)
                self._testPlain(type, STYLE_HOLLOW, True)
                self._testForeShoulder(type, STYLE_HOLLOW, True)
                self._testAftShoulder(type, STYLE_HOLLOW, True)
                self._testBothShoulder(type, STYLE_HOLLOW, True)

    def testTypesCapped(self):
        for type in [TYPE_CONE, TYPE_ELLIPTICAL, TYPE_HAACK, TYPE_OGIVE, TYPE_VON_KARMAN, TYPE_PARABOLA, TYPE_PARABOLIC, TYPE_POWER]:
            with self.subTest(t=type):
                for capStyle in [STYLE_CAP_SOLID, STYLE_CAP_BAR, STYLE_CAP_CROSS]:
                    with self.subTest(capStyle=capStyle):
                        self._testPlain(type, STYLE_CAPPED, False, capStyle)
                        self._testForeShoulder(type, STYLE_CAPPED, False, capStyle)
                        self._testAftShoulder(type, STYLE_CAPPED, False, capStyle)
                        self._testBothShoulder(type, STYLE_CAPPED, False, capStyle)
                        self._testPlain(type, STYLE_CAPPED, True, capStyle)
                        self._testForeShoulder(type, STYLE_CAPPED, True, capStyle)
                        self._testAftShoulder(type, STYLE_CAPPED, True, capStyle)
                        self._testBothShoulder(type, STYLE_CAPPED, True, capStyle)
