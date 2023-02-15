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
        if self._obj.RootPerCent:
            rootLength2 = float(self._obj.RootLength2)
        else:
            rootLength2 = float(self._obj.RootChord) - float(self._obj.RootLength2)
        return self._makeChordProfile(self._obj.RootCrossSection, float(self._obj.RootChord), float(self._obj.RootChord), float(self._obj.RootThickness), 0.0, self._obj.RootPerCent, float(self._obj.RootLength1), rootLength2)

    def _makeTipProfile(self):
        # Create the tip profile, casting everything to float to avoid typing issues
        crossSection = self._obj.TipCrossSection
        if crossSection == FIN_CROSS_SAME:
            crossSection = self._obj.RootCrossSection
        if self._obj.RootPerCent:
            tipLength2 = float(self._obj.RootLength2)
        else:
            tipLength2 = -float(self._obj.RootLength2)
        tipThickness = float(self._obj.RootThickness)
        chord, height = self._topChord()
        return self._makeChordProfile(crossSection, float(self._obj.RootChord - self._obj.SweepLength), chord, tipThickness, height, self._obj.RootPerCent, float(self._obj.RootLength1), tipLength2)

    def _heightAtChord(self, chord):
        return float(self._obj.Height) - chord

    def _topChord(self):
        chord = 0
        height = float(self._obj.Height)
        crossSection = self._obj.TipCrossSection
        if crossSection == FIN_CROSS_SAME:
            crossSection = self._obj.RootCrossSection
        tip1 = float(self._obj.RootLength1)
        tip2 = float(self._obj.RootLength2)

        if crossSection in [FIN_CROSS_WEDGE, FIN_CROSS_ROUND]:
            chord = float(self._obj.RootThickness)
            height = float(self._obj.Height - self._obj.RootThickness)
        elif crossSection in [FIN_CROSS_TAPER_LE, FIN_CROSS_TAPER_TE]:
            chord = tip1
            height = self._heightAtChord(chord)
        elif crossSection in [FIN_CROSS_DIAMOND, FIN_CROSS_TAPER_LETE]:
            chord = tip1 + tip2
            height = self._heightAtChord(chord)

        return chord, height

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
        profiles.append(self._makeTip())
        return profiles

    def _makeTip(self):
        # Just a point at the tip of the fin, used for lofts
        point=Part.Point(FreeCAD.Vector(self._obj.SweepLength, self._obj.Height))
        return point
