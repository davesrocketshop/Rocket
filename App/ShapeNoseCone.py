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
    
from App.ShapeBase import TRACE_POSITION, TRACE_EXECUTION
from App.ShapeComponent import ShapeComponent
from App.Constants import FEATURE_NOSE_CONE

from App.NoseConeShapeHandler import NoseConeShapeHandler
from App.NoseBluntedConeShapeHandler import NoseBluntedConeShapeHandler
from App.NoseEllipseShapeHandler import NoseEllipseShapeHandler
from App.NoseHaackShapeHandler import NoseHaackShapeHandler
from App.NoseOgiveShapeHandler import NoseOgiveShapeHandler
from App.NoseBluntedOgiveShapeHandler import NoseBluntedOgiveShapeHandler
from App.NoseSecantOgiveShapeHandler import NoseSecantOgiveShapeHandler
from App.NoseParabolicShapeHandler import NoseParabolicShapeHandler
from App.NosePowerShapeHandler import NosePowerShapeHandler

from App.Constants import TYPE_CONE, TYPE_BLUNTED_CONE, TYPE_SPHERICAL, TYPE_ELLIPTICAL, TYPE_HAACK, TYPE_OGIVE, TYPE_BLUNTED_OGIVE, TYPE_SECANT_OGIVE, TYPE_VON_KARMAN, TYPE_PARABOLA, TYPE_PARABOLIC, TYPE_POWER
from App.Constants import STYLE_CAPPED, STYLE_HOLLOW, STYLE_SOLID
from App.Constants import STYLE_CAP_SOLID, STYLE_CAP_BAR, STYLE_CAP_CROSS

from App.Utilities import _wrn

from DraftTools import translate

def _migrate_from_1_0(obj):
    _wrn("Nose cone migrating object from 1.0")

    old = {}
    old["Radius"] = obj.Radius
    old["ShoulderRadius"] = obj.ShoulderRadius
    old["NoseType"] = obj.NoseType

    obj.removeProperty("Radius")
    obj.removeProperty("ShoulderRadius")
    obj.removeProperty("NoseType")

    ShapeNoseCone(obj)

    obj.Diameter = 2.0 * old["Radius"]
    obj.ShoulderDiameter = 2.0 * old["ShoulderRadius"]
    obj.NoseType = old["NoseType"]

def _migrate_from_2_0(obj):
    _wrn("Nose cone migrating object from 2.0")

    blunted = False
    secant = False
    old = {}
    if hasattr(obj, 'BluntedRadius'):
        old["BluntedRadius"] = obj.BluntedRadius
        blunted = True
    if hasattr(obj, 'OgiveRadius'):
        old["OgiveRadius"] = obj.OgiveRadius
        secant = True
    old["NoseType"] = obj.NoseType

    obj.removeProperty("BluntedRadius")
    obj.removeProperty("OgiveRadius")
    obj.removeProperty("NoseType")

    ShapeNoseCone(obj)

    if blunted:
        obj.BluntedDiameter = 2.0 * old["BluntedRadius"]
    if secant:
        obj.OgiveDiameter = 2.0 * old["OgiveRadius"]
    obj.NoseType = old["NoseType"]

