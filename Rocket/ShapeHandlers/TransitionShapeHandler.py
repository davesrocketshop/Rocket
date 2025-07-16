# ***************************************************************************
# *   Copyright (c) 2021-2025 David Carter <dcarter@davidcarter.ca>         *
# *                                                                         *
# *   Significant portions of this code are derived directly or indirectly  *
# *   from the OpenRocket project                                           *
# *   https://github.com/openrocket/openrocket                              *
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
"""Base class for drawing transitions"""

__title__ = "FreeCAD Transition Shape Handler"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

from typing import Any

import FreeCAD
import Part
import math

from abc import abstractmethod

from DraftTools import translate

from Rocket.Constants import STYLE_CAPPED, STYLE_HOLLOW, STYLE_SOLID, STYLE_SOLID_CORE
from Rocket.Constants import STYLE_CAP_BAR, STYLE_CAP_CROSS

from Rocket.Utilities import _err, validationError

CLIP_PRECISION = 0.00001

class TransitionShapeHandler():
    def __init__(self, obj : Any) -> None:

        # This gets changed when redrawn so it's very important to save a copy
        self._placement = FreeCAD.Placement(obj.Placement)

        # Common parameters
        self._type = str(obj.TransitionType)
        self._style = str(obj.TransitionStyle)
        self._foreCapStyle = str(obj.ForeCapStyle)
        self._foreCapBarWidth = float(obj.ForeCapBarWidth)
        self._aftCapStyle = str(obj.AftCapStyle)
        self._aftCapBarWidth = float(obj.AftCapBarWidth)
        self._thickness = float(obj.Thickness)

        self._length = float(obj.Length)
        self._foreRadius = float(obj.ForeDiameter) / 2.0
        self._foreAuto = bool(obj.ForeAutoDiameter)
        self._aftRadius = float(obj.AftDiameter) / 2.0
        self._aftAuto = bool(obj.AftAutoDiameter)
        self._coreRadius = float(obj.CoreDiameter) / 2.0
        self._coefficient = float(obj.Coefficient)
        self._resolution = int(obj.Resolution)

        self._clipped = (bool(obj.Clipped) and self.isClippable()) # lgtm [py/init-calls-subclass]
        self._clipLength = -1.0
        self._clipR1 = -1.0
        self._clipR2 = -1.0

        self._foreShoulder = bool(obj.ForeShoulder)
        self._foreShoulderLength = float(obj.ForeShoulderLength)
        self._foreShoulderRadius = float(obj.ForeShoulderDiameter) / 2.0
        self._foreShoulderAuto = bool(obj.ForeShoulderAutoDiameter)
        self._foreShoulderThickness = float(obj.ForeShoulderThickness)

        self._aftShoulder = bool(obj.AftShoulder)
        self._aftShoulderLength = float(obj.AftShoulderLength)
        self._aftShoulderRadius = float(obj.AftShoulderDiameter) / 2.0
        self._aftShoulderAuto = bool(obj.AftShoulderAutoDiameter)
        self._aftShoulderThickness = float(obj.AftShoulderThickness)

        self._shoulder = (self._foreShoulder or self._aftShoulder)

        # Apply scaling
        self._scale = 1.0
        if obj.Proxy.isScaled():
            self._scale = 1.0 / obj.Proxy.getScale()
            self._length = self._length * self._scale
            if not self._foreAuto:
                self._foreRadius = self._foreRadius * self._scale
            if not self._aftAuto:
                self._aftRadius = self._aftRadius * self._scale
            if self._foreShoulderRadius > self._foreRadius:
                self._foreShoulderRadius = self._foreRadius - 0.001
            if self._aftShoulderRadius > self._aftRadius:
                self._aftShoulderRadius = self._aftRadius - 0.001

        # Used to show the shape outline for debugging
        self._debugShape = False

        self._obj = obj

    def makeSpline(self, points : list) -> Any:

        spline = Part.BSplineCurve()
        spline.buildFromPoles(points)
        return spline

    def isClippable(self) -> bool:
        return True # Override if the shape is not clippable

    def isValidShape(self) -> bool:

        #Perform some general validations
        if self._style in [STYLE_HOLLOW, STYLE_CAPPED]:
            if self._thickness <= 0:
                validationError(translate('Rocket', "For %s transitions thickness must be > 0") % self._style)
                return False
            if self._thickness >= self._foreRadius or self._thickness >= self._aftRadius:
                validationError(translate('Rocket', "Transition thickness must be less than the front or back radius"))
                return False

        elif self._style == STYLE_SOLID_CORE:
            if self._coreRadius >= self._foreRadius or self._coreRadius >= self._aftRadius:
                validationError(translate('Rocket', "Transition core must be less than the front or back diameter"))
                return False
            if self._foreShoulder:
                if self._coreRadius >= self._foreShoulderRadius:
                    validationError(translate('Rocket', "Transition core must be less than the shoulder diameter"))
                    return False
            if self._aftShoulder:
                if self._coreRadius >= self._aftShoulderRadius:
                    validationError(translate('Rocket', "Transition core must be less than the shoulder diameter"))
                    return False

        if self._foreShoulder:
            if self._foreShoulderLength <= 0:
                validationError(translate('Rocket', "Forward shoulder length must be > 0"))
                return False
            if self._foreShoulderRadius <= 0:
                validationError(translate('Rocket', "Forward shoulder diameter must be > 0"))
                return False
            if self._foreShoulderRadius > self._foreRadius:
                if self._foreShoulderAuto:
                    self._foreRadius = self._foreShoulderRadius + 0.001
                elif self._foreAuto:
                    self._foreShoulderRadius = self._foreRadius - 0.001
                else:
                    validationError(translate('Rocket', "Forward shoulder diameter can not exceed the transition diameter at the shoulder"))
                    return False
            if self._style in [STYLE_HOLLOW, STYLE_CAPPED]:
                if self._foreShoulderThickness <= 0:
                    validationError(translate('Rocket', "For %s transitions with a shoulder, shoulder thickness must be > 0") % self._style)
                    return False
                if self._foreShoulderThickness >= self._foreShoulderRadius:
                    validationError(translate('Rocket', "Shoulder thickness must be less than the shoulder radius"))
                    return False

        if self._aftShoulder:
            if self._aftShoulderLength <= 0:
                validationError(translate('Rocket', "Aft shoulder length must be > 0"))
                return False
            if self._aftShoulderRadius <= 0:
                validationError(translate('Rocket', "Aft shoulder diameter must be > 0"))
                return False
            if self._aftShoulderRadius > self._aftRadius:
                if self._aftShoulderAuto:
                    self._aftRadius = self._aftShoulderRadius + 0.001
                elif self._aftAuto:
                    self._aftShoulderRadius = self._aftRadius - 0.001
                else:
                    validationError(translate('Rocket', "Aft shoulder diameter can not exceed the transition diameter at the shoulder"))
                    return False
            if self._style in [STYLE_HOLLOW, STYLE_CAPPED]:
                if self._aftShoulderThickness <= 0:
                    validationError(translate('Rocket', "For %s transitions with a shoulder, shoulder thickness must be > 0") % self._style)
                    return False
                if self._aftShoulderThickness >= self._aftShoulderRadius:
                    validationError(translate('Rocket', "Shoulder thickness must be less than the shoulder radius"))
                    return False

        return True

    @abstractmethod
    def _radiusAt(self, r1 : float, r2 : float, length : float, pos : float) -> float:
        ...

    def getRadius(self, x : float) -> float:
        if self._clipped:
            self._calculateClip(self._foreRadius, self._aftRadius)

        radius = self._radiusAt(self._foreRadius, self._aftRadius, self._getLength(), x)
        return radius

    #
    # Numerically solve clipLength from the equation
    #     r1 == self._getRadius(clipLength,r2,clipLength+length)
    # using a binary search.  It assumes getOuterRadius() to be monotonically increasing.
    #
    def _calculateClip(self, r1 : float, r2 : float) -> None:

        # check if already calculated
        if self._clipR1 == r1 and self._clipR2 == r2:
            return
        self._clipR1 = r1
        self._clipR2 = r2

        min = 0.0
        max = self._length

        if self._debugShape:
            print("_calculateClip: r1 = %f, r2 = %f, length = %f" % (r1, r2, self._length))

        if r1 >= r2:
            tmp = r1
            r1 = r2
            r2 = tmp

        #
        # Keep increasing the length until our radius gets less than our target radius.
        # This sets the min and max range to search
        #
        n = 0
        rmax = self._radiusAt(r2, 0.0, max, self._length)
        while (rmax - r1) < 0:
            min = max
            max *= 2.0
            n += 1
            if n > 10:
                break
            rmax = self._radiusAt(r2, 0.0, max, self._length)

        # Do a binary search to see where we fit within tolerance
        while True:
            self._clipLength = (min + max) / 2.0
            val =self. _radiusAt(r2, 0.0, self._clipLength, self._length)
            err = (val - r1)
            if math.fabs(err) < CLIP_PRECISION:
                if self._debugShape:
                   print("_calculateClip: r1 = %f, r2 = %f, clip length = %f, err = %f" % (r1, r2, self._clipLength, err))
                return
            if err > 0:
                max = self._clipLength
            else:
                min = self._clipLength

    def _foreBarCap(self) -> Any:
        return self._foreCrossCap(barOnly = True)

    def _foreCrossCap(self, barOnly : bool = False) -> Any:
        BASE_WIDTH = 5
        base = 0.0 - BASE_WIDTH
        length = self._foreShoulderThickness + BASE_WIDTH
        if self._foreShoulder:
            length += self._foreShoulderLength
            base -= self._foreShoulderLength

        point = FreeCAD.Vector(base, 0, 0)
        direction = FreeCAD.Vector(1,0,0)

        mask = Part.makeCylinder(self._foreShoulderRadius - self._foreShoulderThickness, length, point, direction)

        point = FreeCAD.Vector(base + BASE_WIDTH, self._foreShoulderRadius, -(self._foreCapBarWidth / 2.0))
        box = Part.makeBox(self._foreCapBarWidth, 2.0 * self._foreShoulderRadius, length - BASE_WIDTH, point, direction)
        mask = mask.cut(box)
        if not barOnly:
            point = FreeCAD.Vector(base + BASE_WIDTH, (self._foreCapBarWidth / 2.0), -self._foreShoulderRadius)
            box = Part.makeBox(2.0 * self._foreShoulderRadius, self._foreCapBarWidth, length - BASE_WIDTH, point, direction)
            mask = mask.cut(box)

        return mask

    def _aftBarCap(self) -> Any:
        return self._aftCrossCap(barOnly = True)

    def _aftCrossCap(self, barOnly : bool = False) -> Any:
        BASE_WIDTH = 5
        base = self._length + BASE_WIDTH
        length = self._aftShoulderThickness + 2 * BASE_WIDTH
        if self._aftShoulder:
            length += self._aftShoulderLength
            base += self._aftShoulderLength

        point = FreeCAD.Vector(base, 0, 0)
        direction = FreeCAD.Vector(-1,0,0)

        mask = Part.makeCylinder(self._aftShoulderRadius - self._aftShoulderThickness, length, point, direction)

        point = FreeCAD.Vector(base + BASE_WIDTH, self._aftShoulderRadius, (self._aftCapBarWidth / 2.0))
        box = Part.makeBox(self._aftCapBarWidth, 2.0 * self._aftShoulderRadius, length, point, direction)
        mask = mask.cut(box)
        if not barOnly:
            point = FreeCAD.Vector(base + BASE_WIDTH, (self._aftCapBarWidth / 2.0), self._aftShoulderRadius)
            box = Part.makeBox(2.0 * self._aftShoulderRadius, self._aftCapBarWidth, length, point, direction)
            mask = mask.cut(box)

        return mask


    def draw(self) -> None:

        if not self.isValidShape():
            return

        self._debugShape = False
        edges = None
        try:
            if self._style == STYLE_SOLID:
                if self._shoulder:
                    edges = self._drawSolidShoulder()
                else:
                    edges = self._drawSolid()
            elif self._style == STYLE_SOLID_CORE:
                if self._shoulder:
                    edges = self._drawSolidShoulderCore()
                else:
                    edges = self._drawSolidCore()
            elif self._style == STYLE_HOLLOW:
                if self._shoulder:
                    edges = self._drawHollowShoulder()
                else:
                    edges = self._drawHollow()
            else:
                if self._shoulder:
                    edges = self._drawCappedShoulder()
                else:
                    edges = self._drawCapped()
        except (ValueError, ZeroDivisionError, Part.OCCError) as ex:
            if self._debugShape:
                raise ex
            _err(translate('Rocket', "Transition parameters produce an invalid shape"))
            return

        if edges is not None:
            try:
                if self._debugShape:
                    for edge in edges:
                        Part.show(edge)
                wire = Part.Wire(edges)
                face = Part.Face(wire)
                shape = face.revolve(FreeCAD.Vector(0, 0, 0),FreeCAD.Vector(1, 0, 0), 360)
            except Part.OCCError as ex:
                if self._debugShape:
                    raise ex
                _err(translate('Rocket', "Transition parameters produce an invalid shape"))
                return
        else:
            _err(translate('Rocket', "Transition parameters produce an invalid shape"))

        try:
            if self._style == STYLE_CAPPED:
                mask = None
                if self._foreCapStyle == STYLE_CAP_BAR:
                    mask = self._foreBarCap()
                elif self._foreCapStyle == STYLE_CAP_CROSS:
                    mask = self._foreCrossCap()

                if mask is not None:
                    shape = shape.cut(mask)
        except Part.OCCError:
            _err(translate('Rocket', "Forward cap style produces an invalid shape"))
            return

        try:
            if self._style == STYLE_CAPPED:
                mask = None
                if self._aftCapStyle == STYLE_CAP_BAR:
                    mask = self._aftBarCap()
                elif self._aftCapStyle == STYLE_CAP_CROSS:
                    mask = self._aftCrossCap()

                if mask is not None:
                    shape = shape.cut(mask)
        except Part.OCCError:
            _err(translate('Rocket', "Forward cap style produces an invalid shape"))
            return

        self._obj.Shape = shape
        self._obj.Placement = self._placement

    def _generateCurve(self, r1 : float, r2 : float, length : float, min : float = 0.0, max : float = 0.0) -> Any:
        """
            For clipped functions, length will be the clip length and self._length is
            the actual length
        """
        if self._debugShape:
            print("r1 = %f, r2 = %f, length = %f, min = %f, max = %f" % (r1, r2, length, min, max))
        if max <= 0:
            max = self._length

        if self._clipped:
            if r1 < r2:
                points = [FreeCAD.Vector(min, r1)] # 0
            else:
                points = [FreeCAD.Vector(max, r2)] # 1
        else:
            points = [FreeCAD.Vector(min, r1)] # 2,3

        for i in range(1, self._resolution):

            if self._clipped:
                if r1 < r2: # 0
                    x = min + (float(i) * ((max - min) / float(self._resolution)))
                    y = self._radiusAt(r2, 0.0, length, self._length - x)
                else: # 1
                    x = max - (float(i) * ((max - min) / float(self._resolution)))
                    y = self._radiusAt(r1, 0.0, length, x)
            else:
                # 2,3
                x = float(i) * ((max - min) / float(self._resolution)) + min
                y = self._radiusAt(r1, r2, length, x)
            points.append(FreeCAD.Vector(x, y))

        if self._clipped:
            if r1 < r2:
                points.append(FreeCAD.Vector(max, r2)) # 0
            else:
                points.append(FreeCAD.Vector(min, r1)) # 1
        else:
            points.append(FreeCAD.Vector(max, r2)) # 2, 3

        if self._debugShape:
            for point in points:
                print("x,y (%f,%f)" % (point.x, point.y))

        return self.makeSpline(points)

    def _getLength(self) -> float:
        if self._clipped:
            return self._clipLength
        return self._length

    def _curve(self) -> Any:
        if self._clipped:
            self._calculateClip(self._foreRadius, self._aftRadius)

        curve = self._generateCurve(self._foreRadius, self._aftRadius, self._getLength())
        return curve

    def _curveInnerHollow(self) -> Any:
        if self._clipped:
            self._calculateClip(self._foreRadius - self._thickness, self._aftRadius - self._thickness)

        curve = self._generateCurve(self._foreRadius - self._thickness, self._aftRadius - self._thickness, self._getLength())
        return curve

    def _curveInner(self, foreX : float, aftX : float, foreY : float, aftY : float) -> Any:
        if self._clipped:
            self._calculateClip(foreY, aftY)

        curve = self._generateCurve(foreY, aftY, self._getLength(), foreX, aftX)
        return curve

    def _clippedInnerRadius(self, r1 : float, r2 : float, pos : float) -> float:
        radius1 = r1 - self._thickness
        radius2 = r2 - self._thickness

        if self._clipped:
            self._calculateClip(radius1, radius2)
            if r2 > r1:
                radius = self._radiusAt(radius2, 0.0, self._clipLength, self._length - pos)
                return radius
            else:
                radius = self._radiusAt(radius1, 0.0, self._clipLength, pos)
                return radius
        return self._radiusAt(radius1, radius2, self._length, pos)

    def _drawSolid(self) -> list[Part.Edge]:
        outer_curve = self._curve()

        edges = self._solidLines(outer_curve)
        return edges

    def _drawSolidShoulder(self) -> list[Part.Edge]:
        outer_curve = self._curve()

        edges = self._solidShoulderLines(outer_curve)
        return edges

    def _drawSolidCore(self) -> list[Part.Edge]:
        outer_curve = self._curve()

        edges = self._solidCoreLines(outer_curve)
        return edges

    def _drawSolidShoulderCore(self) -> list[Part.Edge]:
        outer_curve = self._curve()

        edges = self._solidShoulderCoreLines(outer_curve)
        return edges

    def _drawHollow(self) -> list[Part.Edge]:
        outer_curve = self._curve()
        inner_curve = self._curveInnerHollow()

        edges = self._hollowLines(outer_curve, inner_curve)
        return edges

    def _drawHollowShoulder(self) -> list[Part.Edge]:
        innerForeX = 0.0
        if self._foreShoulder:
            innerForeX = self._thickness

        innerAftX = self._length
        if self._aftShoulder:
            innerAftX = self._length - self._thickness

        innerForeY = self._clippedInnerRadius(self._foreRadius, self._aftRadius, innerForeX)
        innerAftY = self._clippedInnerRadius(self._foreRadius, self._aftRadius, innerAftX)

        outer_curve = self._curve()
        inner_curve = self._curveInner(innerForeX, innerAftX, innerForeY, innerAftY)

        edges = self._hollowShoulderLines(innerForeY, innerAftY, outer_curve, inner_curve)
        return edges

    def _drawCapped(self) -> list[Part.Edge]:
        innerForeX = self._thickness
        innerAftX = self._length - self._thickness

        innerForeY = self._clippedInnerRadius(self._foreRadius, self._aftRadius, innerForeX)
        innerAftY = self._clippedInnerRadius(self._foreRadius, self._aftRadius, innerAftX)

        outer_curve = self._curve()
        inner_curve = self._curveInner(innerForeX, innerAftX, innerForeY, innerAftY)

        edges = self._cappedLines(innerForeY, innerAftY, outer_curve, inner_curve)
        return edges

    def _drawCappedShoulder(self) -> list[Part.Edge]:
        innerForeX = self._thickness
        innerAftX = self._length - self._thickness

        innerForeY = self._clippedInnerRadius(self._foreRadius, self._aftRadius, innerForeX)
        innerAftY = self._clippedInnerRadius(self._foreRadius, self._aftRadius, innerAftX)

        outer_curve = self._curve()
        inner_curve = self._curveInner(innerForeX, innerAftX, innerForeY, innerAftY)

        edges = self._cappedShoulderLines(innerForeY, innerAftY, outer_curve, inner_curve)
        return edges

    def _solidLines(self, outerShape : Any) -> list[Part.Edge]:

        foreCenter = FreeCAD.Vector(0.0, 0.0)
        aftCenter = FreeCAD.Vector(self._length, 0.0)

        foreRadius = FreeCAD.Vector(0.0, self._foreRadius)
        aftRadius = FreeCAD.Vector(self._length, self._aftRadius)

        line1 = Part.LineSegment(foreRadius, foreCenter)
        line2 = Part.LineSegment(foreCenter, aftCenter)
        line3 = Part.LineSegment(aftCenter, aftRadius)
        return [outerShape.toShape(), line1.toShape(), line2.toShape(), line3.toShape()]

    def _solidShoulderLines(self, outerShape : Any) -> list[Part.Edge]:

        front = []
        back = []
        if self._foreShoulder:
            step = (self._foreRadius > self._foreShoulderRadius)
            if step:
                line1 = Part.LineSegment(FreeCAD.Vector(0.0, self._foreRadius),                                FreeCAD.Vector(0.0, self._foreShoulderRadius))
            line2 = Part.LineSegment(FreeCAD.Vector(0.0, self._foreShoulderRadius),                        FreeCAD.Vector(-self._foreShoulderLength,self._foreShoulderRadius))
            line3 = Part.LineSegment(FreeCAD.Vector(-self._foreShoulderLength,self._foreShoulderRadius), FreeCAD.Vector(-self._foreShoulderLength,0))

            # Have to factor in an aft shoulder
            if self._aftShoulder:
                line4 = Part.LineSegment(FreeCAD.Vector(-self._foreShoulderLength,0), FreeCAD.Vector(self._aftShoulderLength, 0))
            else:
                line4 = Part.LineSegment(FreeCAD.Vector(-self._foreShoulderLength,0), FreeCAD.Vector(0, 0))

            if step:
                front = [line1.toShape(), line2.toShape(), line3.toShape(), line4.toShape()]
            else:
                front = [line2.toShape(), line3.toShape(), line4.toShape()]
        else:
            line1 = Part.LineSegment(FreeCAD.Vector(0.0, self._foreRadius), FreeCAD.Vector(0.0, 0))

            # Have to factor in an aft shoulder
            if self._aftShoulder:
                line2 = Part.LineSegment(FreeCAD.Vector(0.0,0), FreeCAD.Vector(self._aftShoulderLength, 0))
            else:
                line2 = Part.LineSegment(FreeCAD.Vector(0.0,0), FreeCAD.Vector(0, 0))
            front = [line1.toShape(), line2.toShape()]

        if self._aftShoulder:
            step = (self._aftRadius > self._aftShoulderRadius)
            if step:
                line1 = Part.LineSegment(FreeCAD.Vector(self._length, self._aftRadius),                                  FreeCAD.Vector(self._length, self._aftShoulderRadius))
            line2 = Part.LineSegment(FreeCAD.Vector(self._length, self._aftShoulderRadius),                          FreeCAD.Vector(self._length + self._aftShoulderLength,self._aftShoulderRadius))
            line3 = Part.LineSegment(FreeCAD.Vector(self._length + self._aftShoulderLength,self._aftShoulderRadius), FreeCAD.Vector(self._length + self._aftShoulderLength,0))
            if step:
                back = [line1.toShape(), line2.toShape(), line3.toShape()]
            else:
                back = [line2.toShape(), line3.toShape()]
        else:
            line1 = Part.LineSegment(FreeCAD.Vector(self._length, self._aftRadius), FreeCAD.Vector(self._length, 0))
            back = [line1.toShape()]

        return [outerShape.toShape()] + front + back

    def _solidCoreLines(self, outerShape : Any) -> list[Part.Edge]:

        foreCenter = FreeCAD.Vector(0.0, self._coreRadius)
        aftCenter = FreeCAD.Vector(self._length, self._coreRadius)

        foreRadius = FreeCAD.Vector(0.0, self._foreRadius)
        aftRadius = FreeCAD.Vector(self._length, self._aftRadius)

        line1 = Part.LineSegment(foreRadius, foreCenter)
        line2 = Part.LineSegment(foreCenter, aftCenter)
        line3 = Part.LineSegment(aftCenter, aftRadius)
        return [outerShape.toShape(), line1.toShape(), line2.toShape(), line3.toShape()]

    def _solidShoulderCoreLines(self, outerShape : Any) -> list[Part.Edge]:

        front = []
        back = []
        if self._foreShoulder:
            step = (self._foreRadius > self._foreShoulderRadius)
            if step:
                line1 = Part.LineSegment(FreeCAD.Vector(0.0, self._foreRadius),                                FreeCAD.Vector(0.0, self._foreShoulderRadius))
            line2 = Part.LineSegment(FreeCAD.Vector(0.0, self._foreShoulderRadius),                        FreeCAD.Vector(-self._foreShoulderLength,self._foreShoulderRadius))
            line3 = Part.LineSegment(FreeCAD.Vector(-self._foreShoulderLength,self._foreShoulderRadius), FreeCAD.Vector(-self._foreShoulderLength,self._coreRadius))

            # Have to factor in an aft shoulder
            if self._aftShoulder:
                line4 = Part.LineSegment(FreeCAD.Vector(-self._foreShoulderLength,self._coreRadius), FreeCAD.Vector(self._length + self._aftShoulderLength, self._coreRadius))
            else:
                line4 = Part.LineSegment(FreeCAD.Vector(-self._foreShoulderLength,self._coreRadius), FreeCAD.Vector(self._length, self._coreRadius))
            if step:
                front = [line1.toShape(), line2.toShape(), line3.toShape(), line4.toShape()]
            else:
                front = [line2.toShape(), line3.toShape(), line4.toShape()]
        else:
            line1 = Part.LineSegment(FreeCAD.Vector(0.0, self._foreRadius), FreeCAD.Vector(0.0, self._coreRadius))

            # Have to factor in an aft shoulder
            if self._aftShoulder:
                line2 = Part.LineSegment(FreeCAD.Vector(0.0,self._coreRadius), FreeCAD.Vector(self._length + self._aftShoulderLength, self._coreRadius))
            else:
                line2 = Part.LineSegment(FreeCAD.Vector(self._length,self._coreRadius), FreeCAD.Vector(0, self._coreRadius))
            front = [line1.toShape(), line2.toShape()]

        if self._aftShoulder:
            step = (self._aftRadius > self._aftShoulderRadius)
            if step:
                line1 = Part.LineSegment(FreeCAD.Vector(self._length, self._aftRadius),                                  FreeCAD.Vector(self._length, self._aftShoulderRadius))
            line2 = Part.LineSegment(FreeCAD.Vector(self._length, self._aftShoulderRadius),                          FreeCAD.Vector(self._length + self._aftShoulderLength,self._aftShoulderRadius))
            line3 = Part.LineSegment(FreeCAD.Vector(self._length + self._aftShoulderLength,self._aftShoulderRadius), FreeCAD.Vector(self._length + self._aftShoulderLength,self._coreRadius))
            if step:
                back = [line1.toShape(), line2.toShape(), line3.toShape()]
            else:
                back = [line2.toShape(), line3.toShape()]
        else:
            line1 = Part.LineSegment(FreeCAD.Vector(self._length, self._aftRadius), FreeCAD.Vector(self._length, self._coreRadius))
            back = [line1.toShape()]

        return [outerShape.toShape()] + front + back

    def _hollowLines(self, outerShape : Any, innerShape : Any) -> list[Part.Edge]:

        major = FreeCAD.Vector(self._length, self._aftRadius)
        minor = FreeCAD.Vector(0.0, self._foreRadius)

        innerMajor = FreeCAD.Vector(self._length, self._aftRadius - self._thickness)
        innerMinor = FreeCAD.Vector(0.0, self._foreRadius - self._thickness)

        line1 = Part.LineSegment(major, innerMajor)
        line2 = Part.LineSegment(minor, innerMinor)
        return [outerShape.toShape(), line1.toShape(), line2.toShape(), innerShape.toShape()]

    def _hollowShoulderLines(self, foreY : float, aftY : float, outerShape : Any, innerShape : Any) -> list[Part.Edge]:

        front = []
        back = []
        if self._foreShoulder:
            step = (self._foreRadius > self._foreShoulderRadius)
            if step:
                line1 = Part.LineSegment(FreeCAD.Vector(0.0, self._foreRadius),                                                              FreeCAD.Vector(0.0, self._foreShoulderRadius))
            line2 = Part.LineSegment(FreeCAD.Vector(0.0, self._foreShoulderRadius),                                                      FreeCAD.Vector(-self._foreShoulderLength,self._foreShoulderRadius))
            line3 = Part.LineSegment(FreeCAD.Vector(-self._foreShoulderLength,self._foreShoulderRadius),                               FreeCAD.Vector(-self._foreShoulderLength,self._foreShoulderRadius - self._foreShoulderThickness))
            line4 = Part.LineSegment(FreeCAD.Vector(-self._foreShoulderLength,self._foreShoulderRadius - self._foreShoulderThickness), FreeCAD.Vector(self._thickness,self._foreShoulderRadius - self._foreShoulderThickness))
            line5 = Part.LineSegment(FreeCAD.Vector(self._thickness,self._foreShoulderRadius - self._foreShoulderThickness),           FreeCAD.Vector(self._thickness,foreY))

            if step:
                front = [line1.toShape(), line2.toShape(), line3.toShape(), line4.toShape(), line5.toShape()]
            else:
                front = [line2.toShape(), line3.toShape(), line4.toShape(), line5.toShape()]
        else:
            line1 = Part.LineSegment(FreeCAD.Vector(0.0, self._foreRadius), FreeCAD.Vector(0.0, foreY))

            front = [line1.toShape()]

        if self._aftShoulder:
            step = (self._aftRadius > self._aftShoulderRadius)
            if step:
                line1 = Part.LineSegment(FreeCAD.Vector(self._length, self._aftRadius),                                                               FreeCAD.Vector(self._length, self._aftShoulderRadius))
            line2 = Part.LineSegment(FreeCAD.Vector(self._length, self._aftShoulderRadius),                                                       FreeCAD.Vector(self._length + self._aftShoulderLength,self._aftShoulderRadius))
            line3 = Part.LineSegment(FreeCAD.Vector(self._length + self._aftShoulderLength,self._aftShoulderRadius),                              FreeCAD.Vector(self._length + self._aftShoulderLength,self._aftShoulderRadius - self._aftShoulderThickness))
            line4 = Part.LineSegment(FreeCAD.Vector(self._length + self._aftShoulderLength,self._aftShoulderRadius - self._aftShoulderThickness), FreeCAD.Vector(self._length - self._thickness,self._aftShoulderRadius - self._aftShoulderThickness))
            line5 = Part.LineSegment(FreeCAD.Vector(self._length - self._thickness,self._aftShoulderRadius - self._aftShoulderThickness),         FreeCAD.Vector(self._length - self._thickness,aftY))

            if step:
                back = [line1.toShape(), line2.toShape(), line3.toShape(), line4.toShape(), line5.toShape()]
            else:
                back = [line2.toShape(), line3.toShape(), line4.toShape(), line5.toShape()]
        else:
            line1 = Part.LineSegment(FreeCAD.Vector(self._length, self._aftRadius), FreeCAD.Vector(self._length, aftY))

            back = [line1.toShape()]

        return [outerShape.toShape()] + front + back + [innerShape.toShape()]

    def _cappedLines(self, foreY : float, aftY : float, outerShape : Any, innerShape : Any) -> list[Part.Edge]:

        fore = FreeCAD.Vector(0.0, self._foreRadius)
        aft = FreeCAD.Vector(self._length, self._aftRadius)

        foreInner = FreeCAD.Vector(self._thickness, foreY)
        aftIinner = FreeCAD.Vector(self._length - self._thickness, aftY)

        foreCenter = FreeCAD.Vector(0,0)
        aftCenter = FreeCAD.Vector(self._length,0)

        foreInnerCenter = FreeCAD.Vector(self._thickness,0)
        aftInnerCenter = FreeCAD.Vector(self._length - self._thickness,0)

        line1 = Part.LineSegment(fore, foreCenter)
        line2 = Part.LineSegment(foreCenter, foreInnerCenter)
        line3 = Part.LineSegment(foreInnerCenter, foreInner)
        line4 = Part.LineSegment(aft, aftCenter)
        line5 = Part.LineSegment(aftCenter, aftInnerCenter)
        line6 = Part.LineSegment(aftInnerCenter, aftIinner)
        return [outerShape.toShape(), line1.toShape(), line2.toShape(), line3.toShape(), innerShape.toShape(), line4.toShape(), line5.toShape(), line6.toShape()]

    def _cappedShoulderLines(self, foreY : float, aftY : float, outerShape : Any, innerShape : Any) -> list[Part.Edge]:

        front = []
        back = []
        if self._foreShoulder:
            step = (self._foreRadius > self._foreShoulderRadius)
            if step:
                line1 = Part.LineSegment(FreeCAD.Vector(0.0, self._foreRadius),                                                                FreeCAD.Vector(0.0, self._foreShoulderRadius))
            line2 = Part.LineSegment(FreeCAD.Vector(0.0, self._foreShoulderRadius),                                                        FreeCAD.Vector(-self._foreShoulderLength,self._foreShoulderRadius))
            line3 = Part.LineSegment(FreeCAD.Vector(-self._foreShoulderLength,self._foreShoulderRadius),                                 FreeCAD.Vector(-self._foreShoulderLength,0))
            line4 = Part.LineSegment(FreeCAD.Vector(-self._foreShoulderLength,0),                                                        FreeCAD.Vector(-self._foreShoulderLength + self._foreShoulderThickness,0))
            line5 = Part.LineSegment(FreeCAD.Vector(-self._foreShoulderLength + self._foreShoulderThickness,0),                          FreeCAD.Vector(-self._foreShoulderLength + self._foreShoulderThickness,self._foreShoulderRadius - self._foreShoulderThickness))
            line6 = Part.LineSegment(FreeCAD.Vector(-self._foreShoulderLength + self._foreShoulderThickness,self._foreShoulderRadius - self._foreShoulderThickness),
                                                                                                                                            FreeCAD.Vector(self._thickness,self._foreShoulderRadius - self._foreShoulderThickness))
            line7 = Part.LineSegment(FreeCAD.Vector(self._thickness,self._foreShoulderRadius - self._foreShoulderThickness),
                                                                                                                                            FreeCAD.Vector(self._thickness,foreY))

            if step:
                front = [line1.toShape(), line2.toShape(), line3.toShape(), line4.toShape(), line5.toShape(), line6.toShape(), line7.toShape()]
            else:
                front = [line2.toShape(), line3.toShape(), line4.toShape(), line5.toShape(), line6.toShape(), line7.toShape()]
        else:
            line1 = Part.LineSegment(FreeCAD.Vector(0, self._foreRadius), FreeCAD.Vector(0, 0))
            line2 = Part.LineSegment(FreeCAD.Vector(0, 0),                FreeCAD.Vector(self._thickness, 0))
            line3 = Part.LineSegment(FreeCAD.Vector(self._thickness, 0),    FreeCAD.Vector(self._thickness, foreY))

            front = [line1.toShape(), line2.toShape(), line3.toShape()]

        if self._aftShoulder:
            step = (self._aftRadius > self._aftShoulderRadius)
            if step:
                line1 = Part.LineSegment(FreeCAD.Vector(self._length, self._aftRadius),                                                       FreeCAD.Vector(self._length, self._aftShoulderRadius))
            line2 = Part.LineSegment(FreeCAD.Vector(self._length, self._aftShoulderRadius),                                               FreeCAD.Vector(self._length + self._aftShoulderLength,self._aftShoulderRadius))
            line3 = Part.LineSegment(FreeCAD.Vector(self._length + self._aftShoulderLength,self._aftShoulderRadius),                      FreeCAD.Vector(self._length + self._aftShoulderLength,0))
            line4 = Part.LineSegment(FreeCAD.Vector(self._length + self._aftShoulderLength,0),                                            FreeCAD.Vector(self._length + self._aftShoulderLength - self._aftShoulderThickness,0))
            line5 = Part.LineSegment(FreeCAD.Vector(self._length + self._aftShoulderLength - self._aftShoulderThickness,0),               FreeCAD.Vector(self._length + self._aftShoulderLength - self._aftShoulderThickness,self._aftShoulderRadius - self._aftShoulderThickness))
            line6 = Part.LineSegment(FreeCAD.Vector(self._length + self._aftShoulderLength - self._aftShoulderThickness,self._aftShoulderRadius - self._aftShoulderThickness),
                                                                                                                                            FreeCAD.Vector(self._length - self._thickness,self._aftShoulderRadius - self._aftShoulderThickness))
            line7 = Part.LineSegment(FreeCAD.Vector(self._length - self._thickness,self._aftShoulderRadius - self._aftShoulderThickness), FreeCAD.Vector(self._length - self._thickness,aftY))

            if step:
                back = [line1.toShape(), line2.toShape(), line3.toShape(), line4.toShape(), line5.toShape(), line6.toShape(), line7.toShape()]
            else:
                back = [line2.toShape(), line3.toShape(), line4.toShape(), line5.toShape(), line6.toShape(), line7.toShape()]
        else:
            line1 = Part.LineSegment(FreeCAD.Vector(self._length, self._aftRadius),     FreeCAD.Vector(self._length, 0))
            line2 = Part.LineSegment(FreeCAD.Vector(self._length, 0),                   FreeCAD.Vector(self._length - self._thickness, 0))
            line3 = Part.LineSegment(FreeCAD.Vector(self._length - self._thickness, 0), FreeCAD.Vector(self._length - self._thickness, aftY))

            back = [line1.toShape(), line2.toShape(), line3.toShape()]

        return [outerShape.toShape()] + front + back + [innerShape.toShape()]
