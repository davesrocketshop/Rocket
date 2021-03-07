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

__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"
    
from App.ShapeComponent import ShapeComponent
from App.Constants import FEATURE_TRANSITION

from App.TransitionConeShapeHandler import TransitionConeShapeHandler
from App.TransitionEllipseShapeHandler import TransitionEllipseShapeHandler
from App.TransitionHaackShapeHandler import TransitionHaackShapeHandler
from App.TransitionOgiveShapeHandler import TransitionOgiveShapeHandler
from App.TransitionParabolicShapeHandler import TransitionParabolicShapeHandler
from App.TransitionPowerShapeHandler import TransitionPowerShapeHandler

from App.Constants import TYPE_CONE, TYPE_ELLIPTICAL, TYPE_HAACK, TYPE_OGIVE, TYPE_VON_KARMAN, TYPE_PARABOLA, TYPE_PARABOLIC, TYPE_POWER
from App.Constants import STYLE_CAPPED, STYLE_HOLLOW, STYLE_SOLID, STYLE_SOLID_CORE

from App.Utilities import _wrn

from DraftTools import translate

def _migrate_from_1_0(obj):
    _wrn("Transition migrating object from 1.0")

    old = {}
    old["ForeRadius"] = obj.ForeRadius
    old["AftRadius"] = obj.AftRadius
    old["CoreRadius"] = obj.CoreRadius
    old["ForeShoulderRadius"] = obj.ForeShoulderRadius
    old["AftShoulderRadius"] = obj.AftShoulderRadius

    obj.removeProperty("ForeRadius")
    obj.removeProperty("AftRadius")
    obj.removeProperty("CoreRadius")
    obj.removeProperty("ForeShoulderRadius")
    obj.removeProperty("AftShoulderRadius")

    ShapeTransition(obj)

    obj.ForeDiameter = 2.0 * old["ForeRadius"]
    obj.AftDiameter = 2.0 * old["AftRadius"]
    obj.CoreDiameter = 2.0 * old["CoreRadius"]
    obj.ForeShoulderDiameter = 2.0 * old["ForeShoulderRadius"]
    obj.AftShoulderDiameter = 2.0 * old["AftShoulderRadius"]

def _migrate_from_2_0(obj):
    _wrn("Transition migrating object from 2.0")

    # Object with new properties
    ShapeTransition(obj)