class ShapeNoseCone(ShapeComponent):

    def __init__(self, obj):
        super().__init__(obj)
        self.Type = FEATURE_NOSE_CONE
        
        if not hasattr(obj, 'CapBarWidth'):
            obj.addProperty('App::PropertyLength', 'CapBarWidth', 'NoseCone', translate('App::Property', 'Width of the nose cap bar')).CapBarWidth = 3.0
        if not hasattr(obj, 'Length'):
            obj.addProperty('App::PropertyLength', 'Length', 'NoseCone', translate('App::Property', 'Length of the nose not including any shoulder')).Length = 67.31
        if not hasattr(obj, 'BluntedDiameter'):
            obj.addProperty('App::PropertyLength', 'BluntedDiameter', 'NoseCone', translate('App::Property', 'Nose Radius for a blunted nose cone')).BluntedDiameter = 5.0
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
        if not hasattr(obj, 'OgiveDiameter'):
            obj.addProperty('App::PropertyLength', 'OgiveDiameter', 'NoseCone', translate('App::Property', 'The radius of the circle used to define a secant ogive')).OgiveDiameter = 120.0
        if not hasattr(obj, 'Resolution'):
            obj.addProperty('App::PropertyInteger', 'Resolution', 'NoseCone', translate('App::Property', 'Resolution')).Resolution = 100

        if not hasattr(obj, 'NoseType'):
            obj.addProperty('App::PropertyEnumeration', 'NoseType', 'NoseCone', translate('App::Property', 'Nose cone type'))
            obj.NoseType = [TYPE_CONE,
                        TYPE_BLUNTED_CONE,
                        TYPE_SPHERICAL,
                        TYPE_ELLIPTICAL,
                        TYPE_OGIVE,
                        TYPE_BLUNTED_OGIVE,
                        TYPE_SECANT_OGIVE,
                        TYPE_VON_KARMAN,
                        TYPE_PARABOLA,
                        TYPE_PARABOLIC,
                        TYPE_POWER,
                        TYPE_HAACK]
            obj.NoseType = TYPE_OGIVE

        if not hasattr(obj, 'NoseStyle'):
            obj.addProperty('App::PropertyEnumeration', 'NoseStyle', 'NoseCone', translate('App::Property', 'Nose cone style'))
            obj.NoseStyle = [STYLE_SOLID,
                                STYLE_HOLLOW,
                                STYLE_CAPPED]
            obj.NoseStyle = STYLE_SOLID

        if not hasattr(obj, 'CapStyle'):
            obj.addProperty('App::PropertyEnumeration', 'CapStyle', 'NoseCone', translate('App::Property', 'Nose cone cap style'))
            obj.CapStyle = [STYLE_CAP_SOLID,
                                STYLE_CAP_BAR,
                                STYLE_CAP_CROSS]
            obj.CapStyle = STYLE_CAP_SOLID

        if not hasattr(obj, 'Shape'):
            obj.addProperty('Part::PropertyPartShape', 'Shape', 'NoseCone', translate('App::Property', 'Shape of the nose cone'))

    def onDocumentRestored(self, obj):
        super().onDocumentRestored(obj)
        
        if hasattr(obj, "Radius"):
            _migrate_from_1_0(obj)
        if hasattr(obj.Proxy, "version") and obj.Proxy.version:
            if obj.Proxy.version in ["2.0", "2.1"]:
                _migrate_from_2_0(obj)

    def getAxialLength(self):
        if TRACE_POSITION:
            print("P: ShapeNoseCone::getAxialLength(%s)" % (self._obj.Label))

        # Return the length of this component along the central axis
        return self._obj.Length

    def getMaxForwardPosition(self):
        if TRACE_POSITION:
            print("P: ShapeNoseCone::getMaxForwardPosition(%s)" % (self._obj.Label))

        return float(self._obj.Length) + float(self._obj.Placement.Base.x)

    def getForeRadius(self):
        if TRACE_POSITION:
            print("P: ShapeNoseCone::getForeRadius(%s)" % (self._obj.Label))

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
        if TRACE_EXECUTION:
            print("E: ShapeNoseCone::execute(%s)" % (self._obj.Label))

        shape = None
        if obj.NoseType == TYPE_CONE:
            shape = NoseConeShapeHandler(obj)
        elif obj.NoseType == TYPE_BLUNTED_CONE:
            shape = NoseBluntedConeShapeHandler(obj)
        elif obj.NoseType == TYPE_SPHERICAL:
            shape = NoseEllipseShapeHandler(obj)
        elif obj.NoseType == TYPE_ELLIPTICAL:
            shape = NoseEllipseShapeHandler(obj)
        elif obj.NoseType == TYPE_OGIVE:
            shape = NoseOgiveShapeHandler(obj)
        elif obj.NoseType == TYPE_BLUNTED_OGIVE:
            shape = NoseBluntedOgiveShapeHandler(obj)
        elif obj.NoseType == TYPE_SECANT_OGIVE:
            shape = NoseSecantOgiveShapeHandler(obj)
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
