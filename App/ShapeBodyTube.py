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
"""Class for drawing body tubes"""

__title__ = "FreeCAD Body Tubes"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"
    
import FreeCAD
import FreeCADGui
import Part

from App.ShapeComponent import ShapeComponent

from App.BodyTubeShapeHandler import BodyTubeShapeHandler

def QT_TRANSLATE_NOOP(scope, text):
    return text

class ShapeBodyTube(ShapeComponent):

    def __init__(self, obj):
        super().__init__(obj)

        # Default set to a BT-50
        obj.addProperty('App::PropertyLength', 'InnerDiameter', 'BodyTube', QT_TRANSLATE_NOOP('App::Property', 'Diameter of the inside of the body tube')).InnerDiameter = 24.1
        obj.addProperty('App::PropertyLength', 'OuterDiameter', 'BodyTube', QT_TRANSLATE_NOOP('App::Property', 'Diameter of the outside of the body tube')).OuterDiameter = 24.8
        obj.addProperty('App::PropertyLength', 'Length', 'BodyTube', QT_TRANSLATE_NOOP('App::Property', 'Length of the body tube')).Length = 457.0

        obj.addProperty('Part::PropertyPartShape', 'Shape', 'BodyTube', QT_TRANSLATE_NOOP('App::Property', 'Shape of the body tube'))

    def execute(self, obj):
        shape = BodyTubeShapeHandler(obj)
        if shape is not None:
            shape.draw()
