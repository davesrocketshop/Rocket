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
        t1 = makeTransition('Transition')
        self.Doc.recompute()

        self.assertTrue(t1.Shape.isValid())
        self.assertIsNone(t1.Shape.check(True))

    def _checkStyle(self, t1, message):
        self.assertTrue(t1.Shape.isValid(), message)
        self.assertIsNone(t1.Shape.check(True), message)

    def _reverse(self, t1):
        temp = t1.ForeDiameter
        t1.ForeDiameter = t1.AftDiameter
        t1.AftDiameter = temp

        temp = t1.ForeShoulderDiameter
        t1.ForeShoulderDiameter = t1.AftShoulderDiameter
        t1.AftShoulderDiameter = temp

    def _testPlain(self, type, style, clipped, capStyle = STYLE_CAP_SOLID):
        t1 = makeTransition('Transition')
        t1.TransitionType = type
        if type == TYPE_POWER:
            t1.Coefficient = 0.5
        t1.Clipped = clipped
        t1.TransitionStyle = style
        t1.ForeShoulder = False
        t1.AftShoulder = False
        t1.ForeCapStyle = capStyle
        t1.AftCapStyle = capStyle
        self.Doc.recompute()
        
        message = type + ": " + style + " Plain"
        message += ", " + capStyle
        if clipped:
            message += ", clipped"

        self._checkStyle(t1, message)

        self._reverse(t1)
        message += ", reversed"
        self._checkStyle(t1, message)

    def _testForeShoulder(self, type, style, clipped, capStyle = STYLE_CAP_SOLID):
        t1 = makeTransition('Transition')
        t1.TransitionType = type
        if type == TYPE_POWER:
            t1.Coefficient = 0.5
        t1.Clipped = clipped
        t1.TransitionStyle = style
        t1.ForeShoulder = True
        t1.AftShoulder = False
        t1.ForeCapStyle = capStyle
        t1.AftCapStyle = capStyle
        self.Doc.recompute()

        message = type + ": " + style + " Fore Shoulder"
        message += ", " + capStyle
        if clipped:
            message += ", clipped"

        self._checkStyle(t1, message)

        self._reverse(t1)
        message += ", reversed"
        self._checkStyle(t1, message)

    def _testAftShoulder(self, type, style, clipped, capStyle = STYLE_CAP_SOLID):
        t1 = makeTransition('Transition')
        t1.TransitionType = type
        if type == TYPE_POWER:
            t1.Coefficient = 0.5
        t1.Clipped = clipped
        t1.TransitionStyle = style
        t1.ForeShoulder = False
        t1.AftShoulder = True
        t1.ForeCapStyle = capStyle
        t1.AftCapStyle = capStyle
        self.Doc.recompute()

        message = type + ": " + style + " Aft Shoulder"
        message += ", " + capStyle
        if clipped:
            message += ", clipped"

        self._checkStyle(t1, message)

        self._reverse(t1)
        message += ", reversed"
        self._checkStyle(t1, message)

    def _testBothShoulder(self, type, style, clipped, capStyle = STYLE_CAP_SOLID):
        t1 = makeTransition('Transition')
        t1.TransitionType = type
        if type == TYPE_POWER:
            t1.Coefficient = 0.5
        t1.Clipped = clipped
        t1.TransitionStyle = style
        t1.ForeShoulder = True
        t1.AftShoulder = True
        t1.ForeCapStyle = capStyle
        t1.AftCapStyle = capStyle
        self.Doc.recompute()

        message = type + ": " + style + " Both Shoulder"
        message += ", " + capStyle
        if clipped:
            message += ", clipped"

        self._checkStyle(t1, message)

        self._reverse(t1)
        message += ", reversed"
        self._checkStyle(t1, message)

    def testTypesSolid(self):
        for type in [TYPE_CONE, TYPE_ELLIPTICAL, TYPE_HAACK, TYPE_OGIVE, TYPE_VON_KARMAN, TYPE_PARABOLA, TYPE_PARABOLIC, TYPE_POWER]:
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
            self._testPlain(type, STYLE_CAPPED, False)
            self._testForeShoulder(type, STYLE_CAPPED, False)
            self._testAftShoulder(type, STYLE_CAPPED, False)
            self._testBothShoulder(type, STYLE_CAPPED, False)
            self._testPlain(type, STYLE_CAPPED, True)
            self._testForeShoulder(type, STYLE_CAPPED, True)
            self._testAftShoulder(type, STYLE_CAPPED, True)
            self._testBothShoulder(type, STYLE_CAPPED, True)

            self._testPlain(type, STYLE_CAPPED, False, STYLE_CAP_BAR)
            self._testForeShoulder(type, STYLE_CAPPED, False, STYLE_CAP_BAR)
            self._testAftShoulder(type, STYLE_CAPPED, False, STYLE_CAP_BAR)
            self._testBothShoulder(type, STYLE_CAPPED, False, STYLE_CAP_BAR)
            self._testPlain(type, STYLE_CAPPED, True, STYLE_CAP_BAR)
            self._testForeShoulder(type, STYLE_CAPPED, True, STYLE_CAP_BAR)
            self._testAftShoulder(type, STYLE_CAPPED, True, STYLE_CAP_BAR)
            self._testBothShoulder(type, STYLE_CAPPED, True, STYLE_CAP_BAR)

            self._testPlain(type, STYLE_CAPPED, False, STYLE_CAP_CROSS)
            self._testForeShoulder(type, STYLE_CAPPED, False, STYLE_CAP_CROSS)
            self._testAftShoulder(type, STYLE_CAPPED, False, STYLE_CAP_CROSS)
            self._testBothShoulder(type, STYLE_CAPPED, False, STYLE_CAP_CROSS)
            self._testPlain(type, STYLE_CAPPED, True, STYLE_CAP_CROSS)
            self._testForeShoulder(type, STYLE_CAPPED, True, STYLE_CAP_CROSS)
            self._testAftShoulder(type, STYLE_CAPPED, True, STYLE_CAP_CROSS)
            self._testBothShoulder(type, STYLE_CAPPED, True, STYLE_CAP_CROSS)
