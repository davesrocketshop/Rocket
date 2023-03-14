# ***************************************************************************
# *   Copyright (c) 2021-2023 David Carter <dcarter@davidcarter.ca>         *
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
"""Class for drawing launch lugs"""

__title__ = "FreeCAD Launch Lug Handler"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"
    
import FreeCAD
import Part

from Rocket.ShapeHandlers.BodyTubeShapeHandler import BodyTubeShapeHandler

from Rocket.Utilities import _err
from DraftTools import translate

class LaunchLugShapeHandler(BodyTubeShapeHandler):

    def __init__(self, obj):
        super().__init__(obj)

        self._instanceCount = int(obj.InstanceCount)
        self._separation = float(obj.InstanceSeparation)

    def drawSingle(self):
        edges = None
        edges = self._drawTubeEdges()

        if edges is not None:
            wire = Part.Wire(edges)
            face = Part.Face(wire)
            shape = face.revolve(FreeCAD.Vector(0, 0, 0),FreeCAD.Vector(1, 0, 0), 360)
            return shape

        return None

    def drawInstances(self):
        lugs = []
        base = self.drawSingle()
        for i in range(self._instanceCount):
            lug = Part.Shape(base) # Create a copy
            lug.translate(FreeCAD.Vector(i * (self._length + self._separation),0,0))
            lugs.append(lug)

        return Part.makeCompound(lugs)

    def draw(self):
        if not self.isValidShape():
            return

        try:
            shape = self.drawInstances()

            self._obj.Shape = shape
            self._obj.Placement = self._placement
        except (ZeroDivisionError, Part.OCCError):
            _err(translate('Rocket', "Launch lug parameters produce an invalid shape"))
            return
