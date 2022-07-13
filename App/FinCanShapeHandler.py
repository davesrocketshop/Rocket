# ***************************************************************************
# *   Copyright (c) 2021 David Carter <dcarter@davidcarter.ca>              *
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

import FreeCAD
import Part
import math

from DraftTools import translate

from App.Constants import FINCAN_EDGE_SQUARE, FINCAN_EDGE_ROUND, FINCAN_EDGE_TAPER
from App.Utilities import _err

from App.FinShapeHandler import FinShapeHandler
from App.FinTrapezoidShapeHandler import FinTrapezoidShapeHandler
from App.FinEllipseShapeHandler import FinEllipseShapeHandler
from App.FinSketchShapeHandler import FinSketchShapeHandler

TOLERANCE_OFFSET = 0.5     # Distance to offset a vertex

class FinCanShapeHandler(FinShapeHandler):

    def __init__(self, obj):
        super().__init__(obj)

    def isValidShape(self):
        if self._obj.Thickness <= 0.0:
            _err(translate('Rocket', "Fin can thickness must be greater than zero"))
            return False
        if self._obj.Length <= 0.0:
            _err(translate('Rocket', "Fin can length must be greater than zero"))
            return False

        edge = 0.0
        if self._obj.LeadingEdge != FINCAN_EDGE_SQUARE:
            edge += float(self._obj.LeadingLength)
        if self._obj.TrailingEdge != FINCAN_EDGE_SQUARE:
            edge += float(self._obj.TrailingLength)
        if edge > self._obj.Length:
            _err(translate('Rocket', "Fin can leading and trailing edges can not exceed total length"))
            return False

        return True

    def _leadingRound(self):
        center_x = self._obj.RootChord + self._obj.LeadingEdgeOffset - self._obj.LeadingLength
        center_y = self._obj.InnerDiameter / 2.0
        center = FreeCAD.Vector(center_x, center_y, 0)
        major  = self._obj.LeadingLength
        minor  = self._obj.Thickness
        ellipse = Part.Ellipse(center, major, minor)
        arc = Part.Arc(ellipse, 0, math.pi / 2.0)

        # Create the box
        box1 = Part.LineSegment(FreeCAD.Vector(center_x,                                 center_y + self._obj.Thickness),     FreeCAD.Vector(center_x,                                 center_y + 2 * self._obj.Thickness))
        box2 = Part.LineSegment(FreeCAD.Vector(center_x,                                 center_y + 2 * self._obj.Thickness), FreeCAD.Vector(center_x + 2.0 * self._obj.LeadingLength, center_y + 2 * self._obj.Thickness))
        box3 = Part.LineSegment(FreeCAD.Vector(center_x + 2.0 * self._obj.LeadingLength, center_y + 2 * self._obj.Thickness), FreeCAD.Vector(center_x + 2.0 * self._obj.LeadingLength, center_y))
        box4 = Part.LineSegment(FreeCAD.Vector(center_x + 2.0 * self._obj.LeadingLength, center_y),                           FreeCAD.Vector(center_x + self._obj.LeadingLength,       center_y))

        wire = Part.Wire([arc.toShape(), box1.toShape(), box2.toShape(), box3.toShape(), box4.toShape()])
        face = Part.Face(wire)
        shape = face.revolve(FreeCAD.Vector(0, 0, 0),FreeCAD.Vector(1, 0, 0), 360)
        return shape

    def _leadingTaper(self):
        center_x = self._obj.RootChord + self._obj.LeadingEdgeOffset - self._obj.LeadingLength
        center_y = self._obj.InnerDiameter / 2.0

        # Create the box
        box0 = Part.LineSegment(FreeCAD.Vector(center_x + self._obj.LeadingLength,       center_y),                           FreeCAD.Vector(center_x,                                 center_y + self._obj.Thickness))
        box1 = Part.LineSegment(FreeCAD.Vector(center_x,                                 center_y + self._obj.Thickness),     FreeCAD.Vector(center_x,                                 center_y + 2 * self._obj.Thickness))
        box2 = Part.LineSegment(FreeCAD.Vector(center_x,                                 center_y + 2 * self._obj.Thickness), FreeCAD.Vector(center_x + 2.0 * self._obj.LeadingLength, center_y + 2 * self._obj.Thickness))
        box3 = Part.LineSegment(FreeCAD.Vector(center_x + 2.0 * self._obj.LeadingLength, center_y + 2 * self._obj.Thickness), FreeCAD.Vector(center_x + 2.0 * self._obj.LeadingLength, center_y))
        box4 = Part.LineSegment(FreeCAD.Vector(center_x + 2.0 * self._obj.LeadingLength, center_y),                           FreeCAD.Vector(center_x + self._obj.LeadingLength,       center_y))

        wire = Part.Wire([box0.toShape(), box1.toShape(), box2.toShape(), box3.toShape(), box4.toShape()])
        face = Part.Face(wire)
        shape = face.revolve(FreeCAD.Vector(0, 0, 0),FreeCAD.Vector(1, 0, 0), 360)
        return shape

    def _leadingEdge(self):
        if self._obj.LeadingEdge == FINCAN_EDGE_ROUND:
            return self._leadingRound()
        elif self._obj.LeadingEdge == FINCAN_EDGE_TAPER:
            return self._leadingTaper()
        return None

    def _trailingRound(self):
        center_x = self._obj.RootChord - self._obj.Length + self._obj.LeadingEdgeOffset + self._obj.TrailingLength
        center_y = self._obj.InnerDiameter / 2.0
        center = FreeCAD.Vector(center_x, center_y, 0)
        major  = self._obj.TrailingLength
        minor  = self._obj.Thickness
        ellipse = Part.Ellipse(center, major, minor)
        arc = Part.Arc(ellipse, math.pi / 2.0, math.pi)

        # Create the box
        box1 = Part.LineSegment(FreeCAD.Vector(center_x,                                  center_y + self._obj.Thickness),     FreeCAD.Vector(center_x,                                  center_y + 2 * self._obj.Thickness))
        box2 = Part.LineSegment(FreeCAD.Vector(center_x,                                  center_y + 2 * self._obj.Thickness), FreeCAD.Vector(center_x - 2.0 * self._obj.TrailingLength, center_y + 2 * self._obj.Thickness))
        box3 = Part.LineSegment(FreeCAD.Vector(center_x - 2.0 * self._obj.TrailingLength, center_y + 2 * self._obj.Thickness), FreeCAD.Vector(center_x - 2.0 * self._obj.TrailingLength, center_y))
        box4 = Part.LineSegment(FreeCAD.Vector(center_x - 2.0 * self._obj.TrailingLength, center_y),                           FreeCAD.Vector(center_x - self._obj.TrailingLength,       center_y))

        wire = Part.Wire([arc.toShape(), box1.toShape(), box2.toShape(), box3.toShape(), box4.toShape()])
        face = Part.Face(wire)
        shape = face.revolve(FreeCAD.Vector(0, 0, 0),FreeCAD.Vector(1, 0, 0), 360)
        return shape

    def _trailingTaper(self):
        center_x = self._obj.RootChord - self._obj.Length + self._obj.LeadingEdgeOffset + self._obj.TrailingLength
        center_y = self._obj.InnerDiameter / 2.0

        # Create the box
        box0 = Part.LineSegment(FreeCAD.Vector(center_x - self._obj.TrailingLength,       center_y),                           FreeCAD.Vector(center_x,                                  center_y + self._obj.Thickness))
        box1 = Part.LineSegment(FreeCAD.Vector(center_x,                                  center_y + self._obj.Thickness),     FreeCAD.Vector(center_x,                                  center_y + 2 * self._obj.Thickness))
        box2 = Part.LineSegment(FreeCAD.Vector(center_x,                                  center_y + 2 * self._obj.Thickness), FreeCAD.Vector(center_x - 2.0 * self._obj.TrailingLength, center_y + 2 * self._obj.Thickness))
        box3 = Part.LineSegment(FreeCAD.Vector(center_x - 2.0 * self._obj.TrailingLength, center_y + 2 * self._obj.Thickness), FreeCAD.Vector(center_x - 2.0 * self._obj.TrailingLength, center_y))
        box4 = Part.LineSegment(FreeCAD.Vector(center_x - 2.0 * self._obj.TrailingLength, center_y),                           FreeCAD.Vector(center_x - self._obj.TrailingLength,       center_y))

        wire = Part.Wire([box0.toShape(), box1.toShape(), box2.toShape(), box3.toShape(), box4.toShape()])
        face = Part.Face(wire)
        shape = face.revolve(FreeCAD.Vector(0, 0, 0),FreeCAD.Vector(1, 0, 0), 360)
        return shape

    def _trailingEdge(self):
        if self._obj.TrailingEdge == FINCAN_EDGE_ROUND:
            return self._trailingRound()
        elif self._obj.TrailingEdge == FINCAN_EDGE_TAPER:
            return self._trailingTaper()
        return None

    def rakeZ(self, x, slope, intercept):
        z = x * slope + intercept # In the (x,z) plane
        return z

    def _drawForwardSweep(self, outerRadius, OR, xFore, xAft):
        # We need to calculate our vertices outside of the part to avoid OpenCASCADE's "too exact" problem
        slope = -1.0 / math.tan(math.radians(self._obj.LaunchLugForwardSweepAngle))
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

    def _drawAftSweep(self, outerRadius, OR, xFore, xAft):
        # We need to calculate our vertices outside of the part to avoid OpenCASCADE's "too exact" problem
        slope = 1.0 / math.tan(math.radians(self._obj.LaunchLugAftSweepAngle))
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

    def _launchLug(self):
        if self._obj.LaunchLug:
            try:
                radius = self._obj.LugInnerDiameter / 2.0
                outerRadius = radius + self._obj.LugThickness

                base = float(self._obj.RootChord - self._obj.Length + self._obj.LeadingEdgeOffset)
                if self._obj.TrailingEdge != FINCAN_EDGE_SQUARE:
                    base += float(self._obj.TrailingLength)

                point = FreeCAD.Vector(base, 0, outerRadius + self._obj.InnerDiameter / 2.0 + self._obj.Thickness)
                direction = FreeCAD.Vector(1,0,0)

                outer = Part.makeCylinder(outerRadius, self._obj.LugLength, point, direction)
                inner = Part.makeCylinder(radius, self._obj.LugLength, point, direction)

                # Make the fillet
                point = FreeCAD.Vector(base, 2 * outerRadius, self._obj.InnerDiameter / 2.0)
                filletBase = Part.makeBox(outerRadius + self._obj.Thickness, 4 * outerRadius, self._obj.LugLength, point, direction)
                lug = outer.fuse(filletBase)

                center_x = base
                center_y = 2 * outerRadius
                center_z = outerRadius + self._obj.InnerDiameter / 2.0 + self._obj.Thickness
                center = FreeCAD.Vector(center_x, center_y, center_z)
                major  = outerRadius + self._obj.Thickness
                minor  = outerRadius
                ellipse = Part.Ellipse(FreeCAD.Vector(center_x, center_y, center_z + major), FreeCAD.Vector(center_x, center_y + minor, center_z), center)
                wire = Part.Wire(ellipse.toShape())
                face = Part.Face(wire)
                fillet1 = face.extrude(FreeCAD.Vector(self._obj.LugLength, 0, 0))
                lug = lug.cut(fillet1)

                center_y = -2 * outerRadius
                center = FreeCAD.Vector(center_x, center_y, center_z)
                ellipse = Part.Ellipse(FreeCAD.Vector(center_x, center_y, center_z + major), FreeCAD.Vector(center_x, center_y + minor, center_z), center)
                wire = Part.Wire(ellipse.toShape())
                face = Part.Face(wire)
                fillet2 = face.extrude(FreeCAD.Vector(self._obj.LugLength, 0, 0))
                lug = lug.cut(fillet2)

                # Add the sweeps
                if self._obj.LaunchLugForwardSweep or self._obj.LaunchLugAftSweep:
                    xFore = base + float(self._obj.LugLength)
                    xAft = base
                    if self._obj.LaunchLugForwardSweep:
                        rake = self._drawForwardSweep(outerRadius, self._obj.InnerDiameter / 2.0 + self._obj.Thickness, xFore, xAft)
                        lug = lug.cut(rake)
                    if self._obj.LaunchLugAftSweep:
                        rake = self._drawAftSweep(outerRadius, self._obj.InnerDiameter / 2.0 + self._obj.Thickness, xFore, xAft)
                        lug = lug.cut(rake)

                # Poke a hole for the launch rod
                lug = lug.cut(inner)

                # Rotate to place midway between fins
                lug.rotate(FreeCAD.Vector(0,0,0), FreeCAD.Vector(1,0,0), self._obj.FinSpacing / 2.0)

                return lug
            except:
                _err(translate('Rocket', "Launch lug parameters produce an invalid shape"))

        return None

    def _drawFinCan(self):
        # Make the can
        point = FreeCAD.Vector((self._obj.RootChord - self._obj.Length + self._obj.LeadingEdgeOffset),0,0)
        direction = FreeCAD.Vector(1,0,0)
        radius = self._obj.InnerDiameter / 2.0
        outerRadius = radius + self._obj.Thickness
        outer = Part.makeCylinder(outerRadius, self._obj.Length, point, direction)
        inner = Part.makeCylinder(radius, self._obj.Length, point, direction)
        can = outer.cut(inner)

        # Shape the leading and trailing edges
        shape = self._leadingEdge()
        if shape is not None:
            can = can.cut(shape)
        shape = self._trailingEdge()
        if shape is not None:
            can = can.cut(shape)

        # Add the launch lug
        shape = self._launchLug()
        if shape is not None:
            can = can.fuse(shape)

        # Add the fins
        fins = self._drawFinSet()
        finCan = Part.makeCompound([can, fins])

        return finCan

    def draw(self):
        
        if not self.isValidShape():
            return

        try:
            self._obj.Shape = self._drawFinCan()

            self._obj.Placement = self._placement

        except (ZeroDivisionError, Part.OCCError):
            _err(translate('Rocket', "Fin can parameters produce an invalid shape"))
            return

class FinCanTrapezoidShapeHandler(FinCanShapeHandler, FinTrapezoidShapeHandler):

    def __init__(self, obj):
        super().__init__(obj)

class FinCanEllipseShapeHandler(FinCanShapeHandler, FinEllipseShapeHandler):

    def __init__(self, obj):
        super().__init__(obj)

class FinCanSketchShapeHandler(FinCanShapeHandler, FinSketchShapeHandler):

    def __init__(self, obj):
        super().__init__(obj)
