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

__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

import FreeCAD, unittest
import math

from Analyzers.pyatmos import coesa76
from Analyzers.FinFlutter import FinFlutter
from Ui.CmdFin import makeFin
from Ui.CmdFinCan import makeFinCan

class RocketTestCases(unittest.TestCase):

    def testCoesa76(self):
        for i in range(1,85):
            geo = coesa76([i])

            # print("[%f, %f, %f, %f]" % (i * 1000.0, geo.rho, geo.T - 273.15, geo.P))


    # def testFlutter(self):
    #     G = 2.620008e+9

class FinFlutterTestCases(unittest.TestCase):
    def setUp(self):
        self.Doc = FreeCAD.newDocument("FlutterTest")

        self._fin = makeFin('FlutterFin')
        self._finCan = makeFinCan('flutterFinCan')
        self.Doc.recompute()

    def _setFin(self, finData):
        self._fin.Height = finData[4]
        self._fin.RootChord = finData[3]
        self._fin.TipChord = finData[5]
        self._fin.RootThickness = finData[0]
        self._fin.TipThickness = finData[0]
        self._fin.SweepLength = finData[3] - finData[5]
        self.Doc.recompute()

    def _setFinTab(self, finData):
        self._fin.Height = finData[4]
        self._fin.RootChord = finData[3]
        self._fin.TipChord = finData[5]
        self._fin.RootThickness = finData[0]
        self._fin.TipThickness = finData[0]
        self._fin.SweepLength = finData[3] - finData[5]

        # Add a fin tab
        self._fin.Ttw = True
        self._fin.TtwOffset = 20.0
        self._fin.TtwLength = float(self._fin.RootChord) - 40.0
        self._fin.TtwHeight = 50.0
        self._fin.TtwThickness = self._fin.RootThickness
        self.Doc.recompute()

    def _setFinCan(self, finData):
        self._finCan.Height = finData[4]
        self._finCan.RootChord = finData[3]
        self._finCan.TipChord = finData[5]
        self._finCan.RootThickness = finData[0]
        self._finCan.TipThickness = finData[0]
        self._finCan.SweepLength = finData[3] - finData[5]

        # Create the fin can
        self._finCan.Length = self._finCan.RootChord

        self.Doc.recompute()

    def _checkTolerance(self, calc, reference, value):
        message = "{0:s} Calculated {1:.2f} reference {2:.2f}"
        self.assertLess(math.fabs((calc - reference) / reference), 0.01, message.format(value, calc, reference)) # < 1% difference

    def _getTestArray(self):

        # Fin array row values
        # [0] = thickness
        # [1] = taper ratio
        # [2] = aspect ratio
        # [3] = root chord
        # [4] = semi-span
        # [5] = tip chord
        # [6] = FEA flutter value
        finArray = []
        finArray.append([0.500, 0.350, 0.750, 513.200, 259.808, 179.620,  16.54, 15.60])
        finArray.append([1.500, 0.350, 0.750, 513.200, 259.808, 179.620,  85.96, 81.06])
        finArray.append([0.500, 0.750, 0.750, 395.897, 259.808, 296.923,  21.44, 15.60])
        finArray.append([1.500, 0.750, 0.750, 395.897, 259.808, 296.923, 111.43, 81.06])
        finArray.append([0.500, 0.350, 2.000, 314.270, 424.264, 109.994,   9.56,  9.02])
        finArray.append([1.500, 0.350, 2.000, 314.270, 424.264, 109.994,  49.68, 46.85])
        finArray.append([0.500, 0.750, 2.000, 242.437, 424.264, 181.827,  12.39,  9.02])
        finArray.append([1.500, 0.750, 2.000, 242.437, 424.264, 181.827,  64.40, 46.85])
        finArray.append([0.159, 0.550, 1.375, 330.117, 351.781, 181.564,   2.39,  1.97])
        finArray.append([1.841, 0.550, 1.375, 330.117, 351.781, 181.564,  94.36, 77.50])
        finArray.append([1.000, 0.214, 1.375, 421.609, 351.781,  90.073,  29.58, 31.03])
        finArray.append([1.000, 0.886, 1.375, 271.254, 351.781, 240.428,  45.97, 31.03])
        finArray.append([1.000, 0.550, 0.324, 680.186, 170.731, 374.102,  92.70, 76.14])
        finArray.append([1.000, 0.550, 2.426, 248.521, 467.280, 136.687,  28.26, 23.21])
        finArray.append([1.000, 0.550, 1.375, 330.117, 351.781, 181.564,  37.77, 31.03])

        return finArray

    def testFins(self):
        finArray = self._getTestArray()

        shearModulus = 7.170e+7 # in kPa, for Al 7075 T651
        altitude = 0 # sea level

        for row in finArray:
            self._setFinTab(row)
            flutter = FinFlutter(self._fin)
            
            results = flutter.flutter(altitude, shearModulus)
            self._checkTolerance(results[1], row[6], "Vf")
            
            results = flutter.divergence(altitude, shearModulus)
            self._checkTolerance(results[1], row[7], "Vd")
            
            results = flutter.flutterPOF(altitude, shearModulus)
            self._checkTolerance(results[1], row[6] * math.sqrt(2), "Vf")

    def testFinWithTabs(self):
        finArray = self._getTestArray()

        shearModulus = 7.170e+7 # in kPa, for Al 7075 T651
        altitude = 0 # sea level

        for row in finArray:
            self._setFin(row)
            flutter = FinFlutter(self._fin)
            
            results = flutter.flutter(altitude, shearModulus)
            self._checkTolerance(results[1], row[6], "Vf")
            
            results = flutter.divergence(altitude, shearModulus)
            self._checkTolerance(results[1], row[7], "Vd")
            
            results = flutter.flutterPOF(altitude, shearModulus)
            self._checkTolerance(results[1], row[6] * math.sqrt(2), "Vf")

    def testFinCan(self):
        finArray = self._getTestArray()

        shearModulus = 7.170e+7 # in kPa, for Al 7075 T651
        altitude = 0 # sea level

        for row in finArray:
            self._setFin(row)
            flutter = FinFlutter(self._fin)
            
            results = flutter.flutter(altitude, shearModulus)
            self._checkTolerance(results[1], row[6], "Vf")
            
            results = flutter.divergence(altitude, shearModulus)
            self._checkTolerance(results[1], row[7], "Vd")
            
            results = flutter.flutterPOF(altitude, shearModulus)
            self._checkTolerance(results[1], row[6] * math.sqrt(2), "Vf")


    def tearDown(self):
        #closing doc
        FreeCAD.closeDocument("FlutterTest")
        #print ("omit closing document for debugging")
