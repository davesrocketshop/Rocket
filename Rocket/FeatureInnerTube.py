# SPDX-License-Identifier: LGPL-2.1-or-later
# SPDX-File-Notice: Part of the Rocket addon.

################################################################################
#                                                                              #
#   © 2021 David Carter <dcarter@davidcarter.ca>                               #
#                                                                              #
#   This addon is free software: you can redistribute it and/or modify         #
#   it under the terms of the GNU Lesser General Public License as             #
#   published by the Free Software Foundation, either version 2.1              #
#   of the License, or (at your option) any later version.                     #
#                                                                              #
#   This addon is distributed in the hope that it will be useful,              #
#   but WITHOUT ANY WARRANTY; without even the implied warranty                #
#   of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.                    #
#   See the GNU Lesser General Public License for more details.                #
#                                                                              #
#   You should have received a copy of the GNU Lesser General Public           #
#   License along with this addon. If not, see https://www.gnu.org/licenses    #
#                                                                              #
################################################################################


"""Class for drawing body tubes"""

__title__ = "FreeCAD Body Tubes"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

import math
from typing import Any

import FreeCAD
import Part

from Rocket.interfaces.BoxBounded import BoxBounded
from Rocket.position.AxialPositionable import AxialPositionable
from Rocket.interfaces.Clusterable import Clusterable
from Rocket.interfaces.RadialParent import RadialParent

from Rocket.ThicknessRingComponent import ThicknessRingComponent
from Rocket.util.BoundingBox import BoundingBox
from Rocket.util.Coordinate import Coordinate, ZERO
from Rocket.Utilities import reducePi
from Rocket.ShapeHandlers.InnerTubeShapeHandler import InnerTubeShapeHandler

from Rocket.Constants import FEATURE_INNER_TUBE, FEATURE_TUBE_COUPLER, FEATURE_ENGINE_BLOCK, FEATURE_BULKHEAD, FEATURE_CENTERING_RING

translate = FreeCAD.Qt.translate

