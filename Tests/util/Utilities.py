# SPDX-License-Identifier: LGPL-2.1-or-later
# SPDX-FileCopyrightText: 2025 David Carter <dcarter@davidcarter.ca>
# SPDX-File-Notice: Part of the Rocket addon.


"""General testing utilities for the Rocket Workbench"""

__title__ = "FreeCAD Test Utilities"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

# import FreeCAD
import unittest

from Rocket.util.Coordinate import Coordinate

def assertCoordinateEqual(testCase : unittest.TestCase,
                          actual : Coordinate,
                          expected : Coordinate,
                          msg : str,
                          precision : int = 7) -> None:
    try:
        testCase.assertAlmostEqual(actual.x, expected.x, places=precision)
        testCase.assertAlmostEqual(actual.y, expected.y, places=precision)
        testCase.assertAlmostEqual(actual.z, expected.z, places=precision)
        testCase.assertAlmostEqual(actual._weight, expected._weight, places=precision)
    except AssertionError:
        msg = "actual %s, expected %s: %s" % (str(actual), str(expected), msg)
        testCase.fail(msg)
