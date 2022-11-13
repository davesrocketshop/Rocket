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

# from Tests.TestBodyTube import BodyTubeTests
# from Tests.TestBulkhead import BulkheadTests
# from Tests.TestCenteringRing import CenteringRingTests
# from Tests.TestNoses import NoseTests
# from Tests.TestTransition import TransitionTests
# from Tests.TestFlutter import FinFlutterTestCases

from Tests.TestMotor import TestMotorMethods
from Tests.TestNozzle import TestNozzleMethods
from Tests.TestGeometry import TestGeometryMethods
from Tests.TestPropellant import TestPropellantMethods
from Tests.Grains.TestBates import BatesGrainMethods
from Tests.Grains.TestConical import ConicalGrainMethods
from Tests.Grains.TestEndburner import EndBurningGrainMethods

from Tests.Regression.TestCGrain import TestCGrain
# from Tests.TestRegressions import RegressionTestCases
