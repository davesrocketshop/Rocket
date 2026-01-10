# SPDX-License-Identifier: LGPL-2.1-or-later
# SPDX-FileCopyrightText: 2021 David Carter <dcarter@davidcarter.ca>
# SPDX-File-Notice: Part of the Rocket addon.


__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

from typing import Any

import FreeCAD

translate = FreeCAD.Qt.translate

from Rocket.SymmetricComponent import SymmetricComponent

from Rocket.ShapeHandlers.TransitionConeShapeHandler import TransitionConeShapeHandler
from Rocket.ShapeHandlers.TransitionEllipseShapeHandler import TransitionEllipseShapeHandler
from Rocket.ShapeHandlers.TransitionHaackShapeHandler import TransitionHaackShapeHandler
from Rocket.ShapeHandlers.TransitionOgiveShapeHandler import TransitionOgiveShapeHandler
from Rocket.ShapeHandlers.TransitionParabolicShapeHandler import TransitionParabolicShapeHandler
from Rocket.ShapeHandlers.TransitionPowerShapeHandler import TransitionPowerShapeHandler
from Rocket.ShapeHandlers.TransitionProxyShapeHandler import TransitionProxyShapeHandler

from Rocket.Constants import TYPE_CONE, TYPE_ELLIPTICAL, TYPE_HAACK, TYPE_OGIVE, TYPE_VON_KARMAN, TYPE_PARABOLA, \
    TYPE_PARABOLIC, TYPE_POWER, TYPE_PROXY
from Rocket.Constants import STYLE_CAPPED, STYLE_HOLLOW, STYLE_SOLID, STYLE_SOLID_CORE
from Rocket.Constants import STYLE_CAP_SOLID, STYLE_CAP_BAR, STYLE_CAP_CROSS
from Rocket.Constants import FEATURE_TRANSITION, FEATURE_CENTERING_RING, FEATURE_INNER_TUBE, FEATURE_FIN

from Rocket.Utilities import _wrn

