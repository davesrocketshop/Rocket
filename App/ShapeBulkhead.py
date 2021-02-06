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
    
from App.BulkheadShapeHandler import BulkheadShapeHandler

class ShapeBulkhead:

    def __init__(self, obj):

        obj.addProperty('App::PropertyLength', 'Diameter', 'Bulkhead', 'Outer diameter of the bulkhead').Diameter = 25.0
        obj.addProperty('App::PropertyLength', 'Thickness', 'Bulkhead', 'Thickness of the bulkhead without any inner step').Thickness = 2.0

        obj.addProperty('App::PropertyBool', 'Step', 'Bulkhead', 'Bulkheads may have a step that fits a smaller diameter').Step = False
        obj.addProperty('App::PropertyLength', 'StepDiameter', 'Bulkhead', 'Outer diameter of the step').StepDiameter = 21.0
        obj.addProperty('App::PropertyLength', 'StepThickness', 'Bulkhead', 'Thickness of the step').StepThickness = 2.0

        obj.addProperty('App::PropertyBool', 'Holes', 'Bulkhead', 'Bulkheads may have holes for attaching eyebolts or retainers').Holes = False
        obj.addProperty('App::PropertyLength', 'HoleDiameter', 'Bulkhead', 'Hole diameter').HoleDiameter = 5.0
        obj.addProperty('App::PropertyLength', 'HoleCenter', 'Bulkhead', 'Distance from the center of the bulkhead to the center of the hole').HoleCenter = 6.25
        obj.addProperty('App::PropertyInteger', 'HoleCount', 'Bulkhead', 'Number of holes in a radial pattern').HoleCount = 1
        obj.addProperty('App::PropertyAngle', 'HoleOffset', 'Bulkhead', 'Outer diameter of the bulkhead').HoleOffset = 0

        obj.addProperty('Part::PropertyPartShape', 'Shape', 'Fin', 'Shape of the fin')
        obj.Proxy=self

    def execute(self, obj):
        shape = BulkheadShapeHandler(obj)
        if shape is not None:
            shape.draw()
