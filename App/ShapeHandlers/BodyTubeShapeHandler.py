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
"""Class for drawing body tubes"""

__title__ = "FreeCAD Body Tube Handler"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"
    
import FreeCAD
import Part

from App.Utilities import _err
from DraftTools import translate

class BodyTubeShapeHandler():
    def __init__(self, obj):

        # This gets changed when redrawn so it's very important to save a copy
        self._placement = FreeCAD.Placement(obj.Placement)

        self._OD = float(obj.Diameter)
        if self._OD > 0.0:
            self._ID = self._OD - 2.0 * float(obj.Thickness)
        else:
            self._ID = float(obj.Thickness)
        self._length = float(obj.Length)
        self._obj = obj

    def isValidShape(self):
        
        # Perform some general validations
        if self._ID <= 0:
            # _err(translate('Rocket', "Body tube inner diameter must be greater than zero"))
            return False
        if self._OD <= self._ID:
            # _err(translate('Rocket', "Body tube outer diameter must be greater than the inner"))
            return False
        if self._length <= 0:
            # _err(translate('Rocket', "Body tube length must be greater than zero"))
            return False

        return True

    def _drawTubeEdges(self):
        innerRadius = self._ID / 2.0
        outerRadius = self._OD / 2.0

        line1 = Part.LineSegment(FreeCAD.Vector(0.0, innerRadius),          FreeCAD.Vector(self._length, innerRadius))
        line2 = Part.LineSegment(FreeCAD.Vector(self._length, innerRadius), FreeCAD.Vector(self._length, outerRadius))
        line3 = Part.LineSegment(FreeCAD.Vector(self._length, outerRadius), FreeCAD.Vector(0.0, outerRadius))
        line4 = Part.LineSegment(FreeCAD.Vector(0.0, outerRadius),          FreeCAD.Vector(0.0, innerRadius))

        return [line1.toShape(), line2.toShape(), line3.toShape(), line4.toShape()]
        
    def draw(self):
        if not self.isValidShape():
            return

        edges = None

        try:
            edges = self._drawTubeEdges()
        except (ZeroDivisionError, Part.OCCError):
            _err(translate('Rocket', "Body tube parameters produce an invalid shape"))
            return

        if edges is not None:
            try:
                wire = Part.Wire(edges)
                face = Part.Face(wire)
                self._obj.Shape = face.revolve(FreeCAD.Vector(0, 0, 0),FreeCAD.Vector(1, 0, 0), 360)
                self._obj.Placement = self._placement
            except Part.OCCError:
                _err(translate('Rocket', "Body tube parameters produce an invalid shape"))
                return
        else:
            _err(translate('Rocket', "Body tube parameters produce an invalid shape"))
