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
"""Class for testing geometry functions"""

__title__ = "FreeCAD Geometry Tests"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

import unittest
from App.motor import geometry

class TestGeometryMethods(unittest.TestCase):
    def test_circleArea(self):
        self.assertAlmostEqual(geometry.circleArea(0.5), 0.19634954)

    def test_circlePerimeter(self):
        self.assertAlmostEqual(geometry.circlePerimeter(0.5), 1.57079633)

    def test_circleDiameterFromArea(self):
        self.assertAlmostEqual(geometry.circleDiameterFromArea(0.19634954), 0.5)

    def test_tubeArea(self):
        self.assertAlmostEqual(geometry.tubeArea(0.5, 2), 3.14159265)

    def test_cylinderArea(self):
        self.assertAlmostEqual(geometry.cylinderArea(0.5, 2), 3.53429174)

    def test_cylinderVolume(self):
        self.assertAlmostEqual(geometry.cylinderVolume(0.5, 2), 0.39269908)

    def test_frustumLateralSurfaceArea(self):
        self.assertAlmostEqual(geometry.frustumLateralSurfaceArea(2, 3, 5), 39.46576927)

    def test_frustumVolume(self):
        # Cone case
        self.assertAlmostEqual(geometry.frustumVolume(0, 10, 10), 261.79938779)
        # Frustum case
        self.assertAlmostEqual(geometry.frustumVolume(10, 30, 50), 17016.96020694)

    def test_splitFrustum(self):
        # Simple case
        self.assertAlmostEqual(geometry.splitFrustum(1, 2, 4, 2), ((1, 1.5, 2), (1.5, 2, 2)))
        # Inverted case
        self.assertAlmostEqual(geometry.splitFrustum(2, 1, 4, 2), ((2, 1.5, 2), (1.5, 1, 2)))
        # Make sure that the connected ends of the frustums line up
        upper, lower = geometry.splitFrustum(1, 3, 3, 1)
        self.assertEqual(upper[1], lower[0])

    def test_dist(self):
        self.assertEqual(geometry.dist((5, 5), (5, 5)), 0)
        self.assertEqual(geometry.dist((5, 5), (6, 5)), 1)
        self.assertEqual(geometry.dist((5, 5), (5, 6)), 1)
        self.assertEqual(geometry.dist((0, 0), (-1, -1)), 2 ** 0.5)
