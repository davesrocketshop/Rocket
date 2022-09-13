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

from Analyzers.pyatmos import coesa76
from Analyzers.FinFlutter import FinFlutter
from Ui.CmdFin import makeFin

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
        self.Doc.recompute()

    def _setFin(self, finData):
        self._fin.Height = finData[4]
        self._fin.RootChord = finData[3]
        self._fin.TipChord = finData[5]
        self._fin.RootThickness = finData[0]
        self._fin.TipThickness = finData[0]
        self._fin.SweepLength = finData[3] - finData[5]
        self.Doc.recompute()

    def testFins(self):

        # Fin array row values
        # [0] = thickness
        # [1] = taper ratio
        # [2] = aspect ratio
        # [3] = root chord
        # [4] = semi-span
        # [5] = tip chord
        # [6] = FEA flutter value
        finArray = []
        finArray.append([0.500, 0.350, 0.750, 513.200, 259.808, 179.620,  27.36])
        finArray.append([1.500, 0.350, 0.750, 513.200, 259.808, 179.620, 135.18])
        finArray.append([0.500, 0.750, 0.750, 395.897, 259.808, 296.923,  26.34])
        finArray.append([1.500, 0.750, 0.750, 395.897, 259.808, 296.923, 125.06])
        finArray.append([0.500, 0.350, 2.000, 314.270, 424.264, 109.994,  14.73])
        finArray.append([1.500, 0.350, 2.000, 314.270, 424.264, 109.994,  74.01])
        finArray.append([0.500, 0.750, 2.000, 242.437, 424.264, 181.827,  13.33])
        finArray.append([1.500, 0.750, 2.000, 242.437, 424.264, 181.827,  65.47])
        finArray.append([0.159, 0.550, 1.375, 330.117, 351.781, 181.564,   3.83])
        finArray.append([1.841, 0.550, 1.375, 330.117, 351.781, 181.564, 116.41])
        finArray.append([1.000, 0.214, 1.375, 421.609, 351.781,  90.073,  51.55])
        finArray.append([1.000, 0.886, 1.375, 271.254, 351.781, 240.428,  44.40])
        finArray.append([1.000, 0.550, 0.324, 680.186, 170.731, 374.102, 141.06])
        finArray.append([1.000, 0.550, 2.426, 248.521, 467.280, 136.687,  34.61])
        finArray.append([1.000, 0.550, 1.375, 330.117, 351.781, 181.564,  47.21])

        sheerModulus = 7.170e+10 # in Pascals, for Al 7075 T651
        altitude = 0 # sea level

        for row in finArray:
            self._setFin(row)
            flutter = FinFlutter(self._fin)
            
            print('***')
            results = flutter.flutter(altitude, sheerModulus)

            # Vf = FreeCAD.Units.Quantity(str(flutter[1]) + "m/s")
            # self.flutterInput.setText(Vf.UserString)
            # # self.flutterInput.setText(str(flutter[1]) + "m/s")

            # Vd = FreeCAD.Units.Quantity(str(flutter[3]) + "m/s")
            # self.divergenceInput.setText(Vd.UserString)


    def tearDown(self):
        #closing doc
        FreeCAD.closeDocument("FlutterTest")
        #print ("omit closing document for debugging")
