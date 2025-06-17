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

from typing import Any
import math

import FreeCAD
import Part

from Rocket.ShapeHandlers.NoseShapeHandler import NoseShapeHandler


class NoseProxyShapeHandler:
    def __init__(self, obj : Any) -> None:

        # This gets changed when redrawn so it's very important to save a copy
        self._placement = FreeCAD.Placement(obj.Placement)
        self._obj = obj

        # Common parameters
        self._type = str(obj.NoseType)
        if hasattr(obj, "Base"):
            self._base = obj.Base
        else:
            self._base = None

        self._diameter = self._obj.Diameter
        self._proxyPlacement = self._obj.ProxyPlacement
        self._scale = self._obj.Scale
        self._scaleByValue = self._obj.ScaleByValue
        self._scaleByDiameter = self._obj.ScaleByDiameter
        self._autoScaleDiameter = self._obj.AutoScaleDiameter
        self._scaleValue = self._obj.ScaleValue

        self._obj = obj

    def _shapeUnion(self, shape : Part.Shape) -> Part.Shape:
        # This is a hack.
        # Rotate and translate operations apply to placement, meaning later placement
        # operations undo them. By applying a union with a surrounding box this is
        # eliminated
        offset = 1 # offset in mm
        xLength = shape.BoundBox.XLength + 2 * offset
        yLength = shape.BoundBox.YLength + 2 * offset
        zLength = shape.BoundBox.ZLength + 2 * offset
        x = shape.BoundBox.XMin - offset
        y = -(shape.BoundBox.YMax - shape.BoundBox.YMin) / 2.0 - offset
        z = -(shape.BoundBox.ZMax - shape.BoundBox.ZMin) / 2.0 - offset
        point = FreeCAD.Vector(x,y,z)
        direction = FreeCAD.Vector(0, 0, 1)
        box = Part.makeBox(xLength, yLength, zLength, point, direction)
        return shape.common(box)

    def _getShape(self) -> Part.Solid:
        if self._base is None:
            return Part.Shape() # Empty shape

        shape = Part.Shape(self._base.Shape)

        # Apply the rotations
        shape.rotate(FreeCAD.Vector(0,0,0), FreeCAD.Vector(self._proxyPlacement.Rotation.Axis.x, self._proxyPlacement.Rotation.Axis.y, self._proxyPlacement.Rotation.Axis.z), math.degrees(self._proxyPlacement.Rotation.Angle))

        # Apply the scaling
        if self._scale:
            if self._scaleByValue and self._scaleValue.Value > 0.0:
                shape.scale(1.0 / self._scaleValue.Value)
            elif self._scaleByDiameter:
                if self._diameter > 0 and self._scaleValue > 0:
                    shape.scale(self._scaleValue / self._diameter)

        # Translate so the nose is at (0, 0, 0)
        min = shape.BoundBox.XMin
        shape.translate(FreeCAD.Vector(-min, 0, 0))

        return self._shapeUnion(shape)

    def getLength(self) -> float:
        shape = self._getShape()
        if shape is None:
            return 0
        return shape.BoundBox.XLength - self._proxyPlacement.Base.x

    def draw(self) -> None:
        # shape = None

        self._obj.Shape = self._getShape()
        self._obj.Placement = self._placement

    def drawSolidShape(self) -> Part.Solid:
        return self._getShape()
