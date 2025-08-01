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
"""Class for drawing launch lugs"""

__title__ = "FreeCAD Launch Lug Handler"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

from typing import Any

import FreeCAD
import Part
import math

from Rocket.ShapeHandlers.BodyTubeShapeHandler import BodyTubeShapeHandler

from Rocket.Utilities import _err, validationError
from DraftTools import translate

TOLERANCE_OFFSET = 0.5     # Distance to offset a vertex

class LaunchLugShapeHandler(BodyTubeShapeHandler):

    def __init__(self, obj : Any) -> None:
        super().__init__(obj, scale=False)

        self._instanceCount = int(obj.InstanceCount)
        self._separation = float(obj.InstanceSeparation)

        self._forwardSweep = obj.ForwardSweep
        self._forwardSweepAngle = math.radians(float(obj.ForwardSweepAngle))
        self._aftSweep = obj.AftSweep
        self._aftSweepAngle = math.radians(float(obj.AftSweepAngle))

        self._radius = self._OD / 2.0
        self._zMin = -self._radius # Used for rake

    def isValidShape(self) -> bool:
        # Perform some general validations
        if self._forwardSweep:
            if (self._forwardSweepAngle <= 0.0) or (self._forwardSweepAngle >= 90.0):
                validationError(translate('Rocket', "Forward sweep angle must be greater than 0 degrees and less than 90 degrees"))
                return False

        if self._aftSweep:
            if (self._aftSweepAngle <= 0.0) or (self._aftSweepAngle >= 90.0):
                validationError(translate('Rocket', "Aft sweep angle must be greater than 0 degrees and less than 90 degrees"))
                return False

        return super().isValidShape()

    def rakeZ(self, x : float, slope: float, intercept: float) -> float:
        z = x * slope + intercept # In the (x,z) plane
        return z

    def _drawAftSweep(self) -> Any:
        # We need to calculate our vertices outside of the part to avoid OpenCASCADE's "too exact" problem
        slope = -1.0 / math.tan(self._aftSweepAngle)
        intercept = self._zMin - (slope * self._length)

        y = self._radius + TOLERANCE_OFFSET

        x1 = self._length + TOLERANCE_OFFSET
        z1 = self.rakeZ(x1, slope, intercept)
        v1 = FreeCAD.Vector(x1, y, z1)

        # x2 = self._length - (o + TOLERANCE_OFFSET)
        x2 = self._length - (((self._radius + math.fabs(self._zMin)) * math.tan(self._aftSweepAngle)) + TOLERANCE_OFFSET)
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

    def _drawForwardSweep(self) -> Any:
        # We need to calculate our vertices outside of the part to avoid OpenCASCADE's "too exact" problem
        slope = 1.0 / math.tan(self._forwardSweepAngle)

        y = self._radius + TOLERANCE_OFFSET

        x1 = -TOLERANCE_OFFSET
        z1 = self.rakeZ(x1, slope, self._zMin)
        v1 = FreeCAD.Vector(x1, y, z1)

        # x2 = o + TOLERANCE_OFFSET
        x2 = ((self._radius + math.fabs(self._zMin)) * math.tan(self._forwardSweepAngle)) + TOLERANCE_OFFSET
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

    def drawSingle(self) -> Any:
        edges = None
        edges = self._drawTubeEdges()

        if edges is not None:
            wire = Part.Wire(edges)
            face = Part.Face(wire)
            shape = face.revolve(FreeCAD.Vector(0, 0, 0),FreeCAD.Vector(1, 0, 0), 360)

            if self._forwardSweep:
                rake = self._drawForwardSweep()
                # Part.show(rake)
                shape = shape.cut(rake)
            if self._aftSweep:
                rake = self._drawAftSweep()
                # Part.show(rake)
                shape = shape.cut(rake)

            return shape

        return None

    def drawInstances(self) -> Any:
        lugs = []
        base = self.drawSingle()
        for i in range(self._instanceCount):
            lug = Part.Shape(base) # Create a copy
            lug.translate(FreeCAD.Vector(i * (self._length + self._separation),0,0))
            lugs.append(lug)

        return Part.makeCompound(lugs)

    def draw(self) -> None:
        if not self.isValidShape():
            return

        try:
            self._obj.Shape = self.drawInstances()
            self._obj.Placement = self._placement
        except (ZeroDivisionError, Part.OCCError):
            _err(translate('Rocket', "Launch lug parameters produce an invalid shape"))
            return
