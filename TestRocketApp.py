# SPDX-License-Identifier: LGPL-2.1-or-later
# SPDX-FileCopyrightText: 2022 David Carter <dcarter@davidcarter.ca>
# SPDX-File-Notice: Part of the Rocket addon.


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