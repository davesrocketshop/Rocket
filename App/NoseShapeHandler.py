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
"""Base class for drawing nose cones"""

__title__ = "FreeCAD Nose Shape Handler"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"
    
import FreeCAD
import Part

import math

from DraftTools import translate

from App.Constants import STYLE_CAPPED, STYLE_HOLLOW, STYLE_SOLID
from App.Constants import STYLE_CAP_BAR, STYLE_CAP_CROSS
from App.Constants import TYPE_BLUNTED_CONE, TYPE_BLUNTED_OGIVE, TYPE_SECANT_OGIVE

from App.Utilities import _err

class NoseShapeHandler():
    def __init__(self, obj):

        # This gets changed when redrawn so it's very important to save a copy
        self._placement = obj.Placement

        # Common parameters    
        self._type = str(obj.NoseType)    
        self._style = str(obj.NoseStyle)
        self._capStyle = str(obj.CapStyle)
        self._capBarWidth = float(obj.CapBarWidth)
        self._thickness = float(obj.Thickness)

        self._shoulder = bool(obj.Shoulder)
        self._shoulderLength = float(obj.ShoulderLength)
        self._shoulderRadius = float(obj.ShoulderDiameter) / 2.0
        self._shoulderThickness = float(obj.ShoulderThickness)

        self._length = float(obj.Length)
        self._radius = float(obj.Diameter) / 2.0
        self._noseRadius = float(obj.BluntedDiameter) / 2.0
        self._coefficient = float(obj.Coefficient)
        self._ogiveRadius = float(obj.OgiveDiameter) / 2.0
        self._resolution = int(obj.Resolution)
        self._obj = obj

    def makeSpline(self, points):
        spline = Part.BSplineCurve()
        spline.buildFromPoles(points)
        return spline

    def isValidShape(self):
        # Perform some general validations
        if self._style in [STYLE_HOLLOW, STYLE_CAPPED]:
            if self._thickness <= 0:
                _err(translate('Rocket', "For %s nose cones thickness must be > 0") % self._style)
                return False
            if self._thickness >= self._radius:
                _err(translate('Rocket', "Nose cones thickness must be less than the nose cone radius"))
                return False
        if self._type in [TYPE_BLUNTED_CONE, TYPE_BLUNTED_OGIVE]:
            if self._noseRadius >= self._radius:
                _err(translate('Rocket', "Nose diameter must be less than the base diameter"))
                return False
            if self._noseRadius <= 0:
                _err(translate('Rocket', "Nose diameter must be greater than zero"))
                return False
        if self._type == TYPE_SECANT_OGIVE:
            minDiameter = math.sqrt(self._length * self._length + self._radius * self._radius)
            if self._ogiveRadius < (minDiameter / 2.0):
                _err(translate('Rocket', "Ogive diameter must be greater than %f (sqrt(length^2 + radius^2))" % minDiameter))
                return False
        if self._shoulder:
            if self._shoulderLength <= 0:
                _err(translate('Rocket', "Shoulder length must be > 0"))
                return False
            if self._shoulderRadius <= 0:
                _err(translate('Rocket', "Shoulder diameter must be > 0"))
                return False
            if self._shoulderRadius > self._radius:
                _err(translate('Rocket', "Shoulder diameter can not exceed the nose cone diameter"))
                return False
            if self._style in [STYLE_HOLLOW, STYLE_CAPPED]:
                if self._shoulderThickness <= 0:
                    _err(translate('Rocket', "For %s nose cones with a shoulder, shoulder thickness must be > 0") % self._style)
                    return False
                if self._shoulderThickness >= self._shoulderRadius:
                    _err(translate('Rocket', "Shoulder thickness must be less than the shoulder radius"))
                    return False

        return True

    def _barCap(self):
        return self._crossCap(barOnly = True)

    def _crossCap(self, barOnly = False):
        BASE_WIDTH = 5
        base = 0.0 - BASE_WIDTH
        length = self._thickness + BASE_WIDTH
        if self._shoulder:
            length += self._shoulderLength
            base -= self._shoulderLength

        point = FreeCAD.Vector(base, 0, 0)
        direction = FreeCAD.Vector(1,0,0)

        mask = Part.makeCylinder(self._shoulderRadius - self._shoulderThickness, length, point, direction)

        point = FreeCAD.Vector(base + BASE_WIDTH, self._radius, -(self._capBarWidth / 2.0))
        box = Part.makeBox(self._capBarWidth, 2.0 * self._radius, length - BASE_WIDTH, point, direction)
        mask = mask.cut(box)
        if not barOnly:
            point = FreeCAD.Vector(base + BASE_WIDTH, (self._capBarWidth / 2.0), -self._radius)
            box = Part.makeBox(2.0 * self._radius, self._capBarWidth, length - BASE_WIDTH, point, direction)
            mask = mask.cut(box)
        return mask
        
    def draw(self):
        if not self.isValidShape():
            return

        edges = None

        try:
            if self._style == STYLE_SOLID:
                if self._shoulder:
                    edges = self.drawSolidShoulder()
                else:
                    edges = self.drawSolid()
            elif self._style == STYLE_HOLLOW:
                if self._shoulder:
                    edges = self.drawHollowShoulder()
                else:
                    edges = self.drawHollow()
            else:
                if self._shoulder:
                    edges = self.drawCappedShoulder()
                else:
                    edges = self.drawCapped()
        except (ZeroDivisionError, Part.OCCError):
            _err(translate('Rocket', "Nose cone parameters produce an invalid shape"))
            return

        shape = None
        if edges is not None:
            try:
                wire = Part.Wire(edges)
                face = Part.Face(wire)
                shape = face.revolve(FreeCAD.Vector(0, 0, 0),FreeCAD.Vector(1, 0, 0), 360)
            except Part.OCCError:
                _err(translate('Rocket', "Nose cone parameters produce an invalid shape"))
                return
        else:
            _err(translate('Rocket', "Nose cone parameters produce an invalid shape"))
            return

        try:
            if self._style == STYLE_CAPPED:
                mask = None
                if self._capStyle == STYLE_CAP_BAR:
                    mask = self._barCap()
                elif self._capStyle == STYLE_CAP_CROSS:
                    mask = self._crossCap()

                if mask is not None:
                    shape = shape.cut(mask)
        except Part.OCCError:
            _err(translate('Rocket', "Nose cone cap style produces an invalid shape"))
            return

        self._obj.Shape = shape
        self._obj.Placement = self._placement

    def toShape(self, shapeObject):
        if hasattr(shapeObject, 'toShape'):
            return shapeObject.toShape()
        return shapeObject

    def solidLines(self, outerShape):
        center = FreeCAD.Vector(0.0, 0.0)
        major = FreeCAD.Vector(self._length, 0.0)
        minor = FreeCAD.Vector(0.0, self._radius)

        line1 = Part.LineSegment(center, major)
        line2 = Part.LineSegment(center, minor)
        return [self.toShape(outerShape), line1.toShape(), line2.toShape()]

    def solidShoulderLines(self, outerShape):
        major = FreeCAD.Vector(self._length,0)
        minor = FreeCAD.Vector(0,self._radius)

        line1 = Part.LineSegment(major,                                                     FreeCAD.Vector(-self._shoulderLength,0))
        line2 = Part.LineSegment(FreeCAD.Vector(-self._shoulderLength,0),                   FreeCAD.Vector(-self._shoulderLength,self._shoulderRadius))
        line3 = Part.LineSegment(FreeCAD.Vector(-self._shoulderLength,self._shoulderRadius),FreeCAD.Vector(0,self._shoulderRadius))
        line4 = Part.LineSegment(FreeCAD.Vector(0,self._shoulderRadius),                     minor)
        return [self.toShape(outerShape), line1.toShape(), line2.toShape(), line3.toShape(), line4.toShape()]

    def hollowLines(self, max_x, outerShape, innerShape):
        major = FreeCAD.Vector(self._length,0)
        minor = FreeCAD.Vector(0,self._radius)

        innerMajor = FreeCAD.Vector(max_x,0)
        innerMinor = FreeCAD.Vector(0,self._radius - self._thickness)

        line1 = Part.LineSegment(major, innerMajor)
        line2 = Part.LineSegment(minor, innerMinor)
        return [self.toShape(outerShape), line1.toShape(), line2.toShape(), self.toShape(innerShape)]

    def hollowShoulderLines(self, max_x, minor_y, outerShape, innerShape):
        major = FreeCAD.Vector(self._length,0)
        minor = FreeCAD.Vector(0,self._radius)

        innerMajor = FreeCAD.Vector(max_x,0)
        innerMinor = FreeCAD.Vector(self._thickness, minor_y)

        end2 = FreeCAD.Vector(0,                       self._shoulderRadius)
        end3 = FreeCAD.Vector(-self._shoulderLength,   self._shoulderRadius)
        end4 = FreeCAD.Vector(-self._shoulderLength,   self._shoulderRadius - self._shoulderThickness)
        end5 = FreeCAD.Vector(self._thickness, self._shoulderRadius - self._shoulderThickness)
        line1 = Part.LineSegment(major, innerMajor)
        line2 = Part.LineSegment(minor, end2)
        line3 = Part.LineSegment(end2,  end3)
        line4 = Part.LineSegment(end3,  end4)
        line5 = Part.LineSegment(end4,  end5)
        line6 = Part.LineSegment(end5,  innerMinor)
        return [self.toShape(outerShape), line1.toShape(), line2.toShape(), line3.toShape(), line4.toShape(), line5.toShape(), line6.toShape(), self.toShape(innerShape)]

    def cappedLines(self, max_x, minor_y, outerShape, innerShape):
        center = FreeCAD.Vector(0,0)
        major = FreeCAD.Vector(self._length,0)
        minor = FreeCAD.Vector(0,self._radius)

        innerMajor = FreeCAD.Vector(max_x,0)
        innerMinor = FreeCAD.Vector(self._thickness, minor_y)

        line1 = Part.LineSegment(major, innerMajor)
        line2 = Part.LineSegment(minor, center)
        line3 = Part.LineSegment(center, FreeCAD.Vector(self._thickness, 0))
        line4 = Part.LineSegment(FreeCAD.Vector(self._thickness, 0), innerMinor)
        return [self.toShape(outerShape), line1.toShape(), line2.toShape(), line3.toShape(), line4.toShape(), self.toShape(innerShape)]

    def cappedShoulderLines(self, max_x, minor_y, outerShape, innerShape):
        major = FreeCAD.Vector(self._length,0)
        minor = FreeCAD.Vector(0,self._radius)

        innerMajor = FreeCAD.Vector(max_x,0)
        innerMinor = FreeCAD.Vector(self._thickness, minor_y)

        end2 = FreeCAD.Vector(0,                                            self._shoulderRadius)
        end3 = FreeCAD.Vector(-self._shoulderLength,                        self._shoulderRadius)
        end4 = FreeCAD.Vector(-self._shoulderLength,                        0)
        end5 = FreeCAD.Vector(self._shoulderThickness-self._shoulderLength, 0)
        end6 = FreeCAD.Vector(self._shoulderThickness-self._shoulderLength, self._shoulderRadius-self._shoulderThickness)
        end7 = FreeCAD.Vector(self._thickness,                              self._shoulderRadius-self._shoulderThickness)
        line1 = Part.LineSegment(major, innerMajor)
        line2 = Part.LineSegment(minor, end2)
        line3 = Part.LineSegment(end2,  end3)
        line4 = Part.LineSegment(end3,  end4)
        line5 = Part.LineSegment(end4,  end5)
        line6 = Part.LineSegment(end5,  end6)
        line7 = Part.LineSegment(end6,  end7)
        line8 = Part.LineSegment(end7,  innerMinor)
        return [self.toShape(outerShape), line1.toShape(), line2.toShape(), line3.toShape(), line4.toShape(), 
                line5.toShape(), line6.toShape(), line7.toShape(), line8.toShape(), self.toShape(innerShape)]