class ShapeTransition(ShapeComponent):

    def __init__(self, obj):
        super().__init__(obj)
        self.Type = FEATURE_TRANSITION

        if not hasattr(obj, 'Length'):
            obj.addProperty('App::PropertyLength', 'Length', 'Transition', translate('App::Property', 'Length of the transition not including any shoulder')).Length = 60.0
        if not hasattr(obj, 'ForeDiameter'):
            obj.addProperty('App::PropertyLength', 'ForeDiameter', 'Transition', translate('App::Property', 'Diameter at the front of the transition')).ForeDiameter = 20.0
        if not hasattr(obj, 'AftDiameter'):
            obj.addProperty('App::PropertyLength', 'AftDiameter', 'Transition', translate('App::Property', 'Diameter at the base of the transition')).AftDiameter = 40.0
        if not hasattr(obj, 'CoreDiameter'):
            obj.addProperty('App::PropertyLength', 'CoreDiameter', 'Transition', translate('App::Property', 'Diameter of the transition core')).CoreDiameter = 10.0
        if not hasattr(obj, 'Thickness'):
            obj.addProperty('App::PropertyLength', 'Thickness', 'Transition', translate('App::Property', 'Transition thickness')).Thickness = 2.0
        if not hasattr(obj, 'Clipped'):
            obj.addProperty('App::PropertyBool', 'Clipped', 'Transition', translate('App::Property', 'If the transition is not clipped, then the profile is extended at the center by the corresponding radius')).Clipped = True
        if not hasattr(obj, 'ForeShoulder'):
            obj.addProperty('App::PropertyBool', 'ForeShoulder', 'Transition', translate('App::Property', 'Set to true if the part includes a forward shoulder')).ForeShoulder = False
        if not hasattr(obj, 'ForeShoulderLength'):
            obj.addProperty('App::PropertyLength', 'ForeShoulderLength', 'Transition', translate('App::Property', 'Forward Shoulder Length')).ForeShoulderLength = 10.0
        if not hasattr(obj, 'ForeShoulderDiameter'):
            obj.addProperty('App::PropertyLength', 'ForeShoulderDiameter', 'Transition', translate('App::Property', 'Forward Shoulder diameter')).ForeShoulderDiameter = 16.0
        if not hasattr(obj, 'ForeShoulderThickness'):
            obj.addProperty('App::PropertyLength', 'ForeShoulderThickness', 'Transition', translate('App::Property', 'Forward Shoulder thickness')).ForeShoulderThickness = 2.0
        if not hasattr(obj, 'AftShoulder'):
            obj.addProperty('App::PropertyBool', 'AftShoulder', 'Transition', translate('App::Property', 'Set to true if the part includes an aft shoulder')).ForeShoulder = False
        if not hasattr(obj, 'AftShoulderLength'):
            obj.addProperty('App::PropertyLength', 'AftShoulderLength', 'Transition', translate('App::Property', 'Aft Shoulder Length')).AftShoulderLength = 10.0
        if not hasattr(obj, 'AftShoulderDiameter'):
            obj.addProperty('App::PropertyLength', 'AftShoulderDiameter', 'Transition', translate('App::Property', 'Aft Shoulder diameter')).AftShoulderDiameter = 36.0
        if not hasattr(obj, 'AftShoulderThickness'):
            obj.addProperty('App::PropertyLength', 'AftShoulderThickness', 'Transition', translate('App::Property', 'Aft Shoulder thickness')).AftShoulderThickness = 2.0
        if not hasattr(obj, 'Coefficient'):
            obj.addProperty('App::PropertyFloat', 'Coefficient', 'Transition', translate('App::Property', 'Coefficient')).Coefficient = 0.0
        if not hasattr(obj, 'Resolution'):
            obj.addProperty('App::PropertyInteger', 'Resolution', 'Transition', translate('App::Property', 'Resolution')).Resolution = 100

        if not hasattr(obj, 'TransitionType'):
            obj.addProperty('App::PropertyEnumeration', 'TransitionType', 'Transition', translate('App::Property', 'Transition type'))
        obj.TransitionType = [TYPE_CONE,
                    TYPE_ELLIPTICAL,
                    TYPE_OGIVE,
                    TYPE_VON_KARMAN,
                    TYPE_PARABOLA,
                    TYPE_PARABOLIC,
                    TYPE_POWER,
                    TYPE_HAACK]
        obj.TransitionType = TYPE_CONE

        if not hasattr(obj, 'TransitionStyle'):
            obj.addProperty('App::PropertyEnumeration', 'TransitionStyle', 'Transition', translate('App::Property', 'Transition style'))
        obj.TransitionStyle = [STYLE_SOLID,
                            STYLE_SOLID_CORE,
                            STYLE_HOLLOW,
                            STYLE_CAPPED]
        obj.TransitionStyle = STYLE_SOLID

        if not hasattr(obj, 'Shape'):
            obj.addProperty('Part::PropertyPartShape', 'Shape', 'Transition', translate('App::Property', 'Shape of the transition'))

    def onDocumentRestored(self, obj):
        if hasattr(obj, "ForeRadius"):
            _migrate_from_1_0(obj)
        # elif hasattr(obj, "version") and obj.version:
        #     if obj.version == "2.0":
        #         _migrate_from_2_0(obj)

    def getAxialLength(self):
        # Return the length of this component along the central axis
        return self._obj.Length

    def execute(self, obj):
        shape = None
        if obj.TransitionType == TYPE_CONE:
            shape = TransitionConeShapeHandler(obj)
        elif obj.TransitionType == TYPE_ELLIPTICAL:
            shape = TransitionEllipseShapeHandler(obj)
        elif obj.TransitionType == TYPE_OGIVE:
            shape = TransitionOgiveShapeHandler(obj)
        elif obj.TransitionType == TYPE_VON_KARMAN:
            obj.Coefficient = 0.0
            shape = TransitionHaackShapeHandler(obj)
        elif obj.TransitionType == TYPE_HAACK:
            shape = TransitionHaackShapeHandler(obj)
        elif obj.TransitionType == TYPE_PARABOLIC:
            shape = TransitionParabolicShapeHandler(obj)
        elif obj.TransitionType == TYPE_PARABOLA:
            obj.Coefficient = 0.5
            shape = TransitionPowerShapeHandler(obj)
        elif obj.TransitionType == TYPE_POWER:
            shape = TransitionPowerShapeHandler(obj)

        if shape is not None:
            shape.draw()
