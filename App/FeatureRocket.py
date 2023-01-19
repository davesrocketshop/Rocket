# ***************************************************************************
# *   Copyright (c) 2021-2023 David Carter <dcarter@davidcarter.ca>         *
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

import FreeCAD

from App.interfaces.ComponentChangeListener import ComponentChangeListener
from App.interfaces.StateChangeListener import StateChangeListener

from App.ComponentAssembly import ComponentAssembly
from App.position import AxialMethod

from App.util.BoundingBox import BoundingBox
from App.util.Coordinate import ZERO, X_UNIT
from App.util.UniqueID import UniqueID
from App.util import ReferenceType

from App.events.ComponentChangeEvent import ComponentChangeEvent

from App.Constants import FEATURE_ROCKET, FEATURE_STAGE

class FeatureRocket(ComponentAssembly, ComponentChangeListener):

    """
    List of component change listeners.
    """
    _listenerList = []

    """
    When freezeList != null, events are not dispatched but stored in the list.
    When the structure is thawed, a single combined event will be fired.
    """
    _freezeList = None

    _refType = ReferenceType.MAXIMUM

    _modID = -1
    _massModID = -1
    _aeroModID = -1
    _treeModID = -1
    _functionalModID = -1

    _eventsEnabled = False

    _designer = ""
    _stageMap = {}

    def __init__(self, obj):
        super().__init__(obj)
        self.Type = FEATURE_ROCKET

        self.initialize()

    def initialize(self):

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

    def setDefaults(self):
        super().setDefaults()

    def onDocumentRestored(self, obj):
        FeatureRocket(obj)
        self._obj = obj
        obj.Proxy=self # Required because of the local variables
        self.initialize()
        self.setChildParent()
        # self.updateChildren()
        self._enableEvents(True)

    """
        Enable the monitoring, relay and production of events in this rocket instance.
    """
    def enableEvents(self, enable=True):
        self._enableEvents(enable)
        self.updateChildren()

    def _enableEvents(self, enable):
        if self._eventsEnabled and enable:
            return
        
        if enable:
            self._eventsEnabled = True
            self.fireComponentChangeEvent(ComponentChangeEvent.AEROMASS_CHANGE)
        else:
            self._eventsEnabled = False
        
    def execute(self,obj):
        # self.updateChildren()
        if not hasattr(obj,'Shape'):
            return

    # Return a bounding box enveloping the rocket.  By definition, the bounding box is a convex hull.
    #
    # Note: this function gets the bounding box for the entire rocket.
    def getBoundingBox (self):
        # return selectedConfiguration.getBoundingBoxAerodynamic();
        return BoundingBox(ZERO, X_UNIT) # default from default flight config

    def getDesigner(self):
        return self._designer

    def setDesigner(self, s):
        if s is None:
            s = ""
        self._designer = s
        self.fireComponentChangeEvent(ComponentChangeEvent.NONFUNCTIONAL_CHANGE)
	
    def eligibleChild(self, childType):
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
    def getModID(self):
        return self._modID

    """
        Return the non-negative mass modification ID of this rocket.  See
        {@link #getModID()} for details.
    """
    def getMassModID(self):
        return self._massModID

    """
        Return the non-negative aerodynamic modification ID of this rocket.  See
        {@link #getModID()} for details.
    """
    def getAerodynamicModID(self):
        return self._aeroModID

    """
        Return the non-negative tree modification ID of this rocket.  See
        {@link #getModID()} for details.
    """
    def getTreeModID(self):
        return self.treeModID

    """
        Return the non-negative functional modificationID of this rocket.
        This changes every time a functional change occurs.
    """
    def getFunctionalModID(self):
        return self._functionalModID

    def getStageCount(self):
        return len(self._stageMap)

    def getStageList(self):
        return self._stageMap.values()

    def getStage(self, index):
        return self._stageMap.values()[index]

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

    def getStageNumber(self):
        # Invalid, error value
        return -1

    def getNewStageNumber(self):
        guess = 0
        while guess in self._stageMap:
            guess += 1

        return guess

    def trackStage(self, newStage):
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

    def forgetStage(self, oldStage):
        stage = oldStage.getStageNumber()
        if stage in self._stageMap:
            del self._stageMap[stage]

    def setAxialMethod(self, newAxialMethod):
        self.AxialMethod = AxialMethod.ABSOLUTE

    def setAxialOffset(self, requestOffset):
        self.AxialOffset = 0.0
        self.Position = ZERO

    def getReferenceType(self):
        return self._refType

    def setReferenceType(self, type):
        if self._refType == type:
            return
        self._refType = type

        self.fireComponentChangeEvent(ComponentChangeEvent.NONFUNCTIONAL_CHANGE)

    def getCustomReferenceLength(self):
        return self._customReferenceLength

    def setCustomReferenceLength(self, length):
        if self._customReferenceLength == length:
            return
        
        self._customReferenceLength = max(length, 0.001)
        
        if self._refType == ReferenceType.CUSTOM:
            self.fireComponentChangeEvent(ComponentChangeEvent.NONFUNCTIONAL_CHANGE)

    def getBoundingRadius(self):
        bounding = 0
        for comp in self.getChildren():
            if isinstance(comp, ComponentAssembly):
                bounding = max(bounding, comp.getBoundingRadius())

        return bounding

    # Set whether the rocket has a perfect finish.  This will affect whether the
    # boundary layer is assumed to be fully turbulent or not.
    def setPerfectFinish(self, perfectFinish):
        if self._perfectFinish == perfectFinish:
            return
        self._perfectFinish = perfectFinish
        self.fireComponentChangeEvent(ComponentChangeEvent.AERODYNAMIC_CHANGE)

    # Get whether the rocket has a perfect finish.
    def isPerfectFinish(self):
        return self._perfectFinish
    
    def getFlightConfigurationCount(self):
        return len(self._configSet)

    def resetListeners(self):
        self._listenerList = []

    def addComponentChangeListener(self, l):
        self._listenerList.append(l)

    def removeComponentChangeListener(self, l):
        self._listenerList.remove(l)

    def fireComponentChangeEvent(self, cce):
        if not self._eventsEnabled:
            return
        
        # Check whether frozen
        if self._freezeList is not None:
            # log.debug("Rocket is in frozen state, adding event " + cce + " info freeze list");
            self._freezeList.append(cce)
            return

    
        # Notify all components first
        self.componentChanged(cce)
        for item in self.getChildren():
            item.Proxy.componentChanged(cce)
        self.updateConfigurations()

        self.notifyAllListeners(cce)
            
        # } finally {
        #     mutex.unlock("fireComponentChangeEvent");

    def update(self):
        self.updateStageNumbers()
        self.updateStageMap()
        self.updateConfigurations()
        # self.updateChildren()

    """ Update all the stage numbers based on their position in the component tree """
    def updateStageNumbers(self):
        stageNr = 0
        for stage in self.getSubStages():
            self.forgetStage(stage)
            stage.setStageNumber(stageNr)
            stageNr += 1

    def updateStageMap(self):
        for stage in self.getSubStages():
            self.trackStage(stage)

    def updateConfigurations(self):
        # for config in self._configSet:
        #     config.update()
        pass

    def notifyAllListeners(self, cce):
        # Copy the list before iterating to prevent concurrent modification exceptions.
        # EventListener[] list = listenerList.toArray(new EventListener[0]);
        for l in self._listenerList:
            if isinstance(l, ComponentChangeListener):
                l.componentChanged(cce)
            elif isinstance(l, StateChangeListener):
                l.stateChanged(cce)

    """ Freezes the rocket structure from firing any events.  This may be performed to
        combine several actions on the structure into a single large action.
        <code>thaw()</code> must always be called afterwards.
        
        NOTE:  Always use a try/finally to ensure <code>thaw()</code> is called:
        <pre>
            Rocket r = c.getRocket();
            try {
                r.freeze();
                // do stuff
            } finally {
                r.thaw();
            }
        </pre>"""
    def freeze(self):
        if self._freezeList is None:
            self._freezeList = []
        else:
            raise Exception("Attempting to freeze Rocket when it is already frozen, freezeList=" + self._freezeList)

    """ 
        Thaws a frozen rocket structure and fires a combination of the events fired during
        the freeze.  The event type is a combination of those fired and the source is the
        last component to have been an event source.
    """
    def thaw(self):
        if self._freezeList is None:
            raise Exception("Attempting to thaw Rocket when it is not frozen")
            return

        if len(self._freezeList) == 0:
            # log.warn("Thawing rocket with no changes made");
            self._freezeList = None
            return

        type = 0
        c = None
        for e in self._freezeList:
            type = type | e.getType()
            c = e.getSource()
        self._freezeList = None
    
        self.fireComponentChangeEvent(ComponentChangeEvent(c, type))
