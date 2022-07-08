# ***************************************************************************
# *   Copyright (c) 2021 David Carter <dcarter@davidcarter.ca>              *
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

from App.FinTrapezoidShapeHandler import FinTrapezoidShapeHandler

class FinCanTrapezoidShapeHandler(FinTrapezoidShapeHandler):

    def __init__(self, obj):
        super().__init__(obj)

    def isValidShape(self):
        # Add error checking here

        return True

    def _drawFinCan(self):
        # First make the can
        point = FreeCAD.Vector((self._obj.RootChord - self._obj.Length + self._obj.LeadingEdgeOffset),0,0)
        direction = FreeCAD.Vector(1,0,0)
        radius = self._obj.InnerDiameter / 2.0
        outerRadius = radius + self._obj.Thickness
        outer = Part.makeCylinder(outerRadius, self._obj.Length, point, direction)
        inner = Part.makeCylinder(radius, self._obj.Length, point, direction)
        can = outer.cut(inner)

        fins = self._drawFinSet()
        finCan = Part.makeCompound([can, fins])

        return Part.makeCompound(finCan)

    def draw(self):
        
        if not self.isValidShape():
            return

        try:
            self._obj.Shape = self._drawFinCan()

            self._obj.Placement = self._placement

        except (ZeroDivisionError, Part.OCCError):
            _err(translate('Rocket', "Fin can parameters produce an invalid shape"))
            return
