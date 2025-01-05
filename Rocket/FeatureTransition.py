# ***************************************************************************
# *   Copyright (c) 2021-2025 David Carter <dcarter@davidcarter.ca>         *
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

from Rocket.SymmetricComponent import SymmetricComponent
from Rocket.Constants import FEATURE_TRANSITION

from Rocket.ShapeHandlers.TransitionConeShapeHandler import TransitionConeShapeHandler
from Rocket.ShapeHandlers.TransitionEllipseShapeHandler import TransitionEllipseShapeHandler
from Rocket.ShapeHandlers.TransitionHaackShapeHandler import TransitionHaackShapeHandler
from Rocket.ShapeHandlers.TransitionOgiveShapeHandler import TransitionOgiveShapeHandler
from Rocket.ShapeHandlers.TransitionParabolicShapeHandler import TransitionParabolicShapeHandler
from Rocket.ShapeHandlers.TransitionPowerShapeHandler import TransitionPowerShapeHandler

from Rocket.Constants import TYPE_CONE, TYPE_ELLIPTICAL, TYPE_HAACK, TYPE_OGIVE, TYPE_VON_KARMAN, TYPE_PARABOLA, TYPE_PARABOLIC, TYPE_POWER
from Rocket.Constants import STYLE_CAPPED, STYLE_HOLLOW, STYLE_SOLID, STYLE_SOLID_CORE
from Rocket.Constants import STYLE_CAP_SOLID, STYLE_CAP_BAR, STYLE_CAP_CROSS

from Rocket.events.ComponentChangeEvent import ComponentChangeEvent

from Rocket.Utilities import _wrn

from DraftTools import translate

