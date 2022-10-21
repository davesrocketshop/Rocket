# ***************************************************************************
# *   Copyright (c) 2021 David Carter <dcarter@davidcarter.ca>              *
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

from App.ShapeComponentAssembly import ShapeComponentAssembly
from App.position import AxialMethod
from App.util.ReferenceType import ReferenceType
import FreeCAD

from PySide import QtCore

from App.util.BoundingBox import BoundingBox
from App.util.Coordinate import ZERO, X_UNIT
from App.util import ReferenceType

from App.events.ComponentChangeEvent import ComponentChangeEvent

from App.ShapeBase import TRACE_POSITION, TRACE_EXECUTION
from App.ShapeComponentAssembly import ShapeComponentAssembly
from App.Constants import FEATURE_ROCKET, FEATURE_STAGE

class ShapeRocket(ShapeComponentAssembly):

    _refType = ReferenceType.MAXIMUM

    _designer = ""
    _stageMap = {}

    def __init__(self, obj):
        super().__init__(obj)
        self.Type = FEATURE_ROCKET

        self.setAxialMethod(AxialMethod.ABSOLUTE)
        
    def execute(self,obj):
        if TRACE_EXECUTION:
            print("E: ShapeRocket::execute(%s)" % (self._obj.Label))

        if not hasattr(obj,'Shape'):
            return

    # Return a bounding box enveloping the rocket.  By definition, the bounding box is a convex hull.
    #
    # Note: this function gets the bounding box for the entire rocket.
    def getBoundingBox (self):
        # return selectedConfiguration.getBoundingBoxAerodynamic();
        return BoundingBox(ZERO, X_UNIT) # default from default flight config

    def getDesigner(self):
        self.checkState()
        return self._designer

    def setDesigner(self, s):
        if s is None:
            s = ""
        self._designer = s
        self.fireComponentChangeEvent(ComponentChangeEvent.NONFUNCTIONAL_CHANGE)
	
    def eligibleChild(self, childType):
        return childType == FEATURE_STAGE

    def getStageCount(self):
        self.checkState()
        return len(self._stageMap)

    def getStageList(self):
        return self._stageMap.values()

    def getStage(self, index):
        return self._stageMap.values()[index]

    # Get the topmost stage, only taking into account active stages from the flight configuration.
    def getTopmostStage(self, config):
        # if (config == null) return null;

        for child in self.getChildren():
            if child.Type == FEATURE_STAGE:
                return child
        # for (int i = 0; i < getChildCount(); i++) {
        #     if (getChild(i) instanceof AxialStage && config.isStageActive(getChild(i).getStageNumber())) {
        #         return (AxialStage) getChild(i);
        #     }
 
        return None

    # Get the bottommost stage, only taking into account active stages from the flight configuration.
    def getBottomCoreStage(self, config):
        # if (config == null) return null;

        for child in reversed(self.getChildren()):
            if child.Type == FEATURE_STAGE:
                return child
        # for (int i = getChildCount() - 1; i >= 0; i--) {
        #     if (getChild(i) instanceof AxialStage && config.isStageActive(getChild(i).getStageNumber())) {
        #         return (AxialStage) getChild(i);
        #     }
 
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
        del self._stageMap[oldStage.getStageNumber()]

    def setAxialMethod(self, newAxialMethod):
        self.AxialMethod = AxialMethod.ABSOLUTE

    def setAxialOffset(self, requestOffset):
        self.AxialOffset = 0.0
        self.Position = ZERO

    def getReferenceType(self):
        self.checkState()
        return self._refType

    def setReferenceType(self, type):
        if self._refType == type:
            return
        self._refType = type

        self.fireComponentChangeEvent(ComponentChangeEvent.NONFUNCTIONAL_CHANGE)
