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
"""Class for drawing body tubes"""

__title__ = "FreeCAD Body Tubes"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

from typing import Any

import Part

from Rocket.interfaces.BoxBounded import BoxBounded
from Rocket.interfaces.Coaxial import Coaxial

from Rocket.SymmetricComponent import SymmetricComponent
from Rocket.Constants import FEATURE_BODY_TUBE, FEATURE_INNER_TUBE, FEATURE_TUBE_COUPLER, FEATURE_ENGINE_BLOCK, FEATURE_BULKHEAD, FEATURE_CENTERING_RING, FEATURE_FIN, \
    FEATURE_FINCAN, FEATURE_LAUNCH_LUG, FEATURE_PARALLEL_STAGE, FEATURE_POD, FEATURE_RAIL_BUTTON, FEATURE_RAIL_GUIDE

from Rocket.ShapeHandlers.BodyTubeShapeHandler import BodyTubeShapeHandler
from Rocket.Utilities import _wrn

from Rocket.Utilities import translate

class FeatureBodyTube(SymmetricComponent, BoxBounded, Coaxial):

    _refComp = None	# Reference component that is used for the autoRadius

    def __init__(self, obj):
        super().__init__(obj)
        self.Type = FEATURE_BODY_TUBE

        # self.AxialMethod = AxialMethod.AFTER

        # Default set to a BT-50
        if not hasattr(obj,"Diameter"):
            obj.addProperty('App::PropertyLength', 'Diameter', 'RocketComponent', translate('App::Property', 'Diameter of the outside of the body tube')).Diameter = SymmetricComponent.DEFAULT_RADIUS * 2.0
        if not hasattr(obj, 'AutoDiameter'):
            obj.addProperty('App::PropertyBool', 'AutoDiameter', 'RocketComponent', translate('App::Property', 'Automatically set the outer diameter when possible')).AutoDiameter = False
        if not hasattr(obj,"Thickness"):
            obj.addProperty('App::PropertyLength', 'Thickness', 'RocketComponent', translate('App::Property', 'Diameter of the inside of the body tube')).Thickness = 0.33

        if not hasattr(obj, 'MotorMount'):
            obj.addProperty('App::PropertyBool', 'MotorMount', 'RocketComponent', translate('App::Property', 'This component is a motor mount')).MotorMount = False
        if not hasattr(obj,"Overhang"):
            obj.addProperty('App::PropertyDistance', 'Overhang', 'RocketComponent', translate('App::Property', 'Motor overhang')).Overhang = 3.0

        if not hasattr(obj,"Filled"):
            obj.addProperty('App::PropertyBool', 'Filled', 'RocketComponent', translate('App::Property', 'This component is solid')).Filled = False

    def setDefaults(self) -> None:
        super().setDefaults()

        self._obj.Length = 457.0

    def onDocumentRestored(self, obj : Any) -> None:
        FeatureBodyTube(obj)

        # Convert from the pre-1.0 material system if required
        self.convertMaterialAndAppearance(obj)
        self._obj = obj

    def update(self) -> None:
        super().update()

        # Ensure any automatic variables are set
        self.getOuterDiameter(0)
        self.getInnerDiameter(0)

    """
        Sets the length of the body component.

        Note: This should be overridden by the subcomponents which need to call
        clearPreset().  (BodyTube allows changing length without resetting the preset.)
    """
    def setLength(self, length : float) -> None:
        if self._obj.Length == length:
            return

        self._obj.Length = max(length, 0)
        self.notifyComponentChanged()

    """
        Sets whether the radius is selected automatically or not.
    """
    def setOuterDiameterAutomatic(self, auto : bool) -> None:
        if self._obj.AutoDiameter == auto:
            return

        self._obj.AutoDiameter = auto
        self.notifyComponentChanged()
        self.clearPreset()

    def setOuterRadiusAutomatic(self, auto : bool) -> None:
        self.setOuterDiameterAutomatic(auto)

    def getMaxForwardPosition(self) -> float:
        return (float(self._obj.Length) + float(self._obj.Placement.Base.x)) / self.getScale()

    def _isDiameterScaled(self) -> bool:
        if self._obj.AutoDiameter:
            return False
        return self.isScaled()

    def getDiameterScale(self) -> float:
        if self._isDiameterScaled():
            return self.getScale()
        return 1.0

    def getRadius(self, pos : float) -> float:
        # Body tube has constant diameter
        return self.getForeRadius()

    def getForeRadius(self) -> float:
        # For placing objects on the outer part of the parent
        return self.getOuterRadius(0)

    def isForeRadiusAutomatic(self) -> bool:
        return self._obj.AutoDiameter

    def getAftRadius(self) -> float:
        return self.getForeRadius()

    def isAftRadiusAutomatic(self) -> bool:
        return self._obj.AutoDiameter

    def getInnerRadius(self, pos : float) -> float:
        return self.getInnerDiameter(pos) / 2.0

    def getInnerDiameter(self, pos : float) -> float:
        return (float(self._obj.Diameter) / self.getDiameterScale()) - (2.0 * float(self._obj.Thickness))

    def setInnerRadius(self, radius : float) -> None:
        self.setInnerDiameter(radius * 2.0)

    def setInnerDiameter(self, diameter : float) -> None:
        self.setThickness((self._obj.Diameter - diameter) / 2.0)


    """
        Returns whether the radius is selected automatically or not.
        Returns false also in case automatic radius selection is not possible.
    """
    def isOuterRadiusAutomatic(self):
        return self.isOuterDiameterAutomatic()

    def isOuterDiameterAutomatic(self):
        return self._obj.AutoDiameter

    def setOuterRadius(self, radius : float) -> None:
        self.setOuterDiameter(radius * 2.0)

    def setOuterDiameter(self, diameter : float) -> None:
        if self._obj.Diameter == diameter and not self._obj.AutoDiameter:
            return

        self._obj.AutoDiameter = False
        self._obj.Diameter = max(diameter, 0)

        if self._obj.Thickness > (diameter / 2.0):
            self._obj.Thickness = (diameter / 2.0)

        self.notifyComponentChanged()
        self.clearPreset()

    """
        Return the outer radius of the body tube.
    """
    def getOuterRadius(self, pos : float) -> float:
        return self.getOuterDiameter(pos) / 2.0

    def getOuterDiameter(self, pos : float) -> float:
        if self._obj.AutoDiameter:
            # Return auto radius from front or rear
            d = -1
            c = self.getPreviousSymmetricComponent()
            # Don't use the radius of a component who already has its auto diameter enabled
            if c is not None and not c.usesNextCompAutomatic():
                self._refComp = c
                d = c.getFrontAutoDiameter()
                # if not self.isScaled():
                #     d /= c.getScale() # Apply reference component scale
            if d < 0:
                c = self.getNextSymmetricComponent()
                # Don't use the radius of a component who already has its auto diameter enabled
                if c is not None and not c.usesPreviousCompAutomatic():
                    self._refComp = c
                    d = c.getRearAutoDiameter()
                    # if not self.isScaled():
                    #     d /= c.getScale() # Apply reference component scale

            if d < 0:
                d = self.DEFAULT_RADIUS * 2.0
            self._obj.Diameter = d

        return float(self._obj.Diameter) / self.getDiameterScale()

    """
        Return the outer radius that was manually entered, so not the value that the component received from automatic
        outer radius.
    """
    def getOuterRadiusNoAutomatic(self) -> float:
        return self.getOuterDiameterNoAutomatic() / 2.0

    def getOuterDiameterNoAutomatic(self) -> float:
        return float(self._obj.Diameter)

    def getFrontAutoRadius(self) -> float:
        return self.getFrontAutoDiameter() / 2.0

    def getFrontAutoDiameter(self) -> float:
        if self.isOuterDiameterAutomatic():
            # Search for previous SymmetricComponent
            c = self.getPreviousSymmetricComponent()
            if c is not None:
                return c.getFrontAutoDiameter()
            else:
                return -1

        return self.getOuterDiameter(0)

    def getFrontAutoInnerDiameter(self) -> float:
        return self.getInnerDiameter(0)

    def getRearAutoRadius(self) -> float:
        return self.getRearAutoDiameter() / 2.0

    def getRearAutoDiameter(self) -> float:
        if self.isOuterDiameterAutomatic():
            # Search for next SymmetricComponent
            c = self.getNextSymmetricComponent()
            if c is not None:
                return c.getRearAutoDiameter()
            else:
                return -1

        return self.getOuterDiameter(0)

    def getRearAutoInnerDiameter(self) -> float:
        return self.getInnerDiameter(0)

    def getRearInnerDiameter(self) -> float:
        return self.getInnerDiameter(0)

    def isMotorMount(self) -> bool:
        return self._obj.MotorMount

    def setMotorMount(self, mount) -> None:
        self._obj.MotorMount = mount

    def usesPreviousCompAutomatic(self) -> bool:
        return self.isOuterRadiusAutomatic() and (self._refComp == self.getPreviousSymmetricComponent())

    def usesNextCompAutomatic(self) -> bool:
        return self.isOuterRadiusAutomatic() and (self._refComp == self.getNextSymmetricComponent())

    def execute(self, obj : Any) -> None:
        shape = BodyTubeShapeHandler(obj)
        if shape is not None:
            shape.draw()

    def getSolidShape(self, obj : Any) -> Part.Solid:
        """ Return a filled version of the shape. Useful for CFD """
        shape = BodyTubeShapeHandler(obj)
        if shape is not None:
            x = shape.drawSolidShape()
            return shape.drawSolidShape()
        return None

    def eligibleChild(self, childType : str) -> bool:
        return childType in [
            FEATURE_BULKHEAD,
            #FEATURE_BODY_TUBE,
            FEATURE_INNER_TUBE,
            FEATURE_TUBE_COUPLER,
            FEATURE_ENGINE_BLOCK,
            FEATURE_CENTERING_RING,
            FEATURE_FIN,
            FEATURE_FINCAN,
            FEATURE_LAUNCH_LUG,
            # FEATURE_PARALLEL_STAGE,
            FEATURE_POD,
            FEATURE_RAIL_BUTTON,
            FEATURE_RAIL_GUIDE]

    def onChildEdited(self) -> None:
        try:
            self._obj.Proxy.setEdited()
        except ReferenceError:
            # Already deleted object
            pass

    def getScale(self) -> float:
        if self.hasParent():
            if self.getParent().isScaled():
                return self.getParent().getScale()

        scale = 1.0
        if self._obj.Scale:
            if self._obj.ScaleByValue and self._obj.ScaleValue.Value > 0.0:
                scale = self._obj.ScaleValue.Value
            elif self._obj.ScaleByDiameter:
                diameter = self.getForeRadius() * 2.0
                if diameter > 0 and self._obj.ScaleValue > 0:
                    scale =  float(diameter / self._obj.ScaleValue)
        return scale
