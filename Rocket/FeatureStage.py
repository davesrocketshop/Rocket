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

from DraftTools import translate

from Rocket.ComponentAssembly import ComponentAssembly

from Rocket.Constants import FEATURE_STAGE, FEATURE_NOSE_CONE, FEATURE_BODY_TUBE, FEATURE_TRANSITION, FEATURE_FINCAN

class FeatureStage(ComponentAssembly):

    def __init__(self, obj):
        super().__init__(obj)

        self._initFeatureStage(obj)

    def setDefaults(self):
        super().setDefaults()

    def _initFeatureStage(self, obj):
        self.Type = FEATURE_STAGE

        if not hasattr(obj,"StageNumber"):
            obj.addProperty('App::PropertyInteger', 'StageNumber', 'RocketComponent', translate('App::Property', 'Stage number')).StageNumber = 0

    def onDocumentRestored(self, obj):
        FeatureStage(obj)

        self._obj = obj

    def setStageNumber(self, newStageNumber):
        self._obj.StageNumber = newStageNumber

    def getStageNumber(self):
        return self._obj.StageNumber

    def execute(self,obj):
        if not hasattr(obj,'Shape'):
            return

    def eligibleChild(self, childType):
        return childType in [FEATURE_NOSE_CONE, FEATURE_BODY_TUBE, FEATURE_TRANSITION, FEATURE_FINCAN]

    def getLength(self):
        # Return the length of this component along the central axis
        length = 0.0
        if hasattr(self._obj, "Group"):
            for child in self._obj.Group:
                length += float(child.Proxy.getLength())

        return length

