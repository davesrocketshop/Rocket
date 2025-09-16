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

from typing import Any
import math

import FreeCAD
import Part
from Part import Shape, Wire, BSplineCurve, Vertex

translate = FreeCAD.Qt.translate

from Rocket.Utilities import validationError

from Rocket.ShapeHandlers.FinShapeHandler import FinShapeHandler

class FinTrapezoidShapeHandler(FinShapeHandler):

    def __init__(self, obj : Any) -> None:
        super().__init__(obj)

    def _makeRootProfile(self, height : float = 0.0) -> Wire:
        # Create the root profile
        l1, l2 = self._lengthsFromPercent(self._rootChord, self._rootPerCent,
                                          self._rootLength1, self._rootLength2)
        return self._makeChordProfile(self._rootCrossSection, 0.0, self._rootChord,
            self._rootThickness, height, l1, l2)

    def _makeTipProfile(self) -> Wire:
        # Create the tip profile
        l1, l2 = self._lengthsFromPercent(self._tipChord, self._tipPerCent,
                                          self._tipLength1, self._tipLength2)
        return self._makeChordProfile(self._tipCrossSection, self._sweepLength, self._tipChord,
            self._tipThickness, self._height, l1, l2)

    def _sweepAtHeight(self, height : float) -> float:
        sweep = math.tan(math.radians(self._sweepAngle)) * height
        return sweep

    def _chordAtHeight(self, height : float) -> float:
        x1 = self._sweepAtHeight(height)
        x2 = self._rootChord + (height / self._height) * (self._sweepLength + self._tipChord - self._rootChord)
        return abs(x1 - x2)

    def _makeAtHeightProfile(self, crossSection : str, height : float = 0.0, offset : float = 0.0) -> Wire:
        chord = self._chordAtHeight(height) + 2.0 * offset
        thickness = self._rootThickness + 2.0 * offset
        l1, l2 = self._lengthsFromPercent(chord, self._rootPerCent,
                                          self._rootLength1, self._rootLength2)
        return self._makeChordProfile(crossSection, -offset + self._sweepAtHeight(height), chord,
            thickness, height, l1, l2)

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
        return super().isValidShape()

    def _makeProfiles(self) -> list:
        profiles = []
        profiles.append(self._makeRootProfile())
        profiles.append(self._makeTipProfile())
        return profiles
