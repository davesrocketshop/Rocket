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
"""Class for testing nozzles"""

__title__ = "FreeCAD Nozzle Tests"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"
    
import FreeCAD
import unittest

from App.motor.Motor import Motor, makeMotor
from App.motor.MotorConfig import MotorConfig
from App.motor.grains.bates import BatesGrain
from App.motor.Propellant import Propellant, PropellantTab
from App.motor.Nozzle import eRatioFromPRatio, Nozzle

from Ui.CmdOpenMotor import makeNozzle

from App.Constants import GRAIN_INHIBITED_NEITHER

class TestNozzleMethods(unittest.TestCase):

    def setUp(self):
        self.Doc = FreeCAD.newDocument("NozzleTest")

    def test_expansionRatioFromPressureRatio(self):
        self.assertAlmostEqual(eRatioFromPRatio(1.15, 0.0156), 0.10650602)

    def test_expansionRatio(self):
        nozzle = makeNozzle()

        nozzle.Throat = FreeCAD.Units.Quantity("0.1 m").Value
        nozzle.Exit = FreeCAD.Units.Quantity("0.2 m").Value
        self.assertAlmostEqual(nozzle.Proxy.calcExpansion(), 4.0)

        nozzle.Throat = FreeCAD.Units.Quantity("0.1 m").Value
        nozzle.Exit = FreeCAD.Units.Quantity("0.3 m").Value
        self.assertAlmostEqual(nozzle.Proxy.calcExpansion(), 9.0)

    def test_getExitPressure(self):
        nozzle = makeNozzle()

        nozzle.Throat = FreeCAD.Units.Quantity("0.1 m").Value
        nozzle.Exit = FreeCAD.Units.Quantity("0.2 m").Value
        self.assertAlmostEqual(nozzle.Proxy.getExitPressure(1.25, 5e6), 197579.76030584713)

        nozzle.Throat = FreeCAD.Units.Quantity("0.1 m").Value
        nozzle.Exit = FreeCAD.Units.Quantity("0.3 m").Value
        self.assertAlmostEqual(nozzle.Proxy.getExitPressure(1.25, 5e6), 63174.14300487552)
        self.assertAlmostEqual(nozzle.Proxy.getExitPressure(1.2, 5e6), 72087.22454540983)
        self.assertAlmostEqual(nozzle.Proxy.getExitPressure(1.2, 6e6), 86504.66945449157)
