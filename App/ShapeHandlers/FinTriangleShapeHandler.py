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
    
from App.Constants import FIN_CROSS_SQUARE, FIN_CROSS_ROUND, FIN_CROSS_AIRFOIL, FIN_CROSS_WEDGE, \
    FIN_CROSS_DIAMOND, FIN_CROSS_TAPER_LE, FIN_CROSS_TAPER_TE, FIN_CROSS_TAPER_LETE, FIN_CROSS_BICONVEX, FIN_CROSS_ELLIPSE

from App.Utilities import _err

from App.ShapeHandlers.FinShapeHandler import FinShapeHandler

class FinTriangleShapeHandler(FinShapeHandler):

    def __init__(self, obj):
        super().__init__(obj)

    def _makeRootProfile(self):
        # Create the root profile, casting everything to float to avoid typing issues
        l1, l2 = self._lengthsFromPercent(float(self._obj.RootChord), self._obj.RootPerCent, 
                                          float(self._obj.RootLength1), float(self._obj.RootLength2))
        return self._makeChordProfile(self._obj.RootCrossSection, 0.0, float(self._obj.RootChord),
            float(self._obj.RootThickness), 0.0, l1, l2)

    def _makeMidProfile(self):
        # Create the profile at the mid point, to assist in accurate lofting
        if self._obj.RootCrossSection in [FIN_CROSS_DIAMOND, FIN_CROSS_WEDGE, FIN_CROSS_SQUARE]:
            return None
        
        l1, l2 = self._lengthsFromPercent(float(self._obj.RootChord), self._obj.RootPerCent, 
                                          float(self._obj.RootLength1), float(self._obj.RootLength2))
        chord, height, sweep = self._midChord(float(self._obj.RootChord))
        return self._makeChordProfile(self._obj.RootCrossSection, sweep, chord,
            float(self._obj.RootThickness), height, l1, l2)

    def _makeTipProfile(self):
        # Create the tip profile, casting everything to float to avoid typing issues
        if self._obj.RootCrossSection in [FIN_CROSS_DIAMOND]:
            return Part.Point(FreeCAD.Vector(self._obj.SweepLength, 0.0, self._obj.Height)).toShape()
        
        l1, l2 = self._lengthsFromPercent(float(self._obj.RootChord), self._obj.RootPerCent, 
                                          float(self._obj.RootLength1), float(self._obj.RootLength2))
        chord, height, sweep = self._topChord(l1, l2)
        return self._makeChordProfile(self._obj.RootCrossSection, sweep, chord,
            float(self._obj.RootThickness), height, l1, l2)

    def _heightAtChord(self, chord):
        theta1 = math.radians(float(self._obj.SweepAngle))
        length = float(self._obj.SweepLength) - float(self._obj.RootChord)
        theta2 = (math.pi / 2.0) - math.atan2(float(self._obj.Height), length) # In radians

        height = float(self._obj.Height) - (chord/(math.tan(theta1) - math.tan(theta2)))
        return height
    
    def _sweepAtHeight(self, height):
        sweep = math.tan(math.radians(float(self._obj.SweepAngle))) * height
        return sweep
    
    def _midChord(self, rootChord):

        chord = rootChord / 2.0
        height = self._heightAtChord(chord)

        sweep = self._sweepAtHeight(height)# + (chord / 2)

        return chord, height, sweep
    
    def _topChord(self, tip1, tip2):

        crossSection = self._obj.RootCrossSection
        if crossSection in [FIN_CROSS_WEDGE, FIN_CROSS_SQUARE]:
            chord = 0.00001 # Effectively but not exactly zero
            height = float(self._obj.Height)
        elif crossSection in [FIN_CROSS_ROUND, FIN_CROSS_ELLIPSE, FIN_CROSS_BICONVEX]:
            chord = float(self._obj.RootThickness)
            height = max(float(self._obj.Height) - (float(self._obj.RootThickness) / 2.0), 0)
        elif crossSection in [FIN_CROSS_DIAMOND, FIN_CROSS_TAPER_LE, FIN_CROSS_TAPER_TE]:
            chord = tip1
            height = self._heightAtChord(chord)
        elif crossSection in [FIN_CROSS_TAPER_LETE]:
            chord = tip1 + tip2
            height = self._heightAtChord(chord)
        else:
            chord = 0
            height = float(self._obj.Height)

        sweep = self._sweepAtHeight(height)

        return chord, height, sweep

    def isValidShape(self):
        # Add error checking here
        if self._obj.Ttw:
            if self._obj.TtwOffset >= self._obj.RootChord:
                # _err(translate('Rocket', "Ttw offset must be less than the root chord"))
                return False
            if self._obj.TtwLength <= 0:
                # _err(translate('Rocket', "Ttw length must be greater than 0"))
                return False
            if self._obj.TtwHeight <= 0:
                # _err(translate('Rocket', "Ttw height must be greater than 0"))
                return False
            if self._obj.TtwThickness <= 0:
                # _err(translate('Rocket', "Ttw thickness must be greater than 0"))
                return False
        return super().isValidShape()

    def _makeProfiles(self):
        profiles = []
        profiles.append(self._makeRootProfile())
        profiles.append(self._makeTipProfile())
        top = self._makeTopProfile()
        if top is not None:
            profiles.append(top)
        return profiles

    def _makeTopProfile(self):
        crossSection = self._obj.RootCrossSection
        if crossSection in [FIN_CROSS_AIRFOIL]:
            # Line across the tickness
            tip = Part.LineSegment(FreeCAD.Vector(self._obj.SweepLength, float(self._obj.RootThickness) / 2.0, self._obj.Height), 
                                    FreeCAD.Vector(self._obj.SweepLength, -float(self._obj.RootThickness) / 2.0, self._obj.Height))
        elif self._obj.RootCrossSection in [FIN_CROSS_BICONVEX, FIN_CROSS_ROUND, FIN_CROSS_ELLIPSE, FIN_CROSS_WEDGE, 
                                            FIN_CROSS_SQUARE, FIN_CROSS_DIAMOND, FIN_CROSS_TAPER_LE, FIN_CROSS_TAPER_TE, FIN_CROSS_TAPER_LETE]:
            # Already handled
            return None
        else:
            # Just a point at the tip of the fin, used for lofts
            tip=Part.Point(FreeCAD.Vector(self._obj.SweepLength, 0.0, self._obj.Height)).toShape()
        return tip
   
    def _makeRoundTip(self):
        # Half sphere of radius thickness
        radius = float(self._obj.RootThickness) / 2.0
        height = float(self._obj.Height) - radius
        sweep = self._sweepAtHeight(height) + radius

        _, theta, _ = self._angles()
        x = math.sin(theta)
        z = math.cos(theta)
        base = Part.Circle(FreeCAD.Vector(sweep, 0, height - 0.01),
                            FreeCAD.Vector(x, 0, z), radius)
        arc = Part.Arc(base, 0, math.pi)
        arc2 = Part.Arc(base, math.pi, 2.0 * math.pi)

        point1 = arc.StartPoint
        point1.x += 0.0001 # Offset by a very small amount for the loft to work
        point2 = arc.EndPoint
        point2.x += 0.0001
        mid = FreeCAD.Vector(sweep + radius * x, 0, height + radius * z)

        bezier = Part.BezierCurve()
        bezier.setPoles([point1, mid, point2])
        line1 = Part.makeLine(point1, point2)
        line2 = Part.makeLine(arc.StartPoint, arc.EndPoint)
        line3 = Part.makeLine(arc2.StartPoint, arc2.EndPoint)
        wire1 = Part.Wire([bezier.toShape(), line1])
        wire2 = Part.Wire([arc.toShape(), line2])
        wire3 = Part.Wire([arc2.toShape(), line3])

        loft1 = Part.makeLoft([wire1, wire2], True)
        loft2 = Part.makeLoft([wire1, wire3], True)
        tip = loft1.fuse(loft2)
        return tip
   
    def _makeLETaperTip(self):
        # Wedge at the base, point at the tip
        l1, l2 = self._lengthsFromPercent(float(self._obj.RootChord), self._obj.RootPerCent, 
                                          float(self._obj.RootLength1), float(self._obj.RootLength2))
        chord, height, sweep = self._topChord(l1, l2)
        base = self._makeChordProfile(FIN_CROSS_WEDGE, sweep, chord,
            float(self._obj.RootThickness), height, l1, l2)
        
        top=Part.Point(FreeCAD.Vector(self._obj.SweepLength, 0.0, self._obj.Height)).toShape()
        tip = Part.makeLoft([base, top], True)
        return tip
   
    def _makeTETaperTip(self):
        # Wedge at the base, point at the tip
        l1, l2 = self._lengthsFromPercent(float(self._obj.RootChord), self._obj.RootPerCent, 
                                          float(self._obj.RootLength1), float(self._obj.RootLength2))
        chord, height, sweep = self._topChord(l1, l2)
        base = self._makeChordProfile(FIN_CROSS_WEDGE, sweep + chord, -chord,
            float(self._obj.RootThickness), height, l1, l2)
        
        top=Part.Point(FreeCAD.Vector(self._obj.SweepLength, 0.0, self._obj.Height)).toShape()
        tip = Part.makeLoft([base, top], True)
        return tip
   
    def _makeLETETaperTip(self):
        # Wedge at the base, point at the tip
        l1, l2 = self._lengthsFromPercent(float(self._obj.RootChord), self._obj.RootPerCent, 
                                          float(self._obj.RootLength1), float(self._obj.RootLength2))
        chord, height, sweep = self._topChord(l1, l2)
        base = self._makeChordProfile(FIN_CROSS_DIAMOND, sweep, chord,
            float(self._obj.RootThickness), height, l1, l2)
        
        top=Part.Point(FreeCAD.Vector(self._obj.SweepLength, 0.0, self._obj.Height)).toShape()
        tip = Part.makeLoft([base, top], True)
        return tip

    def _makeTip(self):
        """
            This function adds shapes, rather than profiles to be lofted
        """
        crossSection = self._obj.RootCrossSection
        if crossSection in [FIN_CROSS_ROUND, FIN_CROSS_ELLIPSE, FIN_CROSS_BICONVEX]:
            tip = self._makeRoundTip()
        elif crossSection in [FIN_CROSS_TAPER_LE]:
            tip = self._makeLETaperTip()
        elif crossSection in [FIN_CROSS_TAPER_TE]:
            tip = self._makeTETaperTip()
        elif crossSection in [FIN_CROSS_TAPER_LETE]:
            tip = self._makeLETETaperTip()
        else:
            tip = None
        return tip
