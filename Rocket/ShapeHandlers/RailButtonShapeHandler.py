# ***************************************************************************
# *   Copyright (c) 2021-2023 David Carter <dcarter@davidcarter.ca>         *
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
"""Class for drawing rail buttons"""

__title__ = "FreeCAD Rail Button Handler"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"
    
import FreeCAD
import Part
import math

from Rocket.ShapeHandlers.ShapeHandlerBase import ShapeHandlerBase

from Rocket.Constants import RAIL_BUTTON_AIRFOIL
from Rocket.Constants import CONTERSINK_ANGLE_60, CONTERSINK_ANGLE_82, CONTERSINK_ANGLE_90, CONTERSINK_ANGLE_100, \
                            CONTERSINK_ANGLE_110, CONTERSINK_ANGLE_120

from Rocket.Utilities import _err, validationError
from DraftTools import translate

class RailButtonShapeHandler(ShapeHandlerBase):
    def __init__(self, obj):

        # This gets changed when redrawn so it's very important to save a copy
        self._placement = FreeCAD.Placement(obj.Placement)

        self._railButtonType = obj.RailButtonType

        self._outerDiameter = float(obj.Diameter)
        self._innerDiameter = float(obj.InnerDiameter)
        self._topThickness = float(obj.TopThickness)
        self._baseThickness = float(obj.BaseThickness)
        self._thickness = float(obj.Thickness)
        self._length = float(obj.Length)

        self._hasFastener = obj.Fastener
        self._countersinkAngle = obj.CountersinkAngle
        self._headDiameter = float(obj.HeadDiameter)
        self._shankDiameter = float(obj.ShankDiameter)

        self._hasFillet = obj.FilletedTop
        self._filletRadius = float(obj.FilletRadius)

        self._obj = obj

    def isValidShape(self):
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
        if self._topThickness <= 0:
            validationError(translate('Rocket', "Top thickness must be greater than zero"))
            return False
        if self._baseThickness <= 0:
            validationError(translate('Rocket', "Base thickness must be greater than zero"))
            return False
        if self._thickness <= 0:
            validationError(translate('Rocket', "Thickness must be greater than zero"))
            return False
        if self._thickness <= (self._topThickness + self._baseThickness):
            validationError(translate('Rocket', "Top and base thickness can not excedd the total thickness"))
            return False

        if self._railButtonType == RAIL_BUTTON_AIRFOIL:
            if self._length <= 0:
                validationError(translate('Rocket', "Length must be greater than zero for airfoil rail buttons"))
                return False

            if self._length <= self._outerDiameter:
                validationError(translate('Rocket', "Length must be greater than the outer diameter for airfoil rail buttons"))
                return False

        return True

    def _fastenerCountersinkHeight(self):
        angle = 0
        # Use the half angle
        if self._countersinkAngle == CONTERSINK_ANGLE_60:
            angle = 30.0
        elif self._countersinkAngle == CONTERSINK_ANGLE_82:
            angle = 41.0
        elif self._countersinkAngle == CONTERSINK_ANGLE_90:
            angle = 45.0
        elif self._countersinkAngle == CONTERSINK_ANGLE_100:
            angle = 50.0
        elif self._countersinkAngle == CONTERSINK_ANGLE_110:
            angle = 55.0
        elif self._countersinkAngle == CONTERSINK_ANGLE_120:
            angle = 60.0

        height = (self._headDiameter / 2.0) / math.tan(math.radians(angle))
        
        return height

    def _fastener(self):
        fastener = Part.makeCone(self._headDiameter / 2.0, 0, self._fastenerCountersinkHeight(),
                        FreeCAD.Vector(0,0,self._thickness),
                        FreeCAD.Vector(0,0,-1))
        shank = Part.makeCylinder(self._shankDiameter / 2.0, self._thickness)

        fastener = fastener.fuse(shank)

        return fastener

    def _drawButton(self):
        # For now, only round buttons
        spool = Part.makeCylinder(self._innerDiameter / 2.0, self._thickness, FreeCAD.Vector(0,0,0), FreeCAD.Vector(0,0,1))

        spoolTop = Part.makeCylinder(self._outerDiameter / 2.0, self._topThickness, FreeCAD.Vector(0,0,self._thickness - self._topThickness), FreeCAD.Vector(0,0,1))
        if self._hasFillet:
            spoolTop = spoolTop.makeFillet(self._filletRadius, [spoolTop.Edges[0]])
        spool = spool.fuse(spoolTop)

        # spoolBottom = Part.makeCylinder(self._outerDiameter / 2.0, self._thickness - self._topThickness, FreeCAD.Vector(0,0,0), FreeCAD.Vector(1,0,0))
        spoolBottom = Part.makeCylinder(self._outerDiameter / 2.0, self._baseThickness, FreeCAD.Vector(0,0,0), FreeCAD.Vector(0,0,1))
        spool = spool.fuse(spoolBottom)

        if self._hasFastener:
            spool = spool.cut(self._fastener())

        return spool

    def _airfoil(self, base, thickness, diameter, length):
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
        airfoil = face.extrude(FreeCAD.Vector(0, 0, thickness))

        return airfoil

    def _drawAirfoil(self):
        spool = self._airfoil(0.0, self._thickness, self._innerDiameter, self._length)
        spool.translate(FreeCAD.Vector(-(self._outerDiameter - self._innerDiameter) / 2.0, 0, 0))
        if self._hasFillet:
            spool = spool.makeFillet(self._filletRadius, [spool.Edges[3], spool.Edges[6], spool.Edges[8]])

        spoolTop = self._airfoil(self._thickness - self._topThickness, self._topThickness, self._outerDiameter, self._length)
        if self._hasFillet:
            spoolTop = spoolTop.makeFillet(self._filletRadius, [spoolTop.Edges[3], spoolTop.Edges[6], spoolTop.Edges[8]])
        spool = spool.fuse(spoolTop)

        spoolBottom = self._airfoil(0.0, self._baseThickness, self._outerDiameter, self._length)
        spool = spool.fuse(spoolBottom)

        if self._hasFastener:
            spool = spool.cut(self._fastener())

        return spool
        
    def draw(self):
        if not self.isValidShape():
            return

        try:
            if self._railButtonType == RAIL_BUTTON_AIRFOIL:
                shape = self._drawAirfoil()
            else:
                shape = self._drawButton()
            if self._obj.PodInfo is not None:
                shape = self._drawPods(shape)

            self._obj.Shape = shape
            self._obj.Placement = self._placement
        except (ZeroDivisionError, Part.OCCError):
            _err(translate('Rocket', "Rail button parameters produce an invalid shape"))
            return
