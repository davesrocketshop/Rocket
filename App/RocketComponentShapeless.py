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
"""Base class for rocket components"""

__title__ = "FreeCAD Rocket Components"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

import FreeCAD
import FreeCADGui
# import copy
import math

import Ui

from PySide.QtCore import QObject, Signal
from App.Utilities import _err
from App.events.ComponentChangeEvent import ComponentChangeEvent
from App.position import AxialMethod

import Ui.Commands as Commands

from App.Constants import FEATURE_ROCKET, FEATURE_STAGE

from DraftTools import translate

class EditedShape(QObject):

    edited = Signal(object)

    def __init__(self):
        super().__init__()

    def setEdited(self, event=None):
        # if event is None:
        #     self.edited.emit()
        # else:
        self.edited.emit(event) #- need to figure this out

    def doConnect(self, fn, type):
        self.edited.connect(fn, type)

    def doDisconnect(self):
        self.edited.connect(None)

class RocketComponentShapeless():

    edited = EditedShape()

    def __init__(self, obj):
        super().__init__()
        self.Type = "RocketComponent"
        self.version = '3.0'

        self._obj = obj
        self._parent = None
        obj.Proxy=self
        self._scratch = {} # None persistent property storage, for import properties and similar

        self._configListeners = []

        if not hasattr(obj, 'Comment'):
            obj.addProperty('App::PropertyString', 'Comment', 'Rocket', translate('App::Property', 'User comment')).Comment = ""

        if not hasattr(obj, 'AxialMethod'):
            obj.addProperty('App::PropertyPythonObject', 'AxialMethod', 'Rocket', translate('App::Property', 'Method for calculating axial offsets')).AxialMethod = AxialMethod.AFTER
        if not hasattr(obj,"AxialOffset"):
            obj.addProperty('App::PropertyDistance', 'AxialOffset', 'Rocket', translate('App::Property', 'Offset from the reference point')).AxialOffset = 0.0
        if not hasattr(obj, 'AngleOffset'):
            obj.addProperty('App::PropertyAngle', 'AngleOffset', 'Rocket', translate('App::Property', 'Angle of offset around the center axis')).AngleOffset = 0.0

        if not hasattr(obj,"Group"):
            obj.addExtension("App::GroupExtensionPython")
    
    def __getstate__(self):
        return self.Type, self.version

    def __setstate__(self, state):
        if state:
            self.Type = state[0]
            self.version = state[1]

    def setScratch(self, name, value):
        self._scratch[name] = value

    def getScratch(self, name):
        return self._scratch[name]

    def isScratch(self, name):
        return name in self._scratch

    def setDefaults(self):
        pass

    def setEdited(self, event=None):
        self.edited.setEdited(event)

    def connect(self, fn, type):
        self.edited.doConnect(fn, type)

    def disconnect(self):
        self.edited.doDisconnect()

    def eligibleChild(self, childType):
        return False

    def getType(self):
        return self.Type

    def isAfter(self):
        return isinstance(self.getAxialMethod(), AxialMethod.AfterAxialMethod)

    def isRocketAssembly(self):
        parent = self.getParent()
        while parent is not None:
            if parent.Type == FEATURE_ROCKET:
                return True

            parent = parent.getParent()

        return False

    def getName(self):
        return self._obj.Label

    def setName(self, name):
        self._obj.Label = name

    def getComment(self):
        return self._obj.Comment

    def setComment(self, comment):
        self._obj.Comment = comment

    def setParent(self, obj):
        if hasattr(obj, "Proxy"):
            parent = obj.Proxy
        else:
            parent = obj

        if self._parent == parent:
            return

        self._parent = parent
        self.fireComponentChangeEvent(ComponentChangeEvent.BOTH_CHANGE)

    """
        recursively set the parents for all children
    """
    def setChildParent(self):
        for child in self.getChildren():
            child.Proxy.setParent(self)
            child.Proxy.setChildParent()

    def getParent(self):
        if not hasattr(self, "_parent") or self._parent is None:
            return None

        if hasattr(self._parent, "Proxy"):
            return self._parent.Proxy
        return self._parent

    def getChildren(self):
        try:
            return self._obj.Group
        except ReferenceError:
            return []

    def setChildren(self, list):
        self._obj.Group = list

    def _getChild(self, index):
        try:
            return self._obj.Group[index]
        except IndexError:
            return None

    def _setChild(self, index, value):
        list = self._obj.Group
        list.insert(index, value)
        self._obj.Group = list

    def _moveChild(self, index, value):
        list = self._obj.Group
        list.remove(value)
        list.insert(index, value)
        self._obj.Group = list

    def _removeChild(self, value):
        list = self._obj.Group
        list.remove(value)
        self._obj.Group = list

    def getPrevious(self, obj=None):
        "Previous item along the rocket axis"
        if obj is None:
            if self._parent is not None:
                return self._parent.Proxy.getPrevious(self)
            else:
                return None

        if hasattr(self._obj, "Group"):
            for index in range(len(self._obj.Group)):
                if self._obj.Group[index].Proxy == obj:
                    if index > 0:
                        return self._obj.Group[index - 1]
            return self._obj

        if self._parent is not None:
            return self._parent.Proxy.getPrevious(obj)

        return None

    def getNext(self, obj=None):
        "Next item along the rocket axis"
        if obj is None:
            if self._parent is not None:
                return self._parent.Proxy.getNext(self)
            else:
                return None

        if hasattr(self._obj, "Group"):
            for index in range(len(self._obj.Group)):
                if self._obj.Group[index].Proxy == obj:
                    if index < len(self._obj.Group) - 1:
                        return self._obj.Group[index + 1]
            return self._obj

        if self._parent is not None:
            return self._parent.Proxy.getNext(obj)

        return None

    def getMaxForwardPosition(self):
        # Return the length of this component along the central axis
        length = 0.0
        if hasattr(self._obj, "Group"):
            for child in self._obj.Group:
                length = max(length, float(child.Proxy.getMaxForwardPosition()))

        return length

    def getForeRadius(self):
        # For placing objects on the outer part of the parent
        return 0.0

    def getAftRadius(self):
        # For placing objects on the outer part of the parent
        return self.getForeRadius()

    def getRadius(self, pos=0):
        return self.getForeRadius()

    def setRadius(self):
        # Calculate any auto radii
        self.getRadius()

    def getOuterRadius(self):
        return 0.0

    def getInnerRadius(self):
        return 0.0

    def setRadialPosition(self, outerRadius, innerRadius):
        pass

    def getRadialPositionOffset(self):
        return 0.0

    def _documentRocket(self):
        for obj in FreeCAD.ActiveDocument.Objects:
            if hasattr(obj, "Proxy"):
                if hasattr(obj.Proxy, "getType"):
                    if obj.Proxy.getType() == FEATURE_ROCKET:
                        return obj.Proxy

        return None

    def moveUp(self):
        # Move the part up in the tree
        if self.getParent() is not None:
            self.getParent()._moveChildUp(self._obj)

            self.fireComponentChangeEvent(ComponentChangeEvent.TREE_CHANGE)
            Ui.Commands.CmdRocket.updateRocket()
        # else:
        #     Commands.CmdStage.addToStage(self)

    def _moveChildUp(self, obj):
        if hasattr(self._obj, "Group"):
            for index, child in enumerate(self._obj.Group):
                if child.Proxy == obj.Proxy:
                    if index > 0:
                        if self._obj.Group[index - 1].Proxy.eligibleChild(obj.Proxy.Type):
                            # Append to the end of the previous entry
                            self._obj.removeObject(obj)
                            parent = self._obj.Group[index - 1]
                            obj.Proxy.setParent(parent)
                            parent.addObject(obj)
                            return
                        else:
                            # Swap with the previous entry
                            self._moveChild(index - 1, obj)
                            return
                    else:
                        # Add to the grandparent ahead of the parent, or add to the next greater parent
                        if self.getParent() is not None:
                            grandparent = self.getParent()._obj
                            parent = self
                            for index1, child in enumerate(grandparent.Group):
                                if child.Proxy == parent and grandparent.Proxy.eligibleChild(obj.Proxy.Type):
                                    parent._obj.removeObject(obj)
                                    obj.Proxy.setParent(grandparent)
                                    group = grandparent.Group
                                    group.insert(index1, obj)
                                    grandparent.Group = group
                                    return
                        else:
                            grandparent = None

                        parent = grandparent
                        while parent is not None:
                            if hasattr(parent, "_obj"):
                                parent = parent._obj
                            if parent.Proxy.eligibleChild(obj.Proxy.Type):
                                self._obj.removeObject(obj)
                                obj.Proxy.setParent(parent)
                                parent.addObject(obj)
                                return
                            elif parent.Proxy.Type == FEATURE_STAGE:
                                # Get the previous eligible feature
                                eligible = parent.Proxy.previousEligibleChild(self, obj)
                                if eligible is not None:
                                    self._obj.removeObject(obj)
                                    obj.Proxy.setParent(None)
                                    eligible.addChildPosition(obj, 0)
                                    return
                                # Otherwise move up a stage
                                grandparent = parent.Proxy.getParent()
                                index = grandparent.getChildIndex(parent.Proxy)
                                while index > 0:
                                    nextStage = grandparent.getChild(index - 1)
                                    eligible = nextStage.Proxy.lastEligibleChild(obj)

                                    if eligible is not None:
                                        self._obj.removeObject(obj)
                                        obj.Proxy.setParent(None)
                                        eligible.addChild(obj)
                                        return

                                    index -= 1
                                return
                            elif parent.Proxy.Type == FEATURE_ROCKET:
                                index = parent.Proxy.getChildIndex(self)
                                while index > 0:
                                    nextStage = parent.Proxy.getChild(index - 1)
                                    eligible = nextStage.Proxy.lastEligibleChild(obj)

                                    if eligible is not None:
                                        self._obj.removeObject(obj)
                                        obj.Proxy.setParent(None)
                                        eligible.addChild(obj)
                                        return
                                    index -= 1
                                return
                            parent = parent.Proxy.getParent()

    def moveDown(self):
        # Move the part up in the tree
        if self.getParent() is not None:
            self.getParent()._moveChildDown(self._obj)

            self.fireComponentChangeEvent(ComponentChangeEvent.TREE_CHANGE)
            Ui.Commands.CmdRocket.updateRocket()

    def _moveChildDown(self, obj):
        if hasattr(self._obj, "Group"):
            last = len(self._obj.Group) - 1
            for index, child in enumerate(self._obj.Group):
                if child.Proxy == obj.Proxy:
                    if index < last:
                        # If the next entry is a group object, add it to that
                        if self._obj.Group[index + 1].Proxy.eligibleChild(obj.Proxy.Type):
                            parent = self._obj.Group[index + 1]
                            self._obj.removeObject(obj)
                            obj.Proxy.setParent(parent)
                            group = parent.Group
                            group.insert(0, obj)
                            parent.Group = group
                            return
                        else:
                            # Swap with the next entry
                            self._moveChild(index + 1, obj)
                            return
                    else:
                        current = self # Move out of the current parent
                        parent = self.getParent()
                        if parent is not None:
                            parent = parent._obj
                        while parent is not None:
                            if parent.Proxy.eligibleChild(obj.Proxy.Type):
                                # parentLen = len(parent.Group)
                                for index1, child in enumerate(parent.Group):
                                    if child.Proxy == current:
                                        self._obj.removeObject(obj)
                                        obj.Proxy.setParent(parent)
                                        group = parent.Group
                                        group.insert(index1 + 1, obj)
                                        parent.Group = group
                                        return
                            else:
                                eligible = parent.Proxy.nextEligibleChild(current, obj)
                                if eligible is not None:
                                    self._obj.removeObject(obj)
                                    obj.Proxy.setParent(None)
                                    eligible.addChildPosition(obj, 0)
                                    return

                                break
                            current = parent
                            parent = parent._parent

        parent = self.getParent()
        if parent is not None:
            if parent.Type == FEATURE_STAGE:
                index = parent.getParent().getChildIndex(parent)
                while index < (parent.getParent().getChildCount() - 1):
                    nextStage = parent.getParent().getChild(index + 1)
                    eligible = nextStage.Proxy.firstEligibleChild(obj)

                    if eligible is not None:
                        self._obj.removeObject(obj)
                        obj.Proxy.setParent(None)
                        eligible.addChildPosition(obj, 0)
                        return

                    # Try the next stage
                    index += 1
            elif parent.Type == FEATURE_ROCKET:
                # The child is at the top level of the stage
                index = parent.getChildIndex(self)
                while index < (parent.getChildCount() - 1):
                    nextStage = parent.getChild(index + 1)
                    eligible = nextStage.Proxy.firstEligibleChild(obj)

                    if eligible is not None:
                        self._obj.removeObject(obj)
                        obj.Proxy.setParent(None)
                        eligible.addChildPosition(obj, 0)
                        return
                    index += 1
        return
    
    def firstEligibleChild(self, obj):
        """ Find the first element eligiible to recieve the child object """
        if self.eligibleChild(obj.Proxy.Type):
            return self
        
        for child in self._obj.Group:
            if child.Proxy.eligibleChild(obj.Proxy.Type):
                return child.Proxy
            # Check the children
            eligible = child.firstEligibleChild(obj)
            if eligible is not None:
                return eligible
            
        return None
    
    def nextEligibleChild(self, current, obj):
        """ Find the first element eligiible to recieve the child object """
        currentFound = False
        for child in self._obj.Group:
            if currentFound:
                if child.Proxy.eligibleChild(obj.Proxy.Type):
                    return child.Proxy
                # Check the children
                eligible = child.firstEligibleChild(obj)
                if eligible is not None:
                    return eligible
            elif child.Proxy == current:
                currentFound = True
            
        return None
    
    def lastEligibleChild(self, obj):
        """ Find the last element eligiible to recieve the child object """
        eligible = None
        if self.eligibleChild(obj.Proxy.Type):
            eligible = self
        for child in self._obj.Group:
            if child.Proxy.eligibleChild(obj.Proxy.Type):
                eligible = child.Proxy
            # Check the children
            lastChild = child.Proxy.lastEligibleChild(obj)
            if lastChild is not None:
                eligible = lastChild
            
        return eligible
    
    def previousEligibleChild(self, current, obj):
        """ Find the last element eligiible to recieve the child object """
        eligible = None
        for child in self._obj.Group:
            if child.Proxy == current:
                return eligible

            if child.Proxy.eligibleChild(obj.Proxy.Type):
                eligible = child.Proxy
            # Check the children
            lastChild = child.Proxy.lastEligibleChild(obj)
            if lastChild is not None:
                eligible = lastChild
            
        return eligible


    def getAxialOffsetFromMethod(self, method):
        parentLength = 0
        if self.getParent() is not None:
            parentLength = self.getParent().getLength()

        if method == AxialMethod.ABSOLUTE:
            return self.getComponentLocations()[0]._x
        else:
            return method.getAsOffset(self._obj.Placement.Base.x, self.getLength(), parentLength)

    def getAxialOffset(self):
        return self._obj.AxialOffset

    def _setAxialOffset(self, method, newAxialOffset):
        newX = math.nan

        if self.getParent() is None:
            # best-effort approximation.  this should be corrected later on in the initialization process.
            newX = newAxialOffset
        elif method == AxialMethod.ABSOLUTE:
            # in this case, this is simply the intended result
            newX = float(newAxialOffset) - float(self.getParent().getComponentLocations()[0]._x)
        elif self.isAfter():
            self.setAfter()
            return
        else:
            newX = method.getAsPosition(float(newAxialOffset), float(self.getLength()), float(self.getParent().getLength())) + float(self.getParent().getPosition().x)

        # snap to zero if less than the threshold 'EPSILON'
        EPSILON = 0.000001
        if EPSILON > math.fabs(newX):
            newX = 0.0
        elif math.isnan(newX):
            raise Exception("setAxialOffset is broken -- attempted to update as NaN: ") # + this.toDebugDetail());

        # store for later:
        self._obj.AxialMethod = method
        self._obj.AxialOffset = newAxialOffset
        self._obj.Placement.Base.x = newX

    def setAxialOffset(self, _pos):
        self.updateBounds()
        self._setAxialOffset(self._obj.AxialMethod, _pos)
        self.fireComponentChangeEvent(ComponentChangeEvent.BOTH_CHANGE)
	
    """  Get the positioning of the component relative to its parent component. """
    def getAxialMethod(self):
        return self._obj.AxialMethod

    """
        Set the positioning of the component relative to its parent component.
        The actual position of the component is maintained to the best ability.
        
        The default implementation is of protected visibility, since many components
        do not support setting the relative position.  A component that does support
        it should override this with a public method that simply calls this
        supermethod AND fire a suitable ComponentChangeEvent.
    """
    def setAxialMethod(self, newAxialMethod) :
        for listener in self._configListeners:
            listener.setAxialMethod(newAxialMethod)

        if type(newAxialMethod) == type(self._obj.AxialMethod):
            # no change.
            return

        # this variable changes the internal representation, but not the physical position
        # the relativePosition (method) is just the lens through which external code may view this component's position. 
        self._obj.AxialMethod = newAxialMethod
        self._obj.AxialOffset = self.getAxialOffsetFromMethod(newAxialMethod)

        # this doesn't cause any physical change-- just how it's described.
        # self.fireComponentChangeEvent(ComponentChangeEvent.BOTH_CHANGE)

    def update(self):
        self._setAxialOffset(self._obj.AxialMethod, self._obj.AxialOffset)
        self._setRotation()

    def updateChildren(self):
        self.update()
        for child in self._obj.Group:
            if hasattr(child, "Proxy"):
                # Sketches for custom fins won't have a proxy
                child.Proxy.updateChildren()

    #  Called when any component in the tree fires a ComponentChangeEvent.  This is by
    #  default a no-op, but subclasses may override this method to e.g. invalidate
    #  cached data.  The overriding method *must* call
    #  <code>super.componentChanged(e)</code> at some point.
    def componentChanged(self, event):
        self.updateChildren()

    def _setRotation(self):
        self._obj.Placement = FreeCAD.Placement(self._obj.Placement.Base, FreeCAD.Vector(1,0,0), self._obj.AngleOffset)

    # Adds a child to the rocket component tree.  The component is added to the end
    # of the component's child list.  This is a helper method that calls
    def addChild(self, component):
        if hasattr(component, "_obj"):
            self.addChildPosition(component._obj, len(self._obj.Group))
        else:
            self.addChildPosition(component, len(self._obj.Group))

    # Adds a child to the rocket component tree.  The component is added to
    # the given position of the component's child list.
    # <p>
    # This method may be overridden to enforce more strict component addition rules.
    # The tests should be performed first and then this method called.
    def addChildPosition(self, component, index):
        if component.Proxy.getParent() is not None:
            raise Exception("component " + component.Proxy.getName() + " is already in a tree")

        # Ensure that the no loops are created in component tree [A -> X -> Y -> B, B.addChild(A)]
        if self.getRoot()._obj == component:
            raise Exception("Component " + component.Proxy.getName() +
                    " is a parent of " + self.getName() + ", attempting to create cycle in tree.")

        if not self.eligibleChild(component.Proxy.Type):
            raise Exception("Component: " + component.Proxy.getName() +
                    " not currently compatible with component: " + self.getName())

        self._setChild(index, component)
        component.Proxy.setParent(self)

        if component.Proxy.getType() == FEATURE_STAGE:
            self.getRocket().trackStage(component.Proxy)

        self.checkComponentStructure()
        component.Proxy.checkComponentStructure()

        self.fireAddRemoveEvent(component)

    # Removes a child from the rocket component tree.
    # (redirect to the removed-by-component
    def removeChildPosition(self, n):
        component = self.getChildren()[n].Proxy
        self.removeChild(component)

    # Removes a child from the rocket component tree.  Does nothing if the component
    # is not present as a child.
    def removeChild(self, component):
        if hasattr(component, "Proxy"):
            component = component.Proxy
        component.checkComponentStructure()


        try:
            self._removeChild(component._obj)
            component.setParent(None)
            
            if component.Type == FEATURE_STAGE:
                self.getRocket().forgetStage(component);

            # Remove sub-stages of the removed component
            for stage in component.getSubStages():
                self.getRocket().forgetStage(stage)
            
            self.checkComponentStructure()
            component.checkComponentStructure()
            
            self.fireAddRemoveEvent(component)
            self.updateBounds()
            
            return True
        except ValueError:
            pass
        return False

    # Returns the position of the child in this components child list, or -1 if the
    # component is not a child of this component.
    def getChildIndex(self, child):
        try:
            self.checkComponentStructure()
            return self.getChildren().index(child._obj)
        except ValueError:
            pass
        return -1

    def getChildPosition(self, child):
        return self.getChildIndex(child)

    def getChildCount(self):
        self.checkComponentStructure()
        return len(self.getChildren())

    def getChild(self, n):
        self.checkComponentStructure()
        return self._obj.Group[n]

    # Get the root component of the component tree.
    def getRoot(self):
        gp = self
        while gp.getParent() is not None:
            gp = gp.getParent()

        return gp

    # Returns the root Rocket component of this component tree.  Throws an
    # IllegalStateException if the root component is not a Rocket.
    def getRocket(self):
        root = self.getRoot()
        if root.getType() == FEATURE_ROCKET:
            return root
        if root == self:
            return None

        raise Exception("getRocket() called with root component " + self.getRoot().getName())

    # Return the Stage component that this component belongs to.  Throws an
    # IllegalStateException if a Stage is not in the parentage of this component.
    def getStage(self):
        current = self
        while current is not None:
            if current.Type == FEATURE_STAGE:
                return current
            current = current.getParent().Proxy

        raise Exception("getStage() called on hierarchy without an FeatureStage.")

    # Returns all the stages that are a child or sub-child of this component.
    def getSubStages(self):
        result = []
        for current in self.getChildren():
            proxy = current.Proxy
            if proxy.Type == FEATURE_STAGE:
                result.append(proxy)

        return result

    # Check that the local component structure is correct.  This can be called after changing
    # the component structure in order to verify the integrity.
    def checkComponentStructure(self):
        if self.getParent() is not None:
            # Test that this component is found in parent's children with == operator
            if not self.containsExact(self.getParent().getChildren(), self):
                raise Exception("Inconsistent component structure detected, parent does not contain this " +
                        "component as a child, parent=" + self.getParent().getName() + " this=" + self.getName())
        for child in self.getChildren():
            if child.isDerivedFrom('Sketcher::SketchObject'):
                continue

            if child.Proxy.getParent() != self:
                message = "Inconsistent component structure detected, child does not have this component " + \
                        "as the parent, this=" + self.getName() + " child=" + child.Proxy.getName() + \
                        " child.parent="
                if child.Proxy.getParent() is None:
                    message += "None"
                else:
                    message += child.Proxy.getParent().getName()
                raise Exception(message)

    # Check whether the list contains exactly the searched-for component (with == operator)
    def containsExact(self, haystack, needle):
        for c in haystack:
            if needle == c.Proxy:
                return True

        return False

    # Fires an AERODYNAMIC_CHANGE, MASS_CHANGE or OTHER_CHANGE event depending on the
    # type of component removed.
    def fireAddRemoveEvent(self, component):
        type = ComponentChangeEvent.TREE_CHANGE
        if hasattr(component, "_obj"):
            group = component._obj.Group
        else:
            group = component.Group
        for obj in group:
            if not obj.isDerivedFrom('Sketcher::SketchObject'):
                proxy = obj.Proxy
                if proxy.isAerodynamic():
                    type |= ComponentChangeEvent.AERODYNAMIC_CHANGE
                if proxy.isMassive():
                    type |= ComponentChangeEvent.MASS_CHANGE

        self.fireComponentChangeEvent(type);

    def fireComponentChangeEvent(self, event):
        if self.getParent() is None: # or self._bypassComponentChangeEvent:
            return

        self.getRoot().fireComponentChangeEvent(event)

    def setAfter(self):
        if self.getParent() is None:
            # Probably initialization order issue.  Ignore for now.
            return
        
        self._obj.AxialMethod = AxialMethod.AFTER
        self._obj.AxialOffset = 0.0

        # Stages are reversed from OpenRocket
        count = self.getParent().getChildCount()
        
        # if first component in the stage. => position from the top of the parent
        thisIndex = self.getParent().getChildIndex(self)
        if thisIndex == 0:
            self._obj.Placement.Base.x = self.getParent()._obj.Placement.Base.x
            # self._obj.Placement.Base.x = 0.0
        elif 0 < thisIndex:
            index = thisIndex - 1
            referenceComponent = self.getParent()._getChild( index )
            # while referenceComponent is not None:
            #     if referenceComponent.Proxy.isAfter():
            #         break
            #     index = index + 1
            #     referenceComponent = self.getParent()._getChild( index )

            if referenceComponent is None:
                self._obj.Placement.Base.x = self.getParent()._obj.Placement.Base.x
                return
        
            refLength = float(referenceComponent.Proxy.getLength())
            refRelX = float(referenceComponent.Placement.Base.x)

            self._obj.Placement.Base.x = refRelX + refLength
            # self._obj.Placement.Base.x = refRelX - (refLength + float(self.getLength()))

    """
        Get the characteristic length of the component, for example the length of a body tube
        of the length of the root chord of a fin.  This is used in positioning the component
        relative to its parent.
        
        If the length of a component is settable, the class must define the setter method
        itself.
    """
    def getLength(self):
        # Return the length of this component along the central axis
        return 0

    def setColor(self, red, green, blue, alpha):
        if hasattr(self._obj.ViewObject.Proxy, "setColor"):
            self._obj.ViewObject.Proxy.setColor(red, green, blue, alpha)

    def setAmbient(self, red, green, blue, alpha):
        if hasattr(self._obj.ViewObject.Proxy, "setAmbient"):
            self._obj.ViewObject.Proxy.setAmbient(red, green, blue, alpha)

    def setDiffuse(self, red, green, blue, alpha):
        if hasattr(self._obj.ViewObject.Proxy, "setDiffuse"):
            self._obj.ViewObject.Proxy.setDiffuse(red, green, blue, alpha)

    def setSpecular(self, red, green, blue, alpha):
        if hasattr(self._obj.ViewObject.Proxy, "setSpecular"):
            self._obj.ViewObject.Proxy.setSpecular(red, green, blue, alpha)

    def setShininess(self, shininess):
        if hasattr(self._obj.ViewObject.Proxy, "setShininess"):
            self._obj.ViewObject.Proxy.setShininess(shininess)

    # This will be implemented in the derived class
    def execute(self, obj):
        _err("No execute method defined for %s" % (self.__class__.__name__))
