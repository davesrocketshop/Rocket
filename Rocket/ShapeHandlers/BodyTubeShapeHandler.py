# SPDX-License-Identifier: LGPL-2.1-or-later

# ***************************************************************************
# *   Copyright (c) 2021-2025 David Carter <dcarter@davidcarter.ca>         *
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
"""Class for drawing body tubes"""

__title__ = "FreeCAD Body Tube Handler"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

from typing import Any

import FreeCAD
import Part

from Rocket.Utilities import validationError, _err

translate = FreeCAD.Qt.translate

class BodyTubeShapeHandler():

    def __init__(self, obj : Any, scale : bool = True) -> None:
        self._obj = obj

        # This gets changed when redrawn so it's very important to save a copy
        self._placement = FreeCAD.Placement(obj.Placement)

        self._getScaledValues(scale)

    def _getScaledValues(self, scale : bool):

        self._length = float(self._obj.Length)
        self._OD = float(self._obj.Diameter)
        self._autoDiameter = False
        if hasattr(self._obj, "AutoDiameter"):
            self._autoDiameter = bool(self._obj.AutoDiameter)

        # Apply scaling
        self._scale = 1.0
        if scale and self._obj.Proxy.isScaled():
            self._scale = 1.0 / self._obj.Proxy.getScale()
            self._length *= self._scale
            if not self._autoDiameter:
                self._OD *= self._scale

        if self._OD > 0.0:
            self._ID = self._OD - 2.0 * float(self._obj.Thickness)
        else:
            self._ID = float(self._obj.Thickness)

    def isValidShape(self) -> bool:

        # Perform some general validations
        if self._ID <= 0:
            validationError(translate('Rocket', "Body tube inner diameter must be greater than zero"))
            return False
        if self._OD <= self._ID:
            validationError(translate('Rocket', "Body tube outer diameter must be greater than the inner"))
            return False
        if self._length <= 0:
            validationError(translate('Rocket', "Body tube length must be greater than zero"))
            return False

        return True

    def _drawTubeEdges(self) -> list:
        innerRadius = self._ID / 2.0
        outerRadius = self._OD / 2.0

        line1 = Part.LineSegment(FreeCAD.Vector(0.0, innerRadius),          FreeCAD.Vector(self._length, innerRadius))
        line2 = Part.LineSegment(FreeCAD.Vector(self._length, innerRadius), FreeCAD.Vector(self._length, outerRadius))
        line3 = Part.LineSegment(FreeCAD.Vector(self._length, outerRadius), FreeCAD.Vector(0.0, outerRadius))
        line4 = Part.LineSegment(FreeCAD.Vector(0.0, outerRadius),          FreeCAD.Vector(0.0, innerRadius))

        return [line1.toShape(), line2.toShape(), line3.toShape(), line4.toShape()]

    def _drawTubeEdgesSolid(self) -> list:
        innerRadius = 0.0
        outerRadius = self._OD / 2.0

        line1 = Part.LineSegment(FreeCAD.Vector(0.0, innerRadius),          FreeCAD.Vector(self._length, innerRadius))
        line2 = Part.LineSegment(FreeCAD.Vector(self._length, innerRadius), FreeCAD.Vector(self._length, outerRadius))
        line3 = Part.LineSegment(FreeCAD.Vector(self._length, outerRadius), FreeCAD.Vector(0.0, outerRadius))
        line4 = Part.LineSegment(FreeCAD.Vector(0.0, outerRadius),          FreeCAD.Vector(0.0, innerRadius))

        return [line1.toShape(), line2.toShape(), line3.toShape(), line4.toShape()]

    def draw(self) -> None:
        if not self.isValidShape():
            return

        edges = None

        try:
            edges = self._drawTubeEdges()
        except (ZeroDivisionError, Part.OCCError):
            _err(translate('Rocket', "Body tube parameters produce an invalid shape"))
            return

        if edges:
            try:
                wire = Part.Wire(edges)
                face = Part.Face(wire)
                self._obj.Shape = face.revolve(FreeCAD.Vector(0, 0, 0),FreeCAD.Vector(1, 0, 0), 360)
                self._obj.Placement = self._placement
            except Part.OCCError:
                _err(translate('Rocket', "Body tube parameters produce an invalid shape"))
                return
        else:
            _err(translate('Rocket', "Body tube parameters produce an invalid shape"))

    def drawSolidShape(self) -> Any:
        if not self.isValidShape():
            return None

        edges = None

        try:
            edges = self._drawTubeEdgesSolid()
        except (ZeroDivisionError, Part.OCCError):
            _err(translate('Rocket', "Body tube parameters produce an invalid shape"))
            return None

        if edges:
            try:
                wire = Part.Wire(edges)
                face = Part.Face(wire)
                shape = face.revolve(FreeCAD.Vector(0, 0, 0),FreeCAD.Vector(1, 0, 0), 360)
                shape.translate(self._placement.Base)
                return shape
                # self._obj.Placement = self._placement
            except Part.OCCError:
                _err(translate('Rocket', "Body tube parameters produce an invalid shape"))
                return None
        else:
            _err(translate('Rocket', "Body tube parameters produce an invalid shape"))
