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

import Part

from App.ShapeComponent import ShapeComponent

from App.BodyTubeShapeHandler import BodyTubeShapeHandler

def QT_TRANSLATE_NOOP(scope, text):
    return text

class ShapeFinset(ShapeComponent):

    def __init__(self, obj):
        super().__init__(obj)

        if not hasattr(obj,"InnerDiameter"):
            obj.addProperty('App::PropertyInteger', 'FinCount', 'FinSet', QT_TRANSLATE_NOOP('App::Property', 'Number of fins in a radial pattern')).FinCount = 3
        # Default set to a BT-50
        if not hasattr(obj,"Diameter"):
            obj.addProperty('App::PropertyLength', 'Diameter', 'FinSet', QT_TRANSLATE_NOOP('App::Property', 'Diameter of the fin base')).InnerDiameter = 24.8
        if not hasattr(obj,"Offset"):
            obj.addProperty('App::PropertyAngle', 'Offset', 'FinSet', QT_TRANSLATE_NOOP('App::Property', 'Initial fin offset from vertical')).Offset = 0
        if not hasattr(obj,"Spacing"):
            obj.addProperty('App::PropertyAngle', 'Spacing', 'FinSet', QT_TRANSLATE_NOOP('App::Property', 'Angle between consecutive fins')).Spacing = 120

        if not hasattr(obj,"Shape"):
            obj.addProperty('Part::PropertyPartShape', 'Shape', 'BodyTube', QT_TRANSLATE_NOOP('App::Property', 'Shape of the fin can'))

        if not hasattr(obj,"Group"):
            obj.addExtension("App::GroupExtensionPython")

    def execute(self, obj):
        shape = FinSetShapeHandler(obj)
        if shape is not None:
            shape.draw()