class FeatureInnerTube(ThicknessRingComponent, Clusterable, AxialPositionable, BoxBounded, RadialParent):

    def __init__(self, obj : Any) -> None:
        super().__init__(obj)
        self.Type = FEATURE_INNER_TUBE

        if not hasattr(obj,"Clustered"):
            obj.addProperty('App::PropertyBool', 'Clustered', 'RocketComponent', translate('App::Property', 'Whether the component is part of a cluster')).Clustered = False
        if not hasattr(obj, "ClusterRadial"):
            obj.addProperty('App::PropertyBool', 'ClusterRadial', 'RocketComponent', translate('App::Property', 'Whether the cluster is arranged radially')).ClusterRadial = False
        if not hasattr(obj, "ClusterRadialCount"):
            obj.addProperty('App::PropertyInteger', 'ClusterRadialCount', 'RocketComponent', translate('App::Property', 'Number of radial components')).ClusterRadialCount = 3
        if not hasattr(obj, "ClusterRows"):
            obj.addProperty('App::PropertyInteger', 'ClusterRows', 'RocketComponent', translate('App::Property', 'Number of rows in the cluster')).ClusterRows = 1
        if not hasattr(obj, "ClusterColumns"):
            obj.addProperty('App::PropertyInteger', 'ClusterColumns', 'RocketComponent', translate('App::Property', 'Number of columns in the cluster')).ClusterColumns = 1
        if not hasattr(obj, "ClusterIncludeCenter"):
            obj.addProperty('App::PropertyBool', 'ClusterIncludeCenter', 'RocketComponent', translate('App::Property', 'Whether to include a component at the center of the cluster')).ClusterIncludeCenter = True
        if not hasattr(obj, 'ClusterScale'):
            obj.addProperty('App::PropertyFloat', 'ClusterScale', 'RocketComponent', translate('App::Property', 'Size scaling for the motor mount cluster')).ClusterScale = 1.0
        if not hasattr(obj, "ClusterSeparationAbsolute"):
            obj.addProperty('App::PropertyBool', 'ClusterSeparationAbsolute', 'RocketComponent', translate('App::Property', 'Whether the cluster separation is absolute or relative')).ClusterSeparationAbsolute = False
        if not hasattr(obj,"ClusterRotation"):
            obj.addProperty('App::PropertyAngle', 'ClusterRotation', 'RocketComponent', translate('App::Property', 'Rotation applied to the motor mount cluster')).ClusterRotation = 0.0
        if not hasattr(obj, "ClusterCant"):
            obj.addProperty('App::PropertyBool', 'ClusterCant', 'RocketComponent', translate('App::Property', 'Cant angle applied to the motor mount cluster')).ClusterCant = False
        if not hasattr(obj, "ClusterCantUseAngle"):
            obj.addProperty('App::PropertyBool', 'ClusterCantUseAngle', 'RocketComponent', translate('App::Property', 'Whether to use the cant angle or cant focus')).ClusterCantUseAngle = True
        if not hasattr(obj, "ClusterCantAngle"):
            obj.addProperty('App::PropertyAngle', 'ClusterCantAngle', 'RocketComponent', translate('App::Property', 'Cant angle applied to the motor mount cluster')).ClusterCantAngle = 0.0
        if not hasattr(obj, "ClusterCantFocus"):
            obj.addProperty('App::PropertyDistance', 'ClusterCantFocus', 'RocketComponent', translate('App::Property', 'Distance to the focus point for the cant angle')).ClusterCantFocus = 0.0
        if not hasattr(obj, "ClusterCantFocusAbsolute"):
            obj.addProperty('App::PropertyBool', 'ClusterCantFocusAbsolute', 'RocketComponent', translate('App::Property', 'Whether the cant focus distance is absolute or relative')).ClusterCantFocusAbsolute = False

        if not hasattr(obj,"Overhang"):
            obj.addProperty('App::PropertyDistance', 'Overhang', 'RocketComponent', translate('App::Property', 'Motor overhang')).Overhang = 3.0
        if not hasattr(obj, 'MotorMount'):
            obj.addProperty('App::PropertyBool', 'MotorMount', 'RocketComponent', translate('App::Property', 'This component is a motor mount')).MotorMount = False

    def setDefaults(self) -> None:
        super().setDefaults()

        self.resetCluster()

        self._obj.Diameter = 19.0
        self._obj.Thickness = 0.5
        self._obj.Length = 70.0

    def resetCluster(self) -> None:
        self._obj.Clustered = False
        self._obj.ClusterRadial = False
        self._obj.ClusterRadialCount = 3
        self._obj.ClusterRows = 1
        self._obj.ClusterColumns = 1
        self._obj.ClusterIncludeCenter = True
        self._obj.ClusterScale = 1.0
        self._obj.ClusterSeparationAbsolute = False
        self._obj.ClusterRotation = 0.0
        self._obj.ClusterCant = False
        self._obj.ClusterCantUseAngle = True
        self._obj.ClusterCantAngle = 0.0
        self._obj.ClusterCantFocus = 0.0
        self._obj.ClusterCantFocusAbsolute = False

    def onDocumentRestored(self, obj : Any) -> None:
        FeatureInnerTube(obj)

        # Convert from the pre-1.0 material system if required
        self.convertMaterialAndAppearance(obj)

        self._obj = obj

    def execute(self, obj : Any) -> None:
        # print(f"Executing {self.Type} {obj.Name}")
        shape = InnerTubeShapeHandler(obj)
        if shape:
            shape.draw()

    def getSolidShape(self, obj : Any) -> Part.Solid:
        """ Return a filled version of the shape. Useful for CFD """
        shape = InnerTubeShapeHandler(obj)
        if shape:
            return shape.drawSolidShape()
        return None

    def isAfter(self) -> bool:
        return False

    def getPatternName(self) -> str:
        return None

    def eligibleChild(self, childType : str) -> bool:
        return childType in [
            FEATURE_BULKHEAD,
            FEATURE_INNER_TUBE,
            FEATURE_TUBE_COUPLER,
            FEATURE_ENGINE_BLOCK,
            # FEATURE_BODY_TUBE,
            FEATURE_CENTERING_RING]

    def getInstanceBoundingBox(self) -> BoundingBox:
        instanceBounds = BoundingBox()

        instanceBounds.update(Coordinate(self.getLength(), 0,0))

        r = self.getOuterRadius(0)
        instanceBounds.update(Coordinate(0,r,r))
        instanceBounds.update(Coordinate(0,-r,-r))

        return instanceBounds

    def getInstanceCount(self) -> int:
        if self._obj.Clustered:
            if self._obj.ClusterRadial:
                return self._obj.ClusterRadialCount
            else:
                if self._obj.ClusterIncludeCenter or self._obj.ClusterRows < 2 or self._obj.ClusterColumns < 2:
                    return self._obj.ClusterRows * self._obj.ClusterColumns
                return 2 * self._obj.ClusterColumns + 2 * self._obj.ClusterRows - 4
        return 1

    def setInstanceCount(self, newCount : int) -> None:
        raise ValueError("Setting the cluster instance count directly is not allowed")

    """
        Get the cluster scaling.  A value of 1.0 indicates that the tubes are packed
        touching each other, larger values separate the tubes and smaller values
        pack inside each other.
    """
    def getClusterScale(self) -> float:
        return float(self._obj.ClusterScale)

    def getClusterScaleQuantity(self) -> FreeCAD.Units.Quantity:
        return FreeCAD.Units.Quantity(self.getClusterScale(), "")

    """
        Set the cluster scaling.
        @see #getClusterScale()
    """
    def setClusterScale(self, scale : float) -> None:
        scale = max(float(scale), 0)

        if self._obj.ClusterScale == scale:
            return

        self._obj.ClusterScale = scale
        self.notifyComponentChanged()

    """
        Get the cluster scaling as an absolute distance measurement.  A value of 0 indicates that the tubes are packed
        touching each other, larger values separate the tubes and smaller values pack inside each other.
    """
    def getClusterScaleAbsolute(self) -> float:
        return (self.getClusterScale() - 1) * self.getOuterRadius(0) * 2

    def getClusterScaleAbsoluteQuantity(self) -> FreeCAD.Units.Quantity:
        return FreeCAD.Units.Quantity(self.getClusterScaleAbsolute(), "mm")

    """
        Set the absolute cluster scaling (in terms of distance).
        @see #getClusterScaleAbsolute()
    """
    def setClusterScaleAbsolute(self, scale : float) -> None:
        scaleRel = float(scale) / (self.getOuterRadius(0) * 2) + 1
        self.setClusterScale(scaleRel)

    """
        return the clusterRotation
    """
    def getClusterRotation(self) -> float:
        return float(self._obj.ClusterRotation)

    def getClusterRotationQuantity(self) -> FreeCAD.Units.Quantity:
        return FreeCAD.Units.Quantity(self.getClusterRotation(), "deg")

    """
        the clusterRotation to set
    """
    def setClusterRotation(self, rotation : float) -> None:
        rotation = reducePi(rotation)
        if self._obj.ClusterRotation == rotation:
            return

        self._obj.ClusterRotation = rotation
        self.notifyComponentChanged()


    """
        Return the distance between the closest two cluster inner tube center points.
        This is equivalent to the cluster scale multiplied by the tube diameter.
    """
    def getClusterSeparation(self) -> float:
        return self.getOuterDiameter(0) * float(self._obj.ClusterScale)

    def _getPoints(self) -> list[FreeCAD.Vector]:
        if self._obj.Clustered:
            if self._obj.ClusterRadial:
                return self._getPointsRadial()
            else:
                return self._getPointsGrid()
        return self._getPointsUnclustered()

    def _getPointsUnclustered(self) -> list[FreeCAD.Vector]:
        return [FreeCAD.Vector(0.0, 0.0, 0.0)]

    def _getPointsRadial(self) -> list[FreeCAD.Vector]:
        points = []
        if self._obj.ClusterIncludeCenter:
            # Add the center point
            points.append(FreeCAD.Vector(0.0, 0.0, 0.0))

        for i in range(self._obj.ClusterRadialCount):
            # scale = 0.5
            scale = 0.5 / math.sin(math.pi/self._obj.ClusterRadialCount)
            if self._obj.ClusterIncludeCenter:
                if scale < 1.0:
                    scale = 1.0
            y = scale * math.sin(2*i*math.pi/self._obj.ClusterRadialCount)
            z = scale * math.cos(2*i*math.pi/self._obj.ClusterRadialCount)
            points.append(FreeCAD.Vector(0.0, y, z))

        return points

    def _gridPosition(self, n : int, count : int) -> float:
        position =  -1.0 * math.floor(count / 2) + float(n)
        if count % 2 == 0:
            # even number
            position += 0.5
        return position

    def _getPointsGrid(self) -> list[FreeCAD.Vector]:
        points = []
        for i in range(self._obj.ClusterRows):
            z = self._gridPosition(i, self._obj.ClusterRows)
            for j in range(self._obj.ClusterColumns):
                if self._obj.ClusterIncludeCenter \
                        or ((i == 0) or (i == self._obj.ClusterRows - 1)) \
                        or ((j == 0) or (j == self._obj.ClusterColumns - 1)):
                    y = self._gridPosition(j, self._obj.ClusterColumns)
                    points.append(FreeCAD.Vector(0.0, y, z))
        return points

    def _getPointsRotated(self, rotation) -> list[FreeCAD.Vector]:
        points = self._getPoints()
        cos = math.cos(rotation)
        sin = math.sin(rotation)
        ret = []
        for i in range(len(points)):
            y = points[i].y
            z = points[i].z
            ret.append(FreeCAD.Vector(0.0, y*cos + z*sin, -y*sin + z*cos))

        return ret

    def getClusterPoints(self) -> list[FreeCAD.Vector]:
        list = []

        points = self._getPointsRotated(float(self._obj.ClusterRotation) - self.getRadialDirection())
        separation = self.getClusterSeparation()
        for i in range(len(points)):
            list.append(FreeCAD.Vector(0, points[i].y * separation, points[i].z * separation))

        return list

    def getInstanceOffsets(self) -> list[Coordinate]:
        points = self.getClusterPoints()
        list = [Coordinate(point.x, point.y, point.z) for point in points]
        return list

    def getMotorOverhang(self) -> float:
        return float(self._obj.Overhang) / self.getScale()

    def setMotorOverhang(self, overhang : float) -> None:
        if self._obj.Overhang == overhang:
            return

        self._obj.Overhang = overhang
        self.notifyComponentChanged()

    def setMotorMount(self, active : bool) -> None:
        if self._obj.MotorMount == active:
            return
        self._obj.MotorMount = active
        self.notifyComponentChanged()

    def isMotorMount(self) -> bool:
        return self._obj.MotorMount

    def getScale(self) -> float:
        """
        Return the scale value

        Inner tubes are never scaled.
        """
        return 1.0

    def isScaled(self) -> bool:
        """ Return True if the object or any of its parental lineage is scaled """
        return False

    def resetScale(self) -> None:
        pass
