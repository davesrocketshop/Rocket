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
"""Class for drawing nose cones"""

__title__ = "FreeCAD Nose Cones"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

from typing import Any

import Part

from Rocket.SymmetricComponent import SymmetricComponent

from Rocket.ShapeHandlers.NoseConeShapeHandler import NoseConeShapeHandler
from Rocket.ShapeHandlers.NoseBluntedConeShapeHandler import NoseBluntedConeShapeHandler
from Rocket.ShapeHandlers.NoseEllipseShapeHandler import NoseEllipseShapeHandler
from Rocket.ShapeHandlers.NoseHaackShapeHandler import NoseHaackShapeHandler
from Rocket.ShapeHandlers.NoseOgiveShapeHandler import NoseOgiveShapeHandler
from Rocket.ShapeHandlers.NoseBluntedOgiveShapeHandler import NoseBluntedOgiveShapeHandler
from Rocket.ShapeHandlers.NoseSecantOgiveShapeHandler import NoseSecantOgiveShapeHandler
from Rocket.ShapeHandlers.NoseParabolicShapeHandler import NoseParabolicShapeHandler
from Rocket.ShapeHandlers.NosePowerShapeHandler import NosePowerShapeHandler
from Rocket.ShapeHandlers.NoseNikeSmokeShapeHandler import NoseNikeSmokeShapeHandler
from Rocket.ShapeHandlers.NoseProxyShapeHandler import NoseProxyShapeHandler

from Rocket.Constants import TYPE_CONE, TYPE_BLUNTED_CONE, TYPE_SPHERICAL, TYPE_ELLIPTICAL, \
    TYPE_HAACK, TYPE_OGIVE, TYPE_BLUNTED_OGIVE, TYPE_SECANT_OGIVE, TYPE_VON_KARMAN, TYPE_PARABOLA, \
    TYPE_PARABOLIC, TYPE_POWER, TYPE_NIKE_SMOKE, TYPE_PROXY
from Rocket.Constants import STYLE_CAPPED, STYLE_HOLLOW, STYLE_SOLID
from Rocket.Constants import STYLE_CAP_SOLID, STYLE_CAP_BAR, STYLE_CAP_CROSS
from Rocket.Constants import FEATURE_NOSE_CONE, FEATURE_INNER_TUBE, FEATURE_CENTERING_RING, FEATURE_FIN

from Rocket.events.ComponentChangeEvent import ComponentChangeEvent

from DraftTools import translate

