# SPDX-License-Identifier: LGPL-2.1-or-later
# SPDX-File-Notice: Part of the Rocket addon.

################################################################################
#                                                                              #
#   © 2021 David Carter <dcarter@davidcarter.ca>                               #
#                                                                              #
#   This addon is free software: you can redistribute it and/or modify         #
#   it under the terms of the GNU Lesser General Public License as             #
#   published by the Free Software Foundation, either version 2.1              #
#   of the License, or (at your option) any later version.                     #
#                                                                              #
#   This addon is distributed in the hope that it will be useful,              #
#   but WITHOUT ANY WARRANTY; without even the implied warranty                #
#   of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.                    #
#   See the GNU Lesser General Public License for more details.                #
#                                                                              #
#   You should have received a copy of the GNU Lesser General Public           #
#   License along with this addon. If not, see https://www.gnu.org/licenses    #
#                                                                              #
################################################################################


"""Class for drawing rail buttons"""

__title__ = "FreeCAD Rail Button Handler"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

from typing import Any

import FreeCAD
import Part
import math

from Rocket.Constants import RAIL_BUTTON_AIRFOIL
from Rocket.Constants import COUNTERSINK_ANGLE_60, COUNTERSINK_ANGLE_82, COUNTERSINK_ANGLE_90, COUNTERSINK_ANGLE_100, \
                            COUNTERSINK_ANGLE_110, COUNTERSINK_ANGLE_120, COUNTERSINK_ANGLE_NONE

from Rocket.Utilities import _err, validationError

translate = FreeCAD.Qt.translate

