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


"""Class for rocket assemblies"""

__title__ = "FreeCAD Rocket Assembly"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

from typing import Any

import FreeCAD

translate = FreeCAD.Qt.translate

from Rocket.ComponentAssembly import ComponentAssembly

from Rocket.Constants import FEATURE_STAGE, FEATURE_NOSE_CONE, FEATURE_BODY_TUBE, FEATURE_TRANSITION, FEATURE_FINCAN, \
    FEATURE_PARALLEL_STAGE, FEATURE_POD

class FeatureStage(ComponentAssembly):

    def __init__(self, obj : Any) -> None:
        super().__init__(obj)

        self._initFeatureStage(obj)

    def setDefaults(self) -> None:
        super().setDefaults()

    def _initFeatureStage(self, obj : Any) -> None:
        self.Type = FEATURE_STAGE

        if not hasattr(obj,"StageNumber"):
            obj.addProperty('App::PropertyInteger', 'StageNumber', 'RocketComponent', translate('App::Property', 'Stage number')).StageNumber = 0

    def onDocumentRestored(self, obj : Any) -> None:
        FeatureStage(obj)

        self._obj = obj

    def setStageNumber(self, newStageNumber : int) -> None:
        self._obj.StageNumber = newStageNumber

    def getStageNumber(self) -> int:
        return self._obj.StageNumber

    def execute(self, obj : Any) -> None:
        if not hasattr(obj,'Shape'):
            return

    def eligibleChild(self, childType : str) -> bool:
        return childType in [FEATURE_NOSE_CONE, FEATURE_BODY_TUBE, FEATURE_TRANSITION, FEATURE_FINCAN]

    def getLength(self) -> float:
        # Return the length of this component along the central axis
        length = 0.0
        if hasattr(self._obj, "Group"):
            for child in self._obj.Group:
                if child.Proxy.Type not in [FEATURE_PARALLEL_STAGE, FEATURE_POD]:
                    length += float(child.Proxy.getLength())

        return length
