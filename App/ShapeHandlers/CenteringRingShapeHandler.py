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
"""Class for drawing Centering Rings"""

__title__ = "FreeCAD Centering Ring Handler"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"
    
import FreeCAD
import Part

from DraftTools import translate

from App.ShapeHandlers.BulkheadShapeHandler import BulkheadShapeHandler
from App.Utilities import _err, _wrn

class CenteringRingShapeHandler(BulkheadShapeHandler):
    def __init__(self, obj):
        super().__init__(obj)

        self._centerDiameter = float(obj.CenterDiameter)

        self._notched = bool(obj.Notched)
        self._notchWidth = float(obj.NotchWidth)
        self._notchHeight = float(obj.NotchHeight)

    def isValidShape(self):
        if not super().isValidShape():
            return

        # Perform some general validations
        if self._centerDiameter <= 0:
            _wrn(translate('Rocket', "Centering ring has no hole, as the center diameter must be greater than zero"))

        if self._centerDiameter >= self._diameter:
            _err(translate('Rocket', "Centering ring center diameter must be less than the outer diameter"))
            return False

        if self._step:
            if self._centerDiameter >= self._stepDiameter:
                _err(translate('Rocket', "Centering ring center diameter must be less than the step diameter"))
                return False

        if self._notched:
            if self._notchWidth > self._centerDiameter:
                _err(translate('Rocket', "The notch width must be less than or equal to the center diameter"))
                return False
            if self._notchWidth <= 0:
                _err(translate('Rocket', "The notch width must be greater than zero"))
                return False
            if self._notchHeight <= 0:
                _err(translate('Rocket', "The notch height must be greater than zero"))
                return False

        if self._holes:
            if self._holeCenter - (self._holeDiameter / 2.0) <= (self._centerDiameter / 2.0):
                _err(translate('Rocket', "Hole extends inside the center diameter"))
                return False

        return True

    def _drawCenteringRing(self):
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
        
    def draw(self):
        if not self.isValidShape():
            return

        try:
            self._obj.Shape = self._drawCenteringRing()
            self._obj.Placement = self._placement
        except (ZeroDivisionError, Part.OCCError):
            _err(translate('Rocket', "Centering ring parameters produce an invalid shape"))
            return
