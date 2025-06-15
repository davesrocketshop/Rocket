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

from Rocket.interfaces.ComponentChangeListener import ComponentChangeListener
from Rocket.interfaces.StateChangeListener import StateChangeListener

from Rocket.ComponentAssembly import ComponentAssembly
from Rocket.FeatureStage import FeatureStage
from Rocket.position import AxialMethod

from Rocket.util.BoundingBox import BoundingBox
from Rocket.util.Coordinate import ZERO, X_UNIT
from Rocket.util.UniqueID import UniqueID

from Rocket.events.ComponentChangeEvent import ComponentChangeEvent

from Rocket.Constants import FEATURE_ROCKET, FEATURE_STAGE

class FeatureRocket(ComponentAssembly, ComponentChangeListener):

    """
    List of component change listeners.
    """
    _listenerList = []

    _modID = -1
    _massModID = -1
    _aeroModID = -1
    _treeModID = -1
    _functionalModID = -1

    _eventsEnabled = False

    _designer = ""
    _stageMap = {}

    def __init__(self, obj : Any) -> None:
        super().__init__(obj)
        self.Type = FEATURE_ROCKET

        self.initialize()

    def initialize(self) -> None:

        self.setAxialMethod(AxialMethod.ABSOLUTE)

        modID = UniqueID.next()
        self._massModID = modID
        self._aeroModID = modID
        self._treeModID = modID
        self._functionalModID = modID

        self._listenerList = []
        self._stageMap = {}
        self.addComponentChangeListener(self)
        # self._eventsEnabled = True

    def setDefaults(self) -> None:
        super().setDefaults()

    def onDocumentRestored(self, obj : Any) -> None:
        FeatureRocket(obj)
        self._obj = obj
        obj.Proxy=self # Required because of the local variables
        self._updating = False
        self.initialize()
        self.setChildParent()
        self.enableEvents(True)
        FreeCAD.activeDocument().recompute(None,True,True)

    """
        Enable the monitoring, relay and production of events in this rocket instance.
    """
    def enableEvents(self, enable : bool = True) -> None:
        self._enableEvents(enable)
        self.updateChildren()

    def _enableEvents(self, enable : bool) -> None:
        if self._eventsEnabled and enable:
            return

        if enable:
            self._eventsEnabled = True
            self.fireComponentChangeEvent(ComponentChangeEvent.AEROMASS_CHANGE)
        else:
            self._eventsEnabled = False

    def execute(self, obj : Any) -> None:
        # self.updateChildren()
        if not hasattr(obj,'Shape'):
            return

    # Return a bounding box enveloping the rocket.  By definition, the bounding box is a convex hull.
    #
    # Note: this function gets the bounding box for the entire rocket.
    def getBoundingBox(self) -> BoundingBox:
        # return selectedConfiguration.getBoundingBoxAerodynamic();
        return BoundingBox(ZERO, X_UNIT) # default from default flight config

    def getDesigner(self) -> str:
        return self._designer

    def setDesigner(self, s : str | None) -> None:
        if s is None:
            s = ""
        self._designer = s
        self.fireComponentChangeEvent(ComponentChangeEvent.NONFUNCTIONAL_CHANGE)

    def eligibleChild(self, childType : str) -> bool:
        return childType == FEATURE_STAGE

    """
        Return the non-negative modification ID of this rocket.  The ID is changed
        every time any change occurs in the rocket.  This can be used to check
        whether it is necessary to void cached data in cases where listeners can not
        or should not be used.
        <p>
        Three other modification IDs are also available, {@link #getMassModID()},
        {@link #getAerodynamicModID()} {@link #getTreeModID()}, which change every time
        a mass change, aerodynamic change, or tree change occur.  Even though the values
        of the different modification ID's may be equal, they should be treated totally
        separate.
        <p>
        Note that undo events restore the modification IDs that were in use at the
        corresponding undo level.  Subsequent modifications, however, produce modIDs
        distinct from those already used.
    """
    def getModID(self) -> int:
        return self._modID

    """
        Return the non-negative mass modification ID of this rocket.  See
        {@link #getModID()} for details.
    """
    def getMassModID(self) -> int:
        return self._massModID

    """
        Return the non-negative aerodynamic modification ID of this rocket.  See
        {@link #getModID()} for details.
    """
    def getAerodynamicModID(self) -> int:
        return self._aeroModID

    """
        Return the non-negative tree modification ID of this rocket.  See
        {@link #getModID()} for details.
    """
    def getTreeModID(self) -> int:
        return self._treeModID

    """
        Return the non-negative functional modificationID of this rocket.
        This changes every time a functional change occurs.
    """
    def getFunctionalModID(self) -> int:
        return self._functionalModID

    def getStageCount(self) -> int:
        return len(self._stageMap)

    def getStageList(self) -> list:
        return list(self._stageMap.values())

    def getStageIndex(self, index : int) -> FeatureStage:
        return list(self._stageMap.values())[index]

    # Get the topmost stage, only taking into account active stages from the flight configuration.
    def getTopmostStage(self, config):
        if config is None:
            return None

        for child in self.getChildren():
            if child.Type == FEATURE_STAGE and config.isStageActive(child.getStageNumber()):
                return child

        return None

    # Get the bottommost stage, only taking into account active stages from the flight configuration.
    def getBottomCoreStage(self, config):
        if config is None:
            return None

        for child in reversed(self.getChildren()):
            if child.Type == FEATURE_STAGE and config.isStageActive(child.getStageNumber()):
                return child

        return None

    def getStageNumber(self) -> int:
        # Invalid, error value
        return -1

    def getNewStageNumber(self) -> int:
        guess = 0
        while guess in self._stageMap:
            guess += 1

        return guess

    def trackStage(self, newStage : FeatureStage) -> None:
        stageNumber = newStage.getStageNumber()
        if stageNumber in self._stageMap:
            value = self._stageMap[stageNumber]

            if newStage == value:
                # stage is already added
                if newStage is not value:
                    # but the value is the wrong instance
                    self._stageMap[stageNumber] = newStage
                return

        stageNumber = self.getNewStageNumber()
        newStage.setStageNumber(stageNumber)
        self._stageMap[stageNumber] = newStage

    def forgetStage(self, oldStage : FeatureStage) -> None:
        stage = oldStage.getStageNumber()
        if stage in self._stageMap:
            del self._stageMap[stage]

    def setAxialMethod(self, newAxialMethod : AxialMethod.AxialMethod) -> None:
        self.AxialMethod = AxialMethod.ABSOLUTE

    def setAxialOffset(self, newAxialOffset : float) -> None:
        self.AxialOffset = 0.0
        self.Position = ZERO

    def getBoundingRadius(self) -> float:
        bounding = 0
        for comp in self.getChildren():
            if isinstance(comp, ComponentAssembly):
                bounding = max(bounding, comp.getBoundingRadius())

        return bounding

    def resetListeners(self) -> None:
        self._listenerList = []

    def addComponentChangeListener(self, l : ComponentChangeListener) -> None:
        self._listenerList.append(l)

    def removeComponentChangeListener(self, l : ComponentChangeListener) -> None:
        self._listenerList.remove(l)

    def fireComponentChangeEvent(self, event : int) -> None:
        if not self._eventsEnabled:
            return

        # Notify all components first
        self.componentChanged(event)
        for item in self.getChildren():
            item.Proxy.componentChanged(event)
        self.updateConfigurations()

        self.notifyAllListeners(event)

    def update(self) -> None:
        self.updateStageNumbers()
        self.updateStageMap()
        self.updateConfigurations()
        # self.updateChildren()

    """ Update all the stage numbers based on their position in the component tree """
    def updateStageNumbers(self) -> None:
        stageNr = 0
        for stage in self.getSubStages():
            self.forgetStage(stage)
            stage.setStageNumber(stageNr)
            stageNr += 1

    def updateStageMap(self) -> None:
        for stage in self.getSubStages():
            self.trackStage(stage)

    def updateConfigurations(self) -> None:
        # for config in self._configSet:
        #     config.update()
        pass

    def notifyAllListeners(self, cce : int) -> None:
        # Copy the list before iterating to prevent concurrent modification exceptions.
        # EventListener[] list = listenerList.toArray(new EventListener[0]);
        for l in self._listenerList:
            if isinstance(l, ComponentChangeListener):
                l.componentChanged(cce)
            elif isinstance(l, StateChangeListener):
                l.stateChanged(cce)
