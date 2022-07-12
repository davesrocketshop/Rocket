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
"""Class for drawing launch guides"""

__title__ = "FreeCAD Launch Guide Handler"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"
    
import FreeCAD
import Part
import math

from App.Constants import RAIL_GUIDE_BASE_CONFORMAL, RAIL_GUIDE_BASE_V

from App.Utilities import _err
from DraftTools import translate

TOLERANCE_OFFSET = 0.5     # Distance to offset a vertex

class RailGuideShapeHandler():
    def __init__(self, obj):

        # This gets changed when redrawn so it's very important to save a copy
        self._placement = obj.Placement

        self._railGuideBaseType = obj.RailGuideBaseType

        self._topWidth = float(obj.TopWidth)
        self._middleWidth = float(obj.MiddleWidth)
        self._baseWidth = float(obj.BaseWidth)
        self._topThickness = float(obj.TopThickness)
        self._baseThickness = float(obj.BaseThickness)
        self._thickness = float(obj.Thickness)
        self._length = float(obj.Length)

        self._diameter = float(obj.Diameter)
        self._autoDiameter = obj.AutoDiameter
        self._vAngle = math.radians(float(obj.VAngle))

        self._forwardSweep = obj.ForwardSweep
        self._forwardSweepAngle = math.radians(float(obj.ForwardSweepAngle))
        self._aftSweep = obj.AftSweep
        self._aftSweepAngle = math.radians(float(obj.AftSweepAngle))

        self._notch = obj.Notch
        self._notchWidth = float(obj.NotchWidth)
        self._notchDepth = float(obj.NotchDepth)

        self._zMin = 0 # Used for rake

        self._obj = obj

    def isValidShape(self):
        # Perform some general validations
        if self._middleWidth <= 0:
            _err(translate('Rocket', "Middle width must be greater than zero"))
            return False

        if self._topWidth <= self._middleWidth:
            _err(translate('Rocket', "Top width must be greater than the middle width"))
            return False

        if self._baseWidth <= self._middleWidth:
            _err(translate('Rocket', "Base width must be greater than the middle width"))
            return False

        if self._topThickness <= 0:
            _err(translate('Rocket', "Top thickness must be greater than zero"))
            return False

        if self._baseThickness <= 0:
            _err(translate('Rocket', "Base thickness must be greater than zero"))
            return False

        if self._thickness <= (self._topThickness + self._baseThickness):
            _err(translate('Rocket', "Total thickness must be greater than the sum of top and base thickness"))
            return False

        if self._length <= 0:
            _err(translate('Rocket', "Length must be greater than zero"))
            return False

        if self._forwardSweep:
            if (self._forwardSweepAngle <= 0.0) or (self._forwardSweepAngle >= 90.0):
                _err(translate('Rocket', "Forward sweep angle must be greater than 0 degrees and less than 90 degrees"))
                return False

        if self._aftSweep:
            if (self._aftSweepAngle <= 0.0) or (self._aftSweepAngle >= 90.0):
                _err(translate('Rocket', "Aft sweep angle must be greater than 0 degrees and less than 90 degrees"))
                return False

        if self._notch:
            if self._notchWidth <= 0:
                _err(translate('Rocket', "Notch width must be greater than zero"))
                return False

            if self._notchWidth >= self._middleWidth:
                _err(translate('Rocket', "Notch width can not exceed the middle width"))
                return False

            if self._notchDepth <= 0:
                _err(translate('Rocket', "Notch depth must be greater than zero"))
                return False

            if self._notchDepth >= self._thickness:
                _err(translate('Rocket', "Notch depth can not exceed the total thickness"))
                return False

        return True

    def _drawBaseFlat(self):
        base = Part.makeBox(self._length, self._baseWidth, self._baseThickness, FreeCAD.Vector(0,-self._baseWidth / 2.0,0), FreeCAD.Vector(0,0,1))
        return base

    def _drawBaseConformal(self):
        # Calculate end points
        radius = self._diameter / 2.0
        theta = math.asin(self._baseWidth / (self._diameter))
        a = math.cos(theta) * radius
        z = -(radius - a)
        y = self._baseWidth / 2.0

        self._zMin = z

        # draw end face
        v1 = FreeCAD.Vector(0,-y, z)
        v2 = FreeCAD.Vector(0,-y, z + self._baseThickness)
        v3 = FreeCAD.Vector(0, y, z)
        v4 = FreeCAD.Vector(0, y, z + self._baseThickness)
        v5 = FreeCAD.Vector(0, 0, 0)
        v6 = FreeCAD.Vector(0, 0, self._baseThickness)

        arc1 = Part.Arc(v1,v5,v3)
        arc2 = Part.Arc(v2,v6,v4)
        line1 = Part.LineSegment(v1, v2)
        line2 = Part.LineSegment(v3, v4)
        shape = Part.Shape([arc1, line1, line2, arc2])
        # Part.show(shape)
        wire = Part.Wire(shape.Edges)
        face = Part.Face(wire)
        base = face.extrude(FreeCAD.Vector(self._length, 0, 0))

        return base

    def _drawBaseV(self):
        # Calculate end points
        theta = self._vAngle / 2.0
        a = (self._baseWidth / 2.0) / math.fabs(math.tan(theta))
        z = -a
        y = self._baseWidth / 2.0

        self._zMin = z

        # draw end face
        v1 = FreeCAD.Vector(0,-y, z)
        v2 = FreeCAD.Vector(0,-y, z + self._baseThickness)
        v3 = FreeCAD.Vector(0, y, z)
        v4 = FreeCAD.Vector(0, y, z + self._baseThickness)
        v5 = FreeCAD.Vector(0, 0, 0)
        v6 = FreeCAD.Vector(0, 0, self._baseThickness)

        line1 = Part.LineSegment(v1, v5)
        line2 = Part.LineSegment(v5, v3)
        line3 = Part.LineSegment(v3, v4)
        line4 = Part.LineSegment(v4, v6)
        line5 = Part.LineSegment(v6, v2)
        line6 = Part.LineSegment(v1, v2)
        shape = Part.Shape([line1, line2, line3, line4, line5, line6])
        # Part.show(shape)
        wire = Part.Wire(shape.Edges)
        face = Part.Face(wire)
        base = face.extrude(FreeCAD.Vector(self._length, 0, 0))

        return base

    def _drawBase(self):
        if self._railGuideBaseType == RAIL_GUIDE_BASE_CONFORMAL:
            return self._drawBaseConformal()
        elif self._railGuideBaseType == RAIL_GUIDE_BASE_V:
            return self._drawBaseV()
        else:
            return self._drawBaseFlat()

    def rakeZ(self, x, slope, intercept):
        z = x * slope + intercept # In the (x,z) plane
        return z

    def _drawForwardSweep(self):
        # We need to calculate our vertices outside of the part to avoid OpenCASCADE's "too exact" problem
        slope = -1.0 / math.tan(self._forwardSweepAngle)
        intercept = self._zMin - (slope * self._length)

        y = max(self._topWidth, self._middleWidth, self._baseWidth) / 2.0 + TOLERANCE_OFFSET

        x1 = self._length + TOLERANCE_OFFSET
        z1 = self.rakeZ(x1, slope, intercept)        
        v1 = FreeCAD.Vector(x1, y, z1)

        # x2 = self._length - (o + TOLERANCE_OFFSET)
        x2 = self._length - (((self._thickness + math.fabs(self._zMin)) * math.tan(self._forwardSweepAngle)) + TOLERANCE_OFFSET)
        z2 = self.rakeZ(x2, slope, intercept)        
        v2 = FreeCAD.Vector(x2, y, z2)

        v3 = FreeCAD.Vector(x1, y, z2)

        line1 = Part.LineSegment(v1, v2)
        line2 = Part.LineSegment(v2, v3)
        line3 = Part.LineSegment(v3, v1)
        shape = Part.Shape([line1, line2, line3])
        # Part.show(shape)
        wire = Part.Wire(shape.Edges)
        face = Part.Face(wire)
        rake = face.extrude(FreeCAD.Vector(0, -2.0 * y, 0))

        return rake

    def _drawAftSweep(self):
        # We need to calculate our vertices outside of the part to avoid OpenCASCADE's "too exact" problem
        slope = 1.0 / math.tan(self._aftSweepAngle)

        y = max(self._topWidth, self._middleWidth, self._baseWidth) / 2.0 + TOLERANCE_OFFSET

        x1 = -TOLERANCE_OFFSET
        z1 = self.rakeZ(x1, slope, self._zMin)        
        v1 = FreeCAD.Vector(x1, y, z1)

        # x2 = o + TOLERANCE_OFFSET
        x2 = ((self._thickness + math.fabs(self._zMin)) * math.tan(self._aftSweepAngle)) + TOLERANCE_OFFSET
        z2 = self.rakeZ(x2, slope, self._zMin)        
        v2 = FreeCAD.Vector(x2, y, z2)

        v3 = FreeCAD.Vector(x1, y, z2)

        line1 = Part.LineSegment(v1, v2)
        line2 = Part.LineSegment(v2, v3)
        line3 = Part.LineSegment(v3, v1)
        shape = Part.Shape([line1, line2, line3])
        # Part.show(shape)
        wire = Part.Wire(shape.Edges)
        face = Part.Face(wire)
        rake = face.extrude(FreeCAD.Vector(0, -2.0 * y, 0))

        return rake

    def _drawNotch(self):
        return Part.makeBox(self._length, self._notchWidth, self._notchDepth, FreeCAD.Vector(0,-self._notchWidth / 2.0, self._thickness - self._notchDepth), FreeCAD.Vector(0,0,1))

    def _drawGuide(self):
        # Essentially creating an I beam
        guide = Part.makeBox(self._length, self._middleWidth, self._thickness, FreeCAD.Vector(0,-self._middleWidth / 2.0,0), FreeCAD.Vector(0,0,1))

        guideTop = Part.makeBox(self._length, self._topWidth, self._topThickness, FreeCAD.Vector(0,-self._topWidth / 2.0,self._thickness - self._topThickness), FreeCAD.Vector(0,0,1))
        guide = guide.fuse(guideTop)

        guideBottom = self._drawBase()
        guide = guide.fuse(guideBottom)

        if self._forwardSweep:
            rake = self._drawForwardSweep()
            guide = guide.cut(rake)
        if self._aftSweep:
            rake = self._drawAftSweep()
            guide = guide.cut(rake)
        if self._notch:
            notch = self._drawNotch()
            guide = guide.cut(notch)

        return guide
        
    def draw(self):
        if not self.isValidShape():
            return

        try:
            self._obj.Shape = self._drawGuide()
            self._obj.Placement = self._placement
        except (ZeroDivisionError, Part.OCCError):
            _err(translate('Rocket', "Rail Guide parameters produce an invalid shape"))
            return
