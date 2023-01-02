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
"""Class for drawing body tubes"""

__title__ = "FreeCAD Body Tubes"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

from PySide import QtCore
    
from App.interfaces.BoxBounded import BoxBounded
from App.interfaces.Coaxial import Coaxial

from App.events.ComponentChangeEvent import ComponentChangeEvent
from App.SymmetricComponent import SymmetricComponent
from App.Constants import FEATURE_BODY_TUBE, FEATURE_INNER_TUBE, FEATURE_ENGINE_BLOCK, FEATURE_BULKHEAD, FEATURE_CENTERING_RING, FEATURE_FIN, \
    FEATURE_FINCAN, FEATURE_LAUNCH_LUG, FEATURE_PARALLEL_STAGE, FEATURE_POD, FEATURE_RAIL_BUTTON, FEATURE_RAIL_GUIDE

from App.ShapeHandlers.BodyTubeShapeHandler import BodyTubeShapeHandler
from App.Utilities import _wrn

from DraftTools import translate

def _migrate_from_1_0(obj):
    _wrn("Body tube migrating object from 1.0")

    old = {}
    old["InnerDiameter"] = obj.InnerDiameter

    obj.removeProperty("InnerDiameter")

    FeatureBodyTube(obj)

    od = float(obj.OuterDiameter)
    if od > 0.0:
        thickness = (od - float(old["InnerDiameter"])) / 2.0
        obj.Thickness = thickness

