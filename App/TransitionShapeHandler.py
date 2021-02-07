# ***************************************************************************
# *   Copyright (c) 2021 David Carter <dcarter@davidcarter.ca>              *
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
    
import FreeCAD
import FreeCADGui
import Part

from App.Constants import TYPE_CONE, TYPE_ELLIPTICAL, TYPE_HAACK, TYPE_OGIVE, TYPE_VON_KARMAN, TYPE_PARABOLA, TYPE_PARABOLIC, TYPE_POWER
from App.Constants import STYLE_CAPPED, STYLE_HOLLOW, STYLE_SOLID, STYLE_SOLID_CORE

from App.Utilities import _err, _msg

CLIP_PRECISION = 0.0001

class TransitionShapeHandler():
    def __init__(self, obj):

        # Common parameters
        self._type = str(obj.TransitionType)
        self._style = str(obj.TransitionStyle)
        self._thickness = float(obj.Thickness)

        self._length = float(obj.Length)
        self._foreRadius = float(obj.ForeRadius)
        self._aftRadius = float(obj.AftRadius)
        self._coreRadius = float(obj.CoreRadius)
        self._coefficient = float(obj.Coefficient)
        self._resolution = int(obj.Resolution)

        self._clipped = bool(obj.Clipped)
        self._clipLength = -1

        self._foreShoulder = bool(obj.ForeShoulder)
        self._foreShoulderLength = float(obj.ForeShoulderLength)
        self._foreShoulderRadius = float(obj.ForeShoulderRadius)
        self._foreShoulderThickness = float(obj.ForeShoulderThickness)

        self._aftShoulder = bool(obj.AftShoulder)
        self._aftShoulderLength = float(obj.AftShoulderLength)
        self._aftShoulderRadius = float(obj.AftShoulderRadius)
        self._aftShoulderThickness = float(obj.AftShoulderThickness)

        self._shoulder = (self._foreShoulder or self._aftShoulder)

        self._obj = obj

    def makeSpline(self, points):
        
        spline = Part.BSplineCurve()
        spline.buildFromPoles(points)
        return spline

    def isValidShape(self):
        
        #Perform some general validations
        if self._style in [STYLE_HOLLOW, STYLE_CAPPED]:
        	if self._thickness <= 0:
        		_err("For %s transitions thickness must be > 0" % self._style)
        		return False
        	if self._thickness >= self._foreRadius or self._thickness >= self._aftRadius:
        		_err("Transition thickness must be less than the front or back radius")
        		return False

        elif self._style == STYLE_SOLID_CORE:
            if self._coreRadius >= self._foreRadius or self._coreRadius >= self._aftRadius:
                _err("Transition core must be less than the front or back radius")
                return False
            if self._foreShoulder:
                if self._coreRadius >= self._foreShoulderRadius:
                    _err("Transition core must be less than the shoulder radius")
                    return False
            if self._aftShoulder:
                if self._coreRadius >= self._aftShoulderRadius:
                    _err("Transition core must be less than the shoulder radius")
                    return False

        if self._foreShoulder:
        	if self._foreShoulderLength <= 0:
        		_err("Forward shoulder length must be > 0")
        		return False
        	if self._foreShoulderRadius <= 0:
        		_err("Forward shoulder radius must be > 0")
        		return False
        	if self._foreShoulderRadius > self._foreRadius:
        		_err("Forward shoulder radius can not exceed the transition radius at the shoulder")
        		return False
        	if self._style in [STYLE_HOLLOW, STYLE_CAPPED]:
        		if self._foreShoulderThickness <= 0:
        			_err("For %s transitions with a shoulder, shoulder thickness must be > 0" % self._style)
        			return False
        		if self._foreShoulderThickness >= self._foreShoulderRadius:
        			_err("Shoulder thickness must be less than the shoulder radius")
        			return False

        if self._aftShoulder:
        	if self._aftShoulderLength <= 0:
        		_err("Aft shoulder length must be > 0")
        		return False
        	if self._aftShoulderRadius <= 0:
        		_err("Aft shoulder radius must be > 0")
        		return False
        	if self._aftShoulderRadius > self._aftRadius:
        		_err("Aft shoulder radius can not exceed the transition radius at the shoulder")
        		return False
        	if self._style in [STYLE_HOLLOW, STYLE_CAPPED]:
        		if self._aftShoulderThickness <= 0:
        			_err("For %s transitions with a shoulder, shoulder thickness must be > 0" % self._style)
        			return False
        		if self._aftShoulderThickness >= self._aftShoulderRadius:
        			_err("Shoulder thickness must be less than the shoulder radius")
        			return False

        return True

    def getRadius(self, x):
        # Get the radius at the given value of x.
        if x <= 0:
            return self._foreRadius
        if x >= self._length:
            return self._aftRadius

        r1 = self._foreRadius
        r2 = self._aftRadius

        if r1 == r2:
            return r1

        if r1 > r2:
            x = self._length - x
            tmp = r1
            r1 = r2
            r2 = tmp

        if self._clipped:
            # Check clip calculation
            if self._clipLength < 0:
                self._calculateClip(r1, r2)
            return self._getRadius(self._clipLength + x, r2, self._clipLength + self._length, self._coefficient)
        else:
            # Not clipped
            return r1 + self._getRadius(x, r2 - r1, self._length, self._coefficient)

    def _getRadius(self, x, radius, length, param):
        return 0.0

    def _drawCurve(self, radius, length, resolution, min = 0):
        points = []
        for i in range(0, resolution):
            
            x = float(i) * ((length - min) / float(resolution))
            y = self.getRadius(x)
            _msg("(%f,%f)" % (length - x, y))
            points.append(FreeCAD.Vector(length - x, y))

        # points.append(FreeCAD.Vector(min, self.getRadius(length)))
        points.append(FreeCAD.Vector(min, self.getRadius(length)))
        _msg("(%f,%f)" % (length, self.getRadius(length)))
        spline = self.makeSpline(points)
        return spline

    #
    # Numerically solve clipLength from the equation
    #     r1 == self._getRadius(clipLength,r2,clipLength+length)
    # using a binary search.  It assumes getOuterRadius() to be monotonically increasing.
    #
    def _calculateClip(self, r1, r2):
        min = 0
        max = self._length

        if r1 >= r2:
            tmp = r1
            r1 = r2
            r2 = tmp

        if r1 == 0:
            self._clipLength = 0
            return

        if self._length <= 0:
            self._clipLength = 0
            return

        # Required:
        #    getR(min,min+length,r2) - r1 < 0
        #    getR(max,max+length,r2) - r1 > 0

        n = 0
        while self._getRadius(max, r2, max + self._length, self._coefficient) - r1 < 0:
            min = max
            max *= 2
            n += 1
            if n > 10:
                break

        while True:
            self._clipLength = (min + max) / 2;
            if (max - min) < CLIP_PRECISION:
                return
            val = self._getRadius(self._clipLength, r2, self._clipLength + self._length, self._coefficient)
            if (val - r1) > 0:
                max = self._clipLength
            else:
                min = self._clipLength

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
            elif self._style == STYLE_SOLID_CORE:
                if self._shoulder:
                    edges = self.drawSolidShoulderCore()
                else:
                    edges = self.drawSolidCore()
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
            _err("Transition parameters produce an invalid shape")
            return

        if edges is not None:
            try:
                wire = Part.Wire(edges)
                face = Part.Face(wire)
                self._obj.Shape = face.revolve(FreeCAD.Vector(0, 0, 0),FreeCAD.Vector(1, 0, 0), 360)
            except Part.OCCError:
                _err("Transition parameters produce an invalid shape")
                return
        else:
            _err("Transition parameters produce an invalid shape")

    def solidLines(self, outerShape):
        
        foreCenter = FreeCAD.Vector(self._length, 0.0)
        aftCenter = FreeCAD.Vector(0.0, 0.0)

        foreRadius = FreeCAD.Vector(self._length, self._foreRadius)
        aftRadius = FreeCAD.Vector(0.0, self._aftRadius)

        line1 = Part.LineSegment(foreRadius, foreCenter)
        line2 = Part.LineSegment(foreCenter, aftCenter)
        line3 = Part.LineSegment(aftCenter, aftRadius)
        return [outerShape.toShape(), line1.toShape(), line2.toShape(), line3.toShape()]

    def solidShoulderLines(self, outerShape):

        front = []
        back = []
        if self._foreShoulder:
            line1 = Part.LineSegment(FreeCAD.Vector(self._length, self._foreRadius),                                FreeCAD.Vector(self._length, self._foreShoulderRadius))
            line2 = Part.LineSegment(FreeCAD.Vector(self._length, self._foreShoulderRadius),                        FreeCAD.Vector(self._length + self._foreShoulderLength,self._foreShoulderRadius))
            line3 = Part.LineSegment(FreeCAD.Vector(self._length + self._foreShoulderLength,self._foreShoulderRadius), FreeCAD.Vector(self._length + self._foreShoulderLength,0))

            # Have to factor in an aft shoulder
            if self._aftShoulder:
                line4 = Part.LineSegment(FreeCAD.Vector(self._length + self._foreShoulderLength,0), FreeCAD.Vector(-self._aftShoulderLength, 0))
            else:
                line4 = Part.LineSegment(FreeCAD.Vector(self._length + self._foreShoulderLength,0), FreeCAD.Vector(0, 0))
            front = [line1.toShape(), line2.toShape(), line3.toShape(), line4.toShape()]
        else:
            line1 = Part.LineSegment(FreeCAD.Vector(self._length, self._foreRadius), FreeCAD.Vector(self._length, 0))

            # Have to factor in an aft shoulder
            if self._aftShoulder:
                line2 = Part.LineSegment(FreeCAD.Vector(self._length,0), FreeCAD.Vector(-self._aftShoulderLength, 0))
            else:
                line2 = Part.LineSegment(FreeCAD.Vector(self._length,0), FreeCAD.Vector(0, 0))
            front = [line1.toShape(), line2.toShape()]

        if self._aftShoulder:
            line1 = Part.LineSegment(FreeCAD.Vector(0, self._aftRadius),                                  FreeCAD.Vector(0, self._aftShoulderRadius))
            line2 = Part.LineSegment(FreeCAD.Vector(0, self._aftShoulderRadius),                          FreeCAD.Vector(- self._aftShoulderLength,self._aftShoulderRadius))
            line3 = Part.LineSegment(FreeCAD.Vector(-self._aftShoulderLength,self._aftShoulderRadius), FreeCAD.Vector(-self._aftShoulderLength,0))
            back = [line1.toShape(), line2.toShape(), line3.toShape()]
        else:
            line1 = Part.LineSegment(FreeCAD.Vector(0, self._aftRadius), FreeCAD.Vector(0, 0))
            back = [line1.toShape()]

        return [outerShape.toShape()] + front + back

    def solidCoreLines(self, outerShape):
        
        foreCenter = FreeCAD.Vector(self._length, self._coreRadius)
        aftCenter = FreeCAD.Vector(0.0, self._coreRadius)

        foreRadius = FreeCAD.Vector(self._length, self._foreRadius)
        aftRadius = FreeCAD.Vector(0.0, self._aftRadius)

        line1 = Part.LineSegment(foreRadius, foreCenter)
        line2 = Part.LineSegment(foreCenter, aftCenter)
        line3 = Part.LineSegment(aftCenter, aftRadius)
        return [outerShape.toShape(), line1.toShape(), line2.toShape(), line3.toShape()]

    def solidShoulderCoreLines(self, outerShape):
        
        front = []
        back = []
        if self._foreShoulder:
            line1 = Part.LineSegment(FreeCAD.Vector(self._length, self._foreRadius),                                FreeCAD.Vector(self._length, self._foreShoulderRadius))
            line2 = Part.LineSegment(FreeCAD.Vector(self._length, self._foreShoulderRadius),                        FreeCAD.Vector(self._length + self._foreShoulderLength,self._foreShoulderRadius))
            line3 = Part.LineSegment(FreeCAD.Vector(self._length + self._foreShoulderLength,self._foreShoulderRadius), FreeCAD.Vector(self._length + self._foreShoulderLength,self._coreRadius))

            # Have to factor in an aft shoulder
            if self._aftShoulder:
                line4 = Part.LineSegment(FreeCAD.Vector(self._length + self._foreShoulderLength,self._coreRadius), FreeCAD.Vector(-self._aftShoulderLength, self._coreRadius))
            else:
                line4 = Part.LineSegment(FreeCAD.Vector(self._length + self._foreShoulderLength,self._coreRadius), FreeCAD.Vector(0, self._coreRadius))
            front = [line1.toShape(), line2.toShape(), line3.toShape(), line4.toShape()]
        else:
            line1 = Part.LineSegment(FreeCAD.Vector(self._length, self._foreRadius), FreeCAD.Vector(self._length, self._coreRadius))

            # Have to factor in an aft shoulder
            if self._aftShoulder:
                line2 = Part.LineSegment(FreeCAD.Vector(self._length,self._coreRadius), FreeCAD.Vector(-self._aftShoulderLength, self._coreRadius))
            else:
                line2 = Part.LineSegment(FreeCAD.Vector(self._length,self._coreRadius), FreeCAD.Vector(0, self._coreRadius))
            front = [line1.toShape(), line2.toShape()]

        if self._aftShoulder:
            line1 = Part.LineSegment(FreeCAD.Vector(0, self._aftRadius),                                  FreeCAD.Vector(0, self._aftShoulderRadius))
            line2 = Part.LineSegment(FreeCAD.Vector(0, self._aftShoulderRadius),                          FreeCAD.Vector(-self._aftShoulderLength,self._aftShoulderRadius))
            line3 = Part.LineSegment(FreeCAD.Vector(-self._aftShoulderLength,self._aftShoulderRadius), FreeCAD.Vector(-self._aftShoulderLength,self._coreRadius))
            back = [line1.toShape(), line2.toShape(), line3.toShape()]
        else:
            line1 = Part.LineSegment(FreeCAD.Vector(0, self._aftRadius), FreeCAD.Vector(0, self._coreRadius))
            back = [line1.toShape()]

        return [outerShape.toShape()] + front + back

    def hollowLines(self, outerShape, innerShape):
        
        major = FreeCAD.Vector(0.0, self._aftRadius)
        minor = FreeCAD.Vector(self._length, self._foreRadius)

        innerMajor = FreeCAD.Vector(0.0, self._aftRadius - self._thickness)
        innerMinor = FreeCAD.Vector(self._length, self._foreRadius - self._thickness)

        line1 = Part.LineSegment(major, innerMajor)
        line2 = Part.LineSegment(minor, innerMinor)
        return [outerShape.toShape(), line1.toShape(), line2.toShape(), innerShape.toShape()]

    def hollowShoulderLines(self, foreY, aftY, outerShape, innerShape):

        front = []
        back = []
        if self._foreShoulder:
            line1 = Part.LineSegment(FreeCAD.Vector(self._length, self._foreRadius),                                                              FreeCAD.Vector(self._length, self._foreShoulderRadius))
            line2 = Part.LineSegment(FreeCAD.Vector(self._length, self._foreShoulderRadius),                                                      FreeCAD.Vector(self._length + self._foreShoulderLength,self._foreShoulderRadius))
            line3 = Part.LineSegment(FreeCAD.Vector(self._length + self._foreShoulderLength,self._foreShoulderRadius),                               FreeCAD.Vector(self._length + self._foreShoulderLength,self._foreShoulderRadius - self._foreShoulderThickness))
            line4 = Part.LineSegment(FreeCAD.Vector(self._length + self._foreShoulderLength,self._foreShoulderRadius - self._foreShoulderThickness), FreeCAD.Vector(self._length - self._thickness,self._foreShoulderRadius - self._foreShoulderThickness))
            line5 = Part.LineSegment(FreeCAD.Vector(self._length - self._thickness,self._foreShoulderRadius - self._foreShoulderThickness),           FreeCAD.Vector(self._length - self._thickness,foreY))

            front = [line1.toShape(), line2.toShape(), line3.toShape(), line4.toShape(), line5.toShape()]
        else:
            line1 = Part.LineSegment(FreeCAD.Vector(self._length, self._foreRadius), FreeCAD.Vector(self._length, self._foreRadius - self._thickness))

            front = [line1.toShape()]

        if self._aftShoulder:
            line1 = Part.LineSegment(FreeCAD.Vector(0.0, self._aftRadius),                                                               FreeCAD.Vector(0.0, self._aftShoulderRadius))
            line2 = Part.LineSegment(FreeCAD.Vector(0.0, self._aftShoulderRadius),                                                       FreeCAD.Vector(-self._aftShoulderLength,self._aftShoulderRadius))
            line3 = Part.LineSegment(FreeCAD.Vector(-self._aftShoulderLength,self._aftShoulderRadius),                              FreeCAD.Vector(-self._aftShoulderLength,self._aftShoulderRadius - self._aftShoulderThickness))
            line4 = Part.LineSegment(FreeCAD.Vector(-self._aftShoulderLength,self._aftShoulderRadius - self._aftShoulderThickness), FreeCAD.Vector(self._thickness,self._aftShoulderRadius - self._aftShoulderThickness))
            line5 = Part.LineSegment(FreeCAD.Vector(self._thickness,self._aftShoulderRadius - self._aftShoulderThickness),         FreeCAD.Vector(self._thickness,aftY))

            back = [line1.toShape(), line2.toShape(), line3.toShape(), line4.toShape(), line5.toShape()]
        else:
            line1 = Part.LineSegment(FreeCAD.Vector(0.0, self._aftRadius), FreeCAD.Vector(0.0, self._aftRadius - self._thickness))

            back = [line1.toShape()]

        return [outerShape.toShape()] + front + back + [innerShape.toShape()]

    def cappedLines(self, foreY, aftY, outerShape, innerShape):
         
        fore = FreeCAD.Vector(self._length, self._foreRadius)
        aft = FreeCAD.Vector(0.0, self._aftRadius)

        foreInner = FreeCAD.Vector(self._length - self._thickness, foreY)
        aftIinner = FreeCAD.Vector(self._thickness, aftY)
       
        foreCenter = FreeCAD.Vector(self._length,0)
        aftCenter = FreeCAD.Vector(0,0)

        foreInnerCenter = FreeCAD.Vector(self._length - self._thickness,0)
        aftInnerCenter = FreeCAD.Vector(self._thickness,0)

        line1 = Part.LineSegment(fore, foreCenter)
        line2 = Part.LineSegment(foreCenter, foreInnerCenter)
        line3 = Part.LineSegment(foreInnerCenter, foreInner)
        line4 = Part.LineSegment(aft, aftCenter)
        line5 = Part.LineSegment(aftCenter, aftInnerCenter)
        line6 = Part.LineSegment(aftInnerCenter, aftIinner)
        return [outerShape.toShape(), line1.toShape(), line2.toShape(), line3.toShape(), innerShape.toShape(), line4.toShape(), line5.toShape(), line6.toShape(), innerShape.toShape()]

    def cappedShoulderLines(self, foreY, aftY, outerShape, innerShape):

        front = []
        back = []
        if self._foreShoulder:
            line1 = Part.LineSegment(FreeCAD.Vector(self._length, self._foreRadius),                                                                FreeCAD.Vector(self._length, self._foreShoulderRadius))
            line2 = Part.LineSegment(FreeCAD.Vector(self._length, self._foreShoulderRadius),                                                        FreeCAD.Vector(self._length + self._foreShoulderLength,self._foreShoulderRadius))
            line3 = Part.LineSegment(FreeCAD.Vector(self._length + self._foreShoulderLength,self._foreShoulderRadius),                                 FreeCAD.Vector(self._length + self._foreShoulderLength,0))
            line4 = Part.LineSegment(FreeCAD.Vector(self._length + self._foreShoulderLength,0),                                                        FreeCAD.Vector(self._length + self._foreShoulderLength - self._foreShoulderThickness,0))
            line5 = Part.LineSegment(FreeCAD.Vector(self._length + self._foreShoulderLength - self._foreShoulderThickness,0),                          FreeCAD.Vector(self._length + self._foreShoulderLength - self._foreShoulderThickness,self._foreShoulderRadius - self._foreShoulderThickness))
            line6 = Part.LineSegment(FreeCAD.Vector(self._length + self._foreShoulderLength - self._foreShoulderThickness,self._foreShoulderRadius - self._foreShoulderThickness),
                                                                                                                                         FreeCAD.Vector(self._length - self._thickness,self._foreShoulderRadius - self._foreShoulderThickness))
            line7 = Part.LineSegment(FreeCAD.Vector(self._length - self._thickness,self._foreShoulderRadius - self._foreShoulderThickness),
                                                                                                                                         FreeCAD.Vector(self._length - self._thickness,foreY))

            front = [line1.toShape(), line2.toShape(), line3.toShape(), line4.toShape(), line5.toShape(), line6.toShape(), line7.toShape()]
        else:
            line1 = Part.LineSegment(FreeCAD.Vector(self._length, self._foreRadius), FreeCAD.Vector(self._length, 0))
            line2 = Part.LineSegment(FreeCAD.Vector(self._length, 0),                FreeCAD.Vector(self._length - self._thickness, 0))
            line3 = Part.LineSegment(FreeCAD.Vector(self._length - self._thickness, 0),    FreeCAD.Vector(self._length - self._thickness, foreY))

            front = [line1.toShape(), line2.toShape(), line3.toShape()]

        if self._aftShoulder:
            line1 = Part.LineSegment(FreeCAD.Vector(0, self._aftRadius),                                                       FreeCAD.Vector(0, self._aftShoulderRadius))
            line2 = Part.LineSegment(FreeCAD.Vector(0, self._aftShoulderRadius),                                               FreeCAD.Vector(-self._aftShoulderLength,self._aftShoulderRadius))
            line3 = Part.LineSegment(FreeCAD.Vector(-self._aftShoulderLength,self._aftShoulderRadius),                      FreeCAD.Vector(-self._aftShoulderLength,0))
            line4 = Part.LineSegment(FreeCAD.Vector(-self._aftShoulderLength,0),                                            FreeCAD.Vector(-self._aftShoulderLength + self._aftShoulderThickness,0))
            line5 = Part.LineSegment(FreeCAD.Vector(-self._aftShoulderLength + self._aftShoulderThickness,0),               FreeCAD.Vector(-self._aftShoulderLength + self._aftShoulderThickness,self._aftShoulderRadius - self._aftShoulderThickness))
            line6 = Part.LineSegment(FreeCAD.Vector(-self._aftShoulderLength + self._aftShoulderThickness,self._aftShoulderRadius - self._aftShoulderThickness), 
                                                                                                                                          FreeCAD.Vector(self._thickness,self._aftShoulderRadius - self._aftShoulderThickness))
            line7 = Part.LineSegment(FreeCAD.Vector(self._thickness,self._aftShoulderRadius - self._aftShoulderThickness), FreeCAD.Vector(self._thickness,aftY))

            back = [line1.toShape(), line2.toShape(), line3.toShape(), line4.toShape(), line5.toShape(), line6.toShape(), line7.toShape()]
        else:
            line1 = Part.LineSegment(FreeCAD.Vector(0, self._aftRadius),     FreeCAD.Vector(0, 0))
            line2 = Part.LineSegment(FreeCAD.Vector(0, 0),                   FreeCAD.Vector(self._thickness, 0))
            line3 = Part.LineSegment(FreeCAD.Vector(self._thickness, 0), FreeCAD.Vector(self._thickness, aftY))

            back = [line1.toShape(), line2.toShape(), line3.toShape()]

        return [outerShape.toShape()] + front + back + [innerShape.toShape()]
