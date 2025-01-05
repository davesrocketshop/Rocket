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

__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

import unittest

from Tests.TestBodyTube import BodyTubeTests
from Tests.TestBulkhead import BulkheadTests
from Tests.TestCenteringRing import CenteringRingTests
from Tests.TestNoses import NoseTests
from Tests.TestTransition import TransitionTests
from Tests.TestFlutter import FinFlutterTestCases
from Tests.TestFins import FinTests
# from Tests.TestFinCans import FinCanTests
from Tests.Components.RocketTest import RocketTest
from Tests.Components.PositionTests import PositionTests
from Tests.TestMoves import MoveTests

def runRocketUnitTests():
    suite = unittest.TestSuite()
    suite.addTest(unittest.defaultTestLoader.loadTestsFromName("TestRocketApp"))
    r = unittest.TextTestRunner()
    r.run(suite)