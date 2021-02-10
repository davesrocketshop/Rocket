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
"""Class for drawing bulkheads"""

__title__ = "FreeCAD Bulkhead Handler"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"
    
import FreeCAD
import FreeCADGui
import Part
import math

from App.Utilities import _err
from DraftTools import translate

class BulkheadShapeHandler():
    def __init__(self, obj):
        self._diameter = float(obj.Diameter)
        self._thickness = float(obj.Thickness)
        self._step = bool(obj.Step)
        self._stepDiameter = float(obj.StepDiameter)
        self._stepThickness = float(obj.StepThickness)
        self._holes = bool(obj.Holes)
        self._holeDiameter = float(obj.HoleDiameter)
        self._holeCenter = float(obj.HoleCenter)
        self._holeCount = int(obj.HoleCount)
        self._holeOffset = float(obj.HoleOffset)

        self._obj = obj

    def isValidShape(self):
        # Perform some general validations
        if self._diameter <= 0:
            _err(translate('Rocket', "Outer diameter must be greater than zero"))
            return False

        if self._step:
            if self._stepDiameter <= 0:
                _err(translate('Rocket', "Step diameter must be greater than zero"))
                return False
            if self._stepDiameter >= self._diameter:
                _err(translate('Rocket', "Step diameter must less than the outer diameter"))
                return False

        if self._holes:
            if self._holeDiameter <= 0:
                _err(translate('Rocket', "Hole diameter must be greater than zero"))
                return False
            if self._holeCenter + (self._holeDiameter / 2.0) >= (self._diameter / 2.0):
                _err(translate('Rocket', "Hole extends outside the outer diameter"))
                return False
            if self._step:
                if self._holeCenter + (self._holeDiameter / 2.0) >= (self._stepDiameter / 2.0):
                    _err(translate('Rocket', "Hole extends outside the step diameter"))
                    return False

        return True

    def _drawBulkhead(self):
        bulkhead = Part.makeCylinder(self._diameter / 2.0, self._thickness, FreeCAD.Vector(0,0,0), FreeCAD.Vector(1,0,0))
        if self._step:
            step = Part.makeCylinder(self._stepDiameter / 2.0, self._stepThickness, FreeCAD.Vector(self._thickness,0,0), FreeCAD.Vector(1,0,0))
            bulkhead = bulkhead.fuse(step)

        # Add any holes
        if self._holes:
            thickness = self._thickness
            if self._step:
                thickness += self._stepDiameter
            for i in range(0, self._holeCount):
                hole = Part.makeCylinder(self._holeDiameter / 2.0, thickness, FreeCAD.Vector(0,self._holeCenter,0), FreeCAD.Vector(1,0,0))

                # Rotate around the centerline
                aTrsf=FreeCAD.Matrix()
                aTrsf.rotateX(((i * 2.0 *math.pi) / self._holeCount) + math.radians(self._holeOffset) + math.pi/2.0)
                hole.transformShape(aTrsf)
                bulkhead = bulkhead.cut(hole)

        return bulkhead
        
    def draw(self):
        if not self.isValidShape():
            return

        try:
            self._obj.Shape = self._drawBulkhead()
        except (ZeroDivisionError, Part.OCCError):
            _err(translate('Rocket', "Bulkhead parameters produce an invalid shape"))
            return
