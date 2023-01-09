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
"""Class for testing nose cones"""

__title__ = "FreeCAD Nose Cone Tests"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"
    
import FreeCAD
import unittest

from App.Constants import TYPE_CONE, TYPE_BLUNTED_CONE, TYPE_SPHERICAL, TYPE_ELLIPTICAL, TYPE_HAACK, TYPE_OGIVE, TYPE_BLUNTED_OGIVE, TYPE_SECANT_OGIVE, TYPE_VON_KARMAN, TYPE_PARABOLA, TYPE_PARABOLIC, TYPE_POWER
from App.Constants import STYLE_CAPPED, STYLE_HOLLOW, STYLE_SOLID
from App.Constants import STYLE_CAP_SOLID, STYLE_CAP_BAR, STYLE_CAP_CROSS

from Ui.CmdNoseCone import makeNoseCone

class NoseTests(unittest.TestCase):

    def setUp(self):
        self.Doc = FreeCAD.newDocument("NoseTest")

    def _checkShape(self, feature, message):
        self.assertTrue(feature.Shape.isValid(), message)
        self.assertIsNone(feature.Shape.check(True), message)

    def testBasic(self):
        feature = makeNoseCone('NoseCone')
        self.Doc.recompute()

        self._checkShape(feature, "Basic")

    def _testPlain(self, type, style, capStyle = STYLE_CAP_SOLID):
        feature = makeNoseCone('NoseCone')
        feature.NoseType = type
        if type == TYPE_POWER:
            feature.Coefficient = 0.5
        feature.NoseStyle = style
        feature.Shoulder = False
        feature.CapStyle = capStyle
        self.Doc.recompute()
        
        message = type + ": " + style + " Plain"
        message += ", " + capStyle

        self._checkShape(feature, message)

    def _testShoulder(self, type, style, capStyle = STYLE_CAP_SOLID):
        feature = makeNoseCone('NoseCone')
        feature.NoseType = type
        if type == TYPE_POWER:
            feature.Coefficient = 0.5
        feature.NoseStyle = style
        feature.Shoulder = True
        feature.CapStyle = capStyle
        self.Doc.recompute()
        
        message = type + ": " + style + " Plain"
        message += ", " + capStyle

        self._checkShape(feature, message)

    def testTypesSolid(self):
        for type in [TYPE_CONE, TYPE_BLUNTED_CONE, TYPE_SPHERICAL, TYPE_ELLIPTICAL, TYPE_HAACK, TYPE_OGIVE, TYPE_BLUNTED_OGIVE, 
                        TYPE_SECANT_OGIVE, TYPE_VON_KARMAN, TYPE_PARABOLA, TYPE_PARABOLIC, TYPE_POWER]:
            with self.subTest(type=type):
                self._testPlain(type, STYLE_SOLID)
                self._testShoulder(type, STYLE_SOLID)
                self._testPlain(type, STYLE_SOLID)
                self._testShoulder(type, STYLE_SOLID)
                
    def testTypesHollow(self):
        for type in [TYPE_CONE, TYPE_BLUNTED_CONE, TYPE_SPHERICAL, TYPE_ELLIPTICAL, TYPE_HAACK, TYPE_OGIVE, TYPE_BLUNTED_OGIVE, 
                        TYPE_SECANT_OGIVE, TYPE_VON_KARMAN, TYPE_PARABOLA, TYPE_PARABOLIC, TYPE_POWER]:
            with self.subTest(type=type):
                self._testPlain(type, STYLE_HOLLOW)
                self._testShoulder(type, STYLE_HOLLOW)
                self._testPlain(type, STYLE_HOLLOW)
                self._testShoulder(type, STYLE_HOLLOW)
                
    def testTypesCapped(self):
        for type in [TYPE_CONE, TYPE_BLUNTED_CONE, TYPE_SPHERICAL, TYPE_ELLIPTICAL, TYPE_HAACK, TYPE_OGIVE, TYPE_BLUNTED_OGIVE, 
                        TYPE_SECANT_OGIVE, TYPE_VON_KARMAN, TYPE_PARABOLA, TYPE_PARABOLIC, TYPE_POWER]:
            with self.subTest(type=type):
                for capStyle in [STYLE_CAP_SOLID, STYLE_CAP_BAR, STYLE_CAP_CROSS]:
                    with self.subTest(capStyle=capStyle):
                        self._testPlain(type, STYLE_CAPPED, capStyle)
                        self._testShoulder(type, STYLE_CAPPED, capStyle)
                        self._testPlain(type, STYLE_CAPPED, capStyle)
                        self._testShoulder(type, STYLE_CAPPED, capStyle)
    