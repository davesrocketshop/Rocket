# ***************************************************************************
# *   Copyright (c) 2025 David Carter <dcarter@davidcarter.ca>              *
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
"""Class for drawing ring tails"""

__title__ = "FreeCAD Ring Tails"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

from Rocket.interfaces.BoxBounded import BoxBounded
from Rocket.interfaces.Coaxial import Coaxial

from Rocket.events.ComponentChangeEvent import ComponentChangeEvent
from Rocket.SymmetricComponent import SymmetricComponent
from Rocket.Constants import FEATURE_RINGTAIL

from Rocket.ShapeHandlers.RingtailShapeHandler import RingtailShapeHandler
from Rocket.Utilities import _wrn

from DraftTools import translate

class FeatureRingtail(SymmetricComponent, BoxBounded, Coaxial):

    _refComp = None	# Reference component that is used for the autoRadius

    def __init__(self, obj):
        super().__init__(obj)
        self.Type = FEATURE_RINGTAIL

        # self.AxialMethod = AxialMethod.AFTER

        # Default set to a BT-50
        if not hasattr(obj,"Diameter"):
            obj.addProperty('App::PropertyLength', 'Diameter', 'RocketComponent', translate('App::Property', 'Diameter of the outside of the body tube')).Diameter = SymmetricComponent.DEFAULT_RADIUS * 2.0
        if not hasattr(obj,"Thickness"):
            obj.addProperty('App::PropertyLength', 'Thickness', 'RocketComponent', translate('App::Property', 'Thickness of the body tube')).Thickness = 0.33

        if not hasattr(obj,"PylonCount"):
            obj.addProperty('App::PropertyInteger', 'PylonCount', 'RocketComponent', translate('App::Property', 'Number of pylons in a radial pattern')).PylonCount = 3
        if not hasattr(obj,"PylonThickness"):
            obj.addProperty('App::PropertyLength', 'PylonThickness', 'RocketComponent', translate('App::Property', 'Thickness of the pylon')).PylonThickness = 0.33

    def setDefaults(self):
        super().setDefaults()

        self._obj.Length = 30.0

    def update(self):
        super().update()

    """
        Sets the length of the body component.

        Note: This should be overridden by the subcomponents which need to call
        clearPreset().  (BodyTube allows changing length without resetting the preset.)
    """
    def setLength(self, length):
        for listener in self._configListeners:
            if isinstance(listener, FEATURE_RINGTAIL):
                listener.setLength(length)

        if self._obj.Length == length:
            return

        self._obj.Length = max(length, 0)
        self.fireComponentChangeEvent(ComponentChangeEvent.BOTH_CHANGE)

    def getMaxForwardPosition(self):
        return float(self._obj.Length) + float(self._obj.Placement.Base.x)

    def getRadius(self, x):
        # Body tube has constant diameter
        return self.getForeRadius()

    def getForeRadius(self):
        # For placing objects on the outer part of the parent
        return self.getOuterRadius()

    def getAftRadius(self):
        return self.getForeRadius()

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

    def setOuterRadius(self, radius):
        self.setOuterDiameter(radius * 2.0)

    def setOuterDiameter(self, diameter):
        for listener in self._configListeners:
            if isinstance(listener, FeatureBodyTube): # OR used transition base class
                listener.setOuterDiameter(diameter)

        if self._obj.Diameter == diameter and not self._obj.AutoDiameter:
            return

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
        return float(self._obj.Diameter)

    def getRearInnerDiameter(self):
        return self.getInnerDiameter()

    def execute(self, obj):
        shape = RingtailShapeHandler(obj)
        if shape is not None:
            shape.draw()

    def getSolidShape(self, obj):
        """ Return a filled version of the shape. Useful for CFD """
        shape = RingtailShapeHandler(obj)
        if shape is not None:
            return shape.drawSolidShape()
        return None

    def getXProjection(self, obj):
        """ Returns a shape representing the projection of the object onto the YZ plane """
        return None

    def eligibleChild(self, childType):
        # return childType in [
        #     FEATURE_BULKHEAD,
        #     #FEATURE_BODY_TUBE,
        #     FEATURE_INNER_TUBE,
        #     FEATURE_TUBE_COUPLER,
        #     FEATURE_ENGINE_BLOCK,
        #     FEATURE_CENTERING_RING,
        #     FEATURE_FIN,
        #     FEATURE_FINCAN,
        #     FEATURE_LAUNCH_LUG,
        #     # FEATURE_PARALLEL_STAGE,
        #     FEATURE_POD,
        #     FEATURE_RAIL_BUTTON,
        #     FEATURE_RAIL_GUIDE]
        return False

    def onChildEdited(self):
        try:
            self._obj.Proxy.setEdited()
        except ReferenceError:
            # Already deleted object
            pass

