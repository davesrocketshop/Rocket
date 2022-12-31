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

import FreeCAD
    
from App.ShapeBase import TRACE_POSITION, TRACE_EXECUTION
from App.SymmetricComponent import SymmetricComponent
from App.Constants import FEATURE_TRANSITION

from App.ShapeHandlers.TransitionConeShapeHandler import TransitionConeShapeHandler
from App.ShapeHandlers.TransitionEllipseShapeHandler import TransitionEllipseShapeHandler
from App.ShapeHandlers.TransitionHaackShapeHandler import TransitionHaackShapeHandler
from App.ShapeHandlers.TransitionOgiveShapeHandler import TransitionOgiveShapeHandler
from App.ShapeHandlers.TransitionParabolicShapeHandler import TransitionParabolicShapeHandler
from App.ShapeHandlers.TransitionPowerShapeHandler import TransitionPowerShapeHandler

from App.Constants import TYPE_CONE, TYPE_ELLIPTICAL, TYPE_HAACK, TYPE_OGIVE, TYPE_VON_KARMAN, TYPE_PARABOLA, TYPE_PARABOLIC, TYPE_POWER
from App.Constants import STYLE_CAPPED, STYLE_HOLLOW, STYLE_SOLID, STYLE_SOLID_CORE
from App.Constants import STYLE_CAP_SOLID, STYLE_CAP_BAR, STYLE_CAP_CROSS

from App.events.ComponentChangeEvent import ComponentChangeEvent

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

    FeatureTransition(obj)

    obj.ForeDiameter = 2.0 * old["ForeRadius"]
    obj.AftDiameter = 2.0 * old["AftRadius"]
    obj.CoreDiameter = 2.0 * old["CoreRadius"]
    obj.ForeShoulderDiameter = 2.0 * old["ForeShoulderRadius"]
    obj.AftShoulderDiameter = 2.0 * old["AftShoulderRadius"]

def _migrate_from_2_0(obj):
    _wrn("Transition migrating object from 2.0")

    # Object with new properties
    FeatureTransition(obj)

