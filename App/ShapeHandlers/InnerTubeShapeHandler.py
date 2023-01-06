# ***************************************************************************
# *   Copyright (c) 2023 David Carter <dcarter@davidcarter.ca>              *
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

__title__ = "FreeCAD Body Tube Handler"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"
    
import FreeCAD
import Part

from App.ShapeHandlers.BodyTubeShapeHandler import BodyTubeShapeHandler

from App.Utilities import _err
from DraftTools import translate

class InnerTubeShapeHandler(BodyTubeShapeHandler):
    def __init__(self, obj):
        super().__init__(obj)

        self._configuration = obj.ClusterConfiguration
        self._scale = float(obj.ClusterScale)
        self._rotation = float(obj.ClusterRotation)

    def drawSingle(self):
        edges = None
        edges = self._drawTubeEdges()

        if edges is not None:
            wire = Part.Wire(edges)
            face = Part.Face(wire)
            shape = face.revolve(FreeCAD.Vector(0, 0, 0),FreeCAD.Vector(1, 0, 0), 360)
            return shape

        return None

    def _translateCenter(self, x, y):
        x1 = x * self._OD * self._scale
        y1 = y * self._OD * self._scale

        return x1, y1

    def drawInstances(self):
        tubes = []
        base = self.drawSingle()
        if self._rotation == 0:
            points = self._configuration.getPoints()
        else:
            points = self._configuration.getPointsRotated(self._rotation)

        for i in range(self._configuration.getClusterCount()):
            tube = Part.Shape(base) # Create a copy

            y = points[2 * i]
            z = points[2 * i + 1]
            y1, z1 = self._translateCenter(y, z)

            tube.translate(FreeCAD.Vector(0,y1,z1))
            tubes.append(tube)

        return Part.makeCompound(tubes)

    def draw(self):
        if not self.isValidShape():
            return

        try:
            shape = self.drawInstances()

            self._obj.Shape = shape
            self._obj.Placement = self._placement
        except (ZeroDivisionError, Part.OCCError):
            _err(translate('Rocket', "Inner tube parameters produce an invalid shape"))
            return
