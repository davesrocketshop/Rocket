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
"""Class for drawing fins"""

__title__ = "FreeCAD Fins"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

from typing import Any
import math

import FreeCAD
import Part
from Part import Shape

translate = FreeCAD.Qt.translate

from Rocket.Constants import FINCAN_EDGE_SQUARE, FINCAN_EDGE_ROUND, FINCAN_EDGE_TAPER
from Rocket.Constants import FINCAN_STYLE_SLEEVE
from Rocket.Constants import FINCAN_COUPLER_STEPPED
from Rocket.Utilities import validationError, _err

from Rocket.ShapeHandlers.FinShapeHandler import FinShapeHandler
from Rocket.ShapeHandlers.FinTrapezoidShapeHandler import FinTrapezoidShapeHandler
from Rocket.ShapeHandlers.FinTriangleShapeHandler import FinTriangleShapeHandler
from Rocket.ShapeHandlers.FinEllipseShapeHandler import FinEllipseShapeHandler
from Rocket.ShapeHandlers.FinSketchShapeHandler import FinSketchShapeHandler

TOLERANCE_OFFSET = 0.5     # Distance to offset a vertex

class FinCanShapeHandler(FinShapeHandler):

    def __init__(self, obj : Any) -> None:
        super().__init__(obj)

        self._sleeve = (self._obj.FinCanStyle == FINCAN_STYLE_SLEEVE)

        self._length = float(self._obj.Length)
        self._leadingLength = float(self._obj.LeadingLength)
        self._trailingLength = float(self._obj.TrailingLength)

        self._leadingEdge = str(self._obj.LeadingEdge)
        self._trailingEdge = str(self._obj.TrailingEdge)

        self._lug = bool(self._obj.LaunchLug)
        self._lugLength = float(self._obj.LugLength)
        self._lugLeadingEdgeOffset = float(self._obj.LugLeadingEdgeOffset)
        self._lugForwardSweep = bool(self._obj.LaunchLugForwardSweep)
        self._lugAftSweep = bool(self._obj.LaunchLugAftSweep)
        self._lugForwardSweepAngle = float(self._obj.LaunchLugForwardSweepAngle)
        self._lugAftSweepAngle = float(self._obj.LaunchLugAftSweepAngle)
        self._lugRadius = float(self._obj.LugInnerDiameter) / 2.0
        self._lugThickness = float(self._obj.LugThickness)
        self._lugFilletRadius = float(self._obj.LugFilletRadius)

        self._coupler = bool(self._obj.Coupler)
        self._couplerStyle = str(self._obj.CouplerStyle)
        self._couplerLength = float(self._obj.CouplerLength)
        self._couplerRadius = float(self._obj.CouplerDiameter) / 2.0
        self._couplerThickness = float(self._obj.CouplerThickness)

        # apply scaling
        if obj.Proxy.isScaled():
            # self._scale is set in the base class
            self._length *= self._scale
            self._leadingLength *= self._scale
            self._trailingLength *= self._scale
            self._lugLength *= self._scale
            self._lugLeadingEdgeOffset *= self._scale
            if not self._autoDiameter:
                self._couplerRadius *= self._scale


    def isValidShape(self) -> bool:
        if self._thickness <= 0.0:
            validationError(translate('Rocket', "Fin can thickness must be greater than zero"))
            return False
        if self._length <= 0.0:
            validationError(translate('Rocket', "Fin can length must be greater than zero"))
            return False

        edge = 0.0
        if self._leadingEdge != FINCAN_EDGE_SQUARE:
            edge += self._leadingLength
        if self._trailingEdge != FINCAN_EDGE_SQUARE:
            edge += self._trailingLength
        if edge > self._length:
            validationError(translate('Rocket', "Fin can leading and trailing edges can not exceed total length"))
            return False

        if self._coupler:
            if self._couplerLength <= 0:
                validationError(translate('Rocket', "Coupler length must be greater than zero"))
                return False
            if self._couplerThickness <= 0:
                validationError(translate('Rocket', "Coupler thickness must be greater than zero"))
                return False
            if self._couplerRadius <= self._couplerThickness:
                validationError(translate('Rocket', "Coupler outer diameter must be greater than the inner diameter"))
                return False
            if (self._couplerRadius - self._couplerThickness) > self._radius:
                validationError(translate('Rocket', "Coupler inner diameter must be less than or equal to the fin can inner diameter"))
                return False
            if self._couplerRadius >= (self._radius + self._thickness):
                validationError(translate('Rocket', "Coupler outer diameter must be less than fin can outer diameter"))
                return False

        return super().isValidShape()

    def _trailingRound(self) -> Shape:
        lead = self._leadingLength
        center_x = self._length - self._leadingLength
        center_y = self._radius - self._thickness
        center = FreeCAD.Vector(center_x, center_y, 0)
        major  = lead
        minor  = self._thickness
        ellipse = Part.Ellipse(center, major, minor)
        arc = Part.Arc(ellipse, 0, math.pi / 2.0)

        # Create the box
        box1 = Part.LineSegment(FreeCAD.Vector(center_x,              center_y + self._thickness),     FreeCAD.Vector(center_x,              center_y + 2 * self._thickness))
        box2 = Part.LineSegment(FreeCAD.Vector(center_x,              center_y + 2 * self._thickness), FreeCAD.Vector(center_x + 2.0 * lead, center_y + 2 * self._thickness))
        box3 = Part.LineSegment(FreeCAD.Vector(center_x + 2.0 * lead, center_y + 2 * self._thickness), FreeCAD.Vector(center_x + 2.0 * lead, center_y))
        box4 = Part.LineSegment(FreeCAD.Vector(center_x + 2.0 * lead, center_y),                           FreeCAD.Vector(center_x + lead,       center_y))

        wire = Part.Wire([arc.toShape(), box1.toShape(), box2.toShape(), box3.toShape(), box4.toShape()])
        face = Part.Face(wire)
        shape = face.revolve(FreeCAD.Vector(0, 0, 0),FreeCAD.Vector(1, 0, 0), 360)
        return shape

    def _trailingTaper(self) -> Shape:
        lead = self._leadingLength
        center_x = self._length - self._leadingLength
        center_y = self._radius - self._thickness

        # Create the box
        box0 = Part.LineSegment(FreeCAD.Vector(center_x + lead,       center_y),                           FreeCAD.Vector(center_x,              center_y + self._thickness))
        box1 = Part.LineSegment(FreeCAD.Vector(center_x,              center_y + self._thickness),     FreeCAD.Vector(center_x,              center_y + 2 * self._thickness))
        box2 = Part.LineSegment(FreeCAD.Vector(center_x,              center_y + 2 * self._thickness), FreeCAD.Vector(center_x + 2.0 * lead, center_y + 2 * self._thickness))
        box3 = Part.LineSegment(FreeCAD.Vector(center_x + 2.0 * lead, center_y + 2 * self._thickness), FreeCAD.Vector(center_x + 2.0 * lead, center_y))
        box4 = Part.LineSegment(FreeCAD.Vector(center_x + 2.0 * lead, center_y),                           FreeCAD.Vector(center_x + lead,       center_y))

        wire = Part.Wire([box0.toShape(), box1.toShape(), box2.toShape(), box3.toShape(), box4.toShape()])
        face = Part.Face(wire)
        shape = face.revolve(FreeCAD.Vector(0, 0, 0),FreeCAD.Vector(1, 0, 0), 360)
        return shape

    def _getLeadingEdge(self) -> Shape:
        if self._leadingEdge == FINCAN_EDGE_ROUND:
            return self._leadingRound()
        elif self._leadingEdge == FINCAN_EDGE_TAPER:
            return self._leadingTaper()
        return None

    def _leadingRound(self) -> Shape:
        trail  = self._trailingLength
        center_x = trail
        center_y = self._radius - self._thickness
        center = FreeCAD.Vector(center_x, center_y, 0)
        major  = trail
        minor  = self._thickness
        ellipse = Part.Ellipse(center, major, minor)
        arc = Part.Arc(ellipse, math.pi / 2.0, math.pi)

        # Create the box
        box1 = Part.LineSegment(FreeCAD.Vector(center_x,               center_y + self._thickness),     FreeCAD.Vector(center_x,               center_y + 2 * self._thickness))
        box2 = Part.LineSegment(FreeCAD.Vector(center_x,               center_y + 2 * self._thickness), FreeCAD.Vector(center_x - 2.0 * trail, center_y + 2 * self._thickness))
        box3 = Part.LineSegment(FreeCAD.Vector(center_x - 2.0 * trail, center_y + 2 * self._thickness), FreeCAD.Vector(center_x - 2.0 * trail, center_y))
        box4 = Part.LineSegment(FreeCAD.Vector(center_x - 2.0 * trail, center_y),                           FreeCAD.Vector(center_x - trail,       center_y))

        wire = Part.Wire([arc.toShape(), box1.toShape(), box2.toShape(), box3.toShape(), box4.toShape()])
        face = Part.Face(wire)
        shape = face.revolve(FreeCAD.Vector(0, 0, 0),FreeCAD.Vector(1, 0, 0), 360)
        return shape

    def _leadingTaper(self) -> Shape:
        trail  = self._trailingLength
        center_x = trail
        center_y = self._radius - self._thickness

        # Create the box
        box0 = Part.LineSegment(FreeCAD.Vector(center_x - trail,       center_y),                           FreeCAD.Vector(center_x,               center_y + self._thickness))
        box1 = Part.LineSegment(FreeCAD.Vector(center_x,               center_y + self._thickness),     FreeCAD.Vector(center_x,               center_y + 2 * self._thickness))
        box2 = Part.LineSegment(FreeCAD.Vector(center_x,               center_y + 2 * self._thickness), FreeCAD.Vector(center_x - 2.0 * trail, center_y + 2 * self._thickness))
        box3 = Part.LineSegment(FreeCAD.Vector(center_x - 2.0 * trail, center_y + 2 * self._thickness), FreeCAD.Vector(center_x - 2.0 * trail, center_y))
        box4 = Part.LineSegment(FreeCAD.Vector(center_x - 2.0 * trail, center_y),                           FreeCAD.Vector(center_x - trail,       center_y))

        wire = Part.Wire([box0.toShape(), box1.toShape(), box2.toShape(), box3.toShape(), box4.toShape()])
        face = Part.Face(wire)
        shape = face.revolve(FreeCAD.Vector(0, 0, 0),FreeCAD.Vector(1, 0, 0), 360)
        return shape

    def _getTrailingEdge(self) -> Shape:
        if self._trailingEdge == FINCAN_EDGE_ROUND:
            return self._trailingRound()
        elif self._trailingEdge == FINCAN_EDGE_TAPER:
            return self._trailingTaper()
        return None

    def rakeZ(self, x : float, slope : float, intercept : float) -> float:
        z = x * slope + intercept # In the (x,z) plane
        return z

    def _drawForwardSweep(self, outerRadius : float, OR : float, xFore : float, xAft : float) -> Shape:
        # We need to calculate our vertices outside of the part to avoid OpenCASCADE's "too exact" problem
        slope = -1.0 / math.tan(math.radians(self._lugForwardSweepAngle))
        intercept = float(float(OR) - (slope * xFore))

        y = 2.0 * float(outerRadius) + TOLERANCE_OFFSET

        x1 = float(xFore) + TOLERANCE_OFFSET
        z1 = self.rakeZ(x1, slope, intercept)
        v1 = FreeCAD.Vector(x1, y, z1)

        x2 = float(xAft) - TOLERANCE_OFFSET
        z2 = self.rakeZ(x2, slope, intercept)
        v2 = FreeCAD.Vector(x2, y, z2)

        v3 = FreeCAD.Vector(x1, y, z2)

        line1 = Part.LineSegment(v1, v2)
        line2 = Part.LineSegment(v2, v3)
        line3 = Part.LineSegment(v3, v1)
        shape = Part.Shape([line1, line2, line3])
        wire = Part.Wire(shape.Edges)
        face = Part.Face(wire)
        rake = face.extrude(FreeCAD.Vector(0, -2.0 * y, 0))

        return rake

    def _drawAftSweep(self, outerRadius : float, OR : float, xFore : float, xAft : float) -> Shape:
        # We need to calculate our vertices outside of the part to avoid OpenCASCADE's "too exact" problem
        slope = 1.0 / math.tan(math.radians(self._lugAftSweepAngle))
        intercept = float(float(OR) - (slope * xAft))

        y = 2.0 * float(outerRadius) + TOLERANCE_OFFSET

        x1 = float(xFore) + TOLERANCE_OFFSET
        z1 = self.rakeZ(x1, slope, intercept)
        v1 = FreeCAD.Vector(x1, y, z1)

        x2 = float(xAft) - TOLERANCE_OFFSET
        z2 = self.rakeZ(x2, slope, intercept)
        v2 = FreeCAD.Vector(x2, y, z2)

        v3 = FreeCAD.Vector(x2, y, z1)

        line1 = Part.LineSegment(v1, v2)
        line2 = Part.LineSegment(v2, v3)
        line3 = Part.LineSegment(v3, v1)
        shape = Part.Shape([line1, line2, line3])
        wire = Part.Wire(shape.Edges)
        face = Part.Face(wire)
        rake = face.extrude(FreeCAD.Vector(0, -2.0 * y, 0))

        return rake

    def _filletDepth(self, radius : float, width : float) -> float:
        theta = math.asin(width/radius)
        depth = radius - radius * math.cos(theta)
        return depth

    def _safeEllipse(self, major : float, minor : float, center_x : float, center_y : float, center_z : float) -> Shape:
        majorVector = FreeCAD.Vector(center_x, center_y, center_z + major)
        minorVector = FreeCAD.Vector(center_x, center_y + minor, center_z)
        centerVector = FreeCAD.Vector(center_x, center_y, center_z)
        if major < minor:
            return Part.Ellipse(minorVector, majorVector, centerVector)
        return Part.Ellipse(majorVector, minorVector, centerVector)

    def _cutFillet(self, lug : Any, major : float, minor : float, center_x : float, center_y : float, center_z : float) -> Shape:
        ellipse = self._safeEllipse(major, minor, center_x, center_y, center_z)
        wire = Part.Wire(ellipse.toShape())
        face = Part.Face(wire)
        fillet1 = face.extrude(FreeCAD.Vector(self._lugLength, 0, 0))
        return lug.cut(fillet1)


    def _launchLug(self) -> Shape:
        if self._lug:
            try:
                radius = self._lugRadius
                outerRadius = radius + self._lugThickness
                width = outerRadius + self._lugFilletRadius
                bodyRadius = self._radius

                base = self._lugLeadingEdgeOffset
                if not self._lugLeadingEdgeOffset > 0:
                    if self._leadingEdge != FINCAN_EDGE_SQUARE:
                        base += self._leadingLength

                if self._lugThickness > self._thickness:
                    lugCenterZ = radius + self._lugThickness
                else:
                    lugCenterZ = radius + self._thickness

                point = FreeCAD.Vector(base, 0, lugCenterZ + bodyRadius)
                direction = FreeCAD.Vector(1,0,0)

                outer = Part.makeCylinder(outerRadius, self._lugLength, point, direction)
                inner = Part.makeCylinder(radius, self._lugLength, point, direction)

                major  = lugCenterZ + self._filletDepth(bodyRadius, width)
                minor  = width - outerRadius

                # Make the fillet
                point = FreeCAD.Vector(base, width, bodyRadius - self._filletDepth(bodyRadius, width))
                filletBase = Part.makeBox(major, 2 * width, self._lugLength, point, direction)
                lug = outer.fuse(filletBase)
                baseCutout = Part.makeCylinder(bodyRadius, self._lugLength, FreeCAD.Vector(base, 0, 0), direction)
                lug = lug.cut(baseCutout)

                center_x = base
                center_y = width
                center_z = lugCenterZ + bodyRadius
                lug = self._cutFillet(lug, major, minor, center_x, center_y, center_z)

                center_y = -width
                lug = self._cutFillet(lug, major, minor, center_x, center_y, center_z)

                # Add the sweeps
                if self._lugForwardSweep or self._lugAftSweep:
                    xFore = base + self._lugLength
                    xAft = base
                    if self._lugForwardSweep:
                        rake = self._drawForwardSweep(outerRadius, bodyRadius, xFore, xAft)
                        lug = lug.cut(rake)
                    if self._lugAftSweep:
                        rake = self._drawAftSweep(outerRadius, bodyRadius, xFore, xAft)
                        lug = lug.cut(rake)

                # Poke a hole for the launch rod
                lug = lug.cut(inner)

                # Rotate to place midway between fins
                lug.rotate(FreeCAD.Vector(0,0,0), FreeCAD.Vector(1,0,0), self._finSpacing / 2.0)

                return lug
            except Exception:
                _err(translate('Rocket', "Launch lug parameters produce an invalid shape"))

        return None

    def _drawCan(self) -> Shape:
        point = FreeCAD.Vector(0,0,0)
        direction = FreeCAD.Vector(1,0,0)
        outerRadius = self._radius
        innerRadius = self._radius - self._thickness
        if self._coupler:
            length = self._length + self._couplerLength
            point = FreeCAD.Vector(-self._couplerLength,0,0)
            inner = Part.makeCylinder(self._couplerRadius - self._couplerThickness, length, point, direction)
        else:
            length = self._length
            inner = Part.makeCylinder(innerRadius, length, point, direction)
        outer = Part.makeCylinder(outerRadius, length, point, direction)
        can = outer.cut(inner)

        if self._coupler:
            # Cut the outside of the coupler
            cutPoint = FreeCAD.Vector(0,0,0)
            direction = FreeCAD.Vector(-1,0,0)
            cutOuter = Part.makeCylinder(outerRadius + 1.0, self._couplerLength + 1.0, cutPoint, direction)
            cutInner = Part.makeCylinder(self._couplerRadius, self._couplerLength + 1.0, cutPoint, direction)
            cutDisk = cutOuter.cut(cutInner)
            can = can.cut(cutDisk)

            # Add a chamfer
            length = float(point.x)
            chamfer = self._couplerThickness / 2.0
            point1 = FreeCAD.Vector(length, self._couplerRadius - chamfer, 0.0)
            point2 = FreeCAD.Vector(length, self._couplerRadius, 0.0)
            point3 = FreeCAD.Vector(length + chamfer, self._couplerRadius, 0.0)

            edge1 = Part.makeLine(point1, point2)
            edge2 = Part.makeLine(point2, point3)
            edge3 = Part.makeLine(point3, point1)
            wire = Part.Wire([edge1, edge2, edge3])
            face = Part.Face(wire)
            # Part.show(face)

            mask = face.revolve(FreeCAD.Vector(0, 0, 0),FreeCAD.Vector(1, 0, 0), 360)
            can = can.cut(mask)

            if self._couplerStyle == FINCAN_COUPLER_STEPPED:
                # Cut inside up to the step
                point = FreeCAD.Vector(self._couplerLength,0,0)
                direction = FreeCAD.Vector(1,0,0)
                radius = innerRadius
                if self._couplerRadius < innerRadius:
                    radius = self._couplerRadius
                step = Part.makeCylinder(radius, self._length, point, direction)
                can = can.cut(step)

        return can

    def _extendRoot(self) -> bool:
        # Override this if the fin root needs an extension to connect it to the body tube
        return True

    def _drawFinCan(self) -> Shape:
        # Make the can
        can = self._drawCan()

        # Shape the leading and trailing edges
        shape = self._getLeadingEdge()
        if shape:
            can = can.cut(shape)
        shape = self._getTrailingEdge()
        if shape:
            can = can.cut(shape)

        # Add the launch lug
        shape = self._launchLug()
        if shape:
            can = can.fuse(shape)

        # Add the fins
        fins = self._drawFinSet()
        finCan = can.fuse([fins]) # Must be fuse not makeCompund

        return finCan

    def draw(self) -> None:

        if not self.isValidShape():
            return

        try:
            self._obj.Shape = self._drawFinCan()

            self._obj.Placement = self._placement

        except (ZeroDivisionError, Part.OCCError):
            _err(translate('Rocket', "Fin can parameters produce an invalid shape"))
            return

class FinCanTrapezoidShapeHandler(FinCanShapeHandler, FinTrapezoidShapeHandler): # lgtm [py/missing-call-to-init]

    def __init__(self, obj):
        super().__init__(obj)

class FinCanTriangleShapeHandler(FinCanShapeHandler, FinTriangleShapeHandler): # lgtm [py/missing-call-to-init]

    def __init__(self, obj):
        super().__init__(obj)

class FinCanEllipseShapeHandler(FinCanShapeHandler, FinEllipseShapeHandler): # lgtm [py/missing-call-to-init]

    def __init__(self, obj):
        super().__init__(obj)

class FinCanSketchShapeHandler(FinCanShapeHandler, FinSketchShapeHandler): # lgtm [py/missing-call-to-init]

    def __init__(self, obj):
        super().__init__(obj)
