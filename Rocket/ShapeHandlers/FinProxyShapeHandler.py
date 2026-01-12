# SPDX-License-Identifier: LGPL-2.1-or-later
# SPDX-File-Notice: Part of the Rocket addon.

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
from Part import Shape
import MeshPart

from Rocket.cfd.parea import calculateProjectedArea

from Rocket.Constants import FEATURE_FINCAN

_linearDeflection = 0.5 # Linear deflection for a rough mesh with a fast calculation

class FinProxyShapeHandler:
    def __init__(self, obj : Any) -> None:

        # This gets changed when redrawn so it's very important to save a copy
        self._placement = FreeCAD.Placement(obj.Placement)
        self._obj = obj

        self._shape = None

        # Common parameters
        self._type = str(obj.FinType)
        if hasattr(obj, "Base"):
            self._base = obj.Base
        else:
            self._base = None

        # self._diameter = self._obj.Diameter
        self._diameter = float(self._obj.ParentRadius) * 2.0
        self._parentRadius = float(self._obj.ParentRadius)
        self._proxyPlacement = self._obj.ProxyPlacement
        self._cant = float(self._obj.Cant)

        self._finSet = bool(self._obj.FinSet)
        self._fincount = int(self._obj.FinCount)
        self._finSpacing = float(self._obj.FinSpacing)

        # self._scale = bool(self._obj.Scale)
        # self._scaleByValue = bool(self._obj.ScaleByValue)
        # self._scaleByDiameter = bool(self._obj.ScaleByDiameter)
        # self._autoScaleDiameter = bool(self._obj.AutoScaleDiameter)
        # self._scaleValue = float(self._obj.ScaleValue.Value)

        if self._obj.Proxy.Type == FEATURE_FINCAN:
            self._radius = float(self._obj.Diameter.Value) / 2.0
        else:
            self._radius = 0.0

        # Apply scaling
        self._scale = 1.0
        if obj.Proxy.isScaled():
            self._scale = 1.0 / obj.Proxy.getScale()
            if not self._isParentDiameterScaled(): # May already be scaled
                self._parentRadius *= self._scale

    def _isParentDiameterScaled(self) -> bool:
        if self._obj.Proxy.hasParent():
            return self._obj.Proxy.getParent().isScaled()
        return False

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
        y = shape.BoundBox.YMin - offset
        z = shape.BoundBox.ZMin - offset
        point = FreeCAD.Vector(x,y,z)
        direction = FreeCAD.Vector(0, 0, 1)
        box = Part.makeBox(xLength, yLength, zLength, point, direction)
        return shape.common(box)

    # def _getScale(self) -> float:
    #     scale = 1.0
    #     if self._scale:
    #         if self._scaleByValue and self._scaleValue.Value > 0.0:
    #             scale = 1.0 / self._scaleValue.Value
    #         elif self._scaleByDiameter:
    #             if self._diameter > 0 and self._scaleValue > 0:
    #                 scale = self._scaleValue / self._diameter

    #     return float(scale)

    def _getShape(self) -> Part.Solid:
        if self._shape:
            return self._shape

        if self._base is None:
            return Part.Shape() # Empty shape

        shape = Part.Shape(self._base.Shape)

        # Apply the rotations
        shape.rotate(FreeCAD.Vector(0,0,0), FreeCAD.Vector(self._proxyPlacement.Rotation.Axis.x, self._proxyPlacement.Rotation.Axis.y, self._proxyPlacement.Rotation.Axis.z), math.degrees(self._proxyPlacement.Rotation.Angle))

        # Apply the scaling
        # scale = self._getScale()
        if self._scale > 0:
            shape.scale(self._scale)

        # Translate so the fin is at (0, 0, 0)
        min = shape.BoundBox.XMin
        shape.translate(FreeCAD.Vector(-min, 0, 0))
        # shape.translate(FreeCAD.Vector(-min, 0, self._parentRadius))

        self._shape = self._shapeUnion(shape)
        return self._shape

    # def getRadius(self, x : float) -> float:
    #     # Apply the scaling
    #     # scale = self._getScale()
    #     # return scale * (self._diameter / 2.0)
    #     return self._radius

    def getLength(self) -> float:
        shape = self._getShape()
        if shape is None:
            return 0
        return float(shape.BoundBox.XLength - self._proxyPlacement.Base.x)

    def _getTubeRadius(self) -> float:
        if hasattr(self._obj, "Diameter"):
            # This is for fin cans
            return self._radius

        return self._parentRadius

    def _drawFinSet(self, offset : float = 0) -> Shape:
        fins = []
        base = self._getShape()
        baseX = 0
        # if hasattr(self._obj, "LeadingEdgeOffset"):
        #     baseX = self._leadingEdgeOffset
        for i in range(self._fincount):
            fin = Part.Shape(base) # Create a copy
            # if self._cant != 0:
            #     fin.rotate(FreeCAD.Vector(self._rootChord / 2, 0, 0), FreeCAD.Vector(0,0,1), self._cant)
            radius = self._getTubeRadius()
            fin.translate(FreeCAD.Vector(baseX, (fin.BoundBox.YLength / 2.0) + self._proxyPlacement.Base.y, radius + self._proxyPlacement.Base.z))
            fin.rotate(FreeCAD.Vector(0, 0, 0), FreeCAD.Vector(1,0,0), i * self._finSpacing)
            fins.append(fin)

        return Part.makeCompound(fins)

    def draw(self) -> None:
        # shape = None

        if self._finSet:
            self._obj.Shape = self._drawFinSet()
        else:
            self._obj.Shape = self._getShape()
        self._obj.Placement = self._placement

    def drawSolidShape(self) -> Part.Solid:
        return self._getShape()

    def area(self) -> float:
        #
        # Returns the areaa of the fin in the XZ palne
        shape = self._getShape()
        if shape is None:
            return 0.0
        
        # Create a crude mesh and project it on to the YZ plane to calculate the frontal area
        mesh = MeshPart.meshFromShape(shape, LinearDeflection=_linearDeflection)

        area = calculateProjectedArea(mesh, plane='XZ')
        return area

    def findHeight(self) -> float:
        shape = self._getShape()
        if shape is None:
            return 0.0

        return shape.BoundBox.ZMax
    
    def finOnlyShape(self) -> Shape:
        fin = self._getShape()
        if fin is None:
            return Part.Shape()
        return fin