class FeatureTransition(SymmetricComponent):

    def __init__(self, obj):
        super().__init__(obj)
        self.Type = FEATURE_TRANSITION

        # if not hasattr(obj, 'Length'):
        #     obj.addProperty('App::PropertyLength', 'Length', 'Transition', translate('App::Property', 'Length of the transition not including any shoulder')).Length = 60.0
        if not hasattr(obj, 'ForeDiameter'):
            obj.addProperty('App::PropertyLength', 'ForeDiameter', 'Transition', translate('App::Property', 'Diameter at the front of the transition')).ForeDiameter = 20.0
        if not hasattr(obj, 'ForeAutoDiameter'):
            obj.addProperty('App::PropertyBool', 'ForeAutoDiameter', 'NoseCone', translate('App::Property', 'Automatically set the forward diameter when possible')).ForeAutoDiameter = False
        if not hasattr(obj, 'AftDiameter'):
            obj.addProperty('App::PropertyLength', 'AftDiameter', 'Transition', translate('App::Property', 'Diameter at the base of the transition')).AftDiameter = 40.0
        if not hasattr(obj, 'AftAutoDiameter'):
            obj.addProperty('App::PropertyBool', 'AftAutoDiameter', 'NoseCone', translate('App::Property', 'Automatically set the aft diameter when possible')).AftAutoDiameter = False
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
        if not hasattr(obj, 'ForeCapBarWidth'):
            obj.addProperty('App::PropertyLength', 'ForeCapBarWidth', 'Transition', translate('App::Property', 'Width of the foreward cap bar')).ForeCapBarWidth = 3.0
        if not hasattr(obj, 'AftCapBarWidth'):
            obj.addProperty('App::PropertyLength', 'AftCapBarWidth', 'Transition', translate('App::Property', 'Width of the aft cap bar')).AftCapBarWidth = 3.0

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

        if not hasattr(obj, 'ForeCapStyle'):
            obj.addProperty('App::PropertyEnumeration', 'ForeCapStyle', 'Transition', translate('App::Property', 'Foreward cap style'))
            obj.ForeCapStyle = [STYLE_CAP_SOLID,
                                STYLE_CAP_BAR,
                                STYLE_CAP_CROSS]
            obj.ForeCapStyle = STYLE_CAP_SOLID

        if not hasattr(obj, 'AftCapStyle'):
            obj.addProperty('App::PropertyEnumeration', 'AftCapStyle', 'Transition', translate('App::Property', 'Aft cap style'))
            obj.AftCapStyle = [STYLE_CAP_SOLID,
                                STYLE_CAP_BAR,
                                STYLE_CAP_CROSS]
            obj.AftCapStyle = STYLE_CAP_SOLID

        if not hasattr(obj, 'Shape'):
            obj.addProperty('Part::PropertyPartShape', 'Shape', 'Transition', translate('App::Property', 'Shape of the transition'))

        # Set default values
        obj.Length = 60.0

    def onDocumentRestored(self, obj):
        if hasattr(obj, "ForeRadius"):
            _migrate_from_1_0(obj)
        # elif hasattr(obj, "version") and obj.version:
        #     if obj.version == "2.0":
        #         _migrate_from_2_0(obj)
        else:
            # Update properties
            FeatureTransition(obj)
            FreeCAD.ActiveDocument.recompute()

    # def getLength(self):
    #     if TRACE_POSITION:
    #         print("P: FeatureTransition::getLength(%s)" % (self._obj.Label))

    #     # Return the length of this component along the central axis
    #     return self._obj.Length

    def getForeRadius(self):
        return self.getForeDiameter() / 2.0

    def getForeDiameter(self):
        if self.isForeDiameterAutomatic():
            # Get the automatic radius from the front
            d = -1
            c = self.getPreviousSymmetricComponent()
            if c is not None:
                d = c.getFrontAutoRadius()
            if d < 0:
                d = SymmetricComponent.DEFAULT_RADIUS
            return d

        return self._obj.ForeDiameter

    """
        Return the fore radius that was manually entered, so not the value that the component received from automatic
        fore radius.
    """
    def getForeRadiusNoAutomatic(self):
        return self._obj.ForeDiameter / 2.0

    def setForeRadius(self, radius):
        for listener in self._configListeners:
            if isinstance(listener, FeatureTransition):
                listener.setForeRadius(radius)

        r = self._obj.ForeDiameter / 2.0
        if r == radius and not self._obj.ForeAutoDiameter:
            return

        self._obj.ForeAutoDiameter = False
        self._obj.ForeDiameter = 2.0 * max(radius, 0)

        foreRadius = float(self._obj.ForeDiameter) / 2.0
        aftRadius = float(self._obj.AftDiameter) / 2.0
        if self._obj.Thickness > foreRadius and self._obj.Thickness > aftRadius:
            self._obj.Thickness = max(foreRadius, aftRadius);

        self.clearPreset()
        self.fireComponentChangeEvent(ComponentChangeEvent.BOTH_CHANGE);

    def isForeRadiusAutomatic(self):
        return self._obj.ForeAutoDiameter

    def setForeRadiusAutomatic(self, auto):
        for listener in self._configListeners:
            if isinstance(listener, FeatureTransition):
                listener.setForeRadiusAutomatic(auto)

        if self._obj.ForeAutoDiameter == auto:
            return

        self._obj.ForeAutoDiameter = auto

        # clearPreset();
        self.fireComponentChangeEvent(ComponentChangeEvent.BOTH_CHANGE)

    def getAftRadius(self):
        return self.getAftDiameter() / 2.0

    def getAftDiameter(self):

        if self.isAftDiameterAutomatic():
                # Return the auto radius from the rear
                d = -1
                c = self.getNextSymmetricComponent()
                if c is not None:
                    d = c.getRearAutoRadius()

                if d < 0:
                    d = SymmetricComponent.DEFAULT_RADIUS
                return d

        return self._obj.AftDiameter

    """
        Return the aft radius that was manually entered, so not the value that the component received from automatic
        aft radius.
    """
    def getAftRadiusNoAutomatic(self):
        return self._obj.AftDiameter / 2.0

    def setAftRadius(self, radius):
        for listener in self._configListeners:
            if isinstance(listener, FeatureTransition):
                listener.setAftRadius(radius)

        r = self._obj.AftDiameter / 2.0
        if r == radius and not self.isAftRadiusAutomatic():
            return

        self._obj.AftAutoDiameter = False
        self._obj.AftDiameter = 2.0 * max(radius, 0)

        foreRadius = float(self._obj.ForeDiameter) / 2.0
        aftRadius = float(self._obj.AftDiameter) / 2.0
        if self._obj.Thickness > foreRadius and self._obj.Thickness > aftRadius:
            self._obj.Thickness = max(foreRadius, aftRadius);

        self.clearPreset();
        self.fireComponentChangeEvent(ComponentChangeEvent.BOTH_CHANGE)

    def isAftRadiusAutomatic(self):
        return self._obj.AftAutoDiameter

    def isAftDiameterAutomatic(self):
        return self._obj.AftAutoDiameter

    def setAftRadiusAutomatic(self, auto):
        self.setAftDiameterAutomatic(auto)

    def setAftDiameterAutomatic(self, auto):
        for listener in self._configListeners:
            if isinstance(listener, FeatureTransition):
                listener.setAftDiameterAutomatic(auto)

        if self._obj.AftAutoDiameter == auto:
            return

        self._obj.AftAutoDiameter = auto

        self.clearPreset()
        self.fireComponentChangeEvent(ComponentChangeEvent.BOTH_CHANGE)

    def getFrontAutoRadius(self):
        if self.isAftRadiusAutomatic():
            return -1
        return self.getAftRadius()

    def getFrontAutoDiameter(self):
        if self.isAftDiameterAutomatic():
            return -1
        return self.getAftDiameter()

    def getRearAutoRadius(self):
        if self.isForeRadiusAutomatic():
            return -1
        return self.getForeRadius()

    def getRearAutoDiameter(self):
        if self.isForeDiameterAutomatic():
            return -1
        return self.getForeDiameter()

    def usesPreviousCompAutomatic(self):
        return self.isForeRadiusAutomatic()

    def usesNextCompAutomatic(self):
        return self.isAftRadiusAutomatic()

    """
        Return the radius at point x of the transition.
    """
    def getRadius(self, x):
        return 0.0

    def getComponentBounds(self):
        bounds = super().getComponentBounds()
        if self._obj.ForeShoulderLength > 0.001:
            self.addBound(bounds, self._obj.Length + self._obj.ForeShoulderLength, self._obj.ForeShoulderDiameter / 2.0)
        if self._obj.AftShoulderLength > 0.001:
            self.addBound(bounds, -self._obj.AftShoulderLength, self._obj.AftShoulderDiameter / 2.0)
        return bounds

    def execute(self, obj):
        if TRACE_EXECUTION:
            print("E: FeatureTransition::execute(%s)" % (self._obj.Label))

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