class RailButtonShapeHandler():
    def __init__(self, obj : Any) -> None:

        # This gets changed when redrawn so it's very important to save a copy
        self._placement = FreeCAD.Placement(obj.Placement)

        self._railButtonType = obj.RailButtonType

        self._outerDiameter = float(obj.Diameter)
        self._innerDiameter = float(obj.InnerDiameter)
        self._flangeHeight = float(obj.FlangeHeight)
        self._baseHeight = float(obj.BaseHeight)
        self._height = float(obj.Height)
        self._length = float(obj.Length)

        self._hasFastener = obj.Fastener
        self._countersinkAngle = obj.CountersinkAngle
        self._headDiameter = float(obj.HeadDiameter)
        self._shankDiameter = float(obj.ShankDiameter)

        self._hasFillet = obj.FilletedTop
        self._filletRadius = float(obj.FilletRadius)

        self._instanceCount = int(obj.InstanceCount)
        self._separation = float(obj.InstanceSeparation)

        self._obj = obj

    def isValidShape(self) -> bool:
        # Perform some general validations
        if self._outerDiameter <= 0:
            validationError(translate('Rocket', "Outer diameter must be greater than zero"))
            return False
        if self._innerDiameter <= 0:
            validationError(translate('Rocket', "Inner diameter must be greater than zero"))
            return False
        if self._outerDiameter <= self._innerDiameter:
            validationError(translate('Rocket', "Outer diameter must be greater than the inner diameter"))
            return False
        if self._flangeHeight < 0:
            validationError(translate('Rocket', "Top height must be greater than or equal to zero"))
            return False
        if self._baseHeight < 0:
            validationError(translate('Rocket', "Base height must be greater than or equal to zero"))
            return False
        if self._height <= 0:
            validationError(translate('Rocket', "Height must be greater than zero"))
            return False
        if self._height <= (self._flangeHeight + self._baseHeight):
            validationError(translate('Rocket', "Top and base height can not exceed the total height"))
            return False

        if self._railButtonType == RAIL_BUTTON_AIRFOIL:
            if self._length <= 0:
                validationError(translate('Rocket', "Length must be greater than zero for airfoil rail buttons"))
                return False

            if self._length <= self._outerDiameter:
                validationError(translate('Rocket', "Length must be greater than the outer diameter for airfoil rail buttons"))
                return False

        return True

    def _fastenerCountersinkHeight(self) -> float:
        if self._countersinkAngle == COUNTERSINK_ANGLE_NONE:
            return 0

        angle = 0
        # Use the half angle
        if self._countersinkAngle == COUNTERSINK_ANGLE_60:
            angle = 30.0
        elif self._countersinkAngle == COUNTERSINK_ANGLE_82:
            angle = 41.0
        elif self._countersinkAngle == COUNTERSINK_ANGLE_90:
            angle = 45.0
        elif self._countersinkAngle == COUNTERSINK_ANGLE_100:
            angle = 50.0
        elif self._countersinkAngle == COUNTERSINK_ANGLE_110:
            angle = 55.0
        elif self._countersinkAngle == COUNTERSINK_ANGLE_120:
            angle = 60.0

        height = (self._headDiameter / 2.0) / math.tan(math.radians(angle))

        return height

    def _fastener(self) -> Any:
        fastener = Part.makeCylinder(self._shankDiameter / 2.0, self._height)
        if self._fastenerCountersinkHeight() > 0:
            countersink = Part.makeCone(self._headDiameter / 2.0, 0, self._fastenerCountersinkHeight(),
                            FreeCAD.Vector(0,0,self._height),
                            FreeCAD.Vector(0,0,-1))

            fastener = fastener.fuse(countersink)

        return fastener

    def _drawButton(self) -> Any:
        # For now, only round buttons
        spool = Part.makeCylinder(self._innerDiameter / 2.0, self._height, FreeCAD.Vector(0,0,0), FreeCAD.Vector(0,0,1))

        if self._flangeHeight > 0:
            spoolTop = Part.makeCylinder(self._outerDiameter / 2.0, self._flangeHeight, FreeCAD.Vector(0,0,self._height - self._flangeHeight), FreeCAD.Vector(0,0,1))
            if self._hasFillet:
                spoolTop = spoolTop.makeFillet(self._filletRadius, [spoolTop.Edges[0]])
            spool = spool.fuse(spoolTop)

        if self._baseHeight > 0:
            spoolBottom = Part.makeCylinder(self._outerDiameter / 2.0, self._baseHeight, FreeCAD.Vector(0,0,0), FreeCAD.Vector(0,0,1))
            spool = spool.fuse(spoolBottom)

        if self._hasFastener:
            spool = spool.cut(self._fastener())

        return spool

    def _airfoil(self, base : float, height : float, diameter : float, length : float) -> Any:
        # Calculate the tangent points
        radius = diameter/2.0
        theta = math.pi - math.atan2(length - radius, radius)
        x = -(radius * math.cos(theta))
        y = radius * math.sin(theta)

        v1 = FreeCAD.Vector(x,y,base)
        v2 = FreeCAD.Vector(x,-y,base)
        v3 = FreeCAD.Vector(-radius,0,base)
        v4 = FreeCAD.Vector(length - radius,0,base)

        arc = Part.Arc(v1,v3,v2)
        line1 = Part.LineSegment(v1, v4)
        line2 = Part.LineSegment(v2, v4)
        shape = Part.Shape([arc, line1, line2])
        wire = Part.Wire(shape.Edges)
        face = Part.Face(wire)
        airfoil = face.extrude(FreeCAD.Vector(0, 0, height))

        return airfoil

    def _drawAirfoil(self) -> Any:
        spool = self._airfoil(0.0, self._height, self._innerDiameter, self._length)
        spool.translate(FreeCAD.Vector(-(self._outerDiameter - self._innerDiameter) / 2.0, 0, 0))
        if self._hasFillet:
            spool = spool.makeFillet(self._filletRadius, [spool.Edges[3], spool.Edges[6], spool.Edges[8]])

        spoolTop = self._airfoil(self._height - self._flangeHeight, self._flangeHeight, self._outerDiameter, self._length)
        if self._hasFillet:
            spoolTop = spoolTop.makeFillet(self._filletRadius, [spoolTop.Edges[3], spoolTop.Edges[6], spoolTop.Edges[8]])
        spool = spool.fuse(spoolTop)

        spoolBottom = self._airfoil(0.0, self._baseHeight, self._outerDiameter, self._length)
        spool = spool.fuse(spoolBottom)

        if self._hasFastener:
            spool = spool.cut(self._fastener())

        return spool

    def drawSingle(self) -> Any:
        if self._railButtonType == RAIL_BUTTON_AIRFOIL:
            shape = self._drawAirfoil()
        else:
            shape = self._drawButton()

        return shape

    def drawInstances(self) -> Any:
        buttons = []
        base = self.drawSingle()
        for i in range(self._instanceCount):
            button = Part.Shape(base) # Create a copy
            button.translate(FreeCAD.Vector(i * (self._length + self._separation),0,0))
            buttons.append(button)

        return Part.makeCompound(buttons)

    def draw(self) -> None:
        if not self.isValidShape():
            return

        try:
            self._obj.Shape = self.drawInstances()
            self._obj.Placement = self._placement
        except (ZeroDivisionError, Part.OCCError):
            _err(translate('Rocket', "Rail button parameters produce an invalid shape"))
            return
