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
