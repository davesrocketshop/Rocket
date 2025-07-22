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

import FreeCAD
import Part
import math

from DraftTools import translate

from Rocket.Constants import FIN_CROSS_SQUARE, FIN_CROSS_ROUND, FIN_CROSS_AIRFOIL, FIN_CROSS_WEDGE, \
    FIN_CROSS_DIAMOND, FIN_CROSS_TAPER_LE, FIN_CROSS_TAPER_TE, FIN_CROSS_TAPER_LETE, FIN_CROSS_BICONVEX, FIN_CROSS_ELLIPSE

from Rocket.Utilities import validationError

from Rocket.ShapeHandlers.FinShapeHandler import FinShapeHandler

class FinTriangleShapeHandler(FinShapeHandler):

    def __init__(self, obj : Any) -> None:
        super().__init__(obj)

    def _makeRootProfile(self, height : float = 0.0):
        # Create the root profile, casting everything to float to avoid typing issues
        l1, l2 = self._lengthsFromPercent(float(self._obj.RootChord), self._obj.RootPerCent,
                                          float(self._obj.RootLength1), float(self._obj.RootLength2))
        return self._makeChordProfile(self._obj.RootCrossSection, 0.0, float(self._obj.RootChord),
            float(self._obj.RootThickness), height, l1, l2)

    def _makeTipProfile(self) -> Any:
        # Create the tip profile, casting everything to float to avoid typing issues
        if self._obj.RootCrossSection in [FIN_CROSS_DIAMOND]:
            min = self.minimumEdge()
            if min > 0:
                l1, l2 = self._lengthsFromRootRatio(min)
                return self._makeChordProfile(FIN_CROSS_DIAMOND, float(self._obj.SweepLength), min,
                    min + 0.001, float(self._obj.Height), l1, l2)
            else:
                return Part.Point(FreeCAD.Vector(self._obj.SweepLength, 0.0, self._obj.Height)).toShape()

        l1, l2 = self._lengthsFromPercent(float(self._obj.RootChord), self._obj.RootPerCent,
                                          float(self._obj.RootLength1), float(self._obj.RootLength2))
        chord, height, sweep = self._topChord(l1, l2)
        return self._makeChordProfile(self._obj.RootCrossSection, sweep, chord,
            float(self._obj.RootThickness), height, l1, l2)

    def _heightAtChord(self, chord : float) -> float:
        theta1 = math.radians(self._sweepAngleFromLength())
        length = float(self._obj.SweepLength) - float(self._obj.RootChord)
        theta2 = (math.pi / 2.0) - math.atan2(float(self._obj.Height), length) # In radians
        min = self.minimumEdge()

        height = float(self._obj.Height) - ((chord - min)/(math.tan(theta1) - math.tan(theta2)))
        return height

    def _sweepAngleFromLength(self) -> float:
        length = float(self._obj.SweepLength)
        min = self.minimumEdge() / 2.0
        if min > 0:
            length -= min
        theta = 90.0 - math.degrees(math.atan2(float(self._obj.Height), length))
        return theta

    def _sweepAtHeight(self, height : float) -> float:
        angle = self._sweepAngleFromLength()
        sweep = math.tan(math.radians(angle)) * height
        return sweep

    def _chordAtHeight(self, height : float) -> float:
        x1 = self._sweepAtHeight(height)
        x2 = self._rootChord + (height / self._height) * (self._sweepLength - self._rootChord)
        return abs(x1 - x2)

    def _makeAtHeightProfile(self, crossSection : str, height : float = 0.0, offset : float = 0.0) -> Any:
        chord = self._chordAtHeight(height) + 2.0 * offset
        thickness = self._rootThickness + 2.0 * offset
        l1, l2 = self._lengthsFromPercent(chord, self._rootPerCent,
                                          self._rootLength1, self._rootLength2)
        return self._makeChordProfile(crossSection, -offset + self._sweepAtHeight(height), chord,
            thickness, height, l1, l2)

    def _midChord(self, rootChord : float) -> tuple[float, float, float]:

        chord = rootChord / 2.0
        height = self._heightAtChord(chord)

        sweep = self._sweepAtHeight(height)# + (chord / 2)

        return chord, height, sweep

    def _topChord(self, tip1 : float, tip2 : float) -> tuple[float, float, float]:

        crossSection = self._obj.RootCrossSection
        if crossSection in [FIN_CROSS_WEDGE, FIN_CROSS_SQUARE]:
            chord = 0.00001 # Effectively but not exactly zero
            height = float(self._obj.Height)
        elif crossSection in [FIN_CROSS_ROUND, FIN_CROSS_ELLIPSE]:
            chord = float(self._obj.RootThickness)
            height = max(float(self._obj.Height) - (float(self._obj.RootThickness) / 2.0), 0)
        elif crossSection in [FIN_CROSS_AIRFOIL, FIN_CROSS_BICONVEX]:
            chord = float(self._obj.RootThickness)
            height = self._heightAtChord(chord)
        elif crossSection in [FIN_CROSS_DIAMOND, FIN_CROSS_TAPER_LE, FIN_CROSS_TAPER_TE]:
            chord = tip1
            height = self._heightAtChord(chord)
        elif crossSection in [FIN_CROSS_TAPER_LETE]:
            chord = tip1 + tip2 + 0.001
            height = self._heightAtChord(chord)
        else:
            chord = 0
            height = float(self._obj.Height)

        sweep = self._sweepAtHeight(height)

        return chord, height, sweep

    def isValidShape(self) -> bool:
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
        return super().isValidShape()

    def _makeProfiles(self) -> list:
        profiles = []
        profiles.append(self._makeRootProfile())
        profiles.append(self._makeTipProfile())
        top = self._makeTopProfile()
        if top is not None:
            profiles.append(top)
        return profiles

    def _makeTopProfile(self) -> Any:
        if self._obj.RootCrossSection in [FIN_CROSS_BICONVEX, FIN_CROSS_ROUND, FIN_CROSS_ELLIPSE, FIN_CROSS_WEDGE,
                                            FIN_CROSS_SQUARE, FIN_CROSS_DIAMOND, FIN_CROSS_AIRFOIL,
                                            FIN_CROSS_TAPER_LE, FIN_CROSS_TAPER_TE, FIN_CROSS_TAPER_LETE]:
            # Already handled
            return None
        else:
            # Just a point at the tip of the fin, used for lofts
            tip=Part.Point(FreeCAD.Vector(self._obj.SweepLength, 0.0, self._obj.Height)).toShape()
        return tip

    def _makeRoundTip(self) -> Any:
        # Half sphere of radius thickness
        radius = float(self._obj.RootThickness) / 2.0 # + 0.1
        height = float(self._obj.Height) - radius # self._heightAtChord(2.0 * radius)
        sweep = self._sweepAtHeight(height) + radius

        _, theta, _ = self._angles()
        x = math.sin(theta)
        z = math.cos(theta)
        base = Part.Circle(FreeCAD.Vector(sweep, 0, height),
                            FreeCAD.Vector(x, 0, z), radius)
        arc = Part.Arc(base, 0, math.pi)
        arc2 = Part.Arc(base, math.pi, 2.0 * math.pi)

        point1 = arc.StartPoint
        point1.z += 0.0001 # Offset by a very small amount for the loft to work
        point2 = arc.EndPoint
        point2.z += 0.0001
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

    def _makeBiconvexTip(self) -> Any:
        l1, l2 = self._lengthsFromPercent(float(self._obj.RootChord), self._obj.RootPerCent,
                                          float(self._obj.RootLength1), float(self._obj.RootLength2))
        chord, height, sweep = self._topChord(l1, l2)
        base = self._makeChordProfile(FIN_CROSS_BICONVEX, sweep, chord,
            float(self._obj.RootThickness), height, l1, l2)

        min = self.minimumEdge()
        if min > 0:
            top=self._makeChordProfile(FIN_CROSS_BICONVEX, float(self._obj.SweepLength) - (min/2.0), min,
                min, float(self._obj.Height), l1, l2)
        else:
            top=Part.Point(FreeCAD.Vector(self._obj.SweepLength, 0.0, self._obj.Height)).toShape()
        tip = Part.makeLoft([base, top], True)
        return tip

    def _makeLETaperTip(self) -> Any:
        l1, l2 = self._lengthsFromPercent(float(self._obj.RootChord), self._obj.RootPerCent,
                                          float(self._obj.RootLength1), float(self._obj.RootLength2))
        chord, height, sweep = self._topChord(l1, l2)
        base = self._makeChordProfile(FIN_CROSS_WEDGE, sweep, chord,
            float(self._obj.RootThickness), height, l1, l2)

        min = self.minimumEdge()
        if min > 0:
            top=self._makeChordProfile(FIN_CROSS_WEDGE, float(self._obj.SweepLength), min,
                min, float(self._obj.Height), l1, l2)
        else:
            top=Part.Point(FreeCAD.Vector(self._obj.SweepLength, 0.0, self._obj.Height)).toShape()
        tip = Part.makeLoft([base, top], True)
        return tip

    def _makeTETaperTip(self) -> Any:
        # Wedge at the base, point at the tip
        l1, l2 = self._lengthsFromPercent(float(self._obj.RootChord), self._obj.RootPerCent,
                                          float(self._obj.RootLength1), float(self._obj.RootLength2))
        chord, height, sweep = self._topChord(l1, l2)
        base = self._makeChordProfile(FIN_CROSS_WEDGE, sweep + chord, -chord,
            float(self._obj.RootThickness), height, l1, l2)

        min = self.minimumEdge()
        if min > 0:
            top=self._makeChordProfile(FIN_CROSS_WEDGE, float(self._obj.SweepLength), -min,
                min, float(self._obj.Height), l1, l2)
        else:
            top=Part.Point(FreeCAD.Vector(self._obj.SweepLength, 0.0, self._obj.Height)).toShape()
        tip = Part.makeLoft([base, top], True)
        return tip

    def _makeLETETaperTip(self) -> Any:
        # Wedge at the base, point at the tip
        l1, l2 = self._lengthsFromPercent(float(self._obj.RootChord), self._obj.RootPerCent,
                                          float(self._obj.RootLength1), float(self._obj.RootLength2))
        chord, height, sweep = self._topChord(l1, l2)
        base = self._makeChordProfile(FIN_CROSS_DIAMOND, sweep, chord,
            float(self._obj.RootThickness), height, l1, l2)

        min = self.minimumEdge()
        if min > 0:
            top=self._makeChordProfile(FIN_CROSS_DIAMOND, float(self._obj.SweepLength), min,
                min + 0.001, float(self._obj.Height), l1, l2)
        else:
            top=Part.Point(FreeCAD.Vector(self._obj.SweepLength, 0.0, self._obj.Height)).toShape()
        tip = Part.makeLoft([base, top], True)
        return tip

    def _makeAirfoilTip(self) -> Any:
        l1, l2 = self._lengthsFromPercent(float(self._obj.RootChord), self._obj.RootPerCent,
                                    float(self._obj.RootLength1), float(self._obj.RootLength2))
        chord, height, sweep = self._topChord(l1, l2)
        base = self._makeChordProfile(self._obj.RootCrossSection, sweep, chord,
            float(self._obj.RootThickness), height, l1, l2)

        min = self.minimumEdge()
        if min > 0:
            top=self._makeChordProfile(self._obj.RootCrossSection, float(self._obj.SweepLength) - (min/2.0), min,
                min, float(self._obj.Height), l1, l2)
        else:
            thickness = 0.001
            chord = float(self._obj.RootChord) / float(self._obj.RootThickness) * thickness
            top = self._makeChordProfile(self._obj.RootCrossSection, float(self._obj.SweepLength), chord,
                thickness, float(self._obj.Height), l1, l2)

        tip = Part.makeLoft([base, top], True)
        return tip

    def _makeTip(self) -> Any:
        """
            This function adds shapes, rather than profiles to be lofted
        """
        crossSection = self._obj.RootCrossSection
        if crossSection in [FIN_CROSS_ROUND, FIN_CROSS_ELLIPSE]:
            tip = self._makeRoundTip()
        elif crossSection in [FIN_CROSS_BICONVEX]:
            tip = self._makeBiconvexTip()
        elif crossSection in [FIN_CROSS_TAPER_LE]:
            tip = self._makeLETaperTip()
        elif crossSection in [FIN_CROSS_TAPER_TE]:
            tip = self._makeTETaperTip()
        elif crossSection in [FIN_CROSS_TAPER_LETE]:
            tip = self._makeLETETaperTip()
        elif crossSection in [FIN_CROSS_AIRFOIL]:
            tip = self._makeAirfoilTip()
        else:
            tip = None
        return tip
