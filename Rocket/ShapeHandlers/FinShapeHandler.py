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
"""Class for drawing fins"""

__title__ = "FreeCAD Fins"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

from abc import ABC, abstractmethod
from typing import Any
import math

import FreeCAD
import Part
from Part import Shape, Wire, BSplineCurve

translate = FreeCAD.Qt.translate

from Rocket.Constants import FEATURE_FINCAN
from Rocket.Constants import FIN_CROSS_SAME, FIN_CROSS_SQUARE, FIN_CROSS_ROUND, FIN_CROSS_AIRFOIL, FIN_CROSS_WEDGE, \
    FIN_CROSS_DIAMOND, FIN_CROSS_TAPER_LE, FIN_CROSS_TAPER_TE, FIN_CROSS_TAPER_LETE, FIN_CROSS_BICONVEX, FIN_CROSS_ELLIPSE
from Rocket.Constants import FIN_DEBUG_FULL, FIN_DEBUG_PROFILE_ONLY, FIN_DEBUG_MASK_ONLY

from Rocket.Utilities import validationError, _err

class FinShapeHandler(ABC):

    def __init__(self, obj : Any) -> None:
        self._obj = obj

        # This gets changed when redrawn so it's very important to save a copy
        self._placement = FreeCAD.Placement(self._obj.Placement)

        self._debugSketch = FIN_DEBUG_FULL
        if hasattr(self._obj,"DebugSketch"):
            self._debugSketch = str(self._obj.DebugSketch)

        if self._obj.Proxy.Type == FEATURE_FINCAN:
            self._radius = float(self._obj.Diameter.Value) / 2.0
            self._thickness = float(self._obj.Thickness)
            self._leadingEdgeOffset = float(self._obj.LeadingEdgeOffset)
        else:
            self._radius = 0.0
            self._thickness = 0.0
            self._leadingEdgeOffset = 0.0

        self._autoDiameter = bool(self._obj.AutoDiameter)
        self._parentRadius = float(self._obj.ParentRadius)

        self._finSet = bool(self._obj.FinSet)
        self._fincount = int(self._obj.FinCount)
        self._finSpacing = float(self._obj.FinSpacing)

        self._rootChord = float(self._obj.RootChord)
        self._rootPerCent = bool(self._obj.RootPerCent)
        self._rootLength1 = float(self._obj.RootLength1)
        self._rootLength2 = float(self._obj.RootLength2)
        self._rootThickness = float(self._obj.RootThickness)
        self._rootCrossSection = str(self._obj.RootCrossSection)

        self._midChord = self._rootChord / 2.0

        self._tipChord = float(self._obj.TipChord)
        self._tipPerCent = bool(self._obj.TipPerCent)
        self._tipLength1 = float(self._obj.TipLength1)
        self._tipLength2 = float(self._obj.TipLength2)
        self._tipSameThickness = bool(self._obj.TipSameThickness)
        if self._tipSameThickness:
            self._tipThickness = self._rootThickness
        else:
            self._tipThickness = float(self._obj.TipThickness)
        self._tipCrossSection = str(self._obj.TipCrossSection)
        if self._tipCrossSection == FIN_CROSS_SAME:
            self._tipCrossSection = self._rootCrossSection

        self._fillets = bool(self._obj.Fillets)
        self._filletRadius = float(self._obj.FilletRadius)
        self._filletCrossSection = str(self._obj.FilletCrossSection)
        if self._filletCrossSection == FIN_CROSS_SAME:
            self._filletCrossSection = self._rootCrossSection

        self._sweepAngle = float(self._obj.SweepAngle)
        self._sweepLength = float(self._obj.SweepLength) # TODO: Needs to be recalculated based on scaled values
        self._height = float(self._obj.Height)
        self._cant = float(self._obj.Cant)

        self._ttw = bool(self._obj.Ttw)
        self._ttwOffset = float(self._obj.TtwOffset)
        self._ttwLength = float(self._obj.TtwLength)
        self._ttwThickness = float(self._obj.TtwThickness)
        self._ttwHeight = float(self._obj.TtwHeight)

        self._minimumEdge = bool(self._obj.MinimumEdge)
        self._minimumEdgeSize = float(self._obj.MinimumEdgeSize)

        # Apply scaling
        self._scale = 1.0
        if obj.Proxy.isScaled():
            self._scale = 1.0 / obj.Proxy.getScale()
            if self._isDiameterScaled():
                self._radius *= self._scale
                if not self._isParentDiameterScaled(): # May already be scaled
                    self._parentRadius *= self._scale

            if not self._rootPerCent:
                self._rootLength1 *= self._scale
                self._rootLength2 *= self._scale
            self._rootChord *= self._scale
            self._rootThickness *= self._scale

            if not self._tipPerCent:
                self._tipLength1 *= self._scale
                self._tipLength2 *= self._scale
            self._tipChord *= self._scale
            self._tipThickness *= self._scale

            self._filletRadius *= self._scale

            self._height *= self._scale
            self._sweepLength *= self._scale # Is it this simple?

    def _isDiameterScaled(self) -> bool:
        if self._autoDiameter:
            return False
        return self._obj.isScaled()

    def _isParentDiameterScaled(self) -> bool:
        if self._obj.Proxy.hasParent():
            return self._obj.Proxy.getParent().isScaled()
        return False

    def minimumEdge(self) -> float:
        if self._minimumEdge:
            return self._minimumEdgeSize

        return 0.0

    def _foreAngle(self) -> float:
        """
            Angle of the fins leading edge
        """
        return math.radians(self._sweepAngle)

    def _aftAngle(self) -> float:
        """
            Angle of the fins trailing edge
        """
        length = self._sweepLength - self._rootChord
        theta2 = (math.pi / 2.0) - math.atan2(self._height, length) # In radians
        return theta2

    def _midAngle(self, foreAngle : float, aftAngle : float) -> float:
        """
            Angle of the fins mid line
        """
        return (foreAngle + aftAngle) / 2.0

    def _angles(self) -> tuple[float, float, float]:
        """
            Calculate fore, mid, and aft angles
        """
        foreAngle = self._foreAngle()
        aftAngle = self._aftAngle()
        midAngle = self._midAngle(foreAngle, aftAngle)
        return (foreAngle, midAngle, aftAngle)

    def _makeChordProfileSquare(self, foreX : float, chord : float, thickness : float, height : float) -> Wire:
        # Create the root rectangle
        chordFore = foreX
        chordAft = foreX + chord
        halfThickness = thickness / 2
        v1 = FreeCAD.Vector(chordFore, halfThickness, height)
        v2 = FreeCAD.Vector(chordFore, -halfThickness, height)
        v3 = FreeCAD.Vector(chordAft, -halfThickness, height)
        v4 = FreeCAD.Vector(chordAft, halfThickness, height)
        line1 = Part.LineSegment(v1, v2)
        line2 = Part.LineSegment(v2, v3)
        line3 = Part.LineSegment(v3, v4)
        line4 = Part.LineSegment(v4, v1)

        wire = Part.Wire([line1.toShape(), line2.toShape(), line3.toShape(), line4.toShape()])
        return wire

    def _makeChordFemProfileSquare(self, foreX : float, chord : float, thickness : float, height : float, nPoints : int) -> Wire:
        profile = []
        chordFore = foreX
        chordAft = foreX + chord
        halfThickness = thickness / 2
        step = chord / nPoints
        count = nPoints

        # profile.append(FreeCAD.Vector(chordFore, 0, height))
        x = chordFore
        while (count > 0):
            profile.append(FreeCAD.Vector(x, halfThickness, height))
            x = x + step
            count = count - 1
        profile.append(FreeCAD.Vector(chordAft, halfThickness, height))
        # profile.append(FreeCAD.Vector(chordAft, 0, height))

        return profile

    def _makeChordProfileRound(self, foreX : float, chord : float, thickness : float, height : float) -> Wire:
        chordFore = foreX
        chordAft = foreX + chord
        halfThickness = thickness / 2
        if chord <= thickness:
            _, theta, _ = self._angles()
            x = math.sin(theta)
            z = math.cos(theta)
            circle = Part.Circle(FreeCAD.Vector(chordFore + halfThickness, 0, height),
                                     FreeCAD.Vector(x,0,z), halfThickness)

            # Split the circle into 4 arcs so that the loft has proper reference points
            degree = math.radians(1)
            rad1 = (-math.pi/2.0) + degree
            rad2 = (math.pi/2.0) - degree
            rad3 = (math.pi/2.0) + degree
            rad4 = (3.0 * math.pi/2.0) - degree
            rad5 = (3.0 * math.pi/2.0) + degree # Wrap around value for rad1
            arc1 = Part.Arc(circle, rad1, rad2)
            arc2 = Part.Arc(circle, rad2, rad3)
            arc3 = Part.Arc(circle, rad3, rad4)
            arc4 = Part.Arc(circle, rad4, rad5)
            # wire = Part.Wire([circle])
            wire = Part.Wire([arc1.toShape(), arc2.toShape(), arc3.toShape(), arc4.toShape()])
            return wire

        v1 = FreeCAD.Vector(chordFore + halfThickness, halfThickness, height)
        v2 = FreeCAD.Vector(chordFore + halfThickness, -halfThickness, height)
        v3 = FreeCAD.Vector(chordAft - halfThickness, -halfThickness, height)
        v4 = FreeCAD.Vector(chordAft - halfThickness, halfThickness, height)
        centerAft = FreeCAD.Vector(chordAft, 0.0, height)
        centerFore = FreeCAD.Vector(chordFore, 0.0, height)
        line1 = Part.LineSegment(v2, v3)
        line2 = Part.LineSegment(v4, v1)
        arcAft = Part.Arc(v3, centerAft, v4)
        arcFore = Part.Arc(v1, centerFore, v2)

        wire = Part.Wire([arcAft.toShape(), line1.toShape(), arcFore.toShape(), line2.toShape()])
        return wire

    def _makeChordProfileEllipse(self, foreX : float, chord : float, thickness : float, height : float) -> Wire:
        halfThickness = thickness / 2
        if chord <= thickness:
            _, theta, _ = self._angles()
            x = math.sin(theta)
            z = math.cos(theta)
            circle = Part.makeCircle(halfThickness, FreeCAD.Vector(foreX + halfThickness, 0, height),
                                     FreeCAD.Vector(x,0,z))
            wire = Part.Wire([circle])
            return wire
        ellipse = Part.Ellipse(FreeCAD.Vector(foreX + (chord / 2.0), 0, height), chord / 2.0, halfThickness)
        wire = Part.Wire([ellipse.toShape()])
        return wire

    def _makeChordProfileBiconvex(self, foreX : float, chord : float, thickness : float, height : float) -> Wire:
        chordFore = foreX
        chordAft = foreX + chord
        chordMid = foreX + (chord / 2)
        halfThickness = thickness / 2
        min = self.minimumEdge() / 2

        v1 = FreeCAD.Vector(chordFore, -min, height)
        v2 = FreeCAD.Vector(chordAft, -min, height)
        v3 = FreeCAD.Vector(chordFore, min, height)
        v4 = FreeCAD.Vector(chordAft, min, height)
        v5 = FreeCAD.Vector(chordMid, -halfThickness, height)
        v6 = FreeCAD.Vector(chordMid, halfThickness, height)
        if halfThickness == min:
            arc1 = Part.LineSegment(v1, v2)
            arc2 = Part.LineSegment(v3, v4)
        else:
            arc1 = Part.Arc(v1, v5, v2)
            arc2 = Part.Arc(v3, v6, v4)

        if min > 0:
            line1 = Part.LineSegment(v3, v1)
            line2 = Part.LineSegment(v2, v4)
            wire = Part.Wire([line1.toShape(), arc1.toShape(), line2.toShape(), arc2.toShape()])
        else:
            wire = Part.Wire([arc1.toShape(), arc2.toShape()])
        return wire

    def _airfoilY(self, x : float, maxThickness : float) -> float:
        # NACA symmetrical airfoil https://en.wikipedia.org/wiki/NACA_airfoil
        # y = 5 * maxThickness * ((0.2969 * math.sqrt(x)) - (0.1260 * x) - (0.3516 * x * x) + (0.2843 * x * x * x) - (0.1015 * x * x * x * x))

        # Apply Horner's rule
        y = 5 * maxThickness * (0.2969 * math.sqrt(x) + x * (-0.1260 +  x * (-0.3516 + x * (0.2843 - x * 0.1015))))
        return y

    def _airfoilCurve(self, foreX : float, chord : float, thickness : float, height : float, resolution : int) -> BSplineCurve:
        min = self.minimumEdge() / 2
        points = []
        points1 = []
        for i in range(0, resolution):

            x = float(i) / float(resolution)
            y = self._airfoilY(x, thickness)
            if y < min and x > 0:
                y = min
            points.append(FreeCAD.Vector(foreX + (x * chord), y, height))
            points1.append(FreeCAD.Vector(foreX + (x * chord), -y, height))

        if min > 0:
            points.append(FreeCAD.Vector(foreX + chord, min, height))
            points1.append(FreeCAD.Vector(foreX + chord, -min, height))
        else:
            points.append(FreeCAD.Vector(foreX + chord, 0.0, height))
            points1.append(FreeCAD.Vector(foreX + chord, 0.0, height))

        # Creating separate splines for each side of the airfoil adds extra reference
        # points for lofting, reducing geometry errors
        splines = []
        splines.append(self._makeSpline(points).toShape())
        splines.append(self._makeSpline(points1).toShape())
        if min > 0:
            line = Part.LineSegment(FreeCAD.Vector(foreX + chord, min, height),
                                    FreeCAD.Vector(foreX + chord, -min, height))
            splines.append(line.toShape())

        return splines

    def _airfoilFemCurve(self, foreX : float, chord : float, thickness : float, height : float, resolution : int) -> BSplineCurve:
        min = self.minimumEdge() / 2
        points = []
        for i in range(0, resolution):
            
            x = float(i) / float(resolution)
            y = self._airfoilY(x, thickness)
            if y < min and x > 0:
                y = min
            points.append(FreeCAD.Vector(foreX + (x * chord), y, height))

        if min > 0:
            points.append(FreeCAD.Vector(foreX + chord, min, height))
        else:
            points.append(FreeCAD.Vector(foreX + chord, 0.0, height))

        return points 

    def _makeSpline(self, points : list) -> BSplineCurve:
        spline = Part.BSplineCurve()
        spline.buildFromPoles(points)
        return spline

    def _midChordLimit(self, chord : float, value : float, midChordLimit : bool) -> float:
        if midChordLimit and value > (chord / 2.0):
            return chord / 2.0
        return value

    def _makeChordProfileAirfoil(self, foreX : float, chord : float, thickness : float, height : float) -> Wire:
        # Standard NACA 4 digit symmetrical airfoil

        splines = self._airfoilCurve(foreX, chord, thickness, height, 100)

        wire = Part.Wire(splines)
        return wire

    def _makeChordFemProfileAirfoil(self, foreX : float, chord : float, thickness : float, height : float, nPoints : int) -> Wire:
        # Standard NACA 4 digit symmetrical airfoil

        profile = self._airfoilFemCurve(foreX, chord, thickness, height, nPoints)

        return profile

    def _makeChordProfileWedge(self, foreX : float, chord : float, thickness : float, height : float) -> Wire:
        # Create the root rectangle
        chordFore = foreX
        chordAft = foreX + chord
        halfThickness = thickness / 2
        min = self.minimumEdge() / 2
        v1 = FreeCAD.Vector(chordFore, min, height)
        v2 = FreeCAD.Vector(chordAft, halfThickness, height)
        v3 = FreeCAD.Vector(chordAft, -halfThickness, height)
        line1 = Part.LineSegment(v1, v2)
        line2 = Part.LineSegment(v2, v3)

        if min > 0:
            v4 = FreeCAD.Vector(chordFore, -min, height)
            line3 = Part.LineSegment(v3, v4)
            line4 = Part.LineSegment(v4, v1)
            wire = Part.Wire([line1.toShape(), line2.toShape(), line3.toShape(), line4.toShape()])
        else:
            line3 = Part.LineSegment(v3, v1)
            wire = Part.Wire([line1.toShape(), line2.toShape(), line3.toShape()])
        return wire

    def _makeChordProfileDiamond(self, foreX : float, chord : float, thickness : float, height : float,
                                 maxChord : float, midChordLimit : bool) -> Wire:
        chordFore = foreX
        chordMid = foreX + maxChord
        chordAft = foreX + chord
        halfThickness = thickness / 2
        min = self.minimumEdge() / 2
        if chordMid >= chordAft:
            chordMid = (chordFore + chordAft) / 2.0

        v1 = FreeCAD.Vector(chordFore, min, height)
        v2 = FreeCAD.Vector(chordMid, halfThickness, height)
        v3 = FreeCAD.Vector(chordAft, min, height)
        v4 = FreeCAD.Vector(chordAft, -min, height)
        v5 = FreeCAD.Vector(chordMid, -halfThickness, height)
        v6 = FreeCAD.Vector(chordFore, -min, height)
        line1 = Part.LineSegment(v1, v2)
        line2 = Part.LineSegment(v2, v3)
        if min > 0:
            line3 = Part.LineSegment(v3, v4)
            line4 = Part.LineSegment(v4, v5)
            line5 = Part.LineSegment(v5, v6)
            line6 = Part.LineSegment(v6, v1)

            wire = Part.Wire([line1.toShape(), line2.toShape(), line3.toShape(), line4.toShape(), line5.toShape(), line6.toShape()])
        else:
            line3 = Part.LineSegment(v3, v5)
            line4 = Part.LineSegment(v5, v1)

            wire = Part.Wire([line1.toShape(), line2.toShape(), line3.toShape(), line4.toShape()])
        return wire

    def _makeChordProfileTaperLE(self, foreX : float, chord : float, thickness : float, height : float, maxChord : float) -> Wire:
        chordFore = foreX
        if maxChord == chord:
            chordMid = foreX + maxChord - 0.00001
        else:
            chordMid = foreX + maxChord
        chordAft = foreX + chord
        halfThickness = thickness / 2
        min = self.minimumEdge() / 2
        v1 = FreeCAD.Vector(chordFore, min, height)
        v2 = FreeCAD.Vector(chordMid, halfThickness, height)
        v3 = FreeCAD.Vector(chordMid, -halfThickness, height)
        v4 = FreeCAD.Vector(chordAft, halfThickness, height)
        v5 = FreeCAD.Vector(chordAft, -halfThickness, height)
        v6 = FreeCAD.Vector(chordFore, -min, height)
        line1 = Part.LineSegment(v1, v2)
        line2 = Part.LineSegment(v2, v4)
        line3 = Part.LineSegment(v4, v5)
        line4 = Part.LineSegment(v5, v3)
        if min > 0:
            line5 = Part.LineSegment(v3, v6)
            line6 = Part.LineSegment(v6, v1)

            wire = Part.Wire([line1.toShape(), line2.toShape(), line3.toShape(), line4.toShape(), line5.toShape(), line6.toShape()])
        else:
            line5 = Part.LineSegment(v3, v1)

            wire = Part.Wire([line1.toShape(), line2.toShape(), line3.toShape(), line4.toShape(), line5.toShape()])
        return wire

    def _makeChordProfileTaperTE(self, foreX : float, chord : float, thickness : float, height : float, maxChord : float) -> Wire:
        chordFore = foreX
        if maxChord == chord:
            chordMid = foreX + 0.00001
        else:
            chordMid = foreX + chord - maxChord
        chordAft = foreX + chord
        halfThickness = thickness / 2
        min = self.minimumEdge() / 2
        v1 = FreeCAD.Vector(chordAft, min, height)
        v2 = FreeCAD.Vector(chordMid, halfThickness, height)
        v3 = FreeCAD.Vector(chordMid, -halfThickness, height)
        v4 = FreeCAD.Vector(chordFore, halfThickness, height)
        v5 = FreeCAD.Vector(chordFore, -halfThickness, height)
        v6 = FreeCAD.Vector(chordAft, -min, height)
        line1 = Part.LineSegment(v1, v2)
        line2 = Part.LineSegment(v2, v4)
        line3 = Part.LineSegment(v4, v5)
        line4 = Part.LineSegment(v5, v3)
        if min > 0:
            line5 = Part.LineSegment(v3, v6)
            line6 = Part.LineSegment(v6, v1)

            wire = Part.Wire([line1.toShape(), line2.toShape(), line3.toShape(), line4.toShape(), line5.toShape(), line6.toShape()])
        else:
            line5 = Part.LineSegment(v3, v1)

            wire = Part.Wire([line1.toShape(), line2.toShape(), line3.toShape(), line4.toShape(), line5.toShape()])
        return wire

    def _makeChordProfileTaperLETE(self, foreX : float, chord : float, thickness : float, height : float,
                                   foreChord : float, aftChord : float, midChordLimit : bool) -> Wire:
        chordFore = foreX
        chordFore1 = foreX + self._midChordLimit(chord, foreChord, midChordLimit)
        chordAft1 = foreX + chord - self._midChordLimit(chord, aftChord, midChordLimit)
        if chordFore1 == chordAft1:
            chordAft1 += 0.0001
        chordAft = foreX + chord
        halfThickness = thickness / 2
        min = self.minimumEdge() / 2

        v1 = FreeCAD.Vector(chordFore, min, height)
        v2 = FreeCAD.Vector(chordFore1, halfThickness, height)
        v3 = FreeCAD.Vector(chordFore1, -halfThickness, height)
        v4 = FreeCAD.Vector(chordAft1, halfThickness, height)
        v5 = FreeCAD.Vector(chordAft1, -halfThickness, height)
        v6 = FreeCAD.Vector(chordAft, min, height)
        v7 = FreeCAD.Vector(chordFore, -min, height)
        v8 = FreeCAD.Vector(chordAft, -min, height)

        if min > 0:
            line1 = Part.LineSegment(v1, v2)
            line2 = Part.LineSegment(v2, v4)
            line3 = Part.LineSegment(v4, v6)
            line4 = Part.LineSegment(v6, v8)
            line5 = Part.LineSegment(v8, v5)
            line6 = Part.LineSegment(v5, v3)
            line7 = Part.LineSegment(v3, v7)
            line8 = Part.LineSegment(v7, v1)

            wire = Part.Wire([line1.toShape(), line2.toShape(), line3.toShape(), line4.toShape(), line5.toShape(), line6.toShape(),
                              line7.toShape(), line8.toShape()])
        else:
            line1 = Part.LineSegment(v1, v2)
            line2 = Part.LineSegment(v2, v4)
            line3 = Part.LineSegment(v4, v6)
            line4 = Part.LineSegment(v6, v5)
            line5 = Part.LineSegment(v5, v3)
            line6 = Part.LineSegment(v3, v1)

            wire = Part.Wire([line1.toShape(), line2.toShape(), line3.toShape(), line4.toShape(), line5.toShape(), line6.toShape()])
        return wire

    def _lengthsFromPercent(self, chord : float, lengthPerCent : bool, length1 : float, length2 : float) -> tuple[float, float]:
        if lengthPerCent:
            l1 = chord * (length1 / 100.0)
            l2 = chord * ((100.0 - length2) / 100.0)
        else:
            l1 = length1
            l2 = chord - length2

        return l1, l2

    def _lengthsFromRootRatio(self, chord : float) -> tuple[float, float]:
        l1, l2 = self._lengthsFromPercent(self._rootChord, self._rootPerCent,
                                          self._rootLength1, self._rootLength2)
        length1 = chord * (l1 / self._rootChord)
        length2 = chord * (l2 / self._rootChord)
        return length1, length2

    def _makeChordProfile(self, crossSection : str, foreX : float, chord : float, thickness : float, height : float,
                          length1 : float, length2 : float, midChordLimit : bool = False) -> Wire:

        if crossSection == FIN_CROSS_SQUARE:
            return self._makeChordProfileSquare(foreX, chord, thickness, height)
        elif crossSection == FIN_CROSS_ROUND:
            return self._makeChordProfileRound(foreX, chord, thickness, height)
        elif crossSection == FIN_CROSS_BICONVEX:
            return self._makeChordProfileBiconvex(foreX, chord, thickness, height)
        elif crossSection == FIN_CROSS_ELLIPSE:
            return self._makeChordProfileEllipse(foreX, chord, thickness, height)
        elif crossSection == FIN_CROSS_AIRFOIL:
            return self._makeChordProfileAirfoil(foreX, chord, thickness, height)
        elif crossSection == FIN_CROSS_WEDGE:
            return self._makeChordProfileWedge(foreX, chord, thickness, height)
        elif crossSection == FIN_CROSS_DIAMOND:
            return self._makeChordProfileDiamond(foreX, chord, thickness, height, length1, midChordLimit)
        elif crossSection == FIN_CROSS_TAPER_LE:
            return self._makeChordProfileTaperLE(foreX, chord, thickness, height, length1)
        elif crossSection == FIN_CROSS_TAPER_TE:
            return self._makeChordProfileTaperTE(foreX, chord, thickness, height, length1)
        elif crossSection == FIN_CROSS_TAPER_LETE:
            return self._makeChordProfileTaperLETE(foreX, chord, thickness, height, length1, length2, midChordLimit)

        return None

    def _makeChordFemProfile(self, crossSection : str, foreX : float, chord : float, thickness : float, height : float,
                             length1 : float, length2 : float, nPoints : int, midChordLimit : float = False) -> Wire:

        if crossSection == FIN_CROSS_SQUARE:
            return self._makeChordFemProfileSquare(foreX, chord, thickness, height, nPoints)
        elif crossSection == FIN_CROSS_AIRFOIL:
            return self._makeChordFemProfileAirfoil(foreX, chord, thickness, height, nPoints)

        return None

    def _makeTtw(self) -> Shape:
        # Create the Ttw tab
        # origin = FreeCAD.Vector(self._rootChord - self._ttwOffset - self._ttwLength, -0.5 * self._ttwThickness, -1.0 * self._ttwHeight)
        origin = FreeCAD.Vector(self._ttwOffset, -0.5 * self._ttwThickness, -1.0 * self._ttwHeight)
        return Part.makeBox(self._ttwLength, self._ttwThickness, self._ttwHeight, origin)

    def isValidShape(self) -> bool:
        # Add error checking here
        if self._ttw:
            if self._ttwOffset >= self._rootChord:
                validationError(translate('Rocket', "Ttw offset must be less than the root chord"))
                return False
            if self._ttwLength <= 0:
                validationError(translate('Rocket', "Ttw length must be greater than 0"))
                return False
            if self._ttwHeight <= 0:
                validationError(translate('Rocket', "Ttw height must be greater than 0"))
                return False
            if self._ttwThickness <= 0:
                validationError(translate('Rocket', "Ttw thickness must be greater than 0"))
                return False
        return True

    def _makeProfiles(self) -> list[Wire]:
        profiles = []
        return profiles

    def _makeFemProfiles(self, nPoints : int) -> list[Wire]:
        profiles = []
        return profiles

    def _makeExtensionProfiles(self, height : float) -> list[Wire]:
        profiles = []
        profiles.append(self._makeRootProfile(-height))
        profiles.append(self._makeRootProfile(0))
        return profiles

    def _makeFilletProfiles(self, radius : float) -> list[Wire]:
        profiles = []
        height, hSpan = self._getTubeOffsets(radius)
        profiles.append(self._makeAtHeightProfile(self._rootCrossSection, radius, 0.001))
        profiles.append(self._makeAtHeightProfile(self._filletCrossSection, hSpan * 0.75 - height, radius * 0.032))
        profiles.append(self._makeAtHeightProfile(self._filletCrossSection, hSpan * 0.50 - height, radius * 0.134))
        profiles.append(self._makeAtHeightProfile(self._filletCrossSection, hSpan * 0.25 - height, radius * 0.339))
        profiles.append(self._makeAtHeightProfile(self._filletCrossSection, -height, radius))
        return profiles

    @abstractmethod
    def _makeAtHeightProfile(self, crossSection : str, height : float = 0.0, offset : float = 0.0) -> Wire:
        ...

    @abstractmethod
    def _makeRootProfile(self, height : float = 0.0) -> Wire:
        ...

    def _getTubeRadius(self) -> float:
        if hasattr(self._obj, "Diameter"):
            # This is for fin cans
            return self._radius

        return self._parentRadius

    def _getTubeOffsets(self, filletRadius : float) -> tuple[float, float]:
        """ Get the information about how much a fillet extends down over a tube

        returns:
            height: the distance into the tube wrapped by the filler
            hSpan: the width of the fillet at the height
        """
        bodyRadius = self._getTubeRadius()

        # Calculate negative height when on a body tube
        theta = math.asin((filletRadius + self._rootThickness / 2.0) / bodyRadius)
        height = bodyRadius * (1.0 - math.cos(theta))
        hSpan = filletRadius + height
        return height, hSpan

    def _makeTip(self) -> Shape:
        return None

    def _makeCommon(self) -> Shape:
        # Override this if we have a "masking" shape
        return None

    def _makeCut(self) -> Shape:
        # Override this if we need to cut from the shape
        return None

    def _extendRoot(self) -> bool:
        # Override this if the fin root needs an extension to connect it to the body tube
        return False
    
    def finFemProfiles(self, nPoints : int) -> list[Wire]:
        profiles = self._makeFemProfiles(nPoints)
        return profiles

    def finOnlyShape(self) -> Shape:
        fin = self._finOnlyShape(FIN_DEBUG_FULL)
        return Part.makeCompound([fin])

    def _finOnlyShape(self, debug : str) -> Shape:
        #
        # Return the shape of a single fin with no additions, such as fin tabs, fin cans, etc
        #
        # This can be used to determine characteristics such as mass, cg, and volume
        loft = None
        profiles = self._makeProfiles()
        if profiles and len(profiles) > 0:
            if isinstance(profiles[0], list):
                # Using a compound instead of a fuse makes drawing much faster, but also leads to
                # a number of 'BOPAlgo SelfIntersect' errors. So we stick with the fuse

                for profile in profiles:
                    if loft is None:
                        loft = Part.makeLoft(profile, True)
                    else:
                        loft = loft.fuse(Part.makeLoft(profile, True))
            else:
                loft = Part.makeLoft(profiles, True)

            if hasattr(self, "_makeTip"):
                tip = self._makeTip()
                if tip and loft:
                    loft = loft.fuse(tip)

            if loft:
                mask = self._makeCommon()
                if debug == FIN_DEBUG_MASK_ONLY:
                    loft = mask
                elif mask and (debug != FIN_DEBUG_PROFILE_ONLY):
                    loft = loft.common(mask)

        return loft

    def _makeRootExtension(self) -> Shape:
        loft = None
        height = self._radius + self._thickness

        profiles = self._makeExtensionProfiles(self._thickness - 0.0001)
        if profiles and len(profiles) > 0:
            loft = Part.makeLoft(profiles, True)

            # Make a cutout of the body tube center
            if loft:
                center = Part.makeCylinder(self._radius,
                                           2.0 * self._rootChord,
                                           FreeCAD.Vector(-self._rootChord / 2.0, 0, -height),
                                           FreeCAD.Vector(1, 0, 0)
                                           )
                if self._cant != 0:
                    center.rotate(FreeCAD.Vector(self._rootChord / 2, 0, 0), FreeCAD.Vector(0,0,1), -self._cant)
                loft = loft.cut(center)

        return loft

    def _makeFillet(self) -> Shape:
        loft = None
        radius = self._getTubeRadius()

        profiles = self._makeFilletProfiles(self._filletRadius)

        if profiles and len(profiles) > 0:
            loft = Part.makeLoft(profiles, True)
            # Make a cutout of the body tube center
            if loft:
                center = Part.makeCylinder(radius + 0.001,
                                           2.0 * self._rootChord,
                                           FreeCAD.Vector(-self._rootChord / 2.0, 0, -radius),
                                           FreeCAD.Vector(1, 0, 0)
                                           )
                if self._cant != 0:
                    center.rotate(FreeCAD.Vector(self._rootChord / 2, 0, 0), FreeCAD.Vector(0,0,1), -self._cant)
                loft = loft.cut(center)

        return loft

    def _drawFinDebug(self, debug : str) -> Shape:
        fin = self._finOnlyShape(debug)
        if fin:
            if self._fillets:
                fillet = self._makeFillet()
                if fillet:
                    fin = fin.fuse(fillet)
            elif self._extendRoot():
                # Only needed when there are no fillets
                extension = self._makeRootExtension()
                if extension:
                    fin = fin.fuse(extension)
            if self._ttw:
                ttw = self._makeTtw()
                if ttw:
                    fin = fin.fuse(ttw)

        return fin

    def _drawSingleFin(self) -> Shape:
        return self._drawFinDebug(self._debugSketch)

    def _drawFin(self) -> Shape:
        fin = self._drawSingleFin()
        if self._cant != 0:
            fin.rotate(FreeCAD.Vector(self._rootChord / 2, 0, 0), FreeCAD.Vector(0,0,1), self._cant)
        fin.translate(FreeCAD.Vector(0,0,self._parentRadius))
        # return Part.makeCompound([fin])
        return fin

    def _drawFinSet(self) -> Shape:
        fins = []
        base = self._drawSingleFin()
        baseX = 0
        if hasattr(self._obj, "LeadingEdgeOffset"):
            baseX = self._leadingEdgeOffset
        for i in range(self._fincount):
            fin = Part.Shape(base) # Create a copy
            if self._cant != 0:
                fin.rotate(FreeCAD.Vector(self._rootChord / 2, 0, 0), FreeCAD.Vector(0,0,1), self._cant)
            radius = self._getTubeRadius()
            fin.translate(FreeCAD.Vector(baseX, 0, radius))
            fin.rotate(FreeCAD.Vector(0, 0, 0), FreeCAD.Vector(1,0,0), i * self._finSpacing)
            fins.append(fin)

        return Part.makeCompound(fins)

    def draw(self) -> None:

        if not self.isValidShape():
            return

        try:
            if self._finSet:
                self._obj.Shape = self._drawFinSet()
            else:
                self._obj.Shape = self._drawFin()
            self._obj.Placement = self._placement

        except (ZeroDivisionError, Part.OCCError) as ex:
            _err(translate('Rocket', "Fin parameters produce an invalid shape"))
            return

    def _makeFinFrontal(self) -> Shape:
        # The frontal view is either a trapezoid or a triangle
        # TODO: Handle canted fins
        halfRoot = self._rootThickness / 2.0
        thickness = self._tipThickness
        height = self._height
        if self._tipThickness:
            thickness = self._rootThickness
        if thickness > 0.0:
            halfTip = thickness / 2.0

            v1 = FreeCAD.Vector(0.0, -halfRoot, 0.0)
            v2 = FreeCAD.Vector(0.0, halfRoot, 0.0)
            v3 = FreeCAD.Vector(0.0, halfTip, height)
            v4 = FreeCAD.Vector(0.0, -halfTip, height)
            line1 = Part.LineSegment(v1, v2)
            line2 = Part.LineSegment(v2, v3)
            line3 = Part.LineSegment(v3, v4)
            line4 = Part.LineSegment(v4, v1)

            wire = Part.Wire([line1.toShape(), line2.toShape(), line3.toShape(), line4.toShape()])
        else:
            v1 = FreeCAD.Vector(0.0, -halfRoot, 0.0)
            v2 = FreeCAD.Vector(0.0, halfRoot, 0.0)
            v3 = FreeCAD.Vector(0.0, 0.0, height)
            line1 = Part.LineSegment(v1, v2)
            line2 = Part.LineSegment(v2, v3)
            line3 = Part.LineSegment(v3, v1)

            wire = Part.Wire([line1.toShape(), line2.toShape(), line3.toShape()])

        face = Part.Face(wire)
        face.translate(FreeCAD.Vector(0,0,self._parentRadius))
        return face

    def _makeFinFrontalFinSet(self) -> Shape:
        fins = []
        base = self._makeFinFrontal()
        for i in range(self._fincount):
            fin = Part.Shape(base) # Create a copy
            # fin.translate(FreeCAD.Vector(0,0,self._parentRadius))
            fin.rotate(FreeCAD.Vector(0, 0, 0), FreeCAD.Vector(1,0,0), i * self._finSpacing)
            fins.append(fin)

        return Part.makeCompound(fins)
