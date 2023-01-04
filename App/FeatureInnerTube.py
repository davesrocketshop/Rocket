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

from App.interfaces.BoxBounded import BoxBounded
from App.position.AxialPositionable import AxialPositionable
from App.interfaces.Clusterable import Clusterable
from App.interfaces.RadialParent import RadialParent

from App.events.ComponentChangeEvent import ComponentChangeEvent
from App.ThicknessRingComponent import ThicknessRingComponent
from App.ClusterConfiguration import SINGLE, CONFIGURATIONS
from App.util.BoundingBox import BoundingBox
from App.util.Coordinate import Coordinate, ZERO
from App.ShapeHandlers.BodyTubeShapeHandler import BodyTubeShapeHandler

from App.Constants import FEATURE_BODY_TUBE, FEATURE_INNER_TUBE, FEATURE_TUBE_COUPLER, FEATURE_ENGINE_BLOCK, FEATURE_BULKHEAD, FEATURE_CENTERING_RING

from DraftTools import translate

class FeatureInnerTube(ThicknessRingComponent, AxialPositionable, BoxBounded, RadialParent):#, Clusterable - not sure why this is causing errors

    def __init__(self, obj):
        super().__init__(obj)
        self.Type = FEATURE_INNER_TUBE

        if not hasattr(obj,"ClusterConfiguration"):
            obj.addProperty('App::PropertyPythonObject', 'ClusterConfiguration', 'Rocket', translate('App::Property', 'Layout of a clustered motor mount')).ClusterConfiguration = SINGLE
        if not hasattr(obj, 'ClusterScale'):
            obj.addProperty('App::PropertyBool', 'ClusterScale', 'Rocket', translate('App::Property', 'Size scaling for the motor mount cluster')).ClusterScale = False
        if not hasattr(obj,"ClusterRotation"):
            obj.addProperty('App::PropertyAngle', 'ClusterRotation', 'Rocket', translate('App::Property', 'Rotation applied to the motor mount cluster')).ClusterRotation = 0.0

        if not hasattr(obj,"Overhang"):
            obj.addProperty('App::PropertyDistance', 'Overhang', 'Rocket', translate('App::Property', 'Motor overhang')).Overhang = 3.0
        if not hasattr(obj, 'MotorMount'):
            obj.addProperty('App::PropertyBool', 'MotorMount', 'Rocket', translate('App::Property', 'This component is a motor mount')).MotorMount = False

        if not hasattr(obj,"Shape"):
            obj.addProperty('Part::PropertyPartShape', 'Shape', 'Rocket', translate('App::Property', 'Shape of the body tube'))

    def onDocumentRestored(self, obj):
        super().onDocumentRestored(obj)

        FeatureInnerTube(obj)

    def execute(self, obj):
        shape = BodyTubeShapeHandler(obj)
        if shape is not None:
            shape.draw()

    def isAfter(self):
        return False

    def getPatternName(self):
        return self._obj.ClusterConfiguration.getXMLName()

    def eligibleChild(self, childType):
        return childType in [
            FEATURE_BULKHEAD,
            FEATURE_INNER_TUBE,
            FEATURE_TUBE_COUPLER,
            FEATURE_ENGINE_BLOCK,
            FEATURE_BODY_TUBE, 
            FEATURE_CENTERING_RING]

    """
        Get the current cluster configuration.
    """
    def getClusterConfiguration(self):
        return self._obj.ClusterConfiguration

    """
        Set the current cluster configuration.
    """
    def setClusterConfiguration(self, cluster):
        for listener in self._configListeners:
            if isinstance(listener, FeatureInnerTube):
                listener.setClusterConfiguration(cluster)

        if cluster == self._obj.ClusterConfiguration:
            # no change
            return

        self._obj.ClusterConfiguration = cluster
        self.fireComponentChangeEvent(ComponentChangeEvent.MASS_CHANGE)

    def getInstanceBoundingBox(self):
        instanceBounds = BoundingBox()
        
        instanceBounds.update(Coordinate(self.getLength(), 0,0))
        
        r = self.getOuterRadius()
        instanceBounds.update(Coordinate(0,r,r))
        instanceBounds.update(Coordinate(0,-r,-r))
        
        return instanceBounds

    def getInstanceCount(self):
        return self._obj.ClusterConfiguration.getClusterCount()

    def setInstanceCount(self, newCount):
        raise ValueError("Setting the cluster instance count directly is not allowed")

    """
        Get the cluster scaling.  A value of 1.0 indicates that the tubes are packed
        touching each other, larger values separate the tubes and smaller values
        pack inside each other.
    """
    def getClusterScale(self):
        return self._obj.ClusterScale

    """
        Set the cluster scaling.
        @see #getClusterScale()
    """
    def setClusterScale(self, scale):
        scale = max(scale, 0)

        for listener in self._configListeners:
            if isinstance(listener, FeatureInnerTube):
                listener.setClusterScale(scale)

        if self._obj.ClusterScale == scale:
            return

        self._obj.ClusterScale = scale
        self.fireComponentChangeEvent(ComponentChangeEvent.MASS_CHANGE)

    """
        return the clusterRotation
    """
    def getClusterRotation(self):
        return self._obj.ClusterRotation

    """
        the clusterRotation to set
    """
    def setClusterRotation(self, rotation):
        for listener in self._configListeners:
            if isinstance(listener, FeatureInnerTube):
                listener.setClusterRotation(rotation)

        rotation = MathUtil.reducePi(rotation)
        if self._obj.ClusterRotation == rotation:
            return

        self._obj.ClusterRotation = rotation
        self.fireComponentChangeEvent(ComponentChangeEvent.MASS_CHANGE)


    """
        Return the distance between the closest two cluster inner tube center points.
        This is equivalent to the cluster scale multiplied by the tube diameter.
    """
    def getClusterSeparation(self):
        return self.getOuterDiameter() * self._obj.ClusterScale

    def getClusterPoints(self):
        list = []
        points = self._obj.ClusterConfiguration.getPoints(self._obj.ClusterRotation - self.getRadialDirection())
        separation = self.getClusterSeparation()
        for i in range(len(points) / 2):
            list.append(Coordinate(0, points[2 * i] * separation, points[2 * i + 1] * separation))

        return list

    def getInstanceOffsets(self):
        
        if self.getInstanceCount() == 1:
            yOffset = self.getRadialPosition() * math.cos(self.getRadialDirection())
            zOffset = self.getRadialPosition() * math.sin(self.getRadialDirection())
            return [ZERO.addValues(0.0, yOffset, zOffset)]
        
        points = self.getClusterPoints()
        
        return points

    def getMotorOverhang(self):
        return self._obj.Overhang

    def setMotorOverhang(self, overhang):
        for listener in self._configListeners:
            if isinstance(listener, FeatureInnerTube):
                listener.setMotorOverhang(overhang)

        if self._obj.Overhang == overhang:
            return

        self._obj.Overhang = overhang
        self.fireComponentChangeEvent(ComponentChangeEvent.BOTH_CHANGE)

    def setMotorMount(self, active):
        for listener in self._configListeners:
            if isinstance(listener, FeatureInnerTube):
                listener.setMotorMount(active)

        if self._obj.MotorMount == active:
            return
        self._obj.MotorMount = active
        self.fireComponentChangeEvent(ComponentChangeEvent.MOTOR_CHANGE)

    def isMotorMount(self):
        return self._obj.MotorMount
        