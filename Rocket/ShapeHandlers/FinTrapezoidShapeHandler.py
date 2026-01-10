# SPDX-License-Identifier: LGPL-2.1-or-later
# SPDX-FileCopyrightText: 2021 David Carter <dcarter@davidcarter.ca>
# SPDX-File-Notice: Part of the Rocket addon.


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
