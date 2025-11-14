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
"""Class for drawing retainers"""

__title__ = "FreeCAD Retainers"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

from typing import Any

import FreeCAD
import Part

translate = FreeCAD.Qt.translate

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

from Rocket.Constants import RETAINER_TUBE_MOUNT, RETAINER_FLANGE_MOUNT, RETAINER_TAILCONE, TYPE_PROXY
from Rocket.Constants import FEATURE_RETAINER, FEATURE_NOSE_CONE, FEATURE_TRANSITION, FEATURE_INNER_TUBE, \
    FEATURE_CENTERING_RING, FEATURE_FIN

class FeatureRetainer(SymmetricComponent):

    def __init__(self, obj : Any) -> None:
        super().__init__(obj)
        self.Type = FEATURE_RETAINER
        self._shapeHandler = None

        if not hasattr(obj, 'RetainerInnerDiameter'):
            obj.addProperty('App::PropertyLength', 'RetainerInnerDiameter', 'RocketComponent', translate('App::Property', 'Diameter of the inside of the retainer. This will match the intended motor size')).RetainerInnerDiameter = 38.1
        if not hasattr(obj, 'InnerDiameterForMMT'):
            obj.addProperty('App::PropertyLength', 'InnerDiameterForMMT', 'RocketComponent', translate('App::Property', 'Diameter of the inside of the retainer where it fits over the Motor Mount Tube (MMT)')).InnerDiameterForMMT = 41.4
        if not hasattr(obj, 'MMTDepthIntoBody'):
            obj.addProperty('App::PropertyLength', 'MMTDepthIntoBody', 'RocketComponent', translate('App::Property', 'The depth of the retainer portion that fits over the Motor Mount Tube (MMT)')).MMTDepthIntoBody = 9.525
        if not hasattr(obj, 'RetainerOuterDiameter'):
            obj.addProperty('App::PropertyLength', 'RetainerOuterDiameter', 'RocketComponent', translate('App::Property', 'Diameter of the outside of the retainer without the cap installed')).RetainerOuterDiameter = 44.45
        if not hasattr(obj, 'CapDiameter'):
            obj.addProperty('App::PropertyLength', 'CapDiameter', 'RocketComponent', translate('App::Property', 'Diameter of the screw on cap')).CapDiameter = 49.784
        if not hasattr(obj, 'CapHeight'):
            obj.addProperty('App::PropertyLength', 'CapHeight', 'RocketComponent', translate('App::Property', 'Height of the screw on cap')).CapHeight = 12.7
        if not hasattr(obj, 'HeightWithAftClosure'):
            obj.addProperty('App::PropertyLength', 'HeightWithAftClosure', 'RocketComponent', translate('App::Property', 'Height of the full assembly when used with aft closure style moters')).HeightWithAftClosure = 21.59
        if not hasattr(obj, 'HeightWithSnapRing'):
            obj.addProperty('App::PropertyLength', 'HeightWithSnapRing', 'RocketComponent', translate('App::Property', 'Height of the full assembly when used with snap ring style motors')).HeightWithSnapRing = 0.0
        if not hasattr(obj, 'FlangeDiameter'):
            obj.addProperty('App::PropertyLength', 'FlangeDiameter', 'RocketComponent', translate('App::Property', 'Diameter of the flange used to attach the retainer to the base of the rocket')).FlangeDiameter = 0.0
        if not hasattr(obj, 'ScrewHolePatternDiameter'):
            obj.addProperty('App::PropertyLength', 'ScrewHolePatternDiameter', 'RocketComponent', translate('App::Property', 'Diameter of the centers of the screw holes')).ScrewHolePatternDiameter = 0.0
        if not hasattr(obj, 'ScrewCount'):
            obj.addProperty('App::PropertyInteger', 'ScrewCount', 'RocketComponent', translate('App::Property', 'The number of screws used to attach the retainer to the base of the rocket')).ScrewCount = 6
        if not hasattr(obj, 'LargeConeDiameter'):
            obj.addProperty('App::PropertyLength', 'LargeConeDiameter', 'RocketComponent', translate('App::Property', 'Outside diameter of the large end of the tailcone')).LargeConeDiameter = 78.74
        if not hasattr(obj, 'SmallConeDiameter'):
            obj.addProperty('App::PropertyLength', 'SmallConeDiameter', 'RocketComponent', translate('App::Property', 'Outside diameter of the small end of the tailcone')).SmallConeDiameter = 41.91
        if not hasattr(obj, 'SmallOpeningDiameter'):
            obj.addProperty('App::PropertyLength', 'SmallOpeningDiameter', 'RocketComponent', translate('App::Property', 'Opening for the motor at the small end of the tailcone')).SmallOpeningDiameter = 35.56
        if not hasattr(obj, 'ConeLength'):
            obj.addProperty('App::PropertyLength', 'ConeLength', 'RocketComponent', translate('App::Property', 'Exterior length of the tailcone')).ConeLength = 41.91
        if not hasattr(obj, 'AirframeToMMT'):
            obj.addProperty('App::PropertyLength', 'AirframeToMMT', 'RocketComponent', translate('App::Property', 'Airframe to Motor Mount Tube (MMT) size')).AirframeToMMT = 38.1
        if not hasattr(obj, 'Lip'):
            obj.addProperty('App::PropertyLength', 'Lip', 'RocketComponent', translate('App::Property', 'Lip inside the airframe')).Lip = 1.5

        if not hasattr(obj, 'ProxyPlacement'):
            obj.addProperty('App::PropertyPlacement', 'ProxyPlacement', 'RocketComponent', translate('App::Property', 'This is the local coordinate system within the rocket object that will be used for the proxy feature')).ProxyPlacement

        if not hasattr(obj, 'RetainerStyle'):
            obj.addProperty('App::PropertyEnumeration', 'RetainerStyle', 'RocketComponent', translate('App::Property', 'The ratainer style'))
            obj.RetainerStyle = [RETAINER_TUBE_MOUNT,
                        RETAINER_FLANGE_MOUNT,
                        RETAINER_TAILCONE, 
                        TYPE_PROXY]
            obj.RetainerStyle = RETAINER_TUBE_MOUNT
        else:
            obj.RetainerStyle = [RETAINER_TUBE_MOUNT,
                        RETAINER_FLANGE_MOUNT,
                        RETAINER_TAILCONE, 
                        TYPE_PROXY]

        if not hasattr(obj, 'ScrewSize'):
            obj.addProperty('App::PropertyEnumeration', 'ScrewSize', 'RocketComponent', translate('App::Property', 'The screws required to attach the retainer to the rocket base'))
            # TODO: This needs to be generalized
            obj.ScrewSize = ["6-32x1/2", "8-32x1/2"]
            obj.ScrewSize = "6-32x1/2"
        else:
            obj.ScrewSize = ["6-32x1/2", "8-32x1/2"]

        if not hasattr(obj, 'Base'):
            obj.addProperty('App::PropertyLink', 'Base', 'RocketComponent', translate('App::Property', 'The base object used to define the retainer shape'))

    def setDefaults(self) -> None:
        super().setDefaults()

        # self._obj.Length = 67.31

    def onDocumentRestored(self, obj : Any) -> None:
        FeatureRetainer(obj)
        self._obj = obj

    def update(self) -> None:
        super().update()

        # Ensure any automatic variables are set
        # self.getAftDiameter()
        # self.getAftShoulderDiameter()

    def _isDiameterScaled(self) -> bool:
        if self._obj.AutoDiameter:
            return False
        return self.isScaled()

    def getDiameterScale(self) -> float:
        if self._isDiameterScaled():
            return self.getScale()
        return 1.0

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
            if c:
                d = c.getRearAutoDiameter()
                if not self.isScaled():
                    d /= c.getScale() # Apply reference component scale
            if d < 0:
                d = SymmetricComponent.DEFAULT_RADIUS * 2.0
            self._obj.Diameter = d

        return float(self._obj.Diameter) / self.getDiameterScale()

    def getAftShoulderRadius(self) -> float:
        return self.getAftShoulderDiameter() / 2.0

    def getAftShoulderDiameter(self) -> float:
        if self.isAftShoulderDiameterAutomatic():
            # Return the auto radius from the rear
            d = -1
            c = self.getNextSymmetricComponent()
            if c:
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
        return float(self._obj.Diameter) / self.getDiameterScale()

    def setAftRadius(self, radius : float) -> None:
        self.setAftDiameter(radius * 2.0)

    def setAftDiameter(self, diameter : float) -> None:
        if self._obj.Diameter == diameter and self._obj.AutoDiameter == False:
            return

        self._obj.AutoDiameter = False
        self._obj.Diameter = max(diameter, 0)

        # Ensure thickness doesn't exceed the radius
        if self._obj.Thickness > (self._obj.Diameter / 2.0):
            self._obj.Thickness = self._obj.Diameter / 2.0

        self.clearPreset()
        self.notifyComponentChanged()


    def isAftRadiusAutomatic(self) -> bool:
        return self.isAftDiameterAutomatic()

    def isAftDiameterAutomatic(self) -> bool:
        return self._obj.AutoDiameter

    def isAftInnerDiameterAutomatic(self) -> bool:
        return self._obj.ShoulderAutoDiameter

    def setAftRadiusAutomatic(self, auto : bool) -> None:
        self.setAftDiameterAutomatic(auto)

    def setAftDiameterAutomatic(self, auto : bool) -> None:
        if self._obj.AutoDiameter == auto:
            return

        self._obj.AutoDiameter = auto

        self.clearPreset()
        self.notifyComponentChanged()

    def isAftShoulderDiameterAutomatic(self) -> bool:
        return self._obj.ShoulderAutoDiameter

    def setAftShoulderDiameterAutomatic(self, auto : bool) -> None:
        if self._obj.ShoulderAutoDiameter == auto:
            return

        self._obj.ShoulderAutoDiameter = auto

        self.clearPreset()
        self.notifyComponentChanged()

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
            return self._shapeHandler.getLength() / self.getScale()
        return float(self._obj.Length) / self.getScale()

    def isFilled(self) -> bool:
        return False

    def setFilled(self, filled : bool) -> None:
        # if self.isFilled():
        #     return

        # self._obj.Filled = filled
        # self.notifyComponentChanged()
        # self.clearPreset()
        pass

    def getMaxForwardPosition(self) -> float:
        return float(self._obj.Length) + float(self._obj.Placement.Base.x)

    def getForeRadius(self) -> float:
        # For placing objects on the outer part of the parent
        if self._obj.AutoDiameter:
            radius = 0.0
            previous = self.getPrevious()
            if previous:
                radius = previous.Proxy.getAftRadius()
            if radius <= 0.0:
                next = self.getNext()
                if next:
                    radius = next.Proxy.getForeRadius()
            if radius <= 0.0:
                radius = 24.79 # Default to BT50
            diameter = 2.0 * radius
            if self._obj.Diameter != diameter:
                self._obj.Diameter = diameter
                self.setEdited()
        return float(self._obj.Diameter / 2.0) / self.getDiameterScale()

    def _setShapeHandler(self) -> None:
        obj = self._obj
        self._shapeHandler = None
        # if obj.NoseType == TYPE_CONE:
        #     self._shapeHandler = NoseConeShapeHandler(obj)
        # elif obj.NoseType == TYPE_BLUNTED_CONE:
        #     self._shapeHandler = NoseBluntedConeShapeHandler(obj)
        # elif obj.NoseType == TYPE_SPHERICAL:
        #     self._shapeHandler = NoseEllipseShapeHandler(obj)
        # elif obj.NoseType == TYPE_ELLIPTICAL:
        #     self._shapeHandler = NoseEllipseShapeHandler(obj)
        # elif obj.NoseType == TYPE_OGIVE:
        #     self._shapeHandler = NoseOgiveShapeHandler(obj)
        # elif obj.NoseType == TYPE_BLUNTED_OGIVE:
        #     self._shapeHandler = NoseBluntedOgiveShapeHandler(obj)
        # elif obj.NoseType == TYPE_SECANT_OGIVE:
        #     self._shapeHandler = NoseSecantOgiveShapeHandler(obj)
        # elif obj.NoseType == TYPE_VON_KARMAN:
        #     obj.Coefficient = 0.0
        #     self._shapeHandler = NoseHaackShapeHandler(obj)
        # elif obj.NoseType == TYPE_HAACK:
        #     self._shapeHandler = NoseHaackShapeHandler(obj)
        # elif obj.NoseType == TYPE_PARABOLIC:
        #     self._shapeHandler = NoseParabolicShapeHandler(obj)
        # elif obj.NoseType == TYPE_PARABOLA:
        #     obj.Coefficient = 0.5
        #     self._shapeHandler = NosePowerShapeHandler(obj)
        # elif obj.NoseType == TYPE_POWER:
        #     self._shapeHandler = NosePowerShapeHandler(obj)
        # elif obj.NoseType == TYPE_NIKE_SMOKE:
        #     self._shapeHandler = NoseNikeSmokeShapeHandler(obj)
        # elif obj.NoseType == TYPE_PROXY:
        #     self._shapeHandler = NoseProxyShapeHandler(obj)

    def execute(self, obj : Any) -> None:
        self._setShapeHandler()
        if self._shapeHandler:
            self._shapeHandler.draw()

    def getSolidShape(self, obj : Any) -> Part.Solid:
        """ Return a filled version of the shape. Useful for CFD """
        self._setShapeHandler()
        if self._shapeHandler:
            return self._shapeHandler.drawSolidShape()
        return None

    def eligibleChild(self, childType : str) -> bool:
        # return childType in []
        return False

    def getScale(self) -> float:
        if self.hasParent() and not self._obj.ScaleOverride:
            if self.getParent().isScaled():
                return self.getParent().getScale()

        scale = 1.0
        if self._obj.Scale:
            if self._obj.ScaleByValue and self._obj.ScaleValue.Value > 0.0:
                scale = self._obj.ScaleValue.Value
            elif self._obj.ScaleByDiameter:
                # Calling getForeDiameter() introduces infinite recursion. We need to assume
                # the diameter value has been set
                # diameter = self.getForeDiameter()
                # diameter = self.getAftDiameter()
                if self.Type == FEATURE_TRANSITION:
                    if self._obj.ScaleForeDiameter:
                        diameter = float(self._obj.ForeDiameter)
                    else:
                        diameter = float(self._obj.AftDiameter)
                else:
                    diameter = float(self._obj.Diameter)
                if diameter > 0 and self._obj.ScaleValue > 0:
                    scale =  diameter / self._obj.ScaleValue
        return float(scale)

    def setPartScale(self, scale : float) -> None:
        if self._obj.ScaleOverride:
            scale = self._obj.Proxy.getScale()

        self._obj.Scale = False

        # self._obj.Length /= scale
        # self._obj.Diameter /= scale
        # self._obj.OgiveDiameter /= scale
        # self._obj.BluntedDiameter /= scale
        self.setEdited()
