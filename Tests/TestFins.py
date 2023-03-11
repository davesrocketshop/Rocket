# ***************************************************************************
# *   Copyright (c) 2022-2023 David Carter <dcarter@davidcarter.ca>         *
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
"""Class for testing fins"""

__title__ = "FreeCAD Fin Tests"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"
    
import FreeCAD
import unittest

from App.Constants import FIN_TYPE_TRAPEZOID, FIN_TYPE_TRIANGLE, FIN_TYPE_ELLIPSE
from App.Constants import FIN_CROSS_SQUARE, FIN_CROSS_ROUND, FIN_CROSS_AIRFOIL, FIN_CROSS_WEDGE, \
    FIN_CROSS_DIAMOND, FIN_CROSS_TAPER_LE, FIN_CROSS_TAPER_TE, FIN_CROSS_TAPER_LETE, FIN_CROSS_ELLIPSE, FIN_CROSS_BICONVEX
from Ui.Commands.CmdFin import makeFin

class FinTests(unittest.TestCase):

    def setUp(self):
        self.Doc = FreeCAD.newDocument("FinTest")

    def _checkShape(self, feature, message):
        self.assertTrue(feature._obj.Shape.isValid(), message)
        self.assertIsNone(feature._obj.Shape.check(True), message)

    def testBasic(self):
        feature = makeFin('Fin')
        self.Doc.recompute()

        self._checkShape(feature, "Basic")

    def _testCenterTrapezoid(self, crosssection):
        feature = makeFin('Fin')
        feature._obj.FinType = FIN_TYPE_TRAPEZOID
        feature._obj.FinSet = False
        feature._obj.SweepLength = feature._obj.RootChord / 2
        feature._obj.RootCrossSection = crosssection
        feature._obj.TipCrossSection = crosssection
        feature._obj.RootPerCent = False
        feature._obj.RootLength1 = 10.0
        feature._obj.RootLength2 = 10.0
        self.Doc.recompute()
        
        message = "Trapezoid: " + crosssection + " Center"

        self._checkShape(feature, message)

    def _testCenterTrapezoidZeroTip(self, crosssection):
        feature = makeFin('Fin')
        feature._obj.FinType = FIN_TYPE_TRAPEZOID
        feature._obj.FinSet = False
        feature._obj.SweepLength = feature._obj.RootChord / 2
        feature._obj.RootCrossSection = crosssection
        feature._obj.TipCrossSection = crosssection
        feature._obj.RootPerCent = False
        feature._obj.RootLength1 = 10.0
        feature._obj.RootLength2 = 10.0
        feature._obj.TipChord = 0.0
        self.Doc.recompute()
        
        message = "Trapezoid zero tip: " + crosssection + " Center"

        self._checkShape(feature, message)

    def _testCenterEllipse(self, crosssection):
        feature = makeFin('Fin')
        feature._obj.FinType = FIN_TYPE_ELLIPSE
        feature._obj.FinSet = False
        feature._obj.SweepLength = feature._obj.RootChord / 2
        feature._obj.RootCrossSection = crosssection
        feature._obj.RootPerCent = False
        feature._obj.RootLength1 = 10.0
        feature._obj.RootLength2 = 10.0
        self.Doc.recompute()
        
        message = "Ellipse: " + crosssection + " Center"

        self._checkShape(feature, message)

    def _testCenterTriangle(self, crosssection):
        feature = makeFin('Fin')
        feature._obj.FinType = FIN_TYPE_TRIANGLE
        feature._obj.FinSet = False
        feature._obj.SweepLength = feature._obj.RootChord / 2
        feature._obj.RootCrossSection = crosssection
        feature._obj.TipCrossSection = crosssection
        feature._obj.RootPerCent = False
        feature._obj.RootLength1 = 10.0
        feature._obj.RootLength2 = 10.0
        self.Doc.recompute()
        
        message = "Triangle: " + crosssection + " Center"

        self._checkShape(feature, message)

    def _testAftSweepTrapezoid(self, crosssection):
        feature = makeFin('Fin')
        feature._obj.FinType = FIN_TYPE_TRAPEZOID
        feature._obj.FinSet = False
        feature._obj.SweepLength = (3 * feature._obj.RootChord) / 2.0
        feature._obj.RootCrossSection = crosssection
        feature._obj.TipCrossSection = crosssection
        feature._obj.RootPerCent = False
        feature._obj.RootLength1 = 10.0
        feature._obj.RootLength2 = 10.0
        # feature._obj.TipPerCent = False
        # feature._obj.TipLength1 = 10.0
        # feature._obj.TipLength2 = 10.0
        # feature._obj.TipChord = 0.0
        self.Doc.recompute()
        
        message = "Trapezoid: " + crosssection + " Rear Sweep"

        self._checkShape(feature, message)

    def _testAftSweepTrapezoidZeroTip(self, crosssection):
        feature = makeFin('Fin')
        feature._obj.FinType = FIN_TYPE_TRAPEZOID
        feature._obj.FinSet = False
        feature._obj.SweepLength = (3 * feature._obj.RootChord) / 2.0
        feature._obj.RootCrossSection = crosssection
        feature._obj.TipCrossSection = crosssection
        feature._obj.RootPerCent = False
        feature._obj.RootLength1 = 10.0
        feature._obj.RootLength2 = 10.0
        feature._obj.TipChord = 0.0
        self.Doc.recompute()
        
        message = "Trapezoid zero tip: " + crosssection + " Rear Sweep"

        self._checkShape(feature, message)

    def _testAftSweepTriangle(self, crosssection):
        feature = makeFin('Fin')
        feature._obj.FinType = FIN_TYPE_TRIANGLE
        feature._obj.FinSet = False
        feature._obj.SweepLength = (3 * feature._obj.RootChord) / 2.0
        feature._obj.RootCrossSection = crosssection
        feature._obj.TipCrossSection = crosssection
        feature._obj.RootPerCent = False
        feature._obj.RootLength1 = 10.0
        feature._obj.RootLength2 = 10.0
        self.Doc.recompute()
        
        message = "Triangle: " + crosssection + " Rear Sweep"

        self._checkShape(feature, message)

    def _testForeSweepTrapezoid(self, crosssection):
        feature = makeFin('Fin')
        feature._obj.FinType = FIN_TYPE_TRAPEZOID
        feature._obj.FinSet = False
        feature._obj.SweepLength = -(3 * feature._obj.RootChord) / 2.0
        feature._obj.RootCrossSection = crosssection
        feature._obj.TipCrossSection = crosssection
        feature._obj.RootPerCent = False
        feature._obj.RootLength1 = 10.0
        feature._obj.RootLength2 = 10.0
        self.Doc.recompute()
        
        message = "Trapezoid: " + crosssection + " Fore Sweep"

        self._checkShape(feature, message)

    def _testForeSweepTrapezoidZeroTip(self, crosssection):
        feature = makeFin('Fin')
        feature._obj.FinType = FIN_TYPE_TRAPEZOID
        feature._obj.FinSet = False
        feature._obj.SweepLength = -(3 * feature._obj.RootChord) / 2.0
        feature._obj.RootCrossSection = crosssection
        feature._obj.TipCrossSection = crosssection
        feature._obj.RootPerCent = False
        feature._obj.RootLength1 = 10.0
        feature._obj.RootLength2 = 10.0
        feature._obj.TipChord = 0.0
        self.Doc.recompute()
        
        message = "Trapezoid zero tip: " + crosssection + " Fore Sweep"

        self._checkShape(feature, message)

    def _testForeSweepTriangle(self, crosssection):
        feature = makeFin('Fin')
        feature._obj.FinType = FIN_TYPE_TRIANGLE
        feature._obj.FinSet = False
        feature._obj.SweepLength = -(3 * feature._obj.RootChord) / 2.0
        feature._obj.RootCrossSection = crosssection
        feature._obj.TipCrossSection = crosssection
        feature._obj.RootPerCent = False
        feature._obj.RootLength1 = 10.0
        feature._obj.RootLength2 = 10.0
        self.Doc.recompute()
        
        message = "Triangle: " + crosssection + " Fore Sweep"

        self._checkShape(feature, message)

    def testTrapezoid(self):
        for cross in [FIN_CROSS_SQUARE, FIN_CROSS_ROUND, FIN_CROSS_AIRFOIL, FIN_CROSS_WEDGE, FIN_CROSS_DIAMOND, 
                    FIN_CROSS_TAPER_LE, FIN_CROSS_TAPER_TE, FIN_CROSS_TAPER_LETE, FIN_CROSS_ELLIPSE, FIN_CROSS_BICONVEX]:
            with self.subTest(crosssection=cross):
                self._testCenterTrapezoid(cross)
                self._testAftSweepTrapezoid(cross)
                self._testForeSweepTrapezoid(cross)

    def testTrapezoidZeroTip(self):
        for cross in [FIN_CROSS_SQUARE, FIN_CROSS_ROUND, FIN_CROSS_AIRFOIL, FIN_CROSS_WEDGE, FIN_CROSS_DIAMOND, 
                    FIN_CROSS_TAPER_LE, FIN_CROSS_TAPER_TE, FIN_CROSS_TAPER_LETE, FIN_CROSS_ELLIPSE, FIN_CROSS_BICONVEX]:
            with self.subTest(crosssection=cross):
                self._testCenterTrapezoidZeroTip(cross)
                self._testAftSweepTrapezoidZeroTip(cross)
                self._testForeSweepTrapezoidZeroTip(cross)

    def testEllipse(self):
        for cross in [FIN_CROSS_SQUARE, FIN_CROSS_ROUND, FIN_CROSS_AIRFOIL, FIN_CROSS_WEDGE, 
                    FIN_CROSS_TAPER_LETE, FIN_CROSS_ELLIPSE, FIN_CROSS_BICONVEX]:
            with self.subTest(crosssection=cross):
                self._testCenterEllipse(cross)

    def testTriangular(self):
        for cross in [FIN_CROSS_SQUARE, FIN_CROSS_ROUND, FIN_CROSS_AIRFOIL, FIN_CROSS_WEDGE, FIN_CROSS_DIAMOND, 
                    FIN_CROSS_TAPER_LE, FIN_CROSS_TAPER_TE, FIN_CROSS_TAPER_LETE, FIN_CROSS_ELLIPSE, FIN_CROSS_BICONVEX]:
            with self.subTest(crosssection=cross):
                self._testCenterTriangle(cross)
                self._testAftSweepTriangle(cross)
                self._testForeSweepTriangle(cross)
