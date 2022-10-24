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

from App.Constants import FIN_CROSS_SQUARE, FIN_CROSS_ROUND, FIN_CROSS_AIRFOIL, FIN_CROSS_WEDGE, \
    FIN_CROSS_DIAMOND, FIN_CROSS_TAPER_LETE

from App.FinShapeHandler import FinShapeHandler

CROSS_SECTIONS = 100  # Number of cross sections for the ellipse

class FinEllipseShapeHandler(FinShapeHandler):

    def __init__(self, obj):
        super().__init__(obj)

    def _radiusAt(self, chord, height, x):
        major = height
        minor = chord / 2.0
        y = (minor / major) * math.sqrt(major * major - x * x)
        return y

    def _halfEllipse(self, major, minor, thickness, midChord):
        if major > minor:
            ellipse = Part.Ellipse(FreeCAD.Vector(midChord, thickness, major), 
                    FreeCAD.Vector(midChord - minor, thickness, 0), 
                    FreeCAD.Vector(midChord, thickness, 0))
            arc = Part.ArcOfEllipse(ellipse, -math.pi/2, math.pi/2)
        else:
            ellipse = Part.Ellipse(FreeCAD.Vector(midChord - minor, thickness, 0), 
                    FreeCAD.Vector(midChord, thickness, major), 
                    FreeCAD.Vector(midChord, thickness, 0))
            arc =  Part.ArcOfEllipse(ellipse, 0, math.pi)

        line = Part.makeLine((midChord + minor, thickness, 0), (midChord - minor, thickness, 0))
        wire = Part.Wire([arc.toShape(), line])
        return wire

    def _taperedEllipse(self):
        # The loft is 3 ellipses, center and both sides
        midChord = float(self._obj.RootChord) / 2.0
        height = float(self._obj.Height)
        center = self._halfEllipse(height, midChord, 0, midChord)

        halfThickness = float(self._obj.RootThickness) / 2.0
        if self._obj.RootPerCent:
            length = float(self._obj.RootChord) * (float(self._obj.RootLength1) / 100.0)
        else:
            length = float(self._obj.RootLength1)
        radius = midChord - length
        height = float(self._obj.Height) - length
        side1 = self._halfEllipse(height, radius, -halfThickness, midChord)
        side2 = self._halfEllipse(height, radius,  halfThickness, midChord)

        return [[side1, center], [center, side2]]

    def _squareEllipse(self):
        # The loft is 3 ellipses, center and both sides
        midChord = float(self._obj.RootChord) / 2.0
        height = float(self._obj.Height)
        halfThickness = float(self._obj.RootThickness) / 2.0

        side1 = self._halfEllipse(height, midChord, -halfThickness, midChord)
        side2 = self._halfEllipse(height, midChord,  halfThickness, midChord)

        return [side1, side2]

    def _makeProfiles(self):
        if self._obj.RootCrossSection == FIN_CROSS_TAPER_LETE:
            return self._taperedEllipse()
        if self._obj.RootCrossSection == FIN_CROSS_SQUARE:
            return self._squareEllipse()

        ellipses = []
        midChord = float(self._obj.RootChord) / 2.0
        tapered = self._obj.RootCrossSection in [FIN_CROSS_ROUND, FIN_CROSS_AIRFOIL, FIN_CROSS_WEDGE, FIN_CROSS_DIAMOND]
        if self._obj.RootPerCent:
            rootLength2 = float(self._obj.RootLength2)
        else:
            rootLength2 = float(self._obj.RootChord) - float(self._obj.RootLength2)
        for i in range(CROSS_SECTIONS):
            height = i * float(self._obj.Height) / float(CROSS_SECTIONS)
            radius = self._radiusAt(float(self._obj.RootChord), float(self._obj.Height), height)
            if tapered:
                thickness = 2.0 * self._radiusAt(float(self._obj.RootThickness) / 2.0, float(self._obj.Height), height)
            else:
                thickness = float(self._obj.RootThickness)
            ellipses.append(self._makeChordProfile(self._obj.RootCrossSection,
                midChord + radius,
                radius * 2.0,
                thickness, #float(self._obj.RootThickness), # need to fix this
                height,
                self._obj.RootPerCent,
                float(self._obj.RootLength1),
                rootLength2,
                midChordLimit = True
            ))

        # The tip is a special case
        radius = 1e-6 # Really small radius
        if tapered:
            thickness = radius
        else:
            thickness = float(self._obj.RootThickness)
        ellipses.append(self._makeChordProfile(self._obj.RootCrossSection,
            midChord + radius,
            radius * 2.0,
            thickness, # need to fix this
            float(self._obj.Height),
            self._obj.RootPerCent,
            float(self._obj.RootLength1),
            rootLength2,
            midChordLimit = True
        ))
        return ellipses