class FeatureBodyTube(SymmetricComponent, BoxBounded, Coaxial):

    _refComp = None	# Reference component that is used for the autoRadius

    def __init__(self, obj):
        super().__init__(obj)
        self.Type = FEATURE_BODY_TUBE

        # self.AxialMethod = AxialMethod.AFTER

        # Default set to a BT-50
        if not hasattr(obj,"OuterDiameter"):
            obj.addProperty('App::PropertyLength', 'OuterDiameter', 'BodyTube', translate('App::Property', 'Diameter of the outside of the body tube')).OuterDiameter = 24.79
        if not hasattr(obj, 'AutoDiameter'):
            obj.addProperty('App::PropertyBool', 'AutoDiameter', 'BodyTube', translate('App::Property', 'Automatically set the outer diameter when possible')).AutoDiameter = False
        if not hasattr(obj,"Thickness"):
            obj.addProperty('App::PropertyLength', 'Thickness', 'BodyTube', translate('App::Property', 'Diameter of the inside of the body tube')).Thickness = 0.33
        # if not hasattr(obj,"Length"):
        #     obj.addProperty('App::PropertyLength', 'Length', 'BodyTube', translate('App::Property', 'Length of the body tube')).Length = 457.0

        if not hasattr(obj, 'MotorMount'):
            obj.addProperty('App::PropertyBool', 'MotorMount', 'BodyTube', translate('App::Property', 'This component is a motor mount')).MotorMount = False
        if not hasattr(obj,"Overhang"):
            obj.addProperty('App::PropertyDistance', 'Overhang', 'BodyTube', translate('App::Property', 'Motor overhang')).Overhang = 3.0

        if not hasattr(obj,"Filled"):
            obj.addProperty('App::PropertyBool', 'Filled', 'BodyTube', translate('App::Property', 'This component is solid')).Filled = False

        if not hasattr(obj,"Shape"):
            obj.addProperty('Part::PropertyPartShape', 'Shape', 'BodyTube', translate('App::Property', 'Shape of the body tube'))

        obj.Length = 457.0


    def onDocumentRestored(self, obj):
        super().onDocumentRestored(obj)

        if hasattr(obj, "InnerDiameter"):
            _migrate_from_1_0(obj)
        else:
            FeatureBodyTube(obj)

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

    # def setThickness(self, thickness):
    #     self._obj.Thickness = thickness

    def setOuterRadius(self, diameter):
        self._obj.OuterDiameter = diameter

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

    def _setAutoDiameter(self):
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
                radius = (24.79 / 2.0) # Default to BT50
            diameter = 2.0 * radius
            if self._obj.OuterDiameter != diameter:
                self._obj.OuterDiameter = diameter
                self.setEdited()

    def getRadius(self, x):
        # Body tube has constant diameter
        return self.getForeRadius()

    def getForeRadius(self):
        # For placing objects on the outer part of the parent
        # self._setAutoDiameter()
        # return self._obj.OuterDiameter / 2.0
        return self.getOuterRadius()

    def isForeRadiusAutomatic(self):
        return self.getFrontAutoRadius()

    def getAftRadius(self):
        return self.getForeRadius()

    def isAftRadiusAutomatic(self):
        return self.getRearAutoDiameter()

    def getInnerRadius(self):
        # Set any autodiameter first
        # self._setAutoDiameter()
        return float(self._obj.OuterDiameter) / 2.0 - float(self._obj.Thickness)

    def setInnerRadius(self, radius):
        self.setInnerDiameter(radius * 2.0)

    def setInnerDiameter(self, diameter):
        for listener in self._configListeners:
            if isinstance(listener, FeatureBodyTube): # OR used transition base class
                listener.setInnerDiameter(diameter)

        self.setThickness((self._obj.OuterDiameter - diameter) / 2.0)


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

        if self._obj.OuterDiameter == diameter and not self._obj.AutoDiameter:
            return
        
        self._obj.AutoDiameter = False
        self._obj.OuterDiameter = max(diameter, 0)
        
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
                # d = c.getRearAutoDiameter()
                refComp = c
            if d < 0:
                c = self.getNextSymmetricComponent()
                # Don't use the radius of a component who already has its auto diameter enabled
                if c is not None and not c.usesPreviousCompAutomatic():
                    d = c.getRearAutoDiameter()
                    # d = c.getFrontAutoDiameter()
                    refComp = c

            if d < 0:
                d = self.DEFAULT_RADIUS * 2.0
            return d

        return float(self._obj.OuterDiameter)

    """
        Return the outer radius that was manually entered, so not the value that the component received from automatic
        outer radius.
    """
    def getOuterRadiusNoAutomatic(self):
        return self.getOuterDiameterNoAutomatic() / 2.0

    def getOuterDiameterNoAutomatic(self):
        return float(self._obj.OuterDiameter)

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
            FEATURE_BODY_TUBE, 
            FEATURE_INNER_TUBE,
            FEATURE_ENGINE_BLOCK,
            FEATURE_CENTERING_RING, 
            FEATURE_FIN, 
            FEATURE_FINCAN, 
            FEATURE_LAUNCH_LUG,
            # FEATURE_PARALLEL_STAGE, 
            # FEATURE_POD,
            FEATURE_RAIL_BUTTON, 
            FEATURE_RAIL_GUIDE]

    def onChildEdited(self):
        try:
            # print("%s: onChildEdited()" % (self.__class__.__name__))
            self._obj.Proxy.setEdited()
        except ReferenceError:
            # Already deleted object
            pass

def hookChildren(obj, group, oldGroup):
    # print("hookChildren()")
    # changed = False
    # for child in group:
    #     if child not in oldGroup:
    #         # print("%s: hookChildren added" % (child.__class__.__name__))
    #         child.Proxy.resetPlacement()
    #         # child.Proxy.edited.connect(obj.Proxy.onChildEdited, QtCore.Qt.QueuedConnection)
    #         child.Proxy.connect(obj.Proxy.onChildEdited, QtCore.Qt.QueuedConnection)
    #         changed = True

    # for child in oldGroup:
    #     if child not in group:
    #         # print("%s: hookChildren removed" % (child.__class__.__name__))
    #         # child.Proxy.edited.connect(None)
    #         try:
    #             child.Proxy.disconnect()
    #             changed = True
    #         except ReferenceError:
    #             pass # object may be deleted

    # if changed:
    #     obj.Proxy.setEdited()
    pass

