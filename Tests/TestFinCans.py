# SPDX-License-Identifier: LGPL-2.1-or-later
# SPDX-FileCopyrightText: 2022 David Carter <dcarter@davidcarter.ca>
# SPDX-File-Notice: Part of the Rocket addon.


"""Class for testing fins"""

__title__ = "FreeCAD Fin Tests"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

import FreeCAD
import unittest

from Rocket.Constants import FIN_TYPE_TRAPEZOID, FIN_TYPE_TRIANGLE, FIN_TYPE_ELLIPSE
from Rocket.Constants import FIN_CROSS_SQUARE, FIN_CROSS_ROUND, FIN_CROSS_AIRFOIL, FIN_CROSS_WEDGE, \
    FIN_CROSS_DIAMOND, FIN_CROSS_TAPER_LE, FIN_CROSS_TAPER_TE, FIN_CROSS_TAPER_LETE, FIN_CROSS_ELLIPSE, FIN_CROSS_BICONVEX
from Rocket.Constants import FINCAN_STYLE_SLEEVE, FINCAN_STYLE_BODYTUBE
from Ui.Commands.CmdFinCan import makeFinCan

class FinCanTests(unittest.TestCase):

    def setUp(self):
        self.Doc = FreeCAD.newDocument("FinTest")

    def tearDown(self):
        FreeCAD.closeDocument(self.Doc.Name)

    def _checkShape(self, feature, message):
        self.assertTrue(feature._obj.Shape.isValid(), message)
        self.assertIsNone(feature._obj.Shape.check(True), message)

    def testBasic(self):
        feature = makeFinCan('FinCan')
        self.Doc.recompute()

        self._checkShape(feature, "Basic")

    def testBasic2(self):
        feature = makeFinCan('FinCan')
        # feature._obj.LaunchLug = False
        # feature._obj.Coupler = True
        feature.setFinCanStyle(FINCAN_STYLE_BODYTUBE)
        self.Doc.recompute()

        self._checkShape(feature, "Basic2")

    def testBasic3(self):
        feature = makeFinCan('FinCan')
        # feature._obj.LaunchLug = False
        # feature._obj.Coupler = True
        feature.setFinCanStyle(FINCAN_STYLE_SLEEVE)
        self.Doc.recompute()

        self._checkShape(feature, "Basic3")

    # def _testCenterTrapezoid(self, crosssection):
    #     feature = makeFinCan('FinCan')
    #     feature._obj.FinType = FIN_TYPE_TRAPEZOID
    #     feature._obj.FinSet = False
    #     feature._obj.SweepLength = feature._obj.RootChord / 2
    #     feature._obj.RootCrossSection = crosssection
    #     feature._obj.TipCrossSection = crosssection
    #     feature._obj.RootPerCent = False
    #     feature._obj.RootLength1 = 10.0
    #     feature._obj.RootLength2 = 10.0
    #     self.Doc.recompute()

    #     message = "Trapezoid: " + crosssection + " Center"

    #     self._checkShape(feature, message)

    # def _testCenterTrapezoidZeroTip(self, crosssection):
    #     feature = makeFinCan('FinCan')
    #     feature._obj.FinType = FIN_TYPE_TRAPEZOID
    #     feature._obj.FinSet = False
    #     feature._obj.SweepLength = feature._obj.RootChord / 2
    #     feature._obj.RootCrossSection = crosssection
    #     feature._obj.TipCrossSection = crosssection
    #     feature._obj.RootPerCent = False
    #     feature._obj.RootLength1 = 10.0
    #     feature._obj.RootLength2 = 10.0
    #     feature._obj.TipChord = 0.0
    #     self.Doc.recompute()

    #     message = "Trapezoid zero tip: " + crosssection + " Center"

    #     self._checkShape(feature, message)

    # def _testCenterEllipse(self, crosssection):
    #     feature = makeFinCan('FinCan')
    #     feature._obj.FinType = FIN_TYPE_ELLIPSE
    #     feature._obj.FinSet = False
    #     feature._obj.SweepLength = feature._obj.RootChord / 2
    #     feature._obj.RootCrossSection = crosssection
    #     feature._obj.RootPerCent = False
    #     feature._obj.RootLength1 = 10.0
    #     feature._obj.RootLength2 = 10.0
    #     self.Doc.recompute()

    #     message = "Ellipse: " + crosssection + " Center"

    #     self._checkShape(feature, message)

    # def _testCenterTriangle(self, crosssection):
    #     feature = makeFinCan('FinCan')
    #     feature._obj.FinType = FIN_TYPE_TRIANGLE
    #     feature._obj.FinSet = False
    #     feature._obj.SweepLength = feature._obj.RootChord / 2
    #     feature._obj.RootCrossSection = crosssection
    #     feature._obj.TipCrossSection = crosssection
    #     feature._obj.RootPerCent = False
    #     feature._obj.RootLength1 = 10.0
    #     feature._obj.RootLength2 = 10.0
    #     self.Doc.recompute()

    #     message = "Triangle: " + crosssection + " Center"

    #     self._checkShape(feature, message)

    # def _testAftSweepTrapezoid(self, crosssection):
    #     feature = makeFinCan('FinCan')
    #     feature._obj.FinType = FIN_TYPE_TRAPEZOID
    #     feature._obj.FinSet = False
    #     feature._obj.SweepLength = (3 * feature._obj.RootChord) / 2.0
    #     feature._obj.RootCrossSection = crosssection
    #     feature._obj.TipCrossSection = crosssection
    #     feature._obj.RootPerCent = False
    #     feature._obj.RootLength1 = 10.0
    #     feature._obj.RootLength2 = 10.0
    #     # feature._obj.TipPerCent = False
    #     # feature._obj.TipLength1 = 10.0
    #     # feature._obj.TipLength2 = 10.0
    #     # feature._obj.TipChord = 0.0
    #     self.Doc.recompute()

    #     message = "Trapezoid: " + crosssection + " Rear Sweep"

    #     self._checkShape(feature, message)

    # def _testAftSweepTrapezoidZeroTip(self, crosssection):
    #     feature = makeFinCan('FinCan')
    #     feature._obj.FinType = FIN_TYPE_TRAPEZOID
    #     feature._obj.FinSet = False
    #     feature._obj.SweepLength = (3 * feature._obj.RootChord) / 2.0
    #     feature._obj.RootCrossSection = crosssection
    #     feature._obj.TipCrossSection = crosssection
    #     feature._obj.RootPerCent = False
    #     feature._obj.RootLength1 = 10.0
    #     feature._obj.RootLength2 = 10.0
    #     feature._obj.TipChord = 0.0
    #     self.Doc.recompute()

    #     message = "Trapezoid zero tip: " + crosssection + " Rear Sweep"

    #     self._checkShape(feature, message)

    # def _testAftSweepTriangle(self, crosssection):
    #     feature = makeFinCan('FinCan')
    #     feature._obj.FinType = FIN_TYPE_TRIANGLE
    #     feature._obj.FinSet = False
    #     feature._obj.SweepLength = (3 * feature._obj.RootChord) / 2.0
    #     feature._obj.RootCrossSection = crosssection
    #     feature._obj.TipCrossSection = crosssection
    #     feature._obj.RootPerCent = False
    #     feature._obj.RootLength1 = 10.0
    #     feature._obj.RootLength2 = 10.0
    #     self.Doc.recompute()

    #     message = "Triangle: " + crosssection + " Rear Sweep"

    #     self._checkShape(feature, message)

    # def _testForeSweepTrapezoid(self, crosssection):
    #     feature = makeFinCan('FinCan')
    #     feature._obj.FinType = FIN_TYPE_TRAPEZOID
    #     feature._obj.FinSet = False
    #     feature._obj.SweepLength = -(3 * feature._obj.RootChord) / 2.0
    #     feature._obj.RootCrossSection = crosssection
    #     feature._obj.TipCrossSection = crosssection
    #     feature._obj.RootPerCent = False
    #     feature._obj.RootLength1 = 10.0
    #     feature._obj.RootLength2 = 10.0
    #     self.Doc.recompute()

    #     message = "Trapezoid: " + crosssection + " Fore Sweep"

    #     self._checkShape(feature, message)

    # def _testForeSweepTrapezoidZeroTip(self, crosssection):
    #     feature = makeFinCan('FinCan')
    #     feature._obj.FinType = FIN_TYPE_TRAPEZOID
    #     feature._obj.FinSet = False
    #     feature._obj.SweepLength = -(3 * feature._obj.RootChord) / 2.0
    #     feature._obj.RootCrossSection = crosssection
    #     feature._obj.TipCrossSection = crosssection
    #     feature._obj.RootPerCent = False
    #     feature._obj.RootLength1 = 10.0
    #     feature._obj.RootLength2 = 10.0
    #     feature._obj.TipChord = 0.0
    #     self.Doc.recompute()

    #     message = "Trapezoid zero tip: " + crosssection + " Fore Sweep"

    #     self._checkShape(feature, message)

    # def _testForeSweepTriangle(self, crosssection):
    #     feature = makeFinCan('FinCan')
    #     feature._obj.FinType = FIN_TYPE_TRIANGLE
    #     feature._obj.FinSet = False
    #     feature._obj.SweepLength = -(3 * feature._obj.RootChord) / 2.0
    #     feature._obj.RootCrossSection = crosssection
    #     feature._obj.TipCrossSection = crosssection
    #     feature._obj.RootPerCent = False
    #     feature._obj.RootLength1 = 10.0
    #     feature._obj.RootLength2 = 10.0
    #     self.Doc.recompute()

    #     message = "Triangle: " + crosssection + " Fore Sweep"

    #     self._checkShape(feature, message)

    # def testTrapezoid(self):
    #     for cross in [FIN_CROSS_SQUARE, FIN_CROSS_ROUND, FIN_CROSS_AIRFOIL, FIN_CROSS_WEDGE, FIN_CROSS_DIAMOND,
    #                 FIN_CROSS_TAPER_LE, FIN_CROSS_TAPER_TE, FIN_CROSS_TAPER_LETE, FIN_CROSS_ELLIPSE, FIN_CROSS_BICONVEX]:
    #         with self.subTest(crosssection=cross):
    #             self._testCenterTrapezoid(cross)
    #             self._testAftSweepTrapezoid(cross)
    #             self._testForeSweepTrapezoid(cross)

    # def testTrapezoidZeroTip(self):
    #     for cross in [FIN_CROSS_SQUARE, FIN_CROSS_ROUND, FIN_CROSS_AIRFOIL, FIN_CROSS_WEDGE, FIN_CROSS_DIAMOND,
    #                 FIN_CROSS_TAPER_LE, FIN_CROSS_TAPER_TE, FIN_CROSS_TAPER_LETE, FIN_CROSS_ELLIPSE, FIN_CROSS_BICONVEX]:
    #         with self.subTest(crosssection=cross):
    #             self._testCenterTrapezoidZeroTip(cross)
    #             self._testAftSweepTrapezoidZeroTip(cross)
    #             self._testForeSweepTrapezoidZeroTip(cross)

    # def testEllipse(self):
    #     for cross in [FIN_CROSS_SQUARE, FIN_CROSS_ROUND, FIN_CROSS_AIRFOIL, FIN_CROSS_WEDGE,
    #                 FIN_CROSS_TAPER_LETE, FIN_CROSS_ELLIPSE, FIN_CROSS_BICONVEX]:
    #         with self.subTest(crosssection=cross):
    #             self._testCenterEllipse(cross)

    # def testTriangular(self):
    #     for cross in [FIN_CROSS_SQUARE, FIN_CROSS_ROUND, FIN_CROSS_AIRFOIL, FIN_CROSS_WEDGE, FIN_CROSS_DIAMOND,
    #                 FIN_CROSS_TAPER_LE, FIN_CROSS_TAPER_TE, FIN_CROSS_TAPER_LETE, FIN_CROSS_ELLIPSE, FIN_CROSS_BICONVEX]:
    #         with self.subTest(crosssection=cross):
    #             self._testCenterTriangle(cross)
    #             self._testAftSweepTriangle(cross)
    #             self._testForeSweepTriangle(cross)
