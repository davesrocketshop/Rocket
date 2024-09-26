# ***************************************************************************
# *   Copyright (c) 2024 David Carter <dcarter@davidcarter.ca>              *
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
"""Class for creating a solid rocket model"""

__title__ = "FreeCAD Create Solid"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

import FreeCAD
import Part
import math

from DraftTools import translate

from Rocket.Constants import FINCAN_EDGE_SQUARE, FINCAN_EDGE_ROUND, FINCAN_EDGE_TAPER
from Rocket.Constants import FINCAN_COUPLER_STEPPED
from Rocket.Utilities import validationError, _err

from Rocket.ShapeHandlers.FinShapeHandler import FinShapeHandler
from Rocket.ShapeHandlers.FinTrapezoidShapeHandler import FinTrapezoidShapeHandler
from Rocket.ShapeHandlers.FinTriangleShapeHandler import FinTriangleShapeHandler
from Rocket.ShapeHandlers.FinEllipseShapeHandler import FinEllipseShapeHandler
from Rocket.ShapeHandlers.FinSketchShapeHandler import FinSketchShapeHandler

TOLERANCE_OFFSET = 0.5     # Distance to offset a vertex

# class CreateSolid():

#     def __init__(self, obj):
#         # super().__init__(obj)
#         self._root = obj

def getProxy(obj):
    if hasattr(obj, "Proxy"):
        return obj.Proxy
    return obj

def createSolid(obj):
    ''' Currently generates a compound object, not necessarily solid '''
    shape = None
    for current in getProxy(obj).getChildren():
        if hasattr(current, "Shape"):
            if shape == None:
                shape = current.Shape
            else:
                shape = Part.makeCompound([shape, current.Shape])
        child = createSolid(current)
        if child is not None:
            if shape == None:
                shape = child
            else:
                shape = Part.makeCompound([shape, child])

    return shape
