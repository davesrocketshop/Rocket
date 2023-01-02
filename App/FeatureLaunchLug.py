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

import math
    
from App.Constants import FEATURE_LAUNCH_LUG

from App.Tube import Tube
from App.position import AxialMethod
from App.position.AngleMethod import AngleMethod
from App.position.AnglePositionable import AnglePositionable
from App.interfaces.BoxBounded import BoxBounded
from App.events.ComponentChangeEvent import ComponentChangeEvent
from App.util.BoundingBox import BoundingBox
from App.util.Coordinate import Coordinate
from App import Utilities
from App.SymmetricComponent import SymmetricComponent
from App.ShapeHandlers.BodyTubeShapeHandler import BodyTubeShapeHandler

from DraftTools import translate

class FeatureLaunchLug(Tube, AnglePositionable, BoxBounded):

    def __init__(self, obj):
        super().__init__(obj, AxialMethod.MIDDLE)

        self.Type = FEATURE_LAUNCH_LUG

        # Default set to 1/8" launch lug
        if not hasattr(obj,"OuterDiameter"):
            obj.addProperty('App::PropertyLength', 'OuterDiameter', 'LaunchLug', translate('App::Property', 'Diameter of the outside of the body tube')).OuterDiameter = 4.06
        if not hasattr(obj,"Thickness"):
            obj.addProperty('App::PropertyLength', 'Thickness', 'LaunchLug', translate('App::Property', 'Diameter of the inside of the body tube')).Thickness = 0.25
        if not hasattr(obj,"Length"):
            obj.addProperty('App::PropertyLength', 'Length', 'LaunchLug', translate('App::Property', 'Length of the body tube')).Length = 25.4

        if not hasattr(obj,"AngleOffset"):
            obj.addProperty('App::PropertyAngle', 'AngleOffset', 'LaunchLug', translate('App::Property', 'Angle offset')).AngleOffset = 180
        if not hasattr(obj,"RadialOffset"):
            obj.addProperty('App::PropertyAngle', 'RadialOffset', 'LaunchLug', translate('App::Property', 'Radial offset')).RadialOffset = 0
        if not hasattr(obj,"InstanceCount"):
            obj.addProperty('App::PropertyLength', 'InstanceCount', 'LaunchLug', translate('App::Property', 'Instance count')).InstanceCount = 1
        if not hasattr(obj,"InstanceSeparation"):
            obj.addProperty('App::PropertyLength', 'InstanceSeparation', 'LaunchLug', translate('App::Property', 'Instance separation')).InstanceSeparation = 0

        if not hasattr(obj,"Shape"):
            obj.addProperty('Part::PropertyPartShape', 'Shape', 'LaunchLug', translate('App::Property', 'Shape of the launch lug'))

    def execute(self, obj):
        shape = BodyTubeShapeHandler(obj)
        if shape is not None:
            shape.draw()

    def eligibleChild(self, childType):
        return False

    def getLength(self):
        # Return the length of this component along the central axis
        length = self._obj.Length

        return float(length)

    def getOuterRadius(self):
        return self.getOuterDiameter() / 2.0

    def getOuterDiameter(self):
        return self._obj.OuterDiameter

    def setOuterRadius(self, radius):
        self.setOuterDiameter(radius * 2.0)

    def setOuterDiameter(self, diameter):
        for listener in self._configListeners:
            if isinstance(listener, FeatureLaunchLug):
                listener.setOuterDiameter(diameter)

        if self._obj.OuterDiameter == diameter:
            return

        self._obj.OuterDiameter = diameter
        self._obj.Thickness = min(self._obj.Thickness, self._obj.OuterDiameter / 2.0)
        self.clearPreset()
        self.fireComponentChangeEvent(ComponentChangeEvent.BOTH_CHANGE)

    def getInnerRadius(self):
        return self.getInnerDiameter() / 2.0

    def getInnerDiameter(self):
        return self._obj.OuterDiameter - (2.0 * self._obj.Thickness)

    def setInnerRadius(self, radius):
        self.setInnerDiameter(radius * 2.0)

    def setInnerDiameter(self, diameter):
        for listener in self._configListeners:
            if isinstance(listener, FeatureLaunchLug):
                listener.setInnerDiameter(diameter)

        # self.setOuterDiameter(float(diameter) + 2.0 * float(self._obj.Thickness))
        self.setThickness((float(self._obj.OuterDiameter) - float(diameter)) / 2.0)

    def getThickness(self):
        return self._obj.Thickness

    def setThickness(self, thickness):
        for listener in self._configListeners:
            if isinstance(listener, FeatureLaunchLug):
                listener.setThickness(thickness)

        if self._obj.Thickness == thickness:
            return

        self._obj.Thickness = Utilities.clamp(thickness, 0, self._obj.OuterDiameter / 2.0)
        self.clearPreset()
        self.fireComponentChangeEvent(ComponentChangeEvent.BOTH_CHANGE)

    def getAngleOffset(self):
        return self._obj.AngleOffset

    def setAngleOffset(self, newAngleRadians):
        for listener in self._configListeners:
            if isinstance(listener, FeatureLaunchLug):
                listener.setAngleOffset(newAngleRadians)

        rad = Utilities.clamp( newAngleRadians, -math.pi, math.pi)
        if self._obj.AngleOffset == rad:
            return

        self._obj.AngleOffset = rad
        self.fireComponentChangeEvent(ComponentChangeEvent.BOTH_CHANGE)

    def setLength(self, length):
        for listener in self._configListeners:
            if isinstance(listener, FeatureLaunchLug):
                listener.setLength(length)

        if self._obj.Length == length:
            return

        self._obj.Length = length
        self.fireComponentChangeEvent(ComponentChangeEvent.BOTH_CHANGE)

    def isAfter(self):
        return False

    def getInstanceOffsets(self):
        toReturn = []
        
        yOffset = math.cos(self._obj.AngleOffset) * (self._obj.RadialOffset);
        zOffset = math.sin(self._obj.AngleOffset) * (self._obj.RadialOffset);
        
        for index in range(self.getInstanceCount()):
            toReturn.append(Coordinate(index*self._obj.InstanceSeparation, yOffset, zOffset))
        
        return toReturn;

    def componentChanged(self, e):
        super().componentChanged(e)
        
        """
            shiftY and shiftZ must be computed here since calculating them
            in shiftCoordinates() would cause an infinite loop due to .toRelative
        """
        body = None
        parentRadius = 0.0
        
        body = self.getParent()
        while body is not None:
            if isinstance(body, SymmetricComponent):
                break
            body = body.getParent()
        
        if body is None:
            parentRadius = 0
        else:
            x1 = self.toRelative(Coordinate.NUL, body)[0].x
            x2 = self.toRelative(Coordinate(self._obj.Length, 0, 0), body)[0].x
            x1 = Utilities.clamp(x1, 0, body.getLength())
            x2 = Utilities.clamp(x2, 0, body.getLength())
            parentRadius = max(body.getRadius(x1), body.getRadius(x2))
        
        self._obj.RadialOffset = parentRadius + self.getRadius()

    # @Override
    # public double getComponentVolume() {
    #     return length * Math.PI * (MathUtil.pow2(radius) - MathUtil.pow2(radius - thickness));
    # }

    def getComponentBounds(self):
        set = []
        self.addBound(set, 0, self.getRadius())
        self.addBound(set, self.getLength(), self.getRadius())
        return set

    # @Override
    # public Coordinate getComponentCG() {
    #     return new Coordinate(length / 2, 0, 0, getComponentMass());
    # }

    # @Override
    # public String getComponentName() {
    #     //// Launch lug
    #     return trans.get("LaunchLug.Launchlug");
    # }

    # @Override
    # public double getLongitudinalUnitInertia() {
    #     // 1/12 * (3 * (r2^2 + r1^2) + h^2)
    #     return (3 * (MathUtil.pow2(getOuterRadius()) + MathUtil.pow2(getInnerRadius())) + MathUtil.pow2(getLength())) / 12;
    # }

    # @Override
    # public double getRotationalUnitInertia() {
    #     // 1/2 * (r1^2 + r2^2)
    #     return (MathUtil.pow2(getInnerRadius()) + MathUtil.pow2(getOuterRadius())) / 2;
    # }

    def allowsChildren(self):
        return False

    def isCompatible(self, type):
        # Allow nothing to be attached to a LaunchLug
        return False

    def getInstanceSeparation(self):
        return self._obj.InstanceSeparation;

    def setInstanceSeparation(self, separation):
        for listener in self._configListeners:
            if isinstance(listener, FeatureLaunchLug):
                listener.setInstanceSeparation(separation)

        self._obj.InstanceSeparation = separation

    def setInstanceCount(self, newCount):
        for listener in self._configListeners:
            if isinstance(listener, FeatureLaunchLug):
                listener.setInstanceCount(newCount)

        if newCount > 0:
            self._obj.InstanceCount = newCount

    def getInstanceCount(self):
        return int(self._obj.InstanceCount)

    def getInstanceBoundingBox(self):
        instanceBounds = BoundingBox()
        
        instanceBounds.update(Coordinate(self.getLength(), 0,0))
        
        r = self.getOuterRadius()
        instanceBounds.update(Coordinate(0,r,r))
        instanceBounds.update(Coordinate(0,-r,-r))
        
        return instanceBounds

    # @Override
    # public String getPatternName(){
    #     return (this.getInstanceCount() + "-Line");
    # }


    def getAngleMethod(self):
        return AngleMethod.RELATIVE


    def setAngleMethod(self, newMethod):
        # no-op
        pass

    # @Override
    # public InsideColorComponentHandler getInsideColorComponentHandler() {
    #     return this.insideColorComponentHandler;
    # }

    # @Override
    # public void setInsideColorComponentHandler(InsideColorComponentHandler handler) {
    #     this.insideColorComponentHandler = handler;
