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

from App.FlightConfigurationId import FlightConfigurationId

class FlightConfiguration():

    _configurationName = ""
    DEFAULT_CONFIG_NAME = "[{motors}]"

    _rocket = None
    _fcid = None

    _configurationInstanceCount = 0
    _configurationInstanceId = None

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

