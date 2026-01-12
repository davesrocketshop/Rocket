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


"""Class for testing fins"""

__title__ = "FreeCAD Fin Tests"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

import FreeCAD
import unittest

from Rocket.Constants import FIN_TYPE_TRAPEZOID, FIN_TYPE_TRIANGLE, FIN_TYPE_ELLIPSE
from Rocket.Constants import FIN_CROSS_SQUARE, FIN_CROSS_ROUND, FIN_CROSS_AIRFOIL, FIN_CROSS_WEDGE, \
    FIN_CROSS_DIAMOND, FIN_CROSS_TAPER_LE, FIN_CROSS_TAPER_TE, FIN_CROSS_TAPER_LETE, FIN_CROSS_ELLIPSE, FIN_CROSS_BICONVEX
from Ui.Commands.CmdFin import makeFin

class FinTests(unittest.TestCase):

    def setUp(self):
        self.Doc = FreeCAD.newDocument("FinTest")

    def tearDown(self):
        FreeCAD.closeDocument(self.Doc.Name)

    def _checkShape(self, feature, message):
        self.assertTrue(feature._obj.Shape.isValid(), message)
        self.assertIsNone(feature._obj.Shape.check(True), message)

    def testBasic(self):
        feature = makeFin('Fin')
        self.Doc.recompute()

        self._checkShape(feature, "Basic")

    def _testCenterTrapezoid(self, crosssection, minEdge):
        feature = makeFin('Fin')
        feature._obj.FinType = FIN_TYPE_TRAPEZOID
        feature._obj.FinSet = False
        feature.setSweepLength(feature._obj.RootChord / 2) # Also sets sweep angle
        feature._obj.RootCrossSection = crosssection
        feature._obj.TipCrossSection = crosssection
        feature._obj.RootPerCent = False
        feature._obj.RootLength1 = 10.0
        feature._obj.RootLength2 = float(feature._obj.RootChord) - 10.0
        feature._obj.MinimumEdge = minEdge
        self.Doc.recompute()

        message = "Trapezoid: " + crosssection + " Center"

        self._checkShape(feature, message)

    def _testCenterTrapezoidZeroTip(self, crosssection, minEdge):
        feature = makeFin('Fin')
        feature._obj.FinType = FIN_TYPE_TRAPEZOID
        feature._obj.FinSet = False
        feature.setSweepLength(feature._obj.RootChord / 2) # Also sets sweep angle
        feature._obj.RootCrossSection = crosssection
        feature._obj.TipCrossSection = crosssection
        feature._obj.RootPerCent = False
        feature._obj.RootLength1 = 10.0
        feature._obj.RootLength2 = float(feature._obj.RootChord) - 10.0
        feature._obj.TipChord = 0.0
        feature._obj.MinimumEdge = minEdge
        self.Doc.recompute()

        message = "Trapezoid zero tip: " + crosssection + " Center"

        self._checkShape(feature, message)

    def _testCenterEllipse(self, crosssection, minEdge):
        feature = makeFin('Fin')
        feature._obj.FinType = FIN_TYPE_ELLIPSE
        feature._obj.FinSet = False
        feature.setSweepLength(feature._obj.RootChord / 2) # Also sets sweep angle
        feature._obj.RootCrossSection = crosssection
        feature._obj.RootPerCent = False
        feature._obj.RootLength1 = 10.0
        feature._obj.RootLength2 = float(feature._obj.RootChord) - 10.0
        feature._obj.MinimumEdge = minEdge
        self.Doc.recompute()

        message = "Ellipse: " + crosssection + " Center"

        self._checkShape(feature, message)

    def _testCenterTriangle(self, crosssection, minEdge):
        feature = makeFin('Fin')
        feature._obj.FinType = FIN_TYPE_TRIANGLE
        feature._obj.FinSet = False
        feature.setSweepLength(feature._obj.RootChord / 2) # Also sets sweep angle
        feature._obj.RootCrossSection = crosssection
        feature._obj.TipCrossSection = crosssection
        feature._obj.RootPerCent = False
        feature._obj.RootLength1 = 10.0
        feature._obj.RootLength2 = float(feature._obj.RootChord) - 10.0
        feature._obj.MinimumEdge = minEdge
        self.Doc.recompute()

        message = "Triangle: " + crosssection + " Center"

        self._checkShape(feature, message)

    def _testAftSweepTrapezoid(self, crosssection, minEdge):
        feature = makeFin('Fin')
        feature._obj.FinType = FIN_TYPE_TRAPEZOID
        feature._obj.FinSet = False
        feature.setSweepLength((3 * feature._obj.RootChord) / 2.0)
        feature._obj.RootCrossSection = crosssection
        feature._obj.TipCrossSection = crosssection
        feature._obj.RootPerCent = False
        feature._obj.RootLength1 = 10.0
        feature._obj.RootLength2 = float(feature._obj.RootChord) - 10.0
        feature._obj.MinimumEdge = minEdge
        self.Doc.recompute()

        message = "Trapezoid: " + crosssection + " Rear Sweep"

        self._checkShape(feature, message)

    def _testAftSweepTrapezoidZeroTip(self, crosssection, minEdge):
        feature = makeFin('Fin')
        feature._obj.FinType = FIN_TYPE_TRAPEZOID
        feature._obj.FinSet = False
        feature.setSweepLength((3 * feature._obj.RootChord) / 2.0)
        feature._obj.RootCrossSection = crosssection
        feature._obj.TipCrossSection = crosssection
        feature._obj.RootPerCent = False
        feature._obj.RootLength1 = 10.0
        feature._obj.RootLength2 = float(feature._obj.RootChord) - 10.0
        feature._obj.TipChord = 0.0
        feature._obj.MinimumEdge = minEdge
        self.Doc.recompute()

        message = "Trapezoid zero tip: " + crosssection + " Rear Sweep"

        self._checkShape(feature, message)

    def _testAftSweepTriangle(self, crosssection, minEdge):
        feature = makeFin('Fin')
        feature._obj.FinType = FIN_TYPE_TRIANGLE
        feature._obj.FinSet = False
        feature.setSweepLength((3 * feature._obj.RootChord) / 2.0)
        feature._obj.RootCrossSection = crosssection
        feature._obj.TipCrossSection = crosssection
        feature._obj.RootPerCent = False
        feature._obj.RootLength1 = 10.0
        feature._obj.RootLength2 = float(feature._obj.RootChord) - 10.0
        feature._obj.MinimumEdge = minEdge
        self.Doc.recompute()

        message = "Triangle: " + crosssection + " Rear Sweep"

        self._checkShape(feature, message)

    def _testForeSweepTrapezoid(self, crosssection, minEdge):
        feature = makeFin('Fin')
        feature._obj.FinType = FIN_TYPE_TRAPEZOID
        feature._obj.FinSet = False
        feature.setSweepLength(-(3 * feature._obj.RootChord) / 2.0)
        feature._obj.RootCrossSection = crosssection
        feature._obj.TipCrossSection = crosssection
        feature._obj.RootPerCent = False
        feature._obj.RootLength1 = 10.0
        feature._obj.RootLength2 = float(feature._obj.RootChord) - 10.0
        feature._obj.MinimumEdge = minEdge
        self.Doc.recompute()

        message = "Trapezoid: " + crosssection + " Fore Sweep"

        self._checkShape(feature, message)

    def _testForeSweepTrapezoidZeroTip(self, crosssection, minEdge):
        feature = makeFin('Fin')
        feature._obj.FinType = FIN_TYPE_TRAPEZOID
        feature._obj.FinSet = False
        feature.setSweepLength(-(3 * feature._obj.RootChord) / 2.0)
        feature._obj.RootCrossSection = crosssection
        feature._obj.TipCrossSection = crosssection
        feature._obj.RootPerCent = False
        feature._obj.RootLength1 = 10.0
        feature._obj.RootLength2 = float(feature._obj.RootChord) - 10.0
        feature._obj.TipChord = 0.0
        feature._obj.MinimumEdge = minEdge
        self.Doc.recompute()

        message = "Trapezoid zero tip: " + crosssection + " Fore Sweep"

        self._checkShape(feature, message)

    def _testForeSweepTriangle(self, crosssection, minEdge):
        feature = makeFin('Fin')
        feature._obj.FinType = FIN_TYPE_TRIANGLE
        feature._obj.FinSet = False
        feature.setSweepLength(-(3 * feature._obj.RootChord) / 2.0)
        feature._obj.RootCrossSection = crosssection
        feature._obj.TipCrossSection = crosssection
        feature._obj.RootPerCent = False
        feature._obj.RootLength1 = 10.0
        feature._obj.RootLength2 = float(feature._obj.RootChord) - 10.0
        feature._obj.MinimumEdge = minEdge
        self.Doc.recompute()

        message = "Triangle: " + crosssection + " Fore Sweep"

        self._checkShape(feature, message)

    def testTrapezoid(self):
        for cross in [FIN_CROSS_SQUARE, FIN_CROSS_ROUND, FIN_CROSS_AIRFOIL, FIN_CROSS_WEDGE, FIN_CROSS_DIAMOND,
                    FIN_CROSS_TAPER_LE, FIN_CROSS_TAPER_TE, FIN_CROSS_TAPER_LETE, FIN_CROSS_ELLIPSE, FIN_CROSS_BICONVEX]:
            with self.subTest(crosssection=cross):
                for minEdge in [False, True]:
                    with self.subTest(minimumEdge=minEdge):
                        self._testCenterTrapezoid(cross, minEdge)
                        self._testAftSweepTrapezoid(cross, minEdge)
                        self._testForeSweepTrapezoid(cross, minEdge)

    def testTrapezoidZeroTip(self):
        for cross in [FIN_CROSS_SQUARE, FIN_CROSS_ROUND, FIN_CROSS_AIRFOIL, FIN_CROSS_WEDGE, FIN_CROSS_DIAMOND,
                    FIN_CROSS_TAPER_LE, FIN_CROSS_TAPER_TE, FIN_CROSS_TAPER_LETE, FIN_CROSS_ELLIPSE, FIN_CROSS_BICONVEX]:
            with self.subTest(crosssection=cross):
                for minEdge in [False, True]:
                    with self.subTest(minimumEdge=minEdge):
                        self._testCenterTrapezoidZeroTip(cross, minEdge)
                        self._testAftSweepTrapezoidZeroTip(cross, minEdge)
                        self._testForeSweepTrapezoidZeroTip(cross, minEdge)

    def testEllipse(self):
        for cross in [FIN_CROSS_SQUARE, FIN_CROSS_ROUND, FIN_CROSS_AIRFOIL, FIN_CROSS_WEDGE,
                    FIN_CROSS_TAPER_LETE, FIN_CROSS_ELLIPSE, FIN_CROSS_BICONVEX]:
            with self.subTest(crosssection=cross):
                for minEdge in [False, True]:
                    with self.subTest(minimumEdge=minEdge):
                        self._testCenterEllipse(cross, minEdge)

    def testTriangular(self):
        for cross in [FIN_CROSS_SQUARE, FIN_CROSS_ROUND, FIN_CROSS_AIRFOIL, FIN_CROSS_WEDGE, FIN_CROSS_DIAMOND,
                    FIN_CROSS_TAPER_LE, FIN_CROSS_TAPER_TE, FIN_CROSS_TAPER_LETE, FIN_CROSS_ELLIPSE, FIN_CROSS_BICONVEX]:
            with self.subTest(crosssection=cross):
                for minEdge in [False, True]:
                    with self.subTest(minimumEdge=minEdge):
                        self._testCenterTriangle(cross, minEdge)
                        self._testAftSweepTriangle(cross, minEdge)
                        self._testForeSweepTriangle(cross, minEdge)
