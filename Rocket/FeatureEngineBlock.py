# SPDX-License-Identifier: LGPL-2.1-or-later
# SPDX-FileCopyrightText: 2021 David Carter <dcarter@davidcarter.ca>
# SPDX-File-Notice: Part of the Rocket addon.


"""Class for drawing body tubes"""

__title__ = "FreeCAD Body Tubes"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

from typing import Any

from Rocket.position.AxialPositionable import AxialPositionable
from Rocket.position.AxialMethod import TOP

from Rocket.ThicknessRingComponent import ThicknessRingComponent
from Rocket.ShapeHandlers.BodyTubeShapeHandler import BodyTubeShapeHandler

from Rocket.Constants import FEATURE_ENGINE_BLOCK
from Rocket.Constants import LOCATION_PARENT_TOP

class FeatureEngineBlock(ThicknessRingComponent, AxialPositionable):

    def __init__(self, obj : Any):
        super().__init__(obj)
        self.Type = FEATURE_ENGINE_BLOCK

    def setDefaults(self) -> None:
        super().setDefaults()

        self._obj.AutoDiameter = True
        self._obj.Thickness = 5.0
        self._obj.Length = 5.0
        self._obj.LocationReference = LOCATION_PARENT_TOP
        self._obj.AxialOffset = 0.0
        self._obj.AxialMethod = TOP

    def onDocumentRestored(self, obj : Any) -> None:
        FeatureEngineBlock(obj)

        # Convert from the pre-1.0 material system if required
        self.convertMaterialAndAppearance(obj)

        self._obj = obj

    def execute(self, obj : Any) -> None:
        shape = BodyTubeShapeHandler(obj)
        if shape:
            shape.draw()

    def isAfter(self) -> bool:
        return False

    def eligibleChild(self, childType : str) -> bool:
        return False
