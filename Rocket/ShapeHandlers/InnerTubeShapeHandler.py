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

        self._scale = float(obj.ClusterScale)
        self._rotation = float(obj.ClusterRotation)

        self._clustered = bool(obj.Clustered)
        self._clusterRadial = bool(obj.ClusterRadial)
        self._clusterRadialCount = int(obj.ClusterRadialCount)
        self._clusterRows = int(obj.ClusterRows)
        self._clusterColumns = int(obj.ClusterColumns)
        self._clusterIncludeCenter = bool(obj.ClusterIncludeCenter)

    def getPoints(self) -> list[FreeCAD.Vector]:
        if self._clustered:
            if self._clusterRadial:
                return self.getPointsRadial()
            else:
                return self.getPointsGrid()
        return self.getPointsUnclustered()

    def getPointsUnclustered(self) -> list[FreeCAD.Vector]:
        return [FreeCAD.Vector(0.0, 0.0, 0.0)]

    def getPointsRadial(self) -> list[FreeCAD.Vector]:
        points = []
        if self._clusterIncludeCenter:
            # Add the center point
            points.append(FreeCAD.Vector(0.0, 0.0, 0.0))

        for i in range(self._clusterRadialCount):
            # scale = 0.5
            scale = 0.5 / math.sin(math.pi/self._clusterRadialCount)
            if self._clusterIncludeCenter:
                if scale < 1.0:
                    scale = 1.0
            y = scale * math.sin(2*i*math.pi/self._clusterRadialCount)
            z = scale * math.cos(2*i*math.pi/self._clusterRadialCount)
            points.append(FreeCAD.Vector(0.0, y, z))

        return points

    def gridPosition(self, n : int, count : int) -> float:
        position =  -1.0 * math.floor(count / 2) + float(n)
        if count % 2 == 0:
            # even number
            position += 0.5
        return position

    def getPointsGrid(self) -> list[FreeCAD.Vector]:
        points = []
        for i in range(self._clusterRows):
            z = self.gridPosition(i, self._clusterRows)
            for j in range(self._clusterColumns):
                if self._clusterIncludeCenter \
                        or ((i == 0) or (i == self._clusterRows - 1)) \
                        or ((j == 0) or (j == self._clusterColumns - 1)):
                    y = self.gridPosition(j, self._clusterColumns)
                    points.append(FreeCAD.Vector(0.0, y, z))
        return points

    def getPointsRotated(self, rotation) -> list[FreeCAD.Vector]:
        points = self.getPoints()
        cos = math.cos(rotation)
        sin = math.sin(rotation)
        ret = []
        for i in range(len(points)):
            y = points[i].y
            z = points[i].z
            ret.append(FreeCAD.Vector(0.0, y*cos + z*sin, -y*sin + z*cos))

        return ret

    def drawSingle(self) -> Any:
        edges = None
        edges = self._drawTubeEdges()

        if edges:
            wire = Part.Wire(edges)
            face = Part.Face(wire)
            shape = face.revolve(FreeCAD.Vector(0, 0, 0),FreeCAD.Vector(1, 0, 0), 360)
            return shape

        return None

    def _translateCenter(self, y : float, z : float) -> FreeCAD.Vector:
        y1 = y * self._OD * self._scale
        z1 = z * self._OD * self._scale

        return FreeCAD.Vector(0.0, y1, z1)

    def drawInstances(self) -> Any:
        tubes = []
        base = self.drawSingle()
        if self._rotation == 0:
            points = self.getPoints()
        else:
            points = self.getPointsRotated(self._rotation)

        for i in range(len(points)):
            tube = Part.Shape(base) # Create a copy

            y = points[i].y
            z = points[i].z
            translation = self._translateCenter(y, z)

            tube.translate(translation)
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
