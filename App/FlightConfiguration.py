# ***************************************************************************
# *   Copyright (c) 2022 David Carter <dcarter@davidcarter.ca>              *
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

import math

from App.FlightConfigurationId import FlightConfigurationId
from App.ComponentAssembly import ComponentAssembly

from App.Constants import FEATURE_ROCKET, FEATURE_STAGE

#
# TODO: Not yet complete
#

class FlightConfiguration():

    _configurationName = ""
    DEFAULT_CONFIG_NAME = "[{motors}]"

    _rocket = None
    _fcid = None

    _configurationInstanceCount = 0
    _configurationInstanceId = None

    _stages = None

    def __init__(self, rocket, fcid=None):
        if fcid is None:
            fcid = FlightConfigurationId()
        else:
            self._fcid = fcid
        self._rocket = rocket

        self._configurationName = self.DEFAULT_CONFIG_NAME
        self._configurationInstanceId = self._configurationInstanceCount
        self._configurationInstanceCount += 1

    # Check whether the stage specified by the index is active.
    def isStageActive(self, stageNumber):
        if stageNumber < 0:
            return True

        stage = self._rocket.getStage(stageNumber)
        return stage is not None and stage.getChildCount() > 0

    def getAllComponents(self):
        traversalOrder = []
        traversalOrder = self.recurseAllComponentsDepthFirst(self.rocket, traversalOrder)
        return traversalOrder

    def recurseAllComponentsDepthFirst(self, comp, traversalOrder):
        traversalOrder.append(comp)
        for child in comp.getChildren():
            traversalOrder = self.recurseAllComponentsDepthFirst(child.Proxy, traversalOrder)

        return traversalOrder

    # Returns all the components on core stages (i.e. centerline)
    # 
    # NOTE: components, NOT instances
    def getCoreComponents(self):
        toProcess = []
        toProcess.append(self.rocket)
        
        toReturn = []
        
        while len(toProcess) > 0:
            comp = toProcess.pop(0)
            
            if comp.type != FEATURE_ROCKET:
                toReturn.append(comp)
            
            for child in comp.getChildren():
                if child.Proxy.Type == FEATURE_STAGE:
                    # recurse through Stage -- these are still centerline.
                    # however -- insist on an exact type match to disallow off-core stages
                    if self.isStageActive(child.getStageNumber()):
                        toProcess.append(child.Proxy)
                elif isinstance(child.Proxy, ComponentAssembly):
                    # i.e. ParallelStage or PodSet
                    pass
                else:
                    toProcess.append(child.Proxy)
        
        return toReturn

    # Return all the stages in this configuration.
    def getAllStages(self):
        stages = []
        for flags in self._stages.values():
            stages.append(self._rocket.getStage(flags.stageId))

        return stages

    def getActiveStages(self):
        # For now, all stages are active
        return self.getAllStages()

    def getActiveStageCount(self):
        return len(self.getActiveStages())

    def getStageCount(self):
        return len(self._stages)

    # Return the reference length associated with the current configuration.  The 
    # reference length type is retrieved from the <code>Rocket</code>.
    def getReferenceLength(self):
        if self._rocket.getModID() != refLengthModID:
            refLengthModID = self._rocket.getModID()
            cachedRefLength = self._rocket.getReferenceType().getReferenceLength(self)

        return cachedRefLength

    def getReferenceArea(self):
        return math.pi * math.pow(self.getReferenceLength() / 2, 2)
