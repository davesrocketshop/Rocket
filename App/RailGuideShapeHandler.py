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
"""Class for drawing launch guides"""

__title__ = "FreeCAD Launch Guide Handler"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"
    
import FreeCAD
import Part

# from App.Utilities import _err
# from DraftTools import translate

class RailGuideShapeHandler():
    def __init__(self, obj):

        # This gets changed when redrawn so it's very important to save a copy
        self._placement = obj.Placement

        self._topWidth = float(obj.TopWidth)
        self._middleWidth = float(obj.MiddleWidth)
        self._baseWidth = float(obj.BaseWidth)
        self._topThickness = float(obj.TopThickness)
        self._bottomThickness = float(obj.BottomThickness)
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

    def _drawGuide(self):
        # Essentially creating an I beam
        # guide = Part.makeCylinder(self._middleWidth / 2.0, self._thickness, FreeCAD.Vector(0,0,0), FreeCAD.Vector(0,0,1))
        guide = Part.makeBox(self._length, self._middleWidth, self._thickness, FreeCAD.Vector(0,-self._middleWidth / 2.0,0), FreeCAD.Vector(0,0,1))

        # guideTop = Part.makeCylinder(self._topWidth / 2.0, self._topThickness, FreeCAD.Vector(0,0,self._thickness - self._topThickness), FreeCAD.Vector(0,0,1))
        guideTop = Part.makeBox(self._length, self._topWidth, self._topThickness, FreeCAD.Vector(0,-self._topWidth / 2.0,self._thickness - self._topThickness), FreeCAD.Vector(0,0,1))
        guide = guide.fuse(guideTop)

        # guideBottom = Part.makeCylinder(self._topWidth / 2.0, self._thickness - self._topThickness, FreeCAD.Vector(0,0,0), FreeCAD.Vector(1,0,0))
        # guideBottom = Part.makeCylinder(self._topWidth / 2.0, self._bottomThickness, FreeCAD.Vector(0,0,0), FreeCAD.Vector(0,0,1))
        guideBottom = Part.makeBox(self._length, self._baseWidth, self._bottomThickness, FreeCAD.Vector(0,-self._baseWidth / 2.0,0), FreeCAD.Vector(0,0,1))
        guide = guide.fuse(guideBottom)

        return guide
        
    def draw(self):
        if not self.isValidShape():
            return

        try:
            self._obj.Shape = self._drawGuide()
            self._obj.Placement = self._placement
        except (ZeroDivisionError, Part.OCCError):
            _err(translate('Rocket', "Launch Guide parameters produce an invalid shape"))
            return
