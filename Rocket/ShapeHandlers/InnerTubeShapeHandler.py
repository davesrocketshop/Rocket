# SPDX-License-Identifier: LGPL-2.1-or-later
# SPDX-File-Notice: Part of the Rocket addon.

################################################################################
#                                                                              #
#   © 2023 David Carter <dcarter@davidcarter.ca>                               #
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

__title__ = "FreeCAD Body Tube Handler"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

from typing import Any

import FreeCAD
import Part
import math

from Rocket.ShapeHandlers.BodyTubeShapeHandler import BodyTubeShapeHandler

from Rocket.Utilities import _err

translate = FreeCAD.Qt.translate

class InnerTubeShapeHandler(BodyTubeShapeHandler):
    def __init__(self, obj : Any) -> None:
        super().__init__(obj)

        self._configuration = obj.ClusterConfiguration
        self._scale = float(obj.ClusterScale)
        self._rotation = float(obj.ClusterRotation)

        self._clustered = bool(obj.Clustered)
        self._clusterRadial = bool(obj.ClusterRadial)
        self._clusterRadialCount = int(obj.ClusterRadialCount)
        self._clusterRows = int(obj.ClusterRows)
        self._clusterColumns = int(obj.ClusterColumns)
        self._clusterIncludeCenter = bool(obj.ClusterIncludeCenter)
        # if not hasattr(obj, 'ClusterScale'):
        #     obj.addProperty('App::PropertyFloat', 'ClusterScale', 'RocketComponent', translate('App::Property', 'Size scaling for the motor mount cluster')).ClusterScale = 1.0
        # if not hasattr(obj, "ClusterSeparation"):
        #     obj.addProperty('App::PropertyDistance', 'ClusterSeparation', 'RocketComponent', translate('App::Property', 'Distance between the closest two cluster components')).ClusterSeparation = 0.0
        # if not hasattr(obj, "ClusterSeparationAbsolute"):
        #     obj.addProperty('App::PropertyBool', 'ClusterSeparationAbsolute', 'RocketComponent', translate('App::Property', 'Whether the cluster separation is absolute or relative')).ClusterSeparationAbsolute = False
        # if not hasattr(obj,"ClusterRotation"):
        #     obj.addProperty('App::PropertyAngle', 'ClusterRotation', 'RocketComponent', translate('App::Property', 'Rotation applied to the motor mount cluster')).ClusterRotation = 0.0
        # if not hasattr(obj, "ClusterCant"):
        #     obj.addProperty('App::PropertyBool', 'ClusterCant', 'RocketComponent', translate('App::Property', 'Cant angle applied to the motor mount cluster')).ClusterCant = False
        # if not hasattr(obj, "ClusterCantUseAngle"):
        #     obj.addProperty('App::PropertyBool', 'ClusterCantUseAngle', 'RocketComponent', translate('App::Property', 'Whether to use the cant angle or cant focus')).ClusterCantUseAngle = True
        # if not hasattr(obj, "ClusterCantAngle"):
        #     obj.addProperty('App::PropertyAngle', 'ClusterCantAngle', 'RocketComponent', translate('App::Property', 'Cant angle applied to the motor mount cluster')).ClusterCantAngle = 0.0
        # if not hasattr(obj, "ClusterCantFocus"):
        #     obj.addProperty('App::PropertyDistance', 'ClusterCantFocus', 'RocketComponent', translate('App::Property', 'Distance to the focus point for the cant angle')).ClusterCantFocus = 0.0
        # if not hasattr(obj, "ClusterCantFocusAbsolute"):
        #     obj.addProperty('App::PropertyBool', 'ClusterCantFocusAbsolute', 'RocketComponent', translate('App::Property', 'Whether the cant focus distance is absolute or relative')).ClusterCantFocusAbsolute = False

   
    def getPoints(self) -> tuple[float, ...]:
        if self._clustered:
            if self._clusterRadial:
                return self.getPointsRadial()
            else:
                return self.getPointsXY()
        return self.getPointsUnclustered()

    def getPointsUnclustered(self) -> tuple[float, ...]:
        return (0.0, 0.0)

    def getPointsRadial(self) -> tuple[float, ...]:
        points = []
        if self._clusterIncludeCenter:
            # Add the center point
            points.append(0.0)
            points.append(0.0)

        for i in range(self._clusterRadialCount):
            # scale = 0.5
            if self._clusterIncludeCenter:
                scale = 1.0
            else:
                scale = 0.5 / math.sin(math.pi/self._clusterRadialCount)
            x = scale * math.sin(2*i*math.pi/self._clusterRadialCount)
            y = scale * math.cos(2*i*math.pi/self._clusterRadialCount)
            points.append(x)
            points.append(y)

        return tuple(points)

    def gridPosition(self, n : int, count : int) -> float:
        position =  -1.0 * math.floor(count / 2) + float(n)
        if count % 2 == 0:
            # even number
            position += 0.5
        print(f"Position({n}, {count}) = {position}")
        return position

    def getPointsXY(self) -> tuple[float, ...]:
        points = []
        for i in range(self._clusterRows):
            y = self.gridPosition(i, self._clusterRows)
            for j in range(self._clusterColumns):
                if self._clusterIncludeCenter \
                        or ((i == 0) or (i == self._clusterRows - 1)) \
                        or ((j == 0) or (j == self._clusterColumns - 1)):
                    x = self.gridPosition(j, self._clusterColumns)
                    points.append(x)
                    points.append(y)
        return tuple(points)
    
    def getPointsRotated(self, rotation) -> tuple[float, ...]:
        points = self.getPoints()
        cos = math.cos(rotation)
        sin = math.sin(rotation)
        ret = []
        for i in range(int(len(points) / 2)):
            x = points[2 * i]
            y = points[2 * i + 1]
            ret.append( x*cos + y*sin)
            ret.append(-x*sin + y*cos)

        return tuple(ret)

    def drawSingle(self) -> Any:
        edges = None
        edges = self._drawTubeEdges()

        if edges:
            wire = Part.Wire(edges)
            face = Part.Face(wire)
            shape = face.revolve(FreeCAD.Vector(0, 0, 0),FreeCAD.Vector(1, 0, 0), 360)
            return shape

        return None

    def _translateCenter(self, x : float, y : float) -> tuple[float, float]:
        x1 = x * self._OD * self._scale
        y1 = y * self._OD * self._scale

        return x1, y1

    def drawInstances(self) -> Any:
        tubes = []
        base = self.drawSingle()
        if self._rotation == 0:
            points = self.getPoints()
        else:
            points = self.getPointsRotated(self._rotation)

        for i in range(int(len(points) / 2)):
            tube = Part.Shape(base) # Create a copy

            y = points[2 * i]
            z = points[2 * i + 1]
            y1, z1 = self._translateCenter(y, z)

            tube.translate(FreeCAD.Vector(0,y1,z1))
            tubes.append(tube)

        return Part.makeCompound(tubes)

    def draw(self) -> None:
        if not self.isValidShape():
            return

        try:
            shape = self.drawInstances()

            self._obj.Shape = shape
            self._obj.Placement = self._placement
        except (ZeroDivisionError, Part.OCCError):
            _err(translate('Rocket', "Inner tube parameters produce an invalid shape"))
            return
