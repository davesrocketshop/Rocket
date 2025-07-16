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

from Rocket.Constants import FIN_CROSS_SQUARE, FIN_CROSS_ROUND, FIN_CROSS_AIRFOIL, FIN_CROSS_WEDGE, \
    FIN_CROSS_DIAMOND, FIN_CROSS_TAPER_LETE, FIN_CROSS_BICONVEX, FIN_CROSS_ELLIPSE

from Rocket.ShapeHandlers.FinShapeHandler import FinShapeHandler

CROSS_SECTIONS = 100  # Number of cross sections for the ellipse

class FinEllipseShapeHandler(FinShapeHandler):

    def __init__(self, obj : Any) -> None:
        super().__init__(obj)

    def _radiusAt(self, chord : float, height : float, x : float) -> float:
        major = height
        minor = chord / 2.0
        y = (minor / major) * math.sqrt(major * major - x * x)
        return y

    def _halfEllipseCurve(self, major : float, minor : float, thickness : float, midChord : float) -> Any:
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

        return arc

    def _halfEllipse(self, major : float, minor : float, thickness : float, midChord : float) -> Any:
        arc = self._halfEllipseCurve(major, minor, thickness, midChord)

        line = Part.makeLine((midChord + minor, thickness, 0), (midChord - minor, thickness, 0))
        wire = Part.Wire([arc.toShape(), line])
        return wire

    def _taperedEllipse(self) -> list:
        # The loft is 3 (or 4) ellipses, center and both sides
        min = self.minimumEdge() / 2
        midChord = self._rootChord / 2.0
        height = self._height
        center1 = self._halfEllipse(height, midChord, min, midChord)
        center2 = self._halfEllipse(height, midChord, -min, midChord)

        halfThickness = self._rootThickness / 2.0
        if self._rootPerCent:
            length = self._rootChord * (self._rootLength1 / 100.0)
        else:
            length = self._rootLength1
        radius = midChord - length
        height = self._height - length
        side1 = self._halfEllipse(height, radius, -halfThickness, midChord)
        side2 = self._halfEllipse(height, radius,  halfThickness, midChord)

        if min > 0:
            return [[side1, center2], [center2, center1], [center1, side2]]
        return [[side1, center1], [center1, side2]]

    def _squareEllipse(self) -> list:
        # The loft is 2 ellipses - both sides
        midChord = self._rootChord / 2.0
        height = self._height
        halfThickness = self._rootThickness / 2.0

        side1 = self._halfEllipse(height, midChord, -halfThickness, midChord)
        side2 = self._halfEllipse(height, midChord,  halfThickness, midChord)

        return [side1, side2]

    def _makeCut(self) -> None:
        # # The loft is 3 ellipses, center and both sides
        # if self._rootCrossSection == FIN_CROSS_ROUND:
        #     midChord = self._rootChord / 2.0
        #     halfThickness = self._rootThickness / 2.0
        #     height = self._height - halfThickness

        #     path = self._halfEllipseCurve(height, midChord - halfThickness,  0.0, midChord)

        #     arc = Part.Arc(FreeCAD.Vector(0, -halfThickness, 0), FreeCAD.Vector(-halfThickness, 0, 0), FreeCAD.Vector(0, halfThickness, 0))
        #     line = Part.LineSegment(FreeCAD.Vector(0, -halfThickness, 0), FreeCAD.Vector(0, halfThickness, 0))
        #     # wire = Part.Wire([arc.toShape(), line])
        #     # face = Part.Face(wire)
        #     shape = Part.Shape([arc, line])
        #     Part.show(shape)
        #     Part.show(path.toShape())

        #     # print(dir(wire))

        #     part = Part.makeSweepSurface(path.toShape(), arc.toShape())
        #     return part

        #     # Create a semi-circle and sweep it along the path

        #     # return path.toShape()
        #     # makeSweep(const TopoDS_Shape& profile, double, int) const;

        return None

    def _makeProfiles(self) -> list:
        if self._rootCrossSection == FIN_CROSS_TAPER_LETE:
            return self._taperedEllipse()
        if self._rootCrossSection in [FIN_CROSS_SQUARE]: #, FIN_CROSS_ROUND]:
            return self._squareEllipse()

        min = self.minimumEdge() / 2
        ellipses = []
        midChord = self._rootChord / 2.0
        tapered = self._rootCrossSection in [FIN_CROSS_ROUND, FIN_CROSS_BICONVEX, FIN_CROSS_ELLIPSE, FIN_CROSS_AIRFOIL, FIN_CROSS_WEDGE, FIN_CROSS_DIAMOND]

        l1, l2 = self._lengthsFromPercent(self._rootChord, self._rootPerCent,
                                        self._rootLength1, self._rootLength2)
        for i in range(CROSS_SECTIONS):
            height = i * self._height / float(CROSS_SECTIONS)
            radius = self._radiusAt(self._rootChord, self._height, height)
            # if radius < min:
            #     radius = min
            if tapered:
                thickness = 2.0 * self._radiusAt(self._rootThickness / 2.0, self._height, height)
            else:
                thickness = self._rootThickness
            if thickness < (2.0 * min):
                thickness = (2.0 * min)
            ellipses.append(self._makeChordProfile(self._rootCrossSection,
                midChord - radius,
                radius * 2.0,
                thickness, #self._rootThickness, # need to fix this
                height,
                l1,
                l2,
                midChordLimit = True
            ))

        # The tip is a special case
        if min > 0:
            radius = min * 2
        else:
            radius = 1e-4 # Really small radius
        if tapered:
            thickness = radius
        else:
            thickness = self._rootThickness
        if thickness < (2.0 * min):
            thickness = (2.0 * min)
        ellipses.append(self._makeChordProfile(self._rootCrossSection,
            midChord - radius,
            radius * 2.0,
            thickness, # need to fix this
            self._height,
            l1,
            l2,
            midChordLimit = True
        ))
        return ellipses
