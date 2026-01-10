# SPDX-License-Identifier: LGPL-2.1-or-later
# SPDX-FileCopyrightText: 2022 David Carter <dcarter@davidcarter.ca>
# SPDX-File-Notice: Part of the Rocket addon.


__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

import unittest

from Tests.Integration.RocketTest import RocketTest
from Tests.Integration.PositionTests import PositionTests
from Tests.TestMoves import MoveTests
from Tests.TestFinCans import FinCanTests

def runRocketUnitTests():
    suite = unittest.TestSuite()
    suite.addTest(unittest.defaultTestLoader.loadTestsFromName("TestRocketGui"))
    r = unittest.TextTestRunner()
    r.run(suite)