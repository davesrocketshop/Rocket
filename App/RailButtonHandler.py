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
"""Class for drawing rail buttons"""

__title__ = "FreeCAD Rail Button Handler"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"
    
import FreeCAD
import Part
import math

from App.Utilities import _err
from DraftTools import translate

class RailButtonShapeHandler():
    def __init__(self, obj):

        # This gets changed when redrawn so it's very important to save a copy
        self._placement = obj.Placement

        self._outerDiameter = float(obj.OuterDiameter)
        self._innerDiameter = float(obj.InnerDiameter)
        self._outerThickness = float(obj.OuterThickness)
        self._innerThickness = float(obj.InnerThickness)
        self._thickness = float(obj.Thickness)
        self._length = float(obj.Length)

        self._obj = obj

    def isValidShape(self):
        # Perform some general validations
        # if self._diameter <= 0:
        #     _err(translate('Rocket', "Outer diameter must be greater than zero"))
        #     return False

        # if self._step:
        #     if self._stepDiameter <= 0:
        #         _err(translate('Rocket', "Step diameter must be greater than zero"))
        #         return False
        #     if self._stepDiameter >= self._diameter:
        #         _err(translate('Rocket', "Step diameter must less than the outer diameter"))
        #         return False

        # if self._holes:
        #     if self._holeDiameter <= 0:
        #         _err(translate('Rocket', "Hole diameter must be greater than zero"))
        #         return False
        #     if self._holeCenter + (self._holeDiameter / 2.0) >= (self._diameter / 2.0):
        #         _err(translate('Rocket', "Hole extends outside the outer diameter"))
        #         return False
        #     if self._step:
        #         if self._holeCenter + (self._holeDiameter / 2.0) >= (self._stepDiameter / 2.0):
        #             _err(translate('Rocket', "Hole extends outside the step diameter"))
        #             return False

        return True

    def _drawButton(self):
        # For now, only round buttons
        spool = Part.makeCylinder(self._innerDiameter / 2.0, self._thickness, FreeCAD.Vector(0,0,0), FreeCAD.Vector(1,0,0))

        spoolTop = Part.makeCylinder(self._outerDiameter / 2.0, self._outerThickness, FreeCAD.Vector(self._thickness - self._outerThickness,0,0), FreeCAD.Vector(1,0,0))
        spool = spool.fuse(spoolTop)

        spoolBottom = Part.makeCylinder(self._outerDiameter / 2.0, self._thickness - self._outerThickness, FreeCAD.Vector(0,0,0), FreeCAD.Vector(1,0,0))
        spool = spool.fuse(spoolBottom)

        return spool
        
    def draw(self):
        if not self.isValidShape():
            return

        try:
            self._obj.Shape = self._drawButton()
            self._obj.Placement = self._placement
        except (ZeroDivisionError, Part.OCCError):
            _err(translate('Rocket', "Rail button parameters produce an invalid shape"))
            return
