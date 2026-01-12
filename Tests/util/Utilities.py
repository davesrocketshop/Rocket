# SPDX-License-Identifier: LGPL-2.1-or-later
# SPDX-File-Notice: Part of the Rocket addon.

################################################################################
#                                                                              #
#   © 2025 David Carter <dcarter@davidcarter.ca>                               #
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
