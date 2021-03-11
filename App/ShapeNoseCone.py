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
"""Class for drawing nose cones"""

__title__ = "FreeCAD Nose Cones"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"
    
from App.ShapeComponent import ShapeComponent
from App.Constants import FEATURE_NOSE_CONE

from App.NoseConeShapeHandler import NoseConeShapeHandler
from App.NoseEllipseShapeHandler import NoseEllipseShapeHandler
from App.NoseHaackShapeHandler import NoseHaackShapeHandler
from App.NoseOgiveShapeHandler import NoseOgiveShapeHandler
from App.NoseParabolicShapeHandler import NoseParabolicShapeHandler
from App.NosePowerShapeHandler import NosePowerShapeHandler

from App.Constants import TYPE_CONE, TYPE_ELLIPTICAL, TYPE_HAACK, TYPE_OGIVE, TYPE_VON_KARMAN, TYPE_PARABOLA, TYPE_PARABOLIC, TYPE_POWER
from App.Constants import STYLE_CAPPED, STYLE_HOLLOW, STYLE_SOLID

from App.Utilities import _wrn

from DraftTools import translate

def _migrate_from_1_0(obj):
    _wrn("Nose cone migrating object from 1.0")

    old = {}
    old["Radius"] = obj.Radius
    old["ShoulderRadius"] = obj.ShoulderRadius

    obj.removeProperty("Radius")
    obj.removeProperty("ShoulderRadius")

    ShapeNoseCone(obj)

    obj.Diameter = 2.0 * old["Radius"]
    obj.ShoulderDiameter = 2.0 * old["ShoulderRadius"]

def _migrate_from_2_0(obj):
    _wrn("Nose cone migrating object from 2.0")

    # Object with new properties
    ShapeNoseCone(obj)

class ShapeNoseCone(ShapeComponent):

    def __init__(self, obj):
        super().__init__(obj)
        self.Type = FEATURE_NOSE_CONE
        
        if not hasattr(obj, 'Length'):
            obj.addProperty('App::PropertyLength', 'Length', 'NoseCone', translate('App::Property', 'Length of the nose not including any shoulder')).Length = 67.31
        if not hasattr(obj, 'Diameter'):
            obj.addProperty('App::PropertyLength', 'Diameter', 'NoseCone', translate('App::Property', 'Diameter at the base of the nose')).Diameter = 24.79
        if not hasattr(obj, 'AutoDiameter'):
            obj.addProperty('App::PropertyBool', 'AutoDiameter', 'NoseCone', translate('App::Property', 'Automatically set the nose diameter when possible')).AutoDiameter = False
        if not hasattr(obj, 'Thickness'):
            obj.addProperty('App::PropertyLength', 'Thickness', 'NoseCone', translate('App::Property', 'Nose cone thickness')).Thickness = 1.57
        if not hasattr(obj, 'Shoulder'):
            obj.addProperty('App::PropertyBool', 'Shoulder', 'NoseCone', translate('App::Property', 'Set to true if the part includes a shoulder')).Shoulder = True
        if not hasattr(obj, 'ShoulderLength'):
            obj.addProperty('App::PropertyLength', 'ShoulderLength', 'NoseCone', translate('App::Property', 'Shoulder Length')).ShoulderLength = 24.79
        if not hasattr(obj, 'ShoulderDiameter'):
            obj.addProperty('App::PropertyLength', 'ShoulderDiameter', 'NoseCone', translate('App::Property', 'Shoulder diameter')).ShoulderDiameter = 23.62
        if not hasattr(obj, 'ShoulderAutoDiameter'):
            obj.addProperty('App::PropertyBool', 'ShoulderAutoDiameter', 'NoseCone', translate('App::Property', 'Automatically set the nose shoulder diameter when possible')).ShoulderAutoDiameter = False
        if not hasattr(obj, 'ShoulderThickness'):
            obj.addProperty('App::PropertyLength', 'ShoulderThickness', 'NoseCone', translate('App::Property', 'Shoulder thickness')).ShoulderThickness = 1.57
        if not hasattr(obj, 'Coefficient'):
            obj.addProperty('App::PropertyFloat', 'Coefficient', 'NoseCone', translate('App::Property', 'Coefficient')).Coefficient = 0.47
        if not hasattr(obj, 'Resolution'):
            obj.addProperty('App::PropertyInteger', 'Resolution', 'NoseCone', translate('App::Property', 'Resolution')).Resolution = 100

        if not hasattr(obj, 'NoseType'):
            obj.addProperty('App::PropertyEnumeration', 'NoseType', 'NoseCone', translate('App::Property', 'Nose cone type'))
        obj.NoseType = [TYPE_CONE,
                    TYPE_ELLIPTICAL,
                    TYPE_OGIVE,
                    TYPE_VON_KARMAN,
                    TYPE_PARABOLA,
                    TYPE_PARABOLIC,
                    TYPE_POWER,
                    TYPE_HAACK]
        obj.NoseType = TYPE_POWER

        if not hasattr(obj, 'NoseStyle'):
            obj.addProperty('App::PropertyEnumeration', 'NoseStyle', 'NoseCone', translate('App::Property', 'Nose cone style'))
        obj.NoseStyle = [STYLE_SOLID,
                            STYLE_HOLLOW,
                            STYLE_CAPPED]
        obj.NoseStyle = STYLE_SOLID

        if not hasattr(obj, 'Shape'):
            obj.addProperty('Part::PropertyPartShape', 'Shape', 'NoseCone', translate('App::Property', 'Shape of the nose cone'))

    def onDocumentRestored(self, obj):
        if hasattr(obj, "Radius"):
            _migrate_from_1_0(obj)
        # elif hasattr(obj, "version") and obj.version:
        #     if obj.version == "2.0":
        #         _migrate_from_2_0(obj)

    def getAxialLength(self):
        # Return the length of this component along the central axis
        return self._obj.Length

    def getForeRadius(self):
        # For placing objects on the outer part of the parent
        if self._obj.AutoDiameter:
            radius = 0.0
            previous = self.getPrevious()
            if previous is not None:
                radius = previous.Proxy.getAftRadius()
            if radius <= 0.0:
                next = self.getNext()
                if next is not None:
                    radius = next.Proxy.getForeRadius()
            if radius <= 0.0:
                radius = 24.79 # Default to BT50
            diameter = 2.0 * radius
            if self._obj.Diameter != diameter:
                self._obj.Diameter = diameter
                self.setEdited()
        return self._obj.Diameter / 2.0

    def execute(self, obj):
        shape = None
        if obj.NoseType == TYPE_CONE:
            shape = NoseConeShapeHandler(obj)
        elif obj.NoseType == TYPE_ELLIPTICAL:
            shape = NoseEllipseShapeHandler(obj)
        elif obj.NoseType == TYPE_OGIVE:
            shape = NoseOgiveShapeHandler(obj)
        elif obj.NoseType == TYPE_VON_KARMAN:
            obj.Coefficient = 0.0
            shape = NoseHaackShapeHandler(obj)
        elif obj.NoseType == TYPE_HAACK:
            shape = NoseHaackShapeHandler(obj)
        elif obj.NoseType == TYPE_PARABOLIC:
            shape = NoseParabolicShapeHandler(obj)
        elif obj.NoseType == TYPE_PARABOLA:
            obj.Coefficient = 0.5
            shape = NosePowerShapeHandler(obj)
        elif obj.NoseType == TYPE_POWER:
            shape = NosePowerShapeHandler(obj)

        if shape is not None:
            shape.draw()
