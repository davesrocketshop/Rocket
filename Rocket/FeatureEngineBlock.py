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
"""Class for drawing body tubes"""

__title__ = "FreeCAD Body Tubes"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

from Rocket.position.AxialPositionable import AxialPositionable
from Rocket.position.AxialMethod import TOP

from Rocket.ThicknessRingComponent import ThicknessRingComponent
from Rocket.ShapeHandlers.BodyTubeShapeHandler import BodyTubeShapeHandler

from Rocket.Constants import FEATURE_ENGINE_BLOCK
from Rocket.Constants import LOCATION_PARENT_TOP

class FeatureEngineBlock(ThicknessRingComponent, AxialPositionable):

    def __init__(self, obj):
        super().__init__(obj)
        self.Type = FEATURE_ENGINE_BLOCK

    def setDefaults(self):
        super().setDefaults()

        self._obj.AutoDiameter = True
        self._obj.Thickness = 5.0
        self._obj.Length = 5.0
        self._obj.LocationReference = LOCATION_PARENT_TOP
        self._obj.AxialOffset = 0.0
        self._obj.AxialMethod = TOP

    def onDocumentRestored(self, obj):
        FeatureEngineBlock(obj)

        self._obj = obj

    def execute(self, obj):
        shape = BodyTubeShapeHandler(obj)
        if shape is not None:
            shape.draw()

    def isAfter(self):
        return False

    def eligibleChild(self, childType):
        return False

    def explodedSize(self):
        length = float(self._obj.Length)
        height = float(self._obj.Diameter)

        for index, child in enumerate(self.getChildren()):
            childLength, childHeight = child.Proxy.explodedSize()
            if index > 0:
                length += childLength + float(self._obj.AnimationDistance)
            else:
                length = childLength
            height = max(height, childHeight)


        return length, height

    def fromCenteringRing(self, ring):
        self.copy(ring)
