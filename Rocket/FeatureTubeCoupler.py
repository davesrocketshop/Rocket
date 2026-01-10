# SPDX-License-Identifier: LGPL-2.1-or-later
# SPDX-FileCopyrightText: 2021 David Carter <dcarter@davidcarter.ca>
# SPDX-File-Notice: Part of the Rocket addon.


"""Class for drawing body tubes"""

__title__ = "FreeCAD Body Tubes"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

from typing import Any

from Rocket.interfaces.RadialParent import RadialParent

from Rocket.ThicknessRingComponent import ThicknessRingComponent
from Rocket.ShapeHandlers.BodyTubeShapeHandler import BodyTubeShapeHandler

from Rocket.Constants import FEATURE_INNER_TUBE, FEATURE_TUBE_COUPLER, FEATURE_ENGINE_BLOCK, FEATURE_BULKHEAD, FEATURE_CENTERING_RING

class FeatureTubeCoupler(ThicknessRingComponent, RadialParent):

    def __init__(self, obj : Any) -> None:
        super().__init__(obj)
        self.Type = FEATURE_TUBE_COUPLER

    def setDefaults(self) -> None:
        super().setDefaults()

        self._obj.AutoDiameter = True
        self._obj.Thickness = 2.0
        self._obj.Length = 60.0

    def onDocumentRestored(self, obj : Any) -> None:
        FeatureTubeCoupler(obj)

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
        return childType in [
            FEATURE_BULKHEAD,
            FEATURE_INNER_TUBE,
            FEATURE_TUBE_COUPLER,
            FEATURE_ENGINE_BLOCK,
            # FEATURE_BODY_TUBE,
            FEATURE_CENTERING_RING]

