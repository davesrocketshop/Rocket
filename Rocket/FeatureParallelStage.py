# SPDX-License-Identifier: LGPL-2.1-or-later
# SPDX-FileCopyrightText: 2021 David Carter <dcarter@davidcarter.ca>
# SPDX-File-Notice: Part of the Rocket addon.


"""Class for rocket assemblies"""

__title__ = "FreeCAD Rocket Assembly"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

from typing import Any

import FreeCAD

translate = FreeCAD.Qt.translate

from Rocket.FeatureStage import FeatureStage
from Rocket.Constants import FEATURE_ROCKET, FEATURE_STAGE, FEATURE_PARALLEL_STAGE

class FeatureParallelStage(FeatureStage):

    def __init__(self, obj : Any) -> None:
        super().__init__(obj)
        self._initFeatureStage(obj)

        self.Type = FEATURE_PARALLEL_STAGE

        if not hasattr(obj,"StageCount"):
            obj.addProperty('App::PropertyInteger', 'StageCount', 'RocketComponent', translate('App::Property', 'Number of stages in a radial pattern')).StageCount = 2
        if not hasattr(obj,"StageSpacing"):
            obj.addProperty('App::PropertyAngle', 'StageSpacing', 'RocketComponent', translate('App::Property', 'Angle between consecutive stages')).StageSpacing = 180

    def setDefaults(self) -> None:
        super().setDefaults()

    def onDocumentRestored(self, obj : Any) -> None:
        FeatureParallelStage(obj)

        # Parallel stages weren't supported in the old material era
        # self.convertMaterialAndAppearance(obj)

        self._obj = obj

    def positionChild(self, parent : Any, parentBase : Any, parentLength : float, parentRadius : float, rotation : float) -> None:
        base = FreeCAD.Vector(parentBase)
        base.z = parentRadius

        # radius = 0.0

        # base = self._obj.Placement.Base
        roll = 0.0
        self._obj.Placement = FreeCAD.Placement(FreeCAD.Vector(base), FreeCAD.Rotation(FreeCAD.Vector(1,0,0), roll))

        # self.positionChildren(base)

    def eligibleChild(self, childType : str) -> bool:
        return childType not in [FEATURE_ROCKET, FEATURE_STAGE, FEATURE_PARALLEL_STAGE]
