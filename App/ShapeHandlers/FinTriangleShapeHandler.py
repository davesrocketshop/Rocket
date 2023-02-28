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
    
from App.Constants import FIN_CROSS_SAME
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
        theta2 = math.radians((math.pi / 2.0) - math.atan2(float(self._obj.Height), length))

        height = float(self._obj.Height) - (chord/(math.tan(theta1) - math.tan(theta2)))
        return height
    
    def _sweepAtHeight(self, height):
        sweep = math.tan(math.radians(float(self._obj.SweepAngle))) * height
        return sweep
    
    def _topChord(self, tip1, tip2):

        crossSection = self._obj.RootCrossSection
        if crossSection in [FIN_CROSS_WEDGE, FIN_CROSS_SQUARE]:
            chord = 0.00001 # Effectively but not exactly zero
            height = float(self._obj.Height)
        elif crossSection in [FIN_CROSS_ROUND, FIN_CROSS_ELLIPSE, FIN_CROSS_BICONVEX]:
            chord = float(self._obj.RootThickness)
            height = max(float(self._obj.Height - self._obj.RootThickness), 0)
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
        elif crossSection in [FIN_CROSS_TAPER_LE]:
            tip = self._makeChordProfileWedge(float(self._obj.SweepLength), 0.001, 0.001, float(self._obj.Height))
        elif self._obj.RootCrossSection in [FIN_CROSS_BICONVEX, FIN_CROSS_ROUND, FIN_CROSS_ELLIPSE, FIN_CROSS_WEDGE, FIN_CROSS_SQUARE, FIN_CROSS_DIAMOND]:
            # Already handled
            return None
        else:
            # Just a point at the tip of the fin, used for lofts
            tip=Part.Point(FreeCAD.Vector(self._obj.SweepLength, 0.0, self._obj.Height)).toShape()
        return tip

    def _makeTip(self):
        """
            This function adds shapes, rather than profiles to be lofted
        """
        crossSection = self._obj.RootCrossSection
        if crossSection in [FIN_CROSS_BICONVEX, FIN_CROSS_ROUND, FIN_CROSS_ELLIPSE]:
            # Half sphere of radius thickness
            radius = float(self._obj.RootThickness) / 2.0
            height = float(self._obj.Height - self._obj.RootThickness)
            sweep = self._sweepAtHeight(height) + radius
            theta = math.radians(float(self._obj.SweepAngle))
            x = math.sin(theta)
            z = math.cos(theta)
            tip = Part.makeSphere(radius, 
                                  FreeCAD.Vector(sweep, 0.0, height), 
                                  FreeCAD.Vector(x, 0, z), -90, 90, 360)
        else:
            tip = None
        return tip
