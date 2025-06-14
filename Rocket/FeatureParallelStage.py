# ***************************************************************************
# *   Copyright (c) 2021-2025 David Carter <dcarter@davidcarter.ca>         *
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
"""Class for rocket assemblies"""

__title__ = "FreeCAD Rocket Assembly"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

from typing import Any

import FreeCAD

from DraftTools import translate

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

        # Convert from the pre-1.0 material system if required
        self.convertMaterialAndAppearance(obj)

        self._obj = obj

    def positionChild(self, parent : Any, parentBase : Any, parentLength : float, parentRadius : float, rotation : float) -> None:
        base = FreeCAD.Vector(parentBase)
        base.z = parentRadius

        # radius = 0.0

        # base = self._obj.Placement.Base
        roll = 0.0
        self._obj.Placement = FreeCAD.Placement(FreeCAD.Vector(base), FreeCAD.Rotation(FreeCAD.Vector(1,0,0), roll))

        self.positionChildren(base)

    def eligibleChild(self, childType : str) -> bool:
        return childType not in [FEATURE_ROCKET, FEATURE_STAGE, FEATURE_PARALLEL_STAGE]
