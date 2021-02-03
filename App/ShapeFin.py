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
import FreeCADGui
import Part
import math

from App.Constants import FIN_TYPE_TRAPEZOID, FIN_TYPE_ELLIPSE, FIN_TYPE_TUBE, FIN_TYPE_SKETCH
from App.Constants import FIN_CROSS_SQUARE, FIN_CROSS_ROUND, FIN_CROSS_AIRFOIL

class ShapeFin:

    def __init__(self, obj):

        obj.addProperty('App::PropertyEnumeration', 'FinType', 'Fin', 'Fin type')
        obj.FinType = [FIN_TYPE_TRAPEZOID, FIN_TYPE_ELLIPSE, FIN_TYPE_TUBE, FIN_TYPE_SKETCH]
        obj.FinType = FIN_TYPE_TRAPEZOID

        obj.addProperty('App::PropertyEnumeration', 'FinCrossSection', 'Fin', 'Fin cross section')
        obj.FinCrossSection = [FIN_CROSS_SQUARE, FIN_CROSS_ROUND, FIN_CROSS_AIRFOIL]
        obj.FinCrossSection = FIN_CROSS_SQUARE

        obj.addProperty('App::PropertyLength', 'RootChord', 'Fin', 'Length of the base of the fin').RootChord = 10.0
        obj.addProperty('App::PropertyLength', 'TipChord', 'Fin', 'Length of the tip of the fin').TipChord = 5.0
        obj.addProperty('App::PropertyLength', 'Height', 'Fin', 'Fin semi-span').Height = 10.0
        obj.addProperty('App::PropertyDistance', 'SweepLength', 'Fin', 'Sweep length').SweepLength = 0.0 # Must be distance since it can be negative
        obj.addProperty('App::PropertyAngle', 'SweepAngle', 'Fin', 'Sweep angle').SweepAngle = 0.0
        obj.addProperty('App::PropertyLength', 'Thickness', 'Fin', 'Fin thickness').Thickness = 2.0

        obj.addProperty('Part::PropertyPartShape', 'Shape', 'Fin', 'Shape of the fin')
        obj.Proxy=self
        self._obj = obj

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

    def _makeChordProfileAirfoil(self, foreX, chord, thickness, height):
        # Airfoil max thickness is typically at 30% of chord. This can be parameterized later
        maxChord = chord * 0.30
        halfThickness = thickness / 2

        ellipse = Part.ArcOfEllipse(Part.Ellipse(FreeCAD.Vector(foreX - maxChord, 0, height), maxChord, halfThickness), -math.pi/2, math.pi/2)
        v1 = FreeCAD.Vector(foreX - maxChord, halfThickness, height)
        v2 = FreeCAD.Vector(foreX - maxChord, -halfThickness, height)
        v3 = FreeCAD.Vector(foreX - chord, 0.0, height)
        line1 = Part.LineSegment(v1, v3)
        line2 = Part.LineSegment(v2, v3)

        wire = Part.Wire([ellipse.toShape(), line1.toShape(), line2.toShape()])
        return wire

    def _makeChordProfile(self, foreX, chord, thickness, height):
        # At the moment, only square cross sections are supported
        if self._obj.FinCrossSection == FIN_CROSS_SQUARE:
            return self._makeChordProfileSquare(foreX, chord, thickness, height)
        elif self._obj.FinCrossSection == FIN_CROSS_ROUND:
            return self._makeChordProfileRound(foreX, chord, thickness, height)
        elif self._obj.FinCrossSection == FIN_CROSS_AIRFOIL:
            return self._makeChordProfileAirfoil(foreX, chord, thickness, height)

        return None

    def _makeRootProfile(self):
        # Create the root profile
        return self._makeChordProfile(self._obj.RootChord, self._obj.RootChord, self._obj.Thickness, 0.0)

    def _makeTipProfile(self):
        # Create the tip profile
        return self._makeChordProfile(self._obj.RootChord - self._obj.SweepLength, self._obj.TipChord, self._obj.Thickness, self._obj.Height)

    def isValidShape(self):
        # Add error checking here
        return True

    def execute(self, obj):
        
        if not self.isValidShape():
            return

        try:
            rootProfile = self._makeRootProfile()
            tipProfile = self._makeTipProfile()
            if rootProfile is not None and tipProfile is not None:
                loft = Part.makeLoft([rootProfile, tipProfile], True)
                if loft is not None:
                    self._obj.Shape = loft
        except (ZeroDivisionError, Part.OCCError):
            _err("Fin parameters produce an invalid shape")
            return
