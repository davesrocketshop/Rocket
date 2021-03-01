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
"""Class for bulkheads"""

__title__ = "FreeCAD Bulkheads"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"
    
from App.ShapeComponent import ShapeLocation

from App.BulkheadShapeHandler import BulkheadShapeHandler

def QT_TRANSLATE_NOOP(scope, text):
    return text

class ShapeBulkhead(ShapeLocation):

    def __init__(self, obj):
        super().__init__(obj)

        obj.addProperty('App::PropertyLength', 'Diameter', 'Bulkhead', QT_TRANSLATE_NOOP('App::Property', 'Outer diameter of the bulkhead')).Diameter = 25.0
        obj.addProperty('App::PropertyLength', 'Thickness', 'Bulkhead', QT_TRANSLATE_NOOP('App::Property', 'Thickness of the bulkhead without any inner step')).Thickness = 2.0

        obj.addProperty('App::PropertyBool', 'Step', 'Bulkhead', QT_TRANSLATE_NOOP('App::Property', 'Bulkheads may have a step that fits a smaller diameter')).Step = False
        obj.addProperty('App::PropertyLength', 'StepDiameter', 'Bulkhead', QT_TRANSLATE_NOOP('App::Property', 'Outer diameter of the step')).StepDiameter = 21.0
        obj.addProperty('App::PropertyLength', 'StepThickness', 'Bulkhead', QT_TRANSLATE_NOOP('App::Property', 'Thickness of the step')).StepThickness = 2.0

        obj.addProperty('App::PropertyBool', 'Holes', 'Bulkhead', QT_TRANSLATE_NOOP('App::Property', 'Bulkheads may have holes for attaching eyebolts or retainers')).Holes = False
        obj.addProperty('App::PropertyLength', 'HoleDiameter', 'Bulkhead', QT_TRANSLATE_NOOP('App::Property', 'Hole diameter')).HoleDiameter = 5.0
        obj.addProperty('App::PropertyLength', 'HoleCenter', 'Bulkhead', QT_TRANSLATE_NOOP('App::Property', 'Distance from the center of the bulkhead to the center of the hole')).HoleCenter = 6.25
        obj.addProperty('App::PropertyInteger', 'HoleCount', 'Bulkhead', QT_TRANSLATE_NOOP('App::Property', 'Number of holes in a radial pattern')).HoleCount = 1
        obj.addProperty('App::PropertyAngle', 'HoleOffset', 'Bulkhead', QT_TRANSLATE_NOOP('App::Property', 'Outer diameter of the bulkhead')).HoleOffset = 0

        obj.addProperty('Part::PropertyPartShape', 'Shape', 'Bulkhead', QT_TRANSLATE_NOOP('App::Property', 'Shape of the bulkhead'))

    def getAxialLength(self):
        # Return the length of this component along the central axis
        return self._obj.Thickness

    def execute(self, obj):
        shape = BulkheadShapeHandler(obj)
        if shape is not None:
            shape.draw()
