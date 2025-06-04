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
"""Class for drawing proxy nose cones"""

__title__ = "FreeCAD proxy Nose Shape Handler"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

import FreeCAD
import Part

from Rocket.ShapeHandlers.NoseShapeHandler import NoseShapeHandler


class NoseProxyShapeHandler:
    def __init__(self, obj):

        # This gets changed when redrawn so it's very important to save a copy
        self._placement = FreeCAD.Placement(obj.Placement)

        # Common parameters
        self._type = str(obj.NoseType)
        if hasattr(obj, "Base"):
            self._base = obj.Base
        else:
            self._base = None

        self._obj = obj

    def draw(self):
        # shape = None

        if self._base is not None:
            self._obj.Shape = self._base.Shape
        else:
            self._obj.Shape = Part.Shape() # Empty shape
        self._obj.Placement = self._placement

    def drawSolidShape(self):
        if self._base is not None:
            return self._base.Shape
        return None