class FeatureTransition(SymmetricComponent):

    def __init__(self, obj):
        super().__init__(obj)
        self.Type = FEATURE_TRANSITION

        if not hasattr(obj, 'ForeDiameter'):
            obj.addProperty('App::PropertyLength', 'ForeDiameter', 'RocketComponent', translate('App::Property', 'Diameter at the front of the transition')).ForeDiameter = 20.0
        if not hasattr(obj, 'ForeAutoDiameter'):
            obj.addProperty('App::PropertyBool', 'ForeAutoDiameter', 'RocketComponent', translate('App::Property', 'Automatically set the forward diameter when possible')).ForeAutoDiameter = False
        if not hasattr(obj, 'AftDiameter'):
            obj.addProperty('App::PropertyLength', 'AftDiameter', 'RocketComponent', translate('App::Property', 'Diameter at the base of the transition')).AftDiameter = 40.0
        if not hasattr(obj, 'AftAutoDiameter'):
            obj.addProperty('App::PropertyBool', 'AftAutoDiameter', 'RocketComponent', translate('App::Property', 'Automatically set the aft diameter when possible')).AftAutoDiameter = False
        if not hasattr(obj, 'CoreDiameter'):
            obj.addProperty('App::PropertyLength', 'CoreDiameter', 'RocketComponent', translate('App::Property', 'Diameter of the transition core')).CoreDiameter = 10.0
        if not hasattr(obj, 'Thickness'):
            obj.addProperty('App::PropertyLength', 'Thickness', 'RocketComponent', translate('App::Property', 'Transition thickness')).Thickness = 2.0
        if not hasattr(obj, 'Clipped'):
            obj.addProperty('App::PropertyBool', 'Clipped', 'RocketComponent', translate('App::Property', 'If the transition is not clipped, then the profile is extended at the center by the corresponding radius')).Clipped = True

        if not hasattr(obj, 'ForeShoulder'):
            obj.addProperty('App::PropertyBool', 'ForeShoulder', 'RocketComponent', translate('App::Property', 'Set to true if the part includes a forward shoulder')).ForeShoulder = False #True
        if not hasattr(obj, 'ForeShoulderLength'):
            obj.addProperty('App::PropertyLength', 'ForeShoulderLength', 'RocketComponent', translate('App::Property', 'Forward Shoulder Length')).ForeShoulderLength = 25.0
        if not hasattr(obj, 'ForeShoulderDiameter'):
            obj.addProperty('App::PropertyLength', 'ForeShoulderDiameter', 'RocketComponent', translate('App::Property', 'Forward Shoulder diameter')).ForeShoulderDiameter = 16.0
        if not hasattr(obj, 'ForeShoulderAutoDiameter'):
            obj.addProperty('App::PropertyBool', 'ForeShoulderAutoDiameter', 'RocketComponent', translate('App::Property', 'Automatically set the forward transition shoulder diameter when possible')).ForeShoulderAutoDiameter = False
        if not hasattr(obj, 'ForeShoulderThickness'):
            obj.addProperty('App::PropertyLength', 'ForeShoulderThickness', 'RocketComponent', translate('App::Property', 'Forward Shoulder thickness')).ForeShoulderThickness = 2.0

        if not hasattr(obj, 'AftShoulder'):
            obj.addProperty('App::PropertyBool', 'AftShoulder', 'RocketComponent', translate('App::Property', 'Set to true if the part includes an aft shoulder')).AftShoulder = False #True
        if not hasattr(obj, 'AftShoulderLength'):
            obj.addProperty('App::PropertyLength', 'AftShoulderLength', 'RocketComponent', translate('App::Property', 'Aft Shoulder Length')).AftShoulderLength = 25.0
        if not hasattr(obj, 'AftShoulderDiameter'):
            obj.addProperty('App::PropertyLength', 'AftShoulderDiameter', 'RocketComponent', translate('App::Property', 'Aft Shoulder diameter')).AftShoulderDiameter = 36.0
        if not hasattr(obj, 'AftShoulderAutoDiameter'):
            obj.addProperty('App::PropertyBool', 'AftShoulderAutoDiameter', 'RocketComponent', translate('App::Property', 'Automatically set the aft transition shoulder diameter when possible')).AftShoulderAutoDiameter = False
        if not hasattr(obj, 'AftShoulderThickness'):
            obj.addProperty('App::PropertyLength', 'AftShoulderThickness', 'RocketComponent', translate('App::Property', 'Aft Shoulder thickness')).AftShoulderThickness = 2.0

        if not hasattr(obj, 'Coefficient'):
            obj.addProperty('App::PropertyFloat', 'Coefficient', 'RocketComponent', translate('App::Property', 'Coefficient')).Coefficient = 0.0
        if not hasattr(obj, 'Resolution'):
            obj.addProperty('App::PropertyInteger', 'Resolution', 'RocketComponent', translate('App::Property', 'Resolution')).Resolution = 100
        if not hasattr(obj, 'ForeCapBarWidth'):
            obj.addProperty('App::PropertyLength', 'ForeCapBarWidth', 'RocketComponent', translate('App::Property', 'Width of the forward cap bar')).ForeCapBarWidth = 3.0
        if not hasattr(obj, 'AftCapBarWidth'):
            obj.addProperty('App::PropertyLength', 'AftCapBarWidth', 'RocketComponent', translate('App::Property', 'Width of the aft cap bar')).AftCapBarWidth = 3.0

        if not hasattr(obj, 'TransitionType'):
            obj.addProperty('App::PropertyEnumeration', 'TransitionType', 'RocketComponent', translate('App::Property', 'Transition type'))
            obj.TransitionType = [TYPE_CONE,
                        TYPE_ELLIPTICAL,
                        TYPE_OGIVE,
                        TYPE_VON_KARMAN,
                        TYPE_PARABOLA,
                        TYPE_PARABOLIC,
                        TYPE_POWER,
                        TYPE_HAACK]
            obj.TransitionType = TYPE_CONE
        else:
            obj.TransitionType = [TYPE_CONE,
                        TYPE_ELLIPTICAL,
                        TYPE_OGIVE,
                        TYPE_VON_KARMAN,
                        TYPE_PARABOLA,
                        TYPE_PARABOLIC,
                        TYPE_POWER,
                        TYPE_HAACK]

        if not hasattr(obj, 'TransitionStyle'):
            obj.addProperty('App::PropertyEnumeration', 'TransitionStyle', 'RocketComponent', translate('App::Property', 'Transition style'))
            obj.TransitionStyle = [STYLE_SOLID,
                                STYLE_SOLID_CORE,
                                STYLE_HOLLOW,
                                STYLE_CAPPED]
            obj.TransitionStyle = STYLE_SOLID
        else:
            obj.TransitionStyle = [STYLE_SOLID,
                                STYLE_SOLID_CORE,
                                STYLE_HOLLOW,
                                STYLE_CAPPED]

        if not hasattr(obj, 'ForeCapStyle'):
            obj.addProperty('App::PropertyEnumeration', 'ForeCapStyle', 'RocketComponent', translate('App::Property', 'Forward cap style'))
            obj.ForeCapStyle = [STYLE_CAP_SOLID,
                                STYLE_CAP_BAR,
                                STYLE_CAP_CROSS]
            obj.ForeCapStyle = STYLE_CAP_SOLID
        else:
            obj.ForeCapStyle = [STYLE_CAP_SOLID,
                                STYLE_CAP_BAR,
                                STYLE_CAP_CROSS]

        if not hasattr(obj, 'AftCapStyle'):
            obj.addProperty('App::PropertyEnumeration', 'AftCapStyle', 'RocketComponent', translate('App::Property', 'Aft cap style'))
            obj.AftCapStyle = [STYLE_CAP_SOLID,
                                STYLE_CAP_BAR,
                                STYLE_CAP_CROSS]
            obj.AftCapStyle = STYLE_CAP_SOLID
        else:
            obj.AftCapStyle = [STYLE_CAP_SOLID,
                                STYLE_CAP_BAR,
                                STYLE_CAP_CROSS]

    def setDefaults(self):
        super().setDefaults()

        self._obj.Length = 60.0

    def onDocumentRestored(self, obj):
        FeatureTransition(obj)

        # Convert from the pre-1.0 material system if required
        self.convertMaterialAndAppearance(obj)

        self._obj = obj

    def update(self):
        super().update()

        # Ensure any automatic variables are set
        self.getForeDiameter()
        self.getAftDiameter()
        self.getForeShoulderDiameter()
        self.getAftShoulderDiameter()

    def getForeRadius(self):
        return self.getForeDiameter() / 2.0

    def getForeDiameter(self):
        if self.isForeDiameterAutomatic():
            # Get the automatic radius from the front
            d = -1
            c = self.getPreviousSymmetricComponent()
            if c is not None:
                d = c.getFrontAutoDiameter()
            if d < 0:
                d = SymmetricComponent.DEFAULT_RADIUS * 2.0
            self._obj.ForeDiameter = d

        return self._obj.ForeDiameter

    def getForeShoulderDiameter(self):
        if self.isForeInnerDiameterAutomatic():
            # Get the automatic radius from the front
            d = -1
            c = self.getPreviousSymmetricComponent()
            if c is not None:
                d = c.getFrontAutoInnerDiameter()
            if d < 0:
                d = SymmetricComponent.DEFAULT_RADIUS * 2.0
            self._obj.ForeShoulderDiameter = d

        return self._obj.ForeShoulderDiameter

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

    def isForeDiameterAutomatic(self):
        return self._obj.ForeAutoDiameter

    def setForeRadiusAutomatic(self, auto):
        self.setForeDiameterAutomatic(auto)

    def setForeDiameterAutomatic(self, auto):
        for listener in self._configListeners:
            if isinstance(listener, FeatureTransition):
                listener.setForeDiameterAutomatic(auto)

        if self._obj.ForeAutoDiameter == auto:
            return

        self._obj.ForeAutoDiameter = auto

        # clearPreset();
        self.fireComponentChangeEvent(ComponentChangeEvent.BOTH_CHANGE)

    def isForeInnerDiameterAutomatic(self):
        return self._obj.ForeShoulderAutoDiameter

    def getAftRadius(self):
        return self.getAftDiameter() / 2.0

    def getAftDiameter(self):
        if self.isAftDiameterAutomatic():
            # Return the auto radius from the rear
            d = -1
            c = self.getNextSymmetricComponent()
            if c is not None:
                d = c.getRearAutoDiameter()

            if d < 0:
                d = SymmetricComponent.DEFAULT_RADIUS * 2.0
            self._obj.AftDiameter = d

        return self._obj.AftDiameter

    def getAftShoulderDiameter(self):
        if self.isAftInnerDiameterAutomatic():
            # Return the auto radius from the rear
            d = -1
            c = self.getNextSymmetricComponent()
            if c is not None:
                d = c.getRearAutoInnerDiameter()

            if d < 0:
                d = SymmetricComponent.DEFAULT_RADIUS * 2.0
            self._obj.AftShoulderDiameter = d

        return self._obj.AftShoulderDiameter

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

    def isAftInnerDiameterAutomatic(self):
        return self._obj.AftShoulderAutoDiameter

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

    def getFrontAutoInnerDiameter(self):
        if self.isAftInnerDiameterAutomatic():
            return -1
        return self.getAftShoulderDiameter()

    def getRearAutoRadius(self):
        if self.isForeRadiusAutomatic():
            return -1
        return self.getForeRadius()

    def getRearAutoDiameter(self):
        if self.isForeDiameterAutomatic():
            return -1
        return self.getForeDiameter()

    def getRearAutoInnerDiameter(self):
        if self.isForeDiameterAutomatic():
            return -1
        return self.getForeShoulderDiameter()

    def usesPreviousCompAutomatic(self):
        return self.isForeRadiusAutomatic()

    def usesNextCompAutomatic(self):
        return self.isAftRadiusAutomatic()

    """
        Return the radius at point x of the transition.
    """
    def getRadius(self, x):
        return 0.0

    def _setShapeHandler(self):
        obj = self._obj
        self._shapeHandler = None
        if obj.TransitionType == TYPE_CONE:
            self._shapeHandler = TransitionConeShapeHandler(obj)
        elif obj.TransitionType == TYPE_ELLIPTICAL:
            self._shapeHandler = TransitionEllipseShapeHandler(obj)
        elif obj.TransitionType == TYPE_OGIVE:
            self._shapeHandler = TransitionOgiveShapeHandler(obj)
        elif obj.TransitionType == TYPE_VON_KARMAN:
            obj.Coefficient = 0.0
            self._shapeHandler = TransitionHaackShapeHandler(obj)
        elif obj.TransitionType == TYPE_HAACK:
            self._shapeHandler = TransitionHaackShapeHandler(obj)
        elif obj.TransitionType == TYPE_PARABOLIC:
            self._shapeHandler = TransitionParabolicShapeHandler(obj)
        elif obj.TransitionType == TYPE_PARABOLA:
            obj.Coefficient = 0.5
            self._shapeHandler = TransitionPowerShapeHandler(obj)
        elif obj.TransitionType == TYPE_POWER:
            self._shapeHandler = TransitionPowerShapeHandler(obj)

    def execute(self, obj):
        self._setShapeHandler()
        if self._shapeHandler is not None:
            self._shapeHandler.draw()

    def getXProjection(self, obj):
        """ Returns a shape representing the projection of the object onto the YZ plane """
        self._setShapeHandler()
        if self._shapeHandler is not None:
            return self._shapeHandler.getXProjection()
        return None