class FeatureTransition(SymmetricComponent):

    def __init__(self, obj : Any) -> None:
        super().__init__(obj)
        self.Type = FEATURE_TRANSITION
        self._shapeHandler = None

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

        if not hasattr(obj, 'ProxyPlacement'):
            obj.addProperty('App::PropertyPlacement', 'ProxyPlacement', 'RocketComponent', translate('App::Property', 'This is the local coordinate system within the rocket object that will be used for the proxy feature')).ProxyPlacement
        if not hasattr(obj, 'ProxyAftOffset'):
            obj.addProperty('App::PropertyLength', 'ProxyAftOffset', 'RocketComponent', translate('App::Property', 'Offset at the aft end of the proxy object')).ProxyAftOffset = 0.0

        if not hasattr(obj, 'TransitionType'):
            obj.addProperty('App::PropertyEnumeration', 'TransitionType', 'RocketComponent', translate('App::Property', 'Transition type'))
            obj.TransitionType = [TYPE_CONE,
                        TYPE_ELLIPTICAL,
                        TYPE_OGIVE,
                        TYPE_VON_KARMAN,
                        TYPE_PARABOLA,
                        TYPE_PARABOLIC,
                        TYPE_POWER,
                        TYPE_HAACK,
                        TYPE_PROXY]
            obj.TransitionType = TYPE_CONE
        else:
            obj.TransitionType = [TYPE_CONE,
                        TYPE_ELLIPTICAL,
                        TYPE_OGIVE,
                        TYPE_VON_KARMAN,
                        TYPE_PARABOLA,
                        TYPE_PARABOLIC,
                        TYPE_POWER,
                        TYPE_HAACK,
                        TYPE_PROXY]

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

        if not hasattr(obj, 'Base'):
            obj.addProperty('App::PropertyLink', 'Base', 'RocketComponent', translate('App::Property', 'The base object used to define the transition shape'))

    def setDefaults(self) -> None:
        super().setDefaults()

        self._obj.Length = 60.0

    def onDocumentRestored(self, obj : Any) -> None:
        FeatureTransition(obj)

        # Convert from the pre-1.0 material system if required
        self.convertMaterialAndAppearance(obj)

        self._obj = obj

    def update(self) -> None:
        super().update()

        # Ensure any automatic variables are set
        self.getForeDiameter()
        self.getAftDiameter()
        self.getForeShoulderDiameter()
        self.getAftShoulderDiameter()

    def _isForeDiameterScaled(self) -> bool:
        if self._obj.Proxy.hasParent():
            return self._obj.Proxy.getParent().isScaled()
        return not self._obj.ForeAutoDiameter

    def getForeDiameterScale(self) -> float:
        if self._isForeDiameterScaled():
            return self.getScale()
        return 1.0

    def _isAftDiameterScaled(self) -> bool:
        if self._obj.Proxy.hasParent():
            return self._obj.Proxy.getParent().isScaled()
        return not self._obj.AftAutoDiameter

    def getAftDiameterScale(self) -> float:
        if self._isAftDiameterScaled():
            return self.getScale()
        return 1.0

    def getForeRadius(self) -> float:
        return self.getForeDiameter() / 2.0

    def getForeDiameter(self) -> float:
        if self.isForeDiameterAutomatic():
            # Get the automatic radius from the front
            d = -1
            c = self.getPreviousSymmetricComponent()
            if c:
                d = c.getFrontAutoDiameter()
            if d < 0:
                d = SymmetricComponent.DEFAULT_RADIUS * 2.0
            self._obj.ForeDiameter = d

        return float(self._obj.ForeDiameter) / self.getForeDiameterScale()

    def getForeShoulderRadius(self) -> float:
        return self.getForeShoulderDiameter() / 2.0

    def getForeShoulderDiameter(self) -> float:
        if self.isForeInnerDiameterAutomatic():
            # Get the automatic radius from the front
            d = -1
            c = self.getPreviousSymmetricComponent()
            if c:
                d = c.getFrontAutoInnerDiameter()
            if d < 0:
                d = SymmetricComponent.DEFAULT_RADIUS * 2.0
            self._obj.ForeShoulderDiameter = d

        return float(self._obj.ForeShoulderDiameter)

    """
        Return the fore radius that was manually entered, so not the value that the component received from automatic
        fore radius.
    """
    def getForeRadiusNoAutomatic(self) -> float:
        return float(self._obj.ForeDiameter / 2.0) / self.getForeDiameterScale()

    def setForeRadius(self, radius : float) -> None:
        r = self._obj.ForeDiameter / 2.0
        if r == radius and not self._obj.ForeAutoDiameter:
            return

        self._obj.ForeAutoDiameter = False
        self._obj.ForeDiameter = 2.0 * max(radius, 0)

        foreRadius = float(self._obj.ForeDiameter) / 2.0
        aftRadius = float(self._obj.AftDiameter) / 2.0
        if self._obj.Thickness > foreRadius and self._obj.Thickness > aftRadius:
            self._obj.Thickness = max(foreRadius, aftRadius)

        self.clearPreset()
        self.notifyComponentChanged()

    def setForeDiameter(self, diameter : float) -> None:
        self.setForeRadius(diameter / 2.0)

    def isForeRadiusAutomatic(self) -> bool:
        return self._obj.ForeAutoDiameter

    def isForeDiameterAutomatic(self) -> bool:
        return self._obj.ForeAutoDiameter

    def setForeRadiusAutomatic(self, auto : bool) -> None:
        self.setForeDiameterAutomatic(auto)

    def setForeDiameterAutomatic(self, auto : bool) -> None:
        if self._obj.ForeAutoDiameter == auto:
            return

        self._obj.ForeAutoDiameter = auto

        # clearPreset();
        self.notifyComponentChanged()

    def isForeInnerDiameterAutomatic(self) -> bool:
        return self._obj.ForeShoulderAutoDiameter

    def getAftRadius(self) -> float:
        return self.getAftDiameter() / 2.0

    def getAftDiameter(self) -> float:
        if self.isAftDiameterAutomatic():
            # Return the auto radius from the rear
            d = -1
            c = self.getNextSymmetricComponent()
            if c:
                d = c.getRearAutoDiameter()

            if d < 0:
                d = SymmetricComponent.DEFAULT_RADIUS * 2.0
            self._obj.AftDiameter = d

        return float(self._obj.AftDiameter) / self.getAftDiameterScale()

    def getAftShoulderRadius(self) -> float:
        return self.getAftShoulderDiameter() / 2.0

    def getAftShoulderDiameter(self) -> float:
        if self.isAftInnerDiameterAutomatic():
            # Return the auto radius from the rear
            d = -1
            c = self.getNextSymmetricComponent()
            if c:
                d = c.getRearAutoInnerDiameter()

            if d < 0:
                d = SymmetricComponent.DEFAULT_RADIUS * 2.0
            self._obj.AftShoulderDiameter = d

        return float(self._obj.AftShoulderDiameter)

    """
        Return the aft radius that was manually entered, so not the value that the component received from automatic
        aft radius.
    """
    def getAftRadiusNoAutomatic(self) -> float:
        return float(self._obj.AftDiameter / 2.0)

    def setAftRadius(self, radius : float) -> None:
        r = self._obj.AftDiameter / 2.0
        if r == radius and not self.isAftRadiusAutomatic():
            return

        self._obj.AftAutoDiameter = False
        self._obj.AftDiameter = 2.0 * max(radius, 0)

        foreRadius = float(self._obj.ForeDiameter) / 2.0
        aftRadius = float(self._obj.AftDiameter) / 2.0
        if self._obj.Thickness > foreRadius and self._obj.Thickness > aftRadius:
            self._obj.Thickness = max(foreRadius, aftRadius);

        self.clearPreset()
        self.notifyComponentChanged()

    def setAftDiameter(self, diameter : float) -> None:
        self.setAftRadius(diameter / 2.0)

    def isAftRadiusAutomatic(self) -> bool:
        return self._obj.AftAutoDiameter

    def isAftDiameterAutomatic(self) -> bool:
        return self._obj.AftAutoDiameter

    def setAftRadiusAutomatic(self, auto : bool) -> None:
        self.setAftDiameterAutomatic(auto)

    def isAftInnerDiameterAutomatic(self) -> bool:
        return self._obj.AftShoulderAutoDiameter

    def setAftDiameterAutomatic(self, auto : bool) -> None:
        if self._obj.AftAutoDiameter == auto:
            return

        self._obj.AftAutoDiameter = auto

        self.clearPreset()
        self.notifyComponentChanged()

    def getFrontAutoRadius(self) -> float:
        if self.isAftRadiusAutomatic():
            return -1
        return self.getAftRadius()

    def getFrontAutoDiameter(self) -> float:
        if self.isAftDiameterAutomatic():
            return -1
        return self.getAftDiameter()

    def getFrontAutoInnerDiameter(self) -> float:
        if self.isAftInnerDiameterAutomatic():
            return -1
        return self.getAftShoulderDiameter()

    def getRearAutoRadius(self) -> float:
        if self.isForeRadiusAutomatic():
            return -1
        return self.getForeRadius()

    def getRearAutoDiameter(self) -> float:
        if self.isForeDiameterAutomatic():
            return -1
        return self.getForeDiameter()

    def getRearAutoInnerDiameter(self) -> float:
        if self.isForeDiameterAutomatic():
            return -1
        return self.getForeShoulderDiameter()

    def usesPreviousCompAutomatic(self) -> bool:
        return self.isForeRadiusAutomatic()

    def usesNextCompAutomatic(self) -> bool:
        return self.isAftRadiusAutomatic()

    """
        Return the radius at point x of the transition.
    """
    def getRadius(self, pos : float) -> float:
        if not hasattr(self, "_shapeHandler") or self._shapeHandler is None:
            self._setShapeHandler()
        return self._shapeHandler.getRadius(pos)

    """
        Return the inner radius at point x of the transition.
    """
    def getInnerRadius(self, pos : float) -> float:
        if self._obj.TransitionStyle == STYLE_SOLID:
            return 0.0
        if self._obj.TransitionStyle == STYLE_SOLID_CORE:
            return self._obj.CoreDiameter
        return max(self.getRadius(0) - float(self._obj.Thickness), 0)

    def getLength(self) -> float:
        # Return the length of this component along the central axis
        if self._obj.TransitionType == TYPE_PROXY:
            if self._shapeHandler == None:
                self._setShapeHandler()
            return self._shapeHandler.getLength() / self.getScale()
        return float(self._obj.Length) / self.getScale()

    def _setShapeHandler(self) -> None:
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
        elif obj.TransitionType == TYPE_PROXY:
            self._shapeHandler = TransitionProxyShapeHandler(obj)

    def execute(self, obj : Any) -> None:
        self._setShapeHandler()
        if self._shapeHandler:
            self._shapeHandler.draw()

    def eligibleChild(self, childType : str) -> bool:
        return childType in [
            FEATURE_CENTERING_RING,
            FEATURE_INNER_TUBE,
            FEATURE_FIN]

    def getScale(self) -> float:
        if self.hasParent() and not self._obj.ScaleOverride:
            if self.getParent().isScaled():
                return self.getParent().getScale()

        scale = 1.0
        if self._obj.Scale:
            if self._obj.ScaleByValue and self._obj.ScaleValue.Value > 0.0:
                scale = self._obj.ScaleValue.Value
            elif self._obj.ScaleByDiameter:
                if self._obj.ScaleForeDiameter:
                    diameter = self.getForeDiameter()
                else:
                    diameter = self.getAftDiameter()
                if diameter > 0 and self._obj.ScaleValue > 0:
                    scale =  diameter / self._obj.ScaleValue
        return float(scale)

    def setPartScale(self, scale : float) -> None:
        if self._obj.ScaleOverride:
            scale = self._obj.Proxy.getScale()

        self._obj.Scale = False

        self._obj.Length /= scale
        self._obj.ForeDiameter /= scale
        self._obj.AftDiameter /= scale
        self.setEdited()
