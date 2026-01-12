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

def runRocketUnitTests():
    suite = unittest.TestSuite()
    suite.addTest(unittest.defaultTestLoader.loadTestsFromName("TestRocketApp"))
    r = unittest.TextTestRunner()
    r.run(suite)