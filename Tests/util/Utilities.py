# ***************************************************************************
# *   Copyright (c) 2025 David Carter <dcarter@davidcarter.ca>              *
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
        testCase.assertAlmostEqual(actual._x, expected._x, places=precision)
        testCase.assertAlmostEqual(actual._y, expected._y, places=precision)
        testCase.assertAlmostEqual(actual._z, expected._z, places=precision)
        testCase.assertAlmostEqual(actual._weight, expected._weight, places=precision)
    except AssertionError:
        msg = "actual %s, expected %s: %s" % (str(actual), str(expected), msg)
        testCase.fail(msg)
