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

from DraftTools import translate

from Rocket.Utilities import validationError

from Rocket.ShapeHandlers.FinShapeHandler import FinShapeHandler

class FinTrapezoidShapeHandler(FinShapeHandler):

    def __init__(self, obj : Any) -> None:
        super().__init__(obj)

    def _makeRootProfile(self, height : float = 0.0) -> Any:
        # Create the root profile, casting everything to float to avoid typing issues
        scaleHeight = self._scale * height
        l1, l2 = self._lengthsFromPercent(self._rootChord, self._rootPerCent,
                                          self._rootLength1, self._rootLength2)
        return self._makeChordProfile(self._rootCrossSection, 0.0, self._rootChord,
            self._rootThickness, scaleHeight, l1, l2)

    def _makeTipProfile(self) -> Any:
        # Create the tip profile, casting everything to float to avoid typing issues
        l1, l2 = self._lengthsFromPercent(self._tipChord, self._tipPerCent,
                                          self._tipLength1, self._tipLength2)
        return self._makeChordProfile(self._tipCrossSection, self._sweepLength, self._tipChord,
            self._tipThickness, self._height, l1, l2)

    def _sweepAtHeight(self, height : float) -> float:
        sweep = math.tan(math.radians(self._sweepAngle)) * height
        return sweep

    def _chordAtHeight(self, height : float) -> float:
        # sweep = math.tan(math.radians(self._sweepAngle)) * height
        return self._rootChord

    def _makeAtHeightProfile(self, crossSection : str, height : float = 0.0, offset : float = 0.0) -> Any:
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

    def _makeExtensionProfiles(self, height : float) -> list:
        profiles = []
        profiles.append(self._makeRootProfile(-height))
        profiles.append(self._makeRootProfile())
        return profiles

    def _makeFilletProfiles(self, radius : float) -> list:
        profiles = []
        profiles.append(self._makeAtHeightProfile(self._rootCrossSection, radius, 0.0))
        profiles.append(self._makeAtHeightProfile(self._filletCrossSection, radius / 2.0, radius * 0.293))
        profiles.append(self._makeAtHeightProfile(self._filletCrossSection, 0.0, radius))
        return profiles
