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
"""Class for drawing fins"""

__title__ = "FreeCAD Fins"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"
    
import FreeCAD
import Part
import math

from DraftTools import translate

from Rocket.Constants import FIN_CROSS_SQUARE, FIN_CROSS_ROUND, FIN_CROSS_AIRFOIL, FIN_CROSS_WEDGE, \
    FIN_CROSS_DIAMOND, FIN_CROSS_TAPER_LE, FIN_CROSS_TAPER_TE, FIN_CROSS_TAPER_LETE, FIN_CROSS_BICONVEX, FIN_CROSS_ELLIPSE
from Rocket.Constants import FIN_DEBUG_FULL, FIN_DEBUG_PROFILE_ONLY, FIN_DEBUG_MASK_ONLY

from Rocket.Utilities import _err, validationError

class FinShapeHandler:

    def __init__(self, obj):
        self._obj = obj

        # This gets changed when redrawn so it's very important to save a copy
        self._placement = FreeCAD.Placement(obj.Placement)
    
    def _foreAngle(self):
        """
            Angle of the fins leading edge
        """
        return math.radians(float(self._obj.SweepAngle))
    
    def _aftAngle(self):
        """
            Angle of the fins trailing edge
        """
        length = float(self._obj.SweepLength) - float(self._obj.RootChord)
        theta2 = (math.pi / 2.0) - math.atan2(float(self._obj.Height), length) # In radians
        return theta2
    
    def _midAngle(self, foreAngle, aftAngle):
        """
            Angle of the fins mid line
        """
        return (foreAngle + aftAngle) / 2.0
    
    def _angles(self):
        """
            Calculate fore, mid, and aft angles
        """
        foreAngle = self._foreAngle()
        aftAngle = self._aftAngle()
        midAngle = self._midAngle(foreAngle, aftAngle)
        return (foreAngle, midAngle, aftAngle)

    def _makeChordProfileSquare(self, foreX, chord, thickness, height):
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

    def _makeChordProfileRound(self, foreX, chord, thickness, height):
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

    def _makeChordProfileEllipse(self, foreX, chord, thickness, height):
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

    def _makeChordProfileBiconvex(self, foreX, chord, thickness, height):
        chordFore = foreX
        chordAft = foreX + chord
        chordMid = foreX + (chord / 2)
        halfThickness = thickness / 2
        if chord <= thickness:
            # Easiest way to calculate the endpoint is to use the endpoints of the arc of a normal circle
            _, theta, _ = self._angles()
            x = math.sin(theta)
            z = math.cos(theta)
            circle = Part.Circle(FreeCAD.Vector(foreX + halfThickness, 0, height),
                                     FreeCAD.Vector(x,0,z), halfThickness)
            arc = Part.Arc(circle, 0, math.pi)
            v1 = arc.StartPoint
            v2 = arc.EndPoint
        else:
            v1 = FreeCAD.Vector(chordFore, 0.0, height)
            v2 = FreeCAD.Vector(chordAft, 0.0, height)
        v3 = FreeCAD.Vector(chordMid, -halfThickness, height)
        v4 = FreeCAD.Vector(chordMid, halfThickness, height)
        arc1 = Part.Arc(v1, v3, v2)
        arc2 = Part.Arc(v1, v4, v2)

        wire = Part.Wire([arc1.toShape(), arc2.toShape()])
        return wire
            
    def _airfoilY(self, x, maxThickness):
        # NACA symmetrical airfoil https://en.wikipedia.org/wiki/NACA_airfoil
        # y = 5 * maxThickness * ((0.2969 * math.sqrt(x)) - (0.1260 * x) - (0.3516 * x * x) + (0.2843 * x * x * x) - (0.1015 * x * x * x * x))

        # Apply Horner's rule
        y = 5 * maxThickness * (0.2969 * math.sqrt(x) + x * (-0.1260 +  x * (-0.3516 + x * (0.2843 - x * 0.1015))))
        return y

    def _airfoilCurve(self, foreX, chord, thickness, height, resolution):
        points = []
        points1 = []
        for i in range(0, resolution):
            
            x = float(i) / float(resolution)
            y = self._airfoilY(x, thickness)
            points.append(FreeCAD.Vector(foreX + (x * chord), y, height))
            points1.append(FreeCAD.Vector(foreX + (x * chord), -y, height))

        points.append(FreeCAD.Vector(foreX + chord, 0.0, height))
        points1.append(FreeCAD.Vector(foreX + chord, 0.0, height))

        # Creating separate splines for each side of the airfoil adds extra reference
        # points for lofting, reducing geometry errors
        splines = []
        splines.append(self._makeSpline(points).toShape())
        splines.append(self._makeSpline(points1).toShape())

        return splines 

    def _makeSpline(self, points):
        spline = Part.BSplineCurve()
        spline.buildFromPoles(points)
        return spline

    def _midChordLimit(self, chord, value, midChordLimit):
        if midChordLimit and value > (chord / 2.0):
            return chord / 2.0
        return value

    def _makeChordProfileAirfoil(self, foreX, chord, thickness, height):
        # Standard NACA 4 digit symmetrical airfoil

        splines = self._airfoilCurve(foreX, chord, thickness, height, 100)

        wire = Part.Wire(splines)
        return wire

    def _makeChordProfileWedge(self, foreX, chord, thickness, height):
        # Create the root rectangle
        chordFore = foreX
        chordAft = foreX + chord
        halfThickness = thickness / 2
        v1 = FreeCAD.Vector(chordFore, 0.0, height)
        v2 = FreeCAD.Vector(chordAft, -halfThickness, height)
        v3 = FreeCAD.Vector(chordAft, halfThickness, height)
        line1 = Part.LineSegment(v1, v2)
        line2 = Part.LineSegment(v1, v3)
        line3 = Part.LineSegment(v2, v3)
        
        wire = Part.Wire([line1.toShape(), line2.toShape(), line3.toShape()])
        return wire

    def _makeChordProfileDiamond(self, foreX, chord, thickness, height, maxChord, midChordLimit):
        chordFore = foreX
        chordMid = foreX + maxChord
        chordAft = foreX + chord
        halfThickness = thickness / 2
        if chordMid >= chordAft:
            chordMid = (chordFore + chordAft) / 2.0
            # # Create a wedge
            # v1 = FreeCAD.Vector(chordFore, 0.0, height)
            # v2 = FreeCAD.Vector(chordAft, -halfThickness, height)
            # v3 = FreeCAD.Vector(chordAft, halfThickness, height)
            # line1 = Part.LineSegment(v1, v2)
            # line2 = Part.LineSegment(v1, v3)
            # line3 = Part.LineSegment(v2, v3)
            
            # wire = Part.Wire([line1.toShape(), line2.toShape(), line3.toShape()])
            # return wire

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
        if maxChord == chord:
            chordMid = foreX + maxChord - 0.00001
        else:
            chordMid = foreX + maxChord
        chordAft = foreX + chord
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
        if maxChord == chord:
            chordMid = foreX + 0.00001
        else:
            chordMid = foreX + chord - maxChord
        chordAft = foreX + chord
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
        chordFore1 = foreX + self._midChordLimit(chord, foreChord, midChordLimit)
        chordAft1 = foreX + chord - self._midChordLimit(chord, aftChord, midChordLimit)
        if chordFore1 == chordAft1:
            chordAft1 += 0.0001
        chordAft = foreX + chord
        halfThickness = thickness / 2

        v1 = FreeCAD.Vector(chordFore, 0.0, height)
        v2 = FreeCAD.Vector(chordFore1, halfThickness, height)
        v3 = FreeCAD.Vector(chordFore1, -halfThickness, height)
        v4 = FreeCAD.Vector(chordAft1, halfThickness, height)
        v5 = FreeCAD.Vector(chordAft1, -halfThickness, height)
        v6 = FreeCAD.Vector(chordAft, 0, height)
        line1 = Part.LineSegment(v1, v2)
        line2 = Part.LineSegment(v2, v4)
        line3 = Part.LineSegment(v4, v6)
        line4 = Part.LineSegment(v6, v5)
        line5 = Part.LineSegment(v5, v3)
        line6 = Part.LineSegment(v3, v1)

        wire = Part.Wire([line1.toShape(), line2.toShape(), line3.toShape(), line4.toShape(), line5.toShape(), line6.toShape()])
        return wire
    
    def _lengthsFromPercent(self, chord, lengthPerCent, length1, length2):
        if lengthPerCent:
            l1 = chord * (length1 / 100.0)
            l2 = chord * ((100.0 - length2) / 100.0)
        else:
            l1 = length1
            l2 = chord - length2

        return l1, l2

    def _makeChordProfile(self, crossSection, foreX, chord, thickness, height, length1, length2, midChordLimit = True):

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

    def _makeTtw(self):
        # Create the Ttw tab
        origin = FreeCAD.Vector(self._obj.RootChord - self._obj.TtwOffset - self._obj.TtwLength, -0.5 * self._obj.TtwThickness, -1.0 * self._obj.TtwHeight)
        return Part.makeBox(self._obj.TtwLength, self._obj.TtwThickness, self._obj.TtwHeight, origin)

    def isValidShape(self):
        # Add error checking here
        if self._obj.Ttw:
            if self._obj.TtwOffset >= self._obj.RootChord:
                validationError(translate('Rocket', "Ttw offset must be less than the root chord"))
                return False
            if self._obj.TtwLength <= 0:
                validationError(translate('Rocket', "Ttw length must be greater than 0"))
                return False
            if self._obj.TtwHeight <= 0:
                validationError(translate('Rocket', "Ttw height must be greater than 0"))
                return False
            if self._obj.TtwThickness <= 0:
                validationError(translate('Rocket', "Ttw thickness must be greater than 0"))
                return False
        return True

    def _makeProfiles(self):
        profiles = []
        return profiles

    def _makeExtensionProfiles(self, height):
        profiles = []
        return profiles

    def _makeTip(self):
        return None

    def _makeCommon(self):
        # Override this if we have a "masking" shape
        return None
    
    def _extendRoot(self):
        # Override this if the fin root needs an extension to connect it to the body tube
        return False

    def finOnlyShape(self):
        fin = self._finOnlyShape(FIN_DEBUG_FULL)
        return Part.makeCompound([fin])

    def _finOnlyShape(self, debug):
        #
        # Return the shape of a single fin with no additions, such as fin tabs, fin cans, etc
        #
        # This can be used to determine characteristics such as mass, cg, and volume
        loft = None
        profiles = self._makeProfiles()
        if profiles is not None and len(profiles) > 0:
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
                if tip is not None:
                    loft = loft.fuse(tip)

            if loft is not None:
                mask = self._makeCommon()
                if debug == FIN_DEBUG_MASK_ONLY:
                    loft = mask
                elif mask is not None and (debug != FIN_DEBUG_PROFILE_ONLY):
                    loft = loft.common(mask)

        return loft

    def _makeRootExtension(self):
        loft = None
        height = float(self._obj.Diameter) / 2.0 + float(self._obj.Thickness)
        profiles = self._makeExtensionProfiles(height)
        if profiles is not None and len(profiles) > 0:
            loft = Part.makeLoft(profiles, True)

            # Make a cutout of the body tube center
            if loft is not None:
                center = Part.makeCylinder((self._obj.Diameter + self._obj.Thickness) / 2.0,
                                           2.0 * self._obj.Length,
                                           FreeCAD.Vector(-self._obj.Length / 2.0, 0, -height),
                                           FreeCAD.Vector(1, 0, 0)
                                           )
                if self._obj.Cant != 0:
                    center.rotate(FreeCAD.Vector(self._obj.Length / 2, 0, 0), FreeCAD.Vector(0,0,1), -self._obj.Cant)
                loft = loft.cut(center)

        return loft

    def _drawFinDebug(self, debug):
        fin = self._finOnlyShape(debug)
        if fin is not None:
            if self._extendRoot():
                extension = self._makeRootExtension()
                if extension:
                    fin = fin.fuse(extension)
            if self._obj.Ttw:
                ttw = self._makeTtw()
                if ttw:
                    fin = fin.fuse(ttw)

        return fin

    def _drawSingleFin(self):
        if hasattr(self._obj,"DebugSketch"):
            return self._drawFinDebug(self._obj.DebugSketch)
        return self._drawFinDebug(FIN_DEBUG_FULL)

    def _drawFin(self):
        fin = self._drawSingleFin()
        if self._obj.Cant != 0:
            fin.rotate(FreeCAD.Vector(self._obj.RootChord / 2, 0, 0), FreeCAD.Vector(0,0,1), self._obj.Cant)
        fin.translate(FreeCAD.Vector(0,0,float(self._obj.ParentRadius)))
        return Part.makeCompound([fin])

    def _drawFinSet(self, offset=0):
        fins = []
        base = self._drawSingleFin()
        baseX = 0
        if hasattr(self._obj, "LeadingEdgeOffset"):
            baseX = self._obj.LeadingEdgeOffset
        for i in range(self._obj.FinCount):
            fin = Part.Shape(base) # Create a copy
            if self._obj.Cant != 0:
                fin.rotate(FreeCAD.Vector(self._obj.RootChord / 2, 0, 0), FreeCAD.Vector(0,0,1), self._obj.Cant)
            fin.translate(FreeCAD.Vector(baseX,0,float(self._obj.ParentRadius) + offset))
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

        except (ZeroDivisionError, Part.OCCError) as ex:
            _err(translate('Rocket', "Fin parameters produce an invalid shape"))
            return
