# ***************************************************************************
# *   Copyright (c) 2021-2024 David Carter <dcarter@davidcarter.ca>         *
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

from Rocket.interfaces.BoxBounded import BoxBounded
from Rocket.interfaces.Coaxial import Coaxial

from Rocket.events.ComponentChangeEvent import ComponentChangeEvent
from Rocket.SymmetricComponent import SymmetricComponent
from Rocket.Constants import FEATURE_BODY_TUBE, FEATURE_INNER_TUBE, FEATURE_TUBE_COUPLER, FEATURE_ENGINE_BLOCK, FEATURE_BULKHEAD, FEATURE_CENTERING_RING, FEATURE_FIN, \
    FEATURE_FINCAN, FEATURE_LAUNCH_LUG, FEATURE_PARALLEL_STAGE, FEATURE_POD, FEATURE_RAIL_BUTTON, FEATURE_RAIL_GUIDE

from Rocket.ShapeHandlers.BodyTubeShapeHandler import BodyTubeShapeHandler
from Rocket.Utilities import _wrn

from DraftTools import translate

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

    def setDefaults(self):
        super().setDefaults()

        self._obj.Length = 457.0

    def onDocumentRestored(self, obj):
        FeatureBodyTube(obj)
        self._obj = obj

    def update(self):
        super().update()

        # Ensure any automatic variables are set
        self.getOuterDiameter()
        self.getInnerDiameter()

    """
        Sets the length of the body component.
        
        Note: This should be overridden by the subcomponents which need to call
        clearPreset().  (BodyTube allows changing length without resetting the preset.)
    """
    def setLength(self, length):
        for listener in self._configListeners:
            if isinstance(listener, FeatureBodyTube):
                listener.setLength(length)

        if self._obj.Length == length:
            return

        self._obj.Length = max(length, 0)
        self.fireComponentChangeEvent(ComponentChangeEvent.BOTH_CHANGE)

    """
        Sets whether the radius is selected automatically or not.
    """
    def setOuterDiameterAutomatic(self, auto):
        for listener in self._configListeners:
            if isinstance(listener, FeatureBodyTube): # OR used transition base class
                listener.setOuterDiameterAutomatic(auto)

        if self._obj.AutoDiameter == auto:
            return
        
        self._obj.AutoDiameter = auto
        self.fireComponentChangeEvent(ComponentChangeEvent.BOTH_CHANGE)
        self.clearPreset()

    def setOuterRadiusAutomatic(self, auto):
        self.setOuterDiameterAutomatic(auto)

    def getMaxForwardPosition(self):
        return float(self._obj.Length) + float(self._obj.Placement.Base.x)

    def getRadius(self, x):
        # Body tube has constant diameter
        return self.getForeRadius()

    def getForeRadius(self):
        # For placing objects on the outer part of the parent
        return self.getOuterRadius()

    def isForeRadiusAutomatic(self):
        return self.getFrontAutoRadius()

    def getAftRadius(self):
        return self.getForeRadius()

    def isAftRadiusAutomatic(self):
        return self.getRearAutoDiameter()

    def getInnerRadius(self, r=0):
        return self.getInnerDiameter(r) / 2.0

    def getInnerDiameter(self, r=0):
        return float(self._obj.Diameter) - (2.0 * float(self._obj.Thickness))

    def setInnerRadius(self, radius):
        self.setInnerDiameter(radius * 2.0)

    def setInnerDiameter(self, diameter):
        for listener in self._configListeners:
            if isinstance(listener, FeatureBodyTube): # OR used transition base class
                listener.setInnerDiameter(diameter)

        self.setThickness((self._obj.Diameter - diameter) / 2.0)


    """
        Returns whether the radius is selected automatically or not.
        Returns false also in case automatic radius selection is not possible.
    """
    def isOuterRadiusAutomatic(self):
        return self.isOuterDiameterAutomatic()

    def isOuterDiameterAutomatic(self):
        return self._obj.AutoDiameter

    def setOuterRadius(self, radius):
        self.setOuterDiameter(radius * 2.0)

    def setOuterDiameter(self, diameter):
        for listener in self._configListeners:
            if isinstance(listener, FeatureBodyTube): # OR used transition base class
                listener.setOuterDiameter(diameter)

        if self._obj.Diameter == diameter and not self._obj.AutoDiameter:
            return
        
        self._obj.AutoDiameter = False
        self._obj.Diameter = max(diameter, 0)
        
        if self._obj.Thickness > (diameter / 2.0):
            self._obj.Thickness = (diameter / 2.0)

        self.fireComponentChangeEvent(ComponentChangeEvent.BOTH_CHANGE)
        self.clearPreset()

    """
        Return the outer radius of the body tube.
    """
    def getOuterRadius(self):
        return self.getOuterDiameter() / 2.0

    def getOuterDiameter(self):
        if self._obj.AutoDiameter:
            # Return auto radius from front or rear
            d = -1
            c = self.getPreviousSymmetricComponent()
            # Don't use the radius of a component who already has its auto diameter enabled
            if c is not None and not c.usesNextCompAutomatic():
                d = c.getFrontAutoDiameter()
                self._refComp = c
            if d < 0:
                c = self.getNextSymmetricComponent()
                # Don't use the radius of a component who already has its auto diameter enabled
                if c is not None and not c.usesPreviousCompAutomatic():
                    d = c.getRearAutoDiameter()
                    self._refComp = c

            if d < 0:
                d = self.DEFAULT_RADIUS * 2.0
            self._obj.Diameter = d

        return float(self._obj.Diameter)

    """
        Return the outer radius that was manually entered, so not the value that the component received from automatic
        outer radius.
    """
    def getOuterRadiusNoAutomatic(self):
        return self.getOuterDiameterNoAutomatic() / 2.0

    def getOuterDiameterNoAutomatic(self):
        return float(self._obj.Diameter)

    def getFrontAutoRadius(self):
        return self.getFrontAutoDiameter() / 2.0

    def getFrontAutoDiameter(self):
        if self.isOuterDiameterAutomatic():
            # Search for previous SymmetricComponent
            c = self.getPreviousSymmetricComponent()
            if c is not None:
                return c.getFrontAutoDiameter()
            else:
                return -1

        return self.getOuterDiameter()

    def getFrontAutoInnerDiameter(self):
        return self.getInnerDiameter()

    def getRearAutoRadius(self):
        return self.getRearAutoDiameter() / 2.0

    def getRearAutoDiameter(self):
        if self.isOuterDiameterAutomatic():
            # Search for next SymmetricComponent
            c = self.getNextSymmetricComponent()
            if c is not None:
                return c.getRearAutoDiameter()
            else:
                return -1

        return self.getOuterDiameter()

    def getRearAutoInnerDiameter(self):
        return self.getInnerDiameter()

    def getRearInnerDiameter(self):
        return self.getInnerDiameter()

    def isMotorMount(self):
        return self._obj.MotorMount

    def setMotorMount(self, mount):
        self._obj.MotorMount = mount

    def usesPreviousCompAutomatic(self):
        return self.isOuterRadiusAutomatic() and (self._refComp == self.getPreviousSymmetricComponent())

    def usesNextCompAutomatic(self):
        return self.isOuterRadiusAutomatic() and (self._refComp == self.getNextSymmetricComponent())

    def execute(self, obj):
        shape = BodyTubeShapeHandler(obj)
        if shape is not None:
            shape.draw()

    def eligibleChild(self, childType):
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

    def onChildEdited(self):
        try:
            self._obj.Proxy.setEdited()
        except ReferenceError:
            # Already deleted object
            pass

