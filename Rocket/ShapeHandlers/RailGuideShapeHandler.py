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
"""Class for drawing launch guides"""

__title__ = "FreeCAD Launch Guide Handler"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

from typing import Any

import FreeCAD
import Part
import math

from Rocket.Constants import RAIL_GUIDE_BASE_CONFORMAL, RAIL_GUIDE_BASE_V

from Rocket.Utilities import _err, validationError
from Rocket.Utilities import translate

TOLERANCE_OFFSET = 0.5     # Distance to offset a vertex

class RailGuideShapeHandler():
    def __init__(self, obj : Any) -> None:

        # This gets changed when redrawn so it's very important to save a copy
        self._placement = FreeCAD.Placement(obj.Placement)

        self._instanceCount = int(obj.InstanceCount)
        self._separation = float(obj.InstanceSeparation)

        self._railGuideBaseType = obj.RailGuideBaseType

        self._flangeWidth = float(obj.FlangeWidth)
        self._middleWidth = float(obj.MiddleWidth)
        self._baseWidth = float(obj.BaseWidth)
        self._flangeHeight = float(obj.FlangeHeight)
        self._baseHeight = float(obj.BaseHeight)
        self._height = float(obj.Height)
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

    def isValidShape(self) -> bool:
        # Perform some general validations
        if self._middleWidth <= 0:
            validationError(translate('Rocket', "Middle width must be greater than zero"))
            return False

        if self._flangeWidth <= self._middleWidth:
            validationError(translate('Rocket', "Flange width must be greater than the middle width"))
            return False

        if self._baseWidth <= self._middleWidth:
            validationError(translate('Rocket', "Base width must be greater than the middle width"))
            return False

        if self._flangeHeight <= 0:
            validationError(translate('Rocket', "Top height must be greater than zero"))
            return False

        if self._baseHeight <= 0:
            validationError(translate('Rocket', "Base height must be greater than zero"))
            return False

        if self._height <= (self._flangeHeight + self._baseHeight):
            validationError(translate('Rocket', "Total height must be greater than the sum of top and base height"))
            return False

        if self._length <= 0:
            validationError(translate('Rocket', "Length must be greater than zero"))
            return False

        if self._forwardSweep:
            if (self._forwardSweepAngle <= 0.0) or (self._forwardSweepAngle >= 90.0):
                validationError(translate('Rocket', "Forward sweep angle must be greater than 0 degrees and less than 90 degrees"))
                return False

        if self._aftSweep:
            if (self._aftSweepAngle <= 0.0) or (self._aftSweepAngle >= 90.0):
                validationError(translate('Rocket', "Aft sweep angle must be greater than 0 degrees and less than 90 degrees"))
                return False

        if self._notch:
            if self._notchWidth <= 0:
                validationError(translate('Rocket', "Notch width must be greater than zero"))
                return False

            if self._notchWidth >= self._middleWidth:
                validationError(translate('Rocket', "Notch width can not exceed the middle width"))
                return False

            if self._notchDepth <= 0:
                validationError(translate('Rocket', "Notch depth must be greater than zero"))
                return False

            if self._notchDepth >= self._height:
                validationError(translate('Rocket', "Notch depth can not exceed the total height"))
                return False

        return True

    def _drawBaseFlat(self) -> Part.Solid:
        base = Part.makeBox(self._length, self._baseWidth, self._baseHeight, FreeCAD.Vector(0,-self._baseWidth / 2.0,0), FreeCAD.Vector(0,0,1))
        return base

    def _drawBaseConformal(self) -> Part.Solid:
        # Calculate end points
        radius = self._diameter / 2.0
        theta = math.asin(self._baseWidth / (self._diameter))
        a = math.cos(theta) * radius
        z = -(radius - a)
        y = self._baseWidth / 2.0

        self._zMin = z

        # draw end face
        v1 = FreeCAD.Vector(0,-y, z)
        v2 = FreeCAD.Vector(0,-y, z + self._baseHeight)
        v3 = FreeCAD.Vector(0, y, z)
        v4 = FreeCAD.Vector(0, y, z + self._baseHeight)
        v5 = FreeCAD.Vector(0, 0, 0)
        v6 = FreeCAD.Vector(0, 0, self._baseHeight)

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

    def _drawBaseV(self) -> Part.Solid:
        # Calculate end points
        theta = self._vAngle / 2.0
        a = (self._baseWidth / 2.0) / math.fabs(math.tan(theta))
        z = -a
        y = self._baseWidth / 2.0

        self._zMin = z

        # draw end face
        v1 = FreeCAD.Vector(0,-y, z)
        v2 = FreeCAD.Vector(0,-y, z + self._baseHeight)
        v3 = FreeCAD.Vector(0, y, z)
        v4 = FreeCAD.Vector(0, y, z + self._baseHeight)
        v5 = FreeCAD.Vector(0, 0, 0)
        v6 = FreeCAD.Vector(0, 0, self._baseHeight)

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

    def _drawBase(self) -> Part.Solid:
        if self._railGuideBaseType == RAIL_GUIDE_BASE_CONFORMAL:
            return self._drawBaseConformal()
        elif self._railGuideBaseType == RAIL_GUIDE_BASE_V:
            return self._drawBaseV()
        else:
            return self._drawBaseFlat()

    def rakeZ(self, x : float, slope : float, intercept : float) -> float:
        z = x * slope + intercept # In the (x,z) plane
        return z

    def _drawAftSweep(self) -> Part.Solid:
        # We need to calculate our vertices outside of the part to avoid OpenCASCADE's "too exact" problem
        slope = -1.0 / math.tan(self._aftSweepAngle)
        intercept = self._zMin - (slope * self._length)

        y = max(self._flangeWidth, self._middleWidth, self._baseWidth) / 2.0 + TOLERANCE_OFFSET

        x1 = self._length + TOLERANCE_OFFSET
        z1 = self.rakeZ(x1, slope, intercept)
        v1 = FreeCAD.Vector(x1, y, z1)

        # x2 = self._length - (o + TOLERANCE_OFFSET)
        x2 = self._length - (((self._height + math.fabs(self._zMin)) * math.tan(self._aftSweepAngle)) + TOLERANCE_OFFSET)
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

    def _drawForwardSweep(self) -> Part.Solid:
        # We need to calculate our vertices outside of the part to avoid OpenCASCADE's "too exact" problem
        slope = 1.0 / math.tan(self._forwardSweepAngle)

        y = max(self._flangeWidth, self._middleWidth, self._baseWidth) / 2.0 + TOLERANCE_OFFSET

        x1 = -TOLERANCE_OFFSET
        z1 = self.rakeZ(x1, slope, self._zMin)
        v1 = FreeCAD.Vector(x1, y, z1)

        # x2 = o + TOLERANCE_OFFSET
        x2 = ((self._height + math.fabs(self._zMin)) * math.tan(self._forwardSweepAngle)) + TOLERANCE_OFFSET
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

    def _drawNotch(self) -> Part.Solid:
        return Part.makeBox(self._length, self._notchWidth, self._notchDepth, FreeCAD.Vector(0,-self._notchWidth / 2.0, self._height - self._notchDepth), FreeCAD.Vector(0,0,1))

    def _drawGuide(self) -> Part.Solid:
        # Essentially creating an I beam
        guide = Part.makeBox(self._length, self._middleWidth, self._height, FreeCAD.Vector(0,-self._middleWidth / 2.0,0), FreeCAD.Vector(0,0,1))

        guideTop = Part.makeBox(self._length, self._flangeWidth, self._flangeHeight, FreeCAD.Vector(0,-self._flangeWidth / 2.0,self._height - self._flangeHeight), FreeCAD.Vector(0,0,1))
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

    def getZ0(self) -> float:
        # Calculate end points
        theta = self._vAngle / 2.0
        r = (self._diameter / 2.0)
        z0 = (r / math.sin(theta)) - r
        return z0

    def drawSingle(self) -> Any:
        shape = self._drawGuide()
        if self._obj.Proxy.isRocketAssembly() and self._railGuideBaseType == RAIL_GUIDE_BASE_V:
            shape.translate(FreeCAD.Vector(0,0,self.getZ0()))
            shape = Part.makeCompound(shape)

        return shape

    def drawInstances(self) -> Any:
        guides = []
        base = self.drawSingle()
        for i in range(self._instanceCount):
            guide = Part.Shape(base) # Create a copy
            guide.translate(FreeCAD.Vector(i * (self._length + self._separation),0,0))
            guides.append(guide)

        return Part.makeCompound(guides)

    def draw(self) -> None:
        if not self.isValidShape():
            return

        try:
            self._obj.Shape = self.drawInstances()
            self._obj.Placement = self._placement
        except (ValueError, ZeroDivisionError, Part.OCCError):
            _err(translate('Rocket', "Rail Guide parameters produce an invalid shape"))
            return
