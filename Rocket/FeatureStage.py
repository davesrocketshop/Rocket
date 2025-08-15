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

from Rocket.ComponentAssembly import ComponentAssembly

from Rocket.Constants import FEATURE_STAGE, FEATURE_NOSE_CONE, FEATURE_BODY_TUBE, FEATURE_TRANSITION, FEATURE_FINCAN

class FeatureStage(ComponentAssembly):

    def __init__(self, obj : Any, origin : Any) -> None:
        super().__init__(obj, origin)

        self._initFeatureStage(obj)

    def setDefaults(self) -> None:
        super().setDefaults()

    def _initFeatureStage(self, obj : Any) -> None:
        self.Type = FEATURE_STAGE

        if not hasattr(obj,"StageNumber"):
            obj.addProperty('App::PropertyInteger', 'StageNumber', 'RocketComponent', translate('App::Property', 'Stage number')).StageNumber = 0

    def onDocumentRestored(self, obj : Any) -> None:
        objs = None
        origin = None
        if hasattr(obj, "Group") and not hasattr(obj, "Origin"):
            objs = obj.Group
            print(f"has group extension before {obj.hasExtension('App::GroupExtensionPython')}")
            # obj.removeExtension("App::GroupExtensionPython")
            obj.removeProperty("Group")
            origin = FreeCAD.ActiveDocument.addObject('App::Origin', obj.Label + 'Origin')

        FeatureStage(obj, origin)
        print(f"has group extension after {obj.hasExtension('App::GroupExtensionPython')}")
        print(f"has origin extension after {obj.hasExtension('App::OriginGroupExtensionPython')}")

        if objs is not None:
            # obj.Group.addObjects(objs)
            obj.Group = objs

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
                length += float(child.Proxy.getLength())

        return length

