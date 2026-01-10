# SPDX-License-Identifier: LGPL-2.1-or-later

# ***************************************************************************
# *   Copyright (c) 2021=2025 David Carter <dcarter@davidcarter.ca>         *
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
"""Class for rocket components"""

__title__ = "FreeCAD Rocket Components"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

import math

"""
    Class that defines different cluster configurations available for the InnerTube.
    The class is immutable, and all the constructors are private.  Therefore the only
    available cluster configurations are those available in the static fields.
"""
class ClusterConfiguration:

    def __init__(self, name : str, points : tuple) -> None:
        self._name = name
        self._points = points # This will be a tuple

    def getXMLName(self) -> str:
        return self._name

    def getClusterCount(self) -> int:
        return int(len(self._points) / 2)

    """
        Returns the relative positions of the cluster components.  The list is of length
        <code>2*getClusterCount()</code> with (x,y) value pairs.  The origin is at (0,0)
        and the values are positioned so that the closest clusters have distance of 1.
    """
    def getPoints(self) -> tuple:
        return self._points

    """
        Return the points rotated by <code>rotation</code> radians.
        @param rotation  Rotation amount.
    """
    def getPointsRotated(self, rotation) -> tuple:
        cos = math.cos(rotation)
        sin = math.sin(rotation)
        ret = []
        for i in range(self.getClusterCount()):
            x = self._points[2 * i]
            y = self._points[2 * i + 1]
            ret.append( x*cos + y*sin)
            ret.append(-x*sin + y*cos)

        return tuple(ret)

    def __str__(self):
        return self._name

# Helper variables
R5 = 1.0/(2*math.sin(2*math.pi/10))
SQRT2 = math.sqrt(2)
SQRT3 = math.sqrt(3)

# A single motor
SINGLE = ClusterConfiguration("single", (0,0))

CONFIGURATIONS = {
	"single": SINGLE,
    "double": ClusterConfiguration("double", (-0.5,0, 0.5,0)),
    "3-row": ClusterConfiguration("3-row", (-1.0,0, 0.0,0, 1.0,0)),
    "4-row": ClusterConfiguration("4-row", (-1.5,0, -0.5,0, 0.5,0, 1.5,0)),

    # Ring of tubes
    "3-ring": ClusterConfiguration("3-ring", (-0.5,-1.0/(2*SQRT3),
                                0.5,-1.0/(2*SQRT3),
                                0, 1.0/SQRT3)),
    "4-ring": ClusterConfiguration("4-ring", (-0.5,0.5, 0.5,0.5, 0.5,-0.5, -0.5,-0.5)),
    "5-ring": ClusterConfiguration("5-ring", (0,R5,
                                R5*math.sin(2*math.pi/5),R5*math.cos(2*math.pi/5),
                                R5*math.sin(2*math.pi*2/5),R5*math.cos(2*math.pi*2/5),
                                R5*math.sin(2*math.pi*3/5),R5*math.cos(2*math.pi*3/5),
                                R5*math.sin(2*math.pi*4/5),R5*math.cos(2*math.pi*4/5))),
    "6-ring": ClusterConfiguration("6-ring", (0,1, SQRT3/2,0.5, SQRT3/2,-0.5,
                                0,-1, -SQRT3/2,-0.5, -SQRT3/2,0.5)),

    # Centered with ring
    "3-star": ClusterConfiguration("3-star", (0,0, 0,1, SQRT3/2,-0.5, -SQRT3/2,-0.5)),
    "4-star": ClusterConfiguration("4-star", (0,0, -1/SQRT2,1/SQRT2, 1/SQRT2,1/SQRT2,
                                1/SQRT2,-1/SQRT2, -1/SQRT2,-1/SQRT2)),
    "5-star": ClusterConfiguration("5-star", (0,0, 0,1,
                                math.sin(2*math.pi/5),math.cos(2*math.pi/5),
                                math.sin(2*math.pi*2/5),math.cos(2*math.pi*2/5),
                                math.sin(2*math.pi*3/5),math.cos(2*math.pi*3/5),
                                math.sin(2*math.pi*4/5),math.cos(2*math.pi*4/5))),
    "6-star": ClusterConfiguration("6-star", (0,0, 0,1, SQRT3/2,0.5, SQRT3/2,-0.5,
                                0,-1, -SQRT3/2,-0.5, -SQRT3/2,0.5)),
    "9-grid": ClusterConfiguration("9-grid",  (-1.4,1.4,  0,1.4,  1.4,1.4,
                                        -1.4,0,    0,0,    1.4,0,
                                        -1.4,-1.4, 0,-1.4, 1.4,-1.4)),
    "9-star": ClusterConfiguration("9-star",  (0, 0,
                                1.4,0, 1.4/SQRT2,-1.4/SQRT2, 0,-1.4, -1.4/SQRT2,-1.4/SQRT2,
                                -1.4,0, -1.4/SQRT2,1.4/SQRT2, 0,1.4, 1.4/SQRT2,1.4/SQRT2))

}