class FeatureNoseCone(SymmetricComponent):

    def __init__(self, obj : Any) -> None:
        super().__init__(obj)
        self.Type = FEATURE_NOSE_CONE
        self._shapeHandler = None

        if not hasattr(obj, 'CapBarWidth'):
            obj.addProperty('App::PropertyLength', 'CapBarWidth', 'RocketComponent', translate('App::Property', 'Width of the nose cap bar')).CapBarWidth = 3.0
        if not hasattr(obj, 'BluntedDiameter'):
            obj.addProperty('App::PropertyLength', 'BluntedDiameter', 'RocketComponent', translate('App::Property', 'Nose Radius for a blunted nose cone')).BluntedDiameter = 5.0
        if not hasattr(obj, 'Diameter'):
            obj.addProperty('App::PropertyLength', 'Diameter', 'RocketComponent', translate('App::Property', 'Diameter at the base of the nose')).Diameter = 24.79
        if not hasattr(obj, 'AutoDiameter'):
            obj.addProperty('App::PropertyBool', 'AutoDiameter', 'RocketComponent', translate('App::Property', 'Automatically set the nose diameter when possible')).AutoDiameter = False
        if not hasattr(obj, 'Thickness'):
            obj.addProperty('App::PropertyLength', 'Thickness', 'RocketComponent', translate('App::Property', 'Nose cone thickness')).Thickness = 1.57
        if not hasattr(obj, 'Shoulder'):
            obj.addProperty('App::PropertyBool', 'Shoulder', 'RocketComponent', translate('App::Property', 'Set to true if the part includes a shoulder')).Shoulder = True
        if not hasattr(obj, 'ShoulderLength'):
            obj.addProperty('App::PropertyLength', 'ShoulderLength', 'RocketComponent', translate('App::Property', 'Shoulder Length')).ShoulderLength = 24.79
        if not hasattr(obj, 'ShoulderDiameter'):
            obj.addProperty('App::PropertyLength', 'ShoulderDiameter', 'RocketComponent', translate('App::Property', 'Shoulder diameter')).ShoulderDiameter = 23.62
        if not hasattr(obj, 'ShoulderAutoDiameter'):
            obj.addProperty('App::PropertyBool', 'ShoulderAutoDiameter', 'RocketComponent', translate('App::Property', 'Automatically set the nose shoulder diameter when possible')).ShoulderAutoDiameter = False
        if not hasattr(obj, 'ShoulderThickness'):
            obj.addProperty('App::PropertyLength', 'ShoulderThickness', 'RocketComponent', translate('App::Property', 'Shoulder thickness')).ShoulderThickness = 1.57
        if not hasattr(obj, 'Coefficient'):
            obj.addProperty('App::PropertyFloat', 'Coefficient', 'RocketComponent', translate('App::Property', 'Coefficient')).Coefficient = 0.47
        if not hasattr(obj, 'OgiveDiameter'):
            obj.addProperty('App::PropertyLength', 'OgiveDiameter', 'RocketComponent', translate('App::Property', 'The radius of the circle used to define a secant ogive')).OgiveDiameter = 120.0
        if not hasattr(obj, 'Resolution'):
            obj.addProperty('App::PropertyInteger', 'Resolution', 'RocketComponent', translate('App::Property', 'Resolution')).Resolution = 100

        if not hasattr(obj, 'ProxyEffectiveDiameter'):
            obj.addProperty('App::PropertyLength', 'ProxyEffectiveDiameter', 'RocketComponent', translate('App::Property', 'Diameter at the base of the nose proxy object')).ProxyEffectiveDiameter = 0.0
        if not hasattr(obj, 'ProxyPlacement'):
            obj.addProperty('App::PropertyPlacement', 'ProxyPlacement', 'RocketComponent', translate('App::Property', 'This is the local coordinate system within the rocket object that will be used for the proxy feature')).ProxyPlacement
        if not hasattr(obj, 'ProxyScale'):
            obj.addProperty('App::PropertyBool', 'ProxyScale', 'RocketComponent', translate('App::Property', 'Scale the proxy object')).ProxyScale = False
        if not hasattr(obj, 'ProxyScaleByValue'):
            obj.addProperty('App::PropertyBool', 'ProxyScaleByValue', 'RocketComponent', translate('App::Property', 'Scale the proxy object by value')).ProxyScaleByValue = True
        if not hasattr(obj, 'ProxyScaleByDiameter'):
            obj.addProperty('App::PropertyBool', 'ProxyScaleByDiameter', 'RocketComponent', translate('App::Property', 'Scale the proxy object by body diameter')).ProxyScaleByDiameter = False
        if not hasattr(obj, 'ProxyAutoScaleDiameter'):
            obj.addProperty('App::PropertyBool', 'ProxyAutoScaleDiameter', 'RocketComponent', translate('App::Property', 'Automatically scale the proxy object by body diameter')).ProxyAutoScaleDiameter = False
        if not hasattr(obj, 'ProxyScaleValue'):
            obj.addProperty('App::PropertyLength', 'ProxyScaleValue', 'RocketComponent', translate('App::Property', 'Proxy scaling value')).ProxyScaleValue = 0.0

        if not hasattr(obj, 'NoseType'):
            obj.addProperty('App::PropertyEnumeration', 'NoseType', 'RocketComponent', translate('App::Property', 'Nose cone type'))
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
                        TYPE_HAACK,
                        TYPE_NIKE_SMOKE,
                        TYPE_PROXY]
            obj.NoseType = TYPE_OGIVE
        else:
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
                        TYPE_HAACK,
                        TYPE_NIKE_SMOKE,
                        TYPE_PROXY]

        if not hasattr(obj, 'NoseStyle'):
            obj.addProperty('App::PropertyEnumeration', 'NoseStyle', 'RocketComponent', translate('App::Property', 'Nose cone style'))
            obj.NoseStyle = [STYLE_SOLID,
                                STYLE_HOLLOW,
                                STYLE_CAPPED]
            obj.NoseStyle = STYLE_SOLID
        else:
            obj.NoseStyle = [STYLE_SOLID,
                                STYLE_HOLLOW,
                                STYLE_CAPPED]

        if not hasattr(obj, 'CapStyle'):
            obj.addProperty('App::PropertyEnumeration', 'CapStyle', 'RocketComponent', translate('App::Property', 'Nose cone cap style'))
            obj.CapStyle = [STYLE_CAP_SOLID,
                                STYLE_CAP_BAR,
                                STYLE_CAP_CROSS]
            obj.CapStyle = STYLE_CAP_SOLID
        else:
            obj.CapStyle = [STYLE_CAP_SOLID,
                                STYLE_CAP_BAR,
                                STYLE_CAP_CROSS]

        if not hasattr(obj, 'Base'):
            obj.addProperty('App::PropertyLink', 'Base', 'RocketComponent', translate('App::Property', 'The base object used to define the nose cone shape'))

    def setDefaults(self) -> None:
        super().setDefaults()

        self._obj.Length = 67.31

    def onDocumentRestored(self, obj : Any) -> None:
        FeatureNoseCone(obj)
        self._obj = obj

        # Convert from the pre-1.0 material system if required
        self.convertMaterialAndAppearance(obj)

    def update(self) -> None:
        super().update()

        # Ensure any automatic variables are set
        self.getAftDiameter()
        self.getAftShoulderDiameter()

    def setNoseType(self, type : str) -> None:
        self._obj.NoseType = type

    def getRadius(self, pos : float) -> float:
        if not hasattr(self, "_shapeHandler") or self._shapeHandler is None:
            self._setShapeHandler()

        return self._shapeHandler.getRadius(pos)

    def getInnerRadius(self, pos : float) -> float:
        if self._obj.NoseStyle == STYLE_SOLID:
            return 0.0
        return max(self.getRadius(pos) - float(self._obj.Thickness), 0)

    def getForeDiameter(self) -> float:
        return 0

    def getForeInnerDiameter(self) -> float:
        return 0

    def setForeRadius(self) -> None:
        pass

    def setForeDiameter(self) -> None:
        pass

    def isForeRadiusAutomatic(self) -> bool:
        return False

    def isForeDiameterAutomatic(self) -> bool:
        return False

    def isForeInnerDiameterAutomatic(self) -> bool:
        return self.isForeInnerDiameterAutomatic()

    def getAftRadius(self) -> float:
        return self.getAftDiameter() / 2.0

    def getAftDiameter(self) -> float:
        if self.isAftDiameterAutomatic():
            # Return the auto radius from the rear
            d = -1
            c = self.getNextSymmetricComponent()
            if c is not None:
                d = c.getRearAutoDiameter()
            if d < 0:
                d = SymmetricComponent.DEFAULT_RADIUS * 2.0
            self._obj.Diameter = d

        return self._obj.Diameter

    def getAftShoulderDiameter(self) -> float:
        if self.isAftShoulderDiameterAutomatic():
            # Return the auto radius from the rear
            d = -1
            c = self.getNextSymmetricComponent()
            if c is not None:
                d = c.getRearAutoInnerDiameter()
            if d < 0:
                d = SymmetricComponent.DEFAULT_RADIUS * 2.0
            self._obj.ShoulderDiameter = d

        return self._obj.ShoulderDiameter

    """
        Return the aft radius that was manually entered, so not the value that the component received from automatic
        aft radius.
    """
    def getAftRadiusNoAutomatic(self) -> float:
        return self.getAftDiameterNoAutomatic() / 2.0

    def getAftDiameterNoAutomatic(self) -> float:
        return self._obj.Diameter

    def setAftRadius(self, radius : float) -> None:
        self.setAftDiameter(radius * 2.0)

    def setAftDiameter(self, diameter : float) -> None:
        for listener in self._configListeners:
            if isinstance(listener, FeatureNoseCone): # OR used transition base class
                listener.setAftDiameter(diameter)

        if self._obj.Diameter == diameter and self._obj.AutoDiameter == False:
            return

        self._obj.AutoDiameter = False
        self._obj.Diameter = max(diameter, 0)

        # Ensure thickness doesn't exceed the radius
        if self._obj.Thickness > (self._obj.Diameter / 2.0):
            self._obj.Thickness = self._obj.Diameter / 2.0

        self.clearPreset()
        self.fireComponentChangeEvent(ComponentChangeEvent.BOTH_CHANGE)


    def isAftRadiusAutomatic(self) -> bool:
        return self.isAftDiameterAutomatic()

    def isAftDiameterAutomatic(self) -> bool:
        return self._obj.AutoDiameter

    def isAftInnerDiameterAutomatic(self) -> bool:
        return self._obj.ShoulderAutoDiameter

    def setAftRadiusAutomatic(self, auto : bool) -> None:
        self.setAftDiameterAutomatic(auto)

    def setAftDiameterAutomatic(self, auto : bool) -> None:
        for listener in self._configListeners:
            if isinstance(listener, FeatureNoseCone):
                listener.setAftDiameterAutomatic(auto)

        if self._obj.AutoDiameter == auto:
            return

        self._obj.AutoDiameter = auto

        self.clearPreset()
        self.fireComponentChangeEvent(ComponentChangeEvent.BOTH_CHANGE)

    def isAftShoulderDiameterAutomatic(self) -> bool:
        return self._obj.ShoulderAutoDiameter

    def setAftShoulderDiameterAutomatic(self, auto : bool) -> None:
        for listener in self._configListeners:
            if isinstance(listener, FeatureNoseCone):
                listener.setAftShoulderDiameterAutomatic(auto)

        if self._obj.ShoulderAutoDiameter == auto:
            return

        self._obj.ShoulderAutoDiameter = auto

        self.clearPreset()
        self.fireComponentChangeEvent(ComponentChangeEvent.BOTH_CHANGE)

    def setShoulderLength(self, length : float) -> None:
        self._obj.ShoulderLength = length

    def setShoulderRadius(self, radius : float) -> None:
        self.setShoulderDiameter(radius * 2.0)

    def setShoulderDiameter(self, diameter : float) -> None:
        self._obj.ShoulderDiameter = diameter

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
        if self.isForeInnerDiameterAutomatic():
            return -1
        return self.getAftShoulderDiameter()

    def usesPreviousCompAutomatic(self) -> bool:
        return self.isForeRadiusAutomatic()

    def usesNextCompAutomatic(self) -> bool:
        return self.isAftRadiusAutomatic()

    def setLength(self, length : float) -> None:
        self._obj.Length = length

    def getLength(self) -> float:
        # Return the length of this component along the central axis
        if self._obj.NoseType == TYPE_PROXY:
            if self._shapeHandler == None:
                self._setShapeHandler()
            return self._shapeHandler.getLength()
        return self._obj.Length

    def isFilled(self) -> bool:
        return False

    def setFilled(self, filled : bool) -> None:
        for listener in self._configListeners:
            if isinstance(listener, SymmetricComponent):
                listener.setFilled(filled)

        # if self.isFilled():
        #     return

        # self._obj.Filled = filled
        # self.fireComponentChangeEvent(ComponentChangeEvent.MASS_CHANGE)
        # self.clearPreset()

    def getMaxForwardPosition(self) -> float:
        return float(self._obj.Length) + float(self._obj.Placement.Base.x)

    def getForeRadius(self) -> float:
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

    def _setShapeHandler(self) -> None:
        obj = self._obj
        self._shapeHandler = None
        if obj.NoseType == TYPE_CONE:
            self._shapeHandler = NoseConeShapeHandler(obj)
        elif obj.NoseType == TYPE_BLUNTED_CONE:
            self._shapeHandler = NoseBluntedConeShapeHandler(obj)
        elif obj.NoseType == TYPE_SPHERICAL:
            self._shapeHandler = NoseEllipseShapeHandler(obj)
        elif obj.NoseType == TYPE_ELLIPTICAL:
            self._shapeHandler = NoseEllipseShapeHandler(obj)
        elif obj.NoseType == TYPE_OGIVE:
            self._shapeHandler = NoseOgiveShapeHandler(obj)
        elif obj.NoseType == TYPE_BLUNTED_OGIVE:
            self._shapeHandler = NoseBluntedOgiveShapeHandler(obj)
        elif obj.NoseType == TYPE_SECANT_OGIVE:
            self._shapeHandler = NoseSecantOgiveShapeHandler(obj)
        elif obj.NoseType == TYPE_VON_KARMAN:
            obj.Coefficient = 0.0
            self._shapeHandler = NoseHaackShapeHandler(obj)
        elif obj.NoseType == TYPE_HAACK:
            self._shapeHandler = NoseHaackShapeHandler(obj)
        elif obj.NoseType == TYPE_PARABOLIC:
            self._shapeHandler = NoseParabolicShapeHandler(obj)
        elif obj.NoseType == TYPE_PARABOLA:
            obj.Coefficient = 0.5
            self._shapeHandler = NosePowerShapeHandler(obj)
        elif obj.NoseType == TYPE_POWER:
            self._shapeHandler = NosePowerShapeHandler(obj)
        elif obj.NoseType == TYPE_NIKE_SMOKE:
            self._shapeHandler = NoseNikeSmokeShapeHandler(obj)
        elif obj.NoseType == TYPE_PROXY:
            self._shapeHandler = NoseProxyShapeHandler(obj)

    def execute(self, obj : Any) -> None:
        self._setShapeHandler()
        if self._shapeHandler is not None:
            self._shapeHandler.draw()

    def getSolidShape(self, obj : Any) -> Part.Solid:
        """ Return a filled version of the shape. Useful for CFD """
        self._setShapeHandler()
        if self._shapeHandler is not None:
            return self._shapeHandler.drawSolidShape()
        return None

    def eligibleChild(self, childType : str) -> bool:
        return childType in [
            FEATURE_CENTERING_RING,
            FEATURE_INNER_TUBE,
            FEATURE_FIN]
