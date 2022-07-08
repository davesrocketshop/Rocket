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

from App.Constants import FIN_CROSS_SQUARE, FIN_CROSS_ROUND, FIN_CROSS_AIRFOIL, FIN_CROSS_WEDGE, \
    FIN_CROSS_DIAMOND, FIN_CROSS_TAPER_LE, FIN_CROSS_TAPER_TE, FIN_CROSS_TAPER_LETE
from App.Constants import FIN_DEBUG_FULL, FIN_DEBUG_PROFILE_ONLY, FIN_DEBUG_MASK_ONLY

from App.Utilities import _err

class FinShapeHandler:

    def __init__(self, obj):
        self._obj = obj

        # This gets changed when redrawn so it's very important to save a copy
        self._placement = obj.Placement

    def _makeChordProfileSquare(self, foreX, chord, thickness, height):
        # Create the root rectangle
        chordFore = foreX
        chordAft = foreX - chord
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

    def _makeChordProfileRound(self, foreX, chord, thickness, height):
        # For now, rounded is an ellipse shape
        ellipse = Part.Ellipse(FreeCAD.Vector(foreX - (chord / 2.0), 0, height), chord / 2.0, thickness / 2.0)
        wire = Part.Wire([ellipse.toShape()])
        return wire
            
    def _airfoilY(self, x, maxThickness):
        # NACA symmetrical airfoil https://en.wikipedia.org/wiki/NACA_airfoil
        # y = 5 * maxThickness * ((0.2969 * math.sqrt(x)) - (0.1260 * x) - (0.3516 * x * x) + (0.2843 * x * x * x) - (0.1015 * x * x * x * x))

        # Apply Horner's rule
        y = 5 * maxThickness * (0.2969 * math.sqrt(x) + x * (-0.1260 +  x * (-0.3516 + x * (0.2843 - x * 0.1015))))
        return y

    def _airfoilCurve(self, foreX, chord, thickness, height, resolution):
        points = []
        for i in range(0, resolution):
            
            x = float(i) / float(resolution)
            y = self._airfoilY(x, thickness)
            points.append(FreeCAD.Vector(foreX - (x * chord), y, height))

        points.append(FreeCAD.Vector(foreX - chord, 0.0, height))

        # Circle back for the other side of the airfoil
        for i in range(0, resolution):
            vector = points[resolution - i]
            points.append(FreeCAD.Vector(vector.x, -vector.y, vector.z))
        points.append(FreeCAD.Vector(foreX, 0.0, height))

        return points 

    def _makeSpline(self, points):
        spline = Part.BSplineCurve()
        spline.buildFromPoles(points)
        return spline

    def _midForeChordLimit(self, chord, value, midChordLimit):
        if midChordLimit and value > (chord / 2.0):
            return chord / 2.0
        return value

    def _midAftChordLimit(self, chord, value, midChordLimit):
        if midChordLimit and value > (chord / 2.0):
            return chord / 2.0
        return value

    def _makeChordProfileAirfoil(self, foreX, chord, thickness, height):
        # Standard NACA 4 digit symmetrical airfoil

        points = self._airfoilCurve(foreX, chord, thickness, height, 100)
        spline = self._makeSpline(points)

        wire = Part.Wire([spline.toShape()])
        return wire

    def _makeChordProfileWedge(self, foreX, chord, thickness, height):
        # Create the root rectangle
        chordFore = foreX
        chordAft = foreX - chord
        halfThickness = thickness / 2
        v1 = FreeCAD.Vector(chordFore, 0.0, height)
        v2 = FreeCAD.Vector(chordAft, -halfThickness, height)
        v3 = FreeCAD.Vector(chordAft, halfThickness, height)
        line1 = Part.LineSegment(v1, v2)
        line2 = Part.LineSegment(v1, v3)
        line3 = Part.LineSegment(v2, v3)
        
        wire = Part.Wire([line1.toShape(), line2.toShape(), line3.toShape()])
        return wire

    def _makeChordProfileDiamond(self, foreX, chord, thickness, height, maxChord):
        chordFore = foreX
        chordMid = foreX - maxChord
        chordAft = foreX - chord
        halfThickness = thickness / 2
        v1 = FreeCAD.Vector(chordFore, 0.0, height)
        v2 = FreeCAD.Vector(chordMid, halfThickness, height)
        v3 = FreeCAD.Vector(chordMid, -halfThickness, height)
        v4 = FreeCAD.Vector(chordAft, 0.0, height)
        line1 = Part.LineSegment(v1, v2)
        line2 = Part.LineSegment(v2, v4)
        line3 = Part.LineSegment(v4, v3)
        line4 = Part.LineSegment(v3, v1)
        
        wire = Part.Wire([line1.toShape(), line2.toShape(), line3.toShape(), line4.toShape()])
        return wire

    def _makeChordProfileTaperLE(self, foreX, chord, thickness, height, maxChord):
        chordFore = foreX
        chordMid = foreX - maxChord
        chordAft = foreX - chord
        halfThickness = thickness / 2
        v1 = FreeCAD.Vector(chordFore, 0.0, height)
        v2 = FreeCAD.Vector(chordMid, halfThickness, height)
        v3 = FreeCAD.Vector(chordMid, -halfThickness, height)
        v4 = FreeCAD.Vector(chordAft, halfThickness, height)
        v5 = FreeCAD.Vector(chordAft, -halfThickness, height)
        line1 = Part.LineSegment(v1, v2)
        line2 = Part.LineSegment(v2, v4)
        line3 = Part.LineSegment(v4, v5)
        line4 = Part.LineSegment(v5, v3)
        line5 = Part.LineSegment(v3, v1)
        
        wire = Part.Wire([line1.toShape(), line2.toShape(), line3.toShape(), line4.toShape(), line5.toShape()])
        return wire

    def _makeChordProfileTaperTE(self, foreX, chord, thickness, height, maxChord):
        chordFore = foreX
        chordMid = foreX - chord + maxChord
        chordAft = foreX - chord
        halfThickness = thickness / 2
        v1 = FreeCAD.Vector(chordAft, 0.0, height)
        v2 = FreeCAD.Vector(chordMid, halfThickness, height)
        v3 = FreeCAD.Vector(chordMid, -halfThickness, height)
        v4 = FreeCAD.Vector(chordFore, halfThickness, height)
        v5 = FreeCAD.Vector(chordFore, -halfThickness, height)
        line1 = Part.LineSegment(v1, v2)
        line2 = Part.LineSegment(v2, v4)
        line3 = Part.LineSegment(v4, v5)
        line4 = Part.LineSegment(v5, v3)
        line5 = Part.LineSegment(v3, v1)
        
        wire = Part.Wire([line1.toShape(), line2.toShape(), line3.toShape(), line4.toShape(), line5.toShape()])
        return wire

    def _makeChordProfileTaperLETE(self, foreX, chord, thickness, height, foreChord, aftChord, midChordLimit):
        chordFore = foreX
        chordFore1 = foreX - self._midForeChordLimit(chord, foreChord, midChordLimit)
        chordAft1 = foreX - chord + self._midAftChordLimit(chord, aftChord, midChordLimit)
        chordAft = foreX - chord
        halfThickness = thickness / 2

        v1 = FreeCAD.Vector(chordFore, 0.0, height)
        v2 = FreeCAD.Vector(chordFore1, halfThickness, height)
        v3 = FreeCAD.Vector(chordFore1, -halfThickness, height)
        v4 = FreeCAD.Vector(chordAft1, halfThickness, height)
        v5 = FreeCAD.Vector(chordAft1, -halfThickness, height)
        v6 = FreeCAD.Vector(chordAft, 0, height)
        if chordFore1 == chordAft1:
            line1 = Part.LineSegment(v1, v2)
            line2 = Part.LineSegment(v2, v6)
            line3 = Part.LineSegment(v6, v3)
            line4 = Part.LineSegment(v3, v1)

            wire = Part.Wire([line1.toShape(), line2.toShape(), line3.toShape(), line4.toShape()])
        else:
            line1 = Part.LineSegment(v1, v2)
            line2 = Part.LineSegment(v2, v4)
            line3 = Part.LineSegment(v4, v6)
            line4 = Part.LineSegment(v6, v5)
            line5 = Part.LineSegment(v5, v3)
            line6 = Part.LineSegment(v3, v1)

            wire = Part.Wire([line1.toShape(), line2.toShape(), line3.toShape(), line4.toShape(), line5.toShape(), line6.toShape()])
        return wire

    def _makeChordProfile(self, crossSection, foreX, chord, thickness, height, lengthPerCent, length1, length2, midChordLimit = True):
        l1 = length1
        l2 = length2
        if lengthPerCent:
            l1 = chord * (length1 / 100.0)
            l2 = chord * ((100.0 - length2) / 100.0)

        if crossSection == FIN_CROSS_SQUARE:
            return self._makeChordProfileSquare(foreX, chord, thickness, height)
        elif crossSection == FIN_CROSS_ROUND:
            return self._makeChordProfileRound(foreX, chord, thickness, height)
        elif crossSection == FIN_CROSS_AIRFOIL:
            return self._makeChordProfileAirfoil(foreX, chord, thickness, height)
        elif crossSection == FIN_CROSS_WEDGE:
            return self._makeChordProfileWedge(foreX, chord, thickness, height)
        elif crossSection == FIN_CROSS_DIAMOND:
            return self._makeChordProfileDiamond(foreX, chord, thickness, height, l1)
        elif crossSection == FIN_CROSS_TAPER_LE:
            return self._makeChordProfileTaperLE(foreX, chord, thickness, height, l1)
        elif crossSection == FIN_CROSS_TAPER_TE:
            return self._makeChordProfileTaperTE(foreX, chord, thickness, height, l1)
        elif crossSection == FIN_CROSS_TAPER_LETE:
            return self._makeChordProfileTaperLETE(foreX, chord, thickness, height, l1, l2, midChordLimit)

        return None

    def _makeTtw(self):
        # Create the Ttw tab
        origin = FreeCAD.Vector(self._obj.RootChord - self._obj.TtwOffset - self._obj.TtwLength, -0.5 * self._obj.TtwThickness, -1.0 * self._obj.TtwHeight)
        return Part.makeBox(self._obj.TtwLength, self._obj.TtwThickness, self._obj.TtwHeight, origin)

    def isValidShape(self):
        # Add error checking here
        if self._obj.Ttw:
            if self._obj.TtwOffset >= self._obj.RootChord:
                _err(translate('Rocket', "Ttw offset must be less than the root chord"))
                return False
            if self._obj.TtwLength <= 0:
                _err(translate('Rocket', "Ttw length must be greater than 0"))
                return False
            if self._obj.TtwHeight <= 0:
                _err(translate('Rocket', "Ttw height must be greater than 0"))
                return False
            if self._obj.TtwThickness <= 0:
                _err(translate('Rocket', "Ttw thickness must be greater than 0"))
                return False
        return True

    def _makeProfiles(self):
        profiles = []
        return profiles

    def _makeCommon(self):
        # Override this id we have a "masking" shape
        return None

    def _drawFinDebug(self, debug):
        profiles = self._makeProfiles()
        if profiles is not None and len(profiles) > 0:
            if isinstance(profiles[0], list):
                # Using a compound instead of a fuse makes drawing much faster, but also leads to
                # a number of 'BOPAlgo SelfIntersect' errors. Se we stick with the fuse

                loft = None
                for profile in profiles:
                    if loft is None:
                        loft = Part.makeLoft(profile, True)
                    else:
                        loft = loft.fuse(Part.makeLoft(profile, True))
            else:
                loft = Part.makeLoft(profiles, True)

            if loft is not None:
                mask = self._makeCommon()
                if debug == FIN_DEBUG_MASK_ONLY:
                    loft = mask
                elif mask is not None and (debug != FIN_DEBUG_PROFILE_ONLY):
                    loft = loft.common(mask)

                if self._obj.Ttw:
                    ttw = self._makeTtw()
                    if ttw:
                        loft = loft = loft.fuse(ttw)

        return loft

    def _drawSingleFin(self):
        if hasattr(self._obj,"DebugSketch"):
            return self._drawFinDebug(self._obj.DebugSketch)
        return self._drawFinDebug(FIN_DEBUG_FULL)

    def _drawFin(self):
        fin = self._drawSingleFin()
        fin.translate(FreeCAD.Vector(0,0,float(self._obj.ParentRadius)))
        # print ("Translate (%s,%s,%s)" % (0, 0, self._obj.ParentRadius))
        return Part.makeCompound([fin])

    def _drawFinSet(self):
        fins = []
        base = self._drawSingleFin()
        for i in range(self._obj.FinCount):
            fin = Part.Shape(base) # Create a copy
            fin.translate(FreeCAD.Vector(0,0,float(self._obj.ParentRadius)))
            fin.rotate(FreeCAD.Vector(0, 0, 0), FreeCAD.Vector(1,0,0), i * float(self._obj.FinSpacing))
            fins.append(fin)

        return Part.makeCompound(fins)

    def draw(self):
        
        if not self.isValidShape():
            return

        try:
            if self._obj.FinSet:
                self._obj.Shape = self._drawFinSet()
            else:
                self._obj.Shape = self._drawFin()
            self._obj.Placement = self._placement

        except (ZeroDivisionError, Part.OCCError):
            _err(translate('Rocket', "Fin parameters produce an invalid shape"))
            return
