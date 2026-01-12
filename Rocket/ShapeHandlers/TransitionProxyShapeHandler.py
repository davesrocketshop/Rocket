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
"""Base class for drawing proxy transitions"""

__title__ = "FreeCAD Proxy Transition Shape Handler"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

from typing import Any
import math

import FreeCAD
import Part

translate = FreeCAD.Qt.translate

from Rocket.Utilities import _err

class TransitionProxyShapeHandler:
    def __init__(self, obj : Any) -> None:

        # This gets changed when redrawn so it's very important to save a copy
        self._placement = FreeCAD.Placement(obj.Placement)
        self._obj = obj

        self._shape = None

        # Common parameters
        self._type = str(obj.TransitionType)
        if hasattr(obj, "Base"):
            self._base = obj.Base
        else:
            self._base = None

        self._foreDiameter = self._obj.ForeDiameter
        self._aftDiameter = self._obj.AftDiameter
        self._proxyPlacement = self._obj.ProxyPlacement
        self._proxyAftOffset = self._obj.ProxyAftOffset
        self._scale = self._obj.Scale
        self._scaleByValue = self._obj.ScaleByValue
        self._scaleByDiameter = self._obj.ScaleByDiameter
        self._autoScaleDiameter = self._obj.AutoScaleDiameter
        self._scaleForeDiameter = self._obj.ScaleForeDiameter
        self._scaleValue = self._obj.ScaleValue

        self._foreShoulder = bool(obj.ForeShoulder)
        self._foreShoulderLength = float(obj.ForeShoulderLength)
        self._foreShoulderRadius = float(obj.ForeShoulderDiameter) / 2.0
        self._foreShoulderAuto = bool(obj.ForeShoulderAutoDiameter)
        self._foreShoulderThickness = float(obj.ForeShoulderThickness)

        self._aftShoulder = bool(obj.AftShoulder)
        self._aftShoulderLength = float(obj.AftShoulderLength)
        self._aftShoulderRadius = float(obj.AftShoulderDiameter) / 2.0
        self._aftShoulderAuto = bool(obj.AftShoulderAutoDiameter)
        self._aftShoulderThickness = float(obj.AftShoulderThickness)

        self._shoulder = (self._foreShoulder or self._aftShoulder)

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

    def _getScale(self) -> float:
        scale = 1.0
        if self._scale:
            if self._scaleByValue and self._scaleValue.Value > 0.0:
                scale = 1.0 / self._scaleValue.Value
            elif self._scaleByDiameter:
                if self._scaleForeDiameter:
                    if self._foreDiameter > 0 and self._scaleValue > 0:
                        scale = self._scaleValue / self._foreDiameter
                else:
                    if self._aftDiameter > 0 and self._scaleValue > 0:
                        scale = self._scaleValue / self._aftDiameter

        return float(scale)

    def _getShape(self) -> Part.Solid:
        if self._shape:
            return self._shape

        if self._base is None:
            return Part.Shape() # Empty shape

        shape = Part.Shape(self._base.Shape)

        # Apply the rotations
        shape.rotate(FreeCAD.Vector(0,0,0), FreeCAD.Vector(self._proxyPlacement.Rotation.Axis.x, self._proxyPlacement.Rotation.Axis.y, self._proxyPlacement.Rotation.Axis.z), math.degrees(self._proxyPlacement.Rotation.Angle))

        # Apply the scaling
        scale = self._getScale()
        if self._scale:
            shape.scale(scale)

        # Translate so the nose is at (0, 0, 0)
        min = shape.BoundBox.XMin
        #     fin.translate(FreeCAD.Vector(self._proxyPlacement.Base.x, 0.0, 0.0))
        shape.translate(FreeCAD.Vector(-min - self._proxyPlacement.Base.x, 0, 0))

        self._shape = self._shapeUnion(shape)
        return self._shape

    def _radiusAt(self, r1 : float, r2 : float, length : float, pos : float) -> float:
        # Treat as a conical transition
        if r1 < r2:
            intercept = r1
            x = pos
            slope = (r2 - r1) / length
        else:
            intercept = r2
            x = length - pos
            slope = (r1 - r2) / length

        y = x * slope + intercept
        return y

    # def getRadius(self, x : float) -> float:
    #     # Apply the scaling
    #     scale = self._getScale()
    #     return scale * (self._diameter / 2.0)
    def getRadius(self, x : float) -> float:
        scale = self._getScale()
        foreRadius = (self._foreDiameter / 2.0) / scale
        aftRadius = (self._aftDiameter / 2.0) / scale
        radius = self._radiusAt(foreRadius, aftRadius, self.getLength(), x)
        return radius

    def getLength(self) -> float:
        shape = self._getShape()
        return self._getShapeLength(shape)

    def _getShapeLength(self, shape : Part.Solid) -> float:
        if not shape:
            return 0
        length = float(shape.BoundBox.XLength - self._proxyPlacement.Base.x - self._proxyAftOffset.Value) / self._getScale()
        if length < 0:
            length = 0
        return length

    def _createForeShoulder(self, length : float) -> Part.Solid:
        end1 = FreeCAD.Vector(0.0, self._foreShoulderRadius - self._foreShoulderThickness)
        end2 = FreeCAD.Vector(0.0, self._foreShoulderRadius)
        end3 = FreeCAD.Vector(-self._foreShoulderLength, self._foreShoulderRadius)
        end4 = FreeCAD.Vector(-self._foreShoulderLength, self._foreShoulderRadius - self._foreShoulderThickness)
        line1 = Part.LineSegment(end1, end2)
        line2 = Part.LineSegment(end2, end3)
        line3 = Part.LineSegment(end3, end4)
        line4 = Part.LineSegment(end4, end1)

        edges = [line1.toShape(), line2.toShape(), line3.toShape(), line4.toShape()]
        try:
            wire = Part.Wire(edges)
            face = Part.Face(wire)
            shape = face.revolve(FreeCAD.Vector(0, 0, 0),FreeCAD.Vector(1, 0, 0), 360)
        except Part.OCCError:
            _err(translate('Rocket', "Transition fore shoulder parameters produce an invalid shape"))
            return None
        return shape

    def _createAftShoulder(self, length : float) -> Part.Solid:
        end1 = FreeCAD.Vector(length, self._aftShoulderRadius - self._aftShoulderThickness)
        end2 = FreeCAD.Vector(length, self._aftShoulderRadius)
        end3 = FreeCAD.Vector(length + self._aftShoulderLength, self._aftShoulderRadius)
        end4 = FreeCAD.Vector(length + self._aftShoulderLength, self._aftShoulderRadius - self._aftShoulderThickness)
        line1 = Part.LineSegment(end1, end2)
        line2 = Part.LineSegment(end2, end3)
        line3 = Part.LineSegment(end3, end4)
        line4 = Part.LineSegment(end4, end1)

        edges = [line1.toShape(), line2.toShape(), line3.toShape(), line4.toShape()]
        try:
            wire = Part.Wire(edges)
            face = Part.Face(wire)
            shape = face.revolve(FreeCAD.Vector(0, 0, 0),FreeCAD.Vector(1, 0, 0), 360)
        except Part.OCCError:
            _err(translate('Rocket', "Transition aft shoulder parameters produce an invalid shape"))
            return None
        return shape

    def drawTransition(self) -> Part.Solid:
        shape = self._getShape()
        
        try:
            if shape and self._shoulder:
                length = float(shape.BoundBox.XLength - self._proxyPlacement.Base.x - self._proxyAftOffset.Value)
                if self._foreShoulder:
                    if self._foreShoulderRadius > max(shape.BoundBox.YMax, shape.BoundBox.ZMax):
                        _err(translate('Rocket', "Transition fore shoulder parameters produce an invalid shape"))
                        return Part.Shape()
                    shoulder = self._createForeShoulder(length)
                    if shoulder:
                        shape = shape.fuse(shoulder)
                if self._aftShoulder:
                    if self._aftShoulderRadius > max(shape.BoundBox.YMax, shape.BoundBox.ZMax):
                        _err(translate('Rocket', "Transition aft shoulder parameters produce an invalid shape"))
                        return Part.Shape()
                    shoulder = self._createAftShoulder(length)
                    if shoulder:
                        shape = shape.fuse(shoulder)
        except Part.OCCError:
            _err(translate('Rocket', "Transition shoulder parameters produce an invalid shape"))
            return Part.Shape()

        return shape

    def draw(self) -> None:
        self._obj.Shape = self.drawTransition()
        self._obj.Placement = self._placement

    def drawSolidShape(self) -> Part.Solid:
        return self.drawTransition()
