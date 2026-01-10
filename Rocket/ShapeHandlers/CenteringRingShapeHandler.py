# SPDX-License-Identifier: LGPL-2.1-or-later
# SPDX-File-Notice: Part of the Rocket addon.

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
"""Class for drawing Centering Rings"""

__title__ = "FreeCAD Centering Ring Handler"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

from typing import Any

import FreeCAD
import Part

translate = FreeCAD.Qt.translate

from Rocket.ShapeHandlers.BulkheadShapeHandler import BulkheadShapeHandler
from Rocket.Utilities import validationError, _err

class CenteringRingShapeHandler(BulkheadShapeHandler):
    def __init__(self, obj : Any) -> None:
        super().__init__(obj)

        self._instanceCount = int(obj.InstanceCount)
        self._separation = float(obj.InstanceSeparation)

        self._centerDiameter = float(obj.CenterDiameter)

        self._notched = bool(obj.Notched)
        self._notchWidth = float(obj.NotchWidth)
        self._notchHeight = float(obj.NotchHeight)

    def isValidShape(self) -> bool:
        if not super().isValidShape():
            return False

        # Perform some general validations
        # if self._centerDiameter <= 0:
        #     validationError(translate('Rocket', "Centering ring has no hole, as the center diameter must be greater than zero"))

        if self._centerDiameter >= self._diameter:
            validationError(translate('Rocket', "Centering ring center diameter must be less than the outer diameter"))
            return False

        if self._step:
            if self._centerDiameter >= self._stepDiameter:
                validationError(translate('Rocket', "Centering ring center diameter must be less than the step diameter"))
                return False

        if self._notched:
            if self._notchWidth > self._centerDiameter:
                validationError(translate('Rocket', "The notch width must be less than or equal to the center diameter"))
                return False
            if self._notchWidth <= 0:
                validationError(translate('Rocket', "The notch width must be greater than zero"))
                return False
            if self._notchHeight <= 0:
                validationError(translate('Rocket', "The notch height must be greater than zero"))
                return False

        if self._holes:
            if self._holeCenter - (self._holeDiameter / 2.0) <= (self._centerDiameter / 2.0):
                validationError(translate('Rocket', "Hole extends inside the center diameter"))
                return False

        return True

    def _drawCenteringRing(self) -> Any:
        bulkhead = self._drawBulkhead()

        # Add CR hole
        thickness = self._thickness
        if self._step:
            thickness += self._stepDiameter
        centerRadius = self._centerDiameter / 2.0

        if centerRadius > 0:
            hole = Part.makeCylinder(centerRadius, thickness, FreeCAD.Vector(0,0,0), FreeCAD.Vector(1,0,0))
            cr = bulkhead.cut(hole)

            if self._notched:
                hole = Part.makeBox(self._notchHeight + centerRadius, self._notchWidth, thickness, FreeCAD.Vector(0,self._notchWidth / 2,0), FreeCAD.Vector(1,0,0))
                cr = cr.cut(hole)
        else:
            cr = bulkhead

        return cr

    def drawInstances(self) -> Any:
        crs = []
        base = self._drawCenteringRing()
        for i in range(self._instanceCount):
            cr = Part.Shape(base) # Create a copy
            cr.translate(FreeCAD.Vector(i * (self._thickness + self._separation),0,0))
            crs.append(cr)

        return Part.makeCompound(crs)

    def draw(self) -> None:
        if not self.isValidShape():
            return

        try:
            self._obj.Shape = self.drawInstances()
            self._obj.Placement = self._placement
        except (ZeroDivisionError, Part.OCCError):
            _err(translate('Rocket', "Centering ring parameters produce an invalid shape"))
            return
