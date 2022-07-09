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

from App.Constants import FINCAN_CROSS_SQUARE, FINCAN_CROSS_ROUND, FINCAN_CROSS_TAPER
from App.Utilities import _err

from App.FinShapeHandler import FinShapeHandler
from App.FinTrapezoidShapeHandler import FinTrapezoidShapeHandler
from App.FinEllipseShapeHandler import FinEllipseShapeHandler
from App.FinSketchShapeHandler import FinSketchShapeHandler

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
        if self._obj.LeadingEdge != FINCAN_CROSS_SQUARE:
            edge += self._obj.LeadingLength
        if self._obj.TrailingEdge != FINCAN_CROSS_SQUARE:
            edge += self._obj.TrailingLength
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
        if self._obj.LeadingEdge == FINCAN_CROSS_ROUND:
            return self._leadingRound()
        elif self._obj.LeadingEdge == FINCAN_CROSS_TAPER:
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
        if self._obj.TrailingEdge == FINCAN_CROSS_ROUND:
            return self._trailingRound()
        elif self._obj.TrailingEdge == FINCAN_CROSS_TAPER:
            return self._trailingTaper()
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
