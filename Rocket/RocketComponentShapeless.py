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
"""Base class for rocket components"""

__title__ = "FreeCAD Rocket Components"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

from abc import abstractmethod
from typing import Self, Any

import FreeCAD
import Part
import math

translate = FreeCAD.Qt.translate

import Ui

from Rocket.Utilities import EPSILON
from Rocket.position import AxialMethod

from Rocket.interfaces.Observer import Subject, Observer
from Rocket.util.Coordinate import Coordinate
from Rocket.position.AxialMethod import AXIAL_METHOD_MAP

import Ui.Commands as Commands

from Rocket.Constants import FEATURE_ROCKET, FEATURE_STAGE, FEATURE_PARALLEL_STAGE, FEATURE_POD
from Rocket.Constants import LOCATION_SURFACE, LOCATION_CENTER

from Rocket.Exceptions import UnsupportedConfiguration, ObjectNotFound

class RocketComponentShapeless(Subject, Observer):

    def __init__(self, obj : Any) -> None:
        super().__init__()
        self.Type = "RocketComponent"
        self.version = '3.0'

        self._obj = obj
        self._parent = None
        obj.Proxy=self
        self._scratch = {} # Non-persistent property storage, for import properties and similar

        self._updating = False

        if not hasattr(obj, 'Comment'):
            obj.addProperty('App::PropertyString', 'Comment', 'RocketComponent', translate('App::Property', 'User comment')).Comment = ""

        if not hasattr(obj, 'AxialMethod'):
            obj.addProperty('App::PropertyPythonObject', 'AxialMethod', 'RocketComponent', translate('App::Property', 'Method for calculating axial offsets')).AxialMethod = AxialMethod.AFTER
        if not hasattr(obj,"AxialOffset"):
            obj.addProperty('App::PropertyDistance', 'AxialOffset', 'RocketComponent', translate('App::Property', 'Offset from the reference point')).AxialOffset = 0.0
        if not hasattr(obj, 'AngleOffset'):
            obj.addProperty('App::PropertyAngle', 'AngleOffset', 'RocketComponent', translate('App::Property', 'Angle of offset around the center axis')).AngleOffset = 0.0

        if not hasattr(obj, 'RadialReference'):
            obj.addProperty('App::PropertyEnumeration', 'RadialReference', 'RocketComponent', translate('App::Property', 'Reference location for the radial offset'))
            obj.RadialReference = [
                        LOCATION_SURFACE,
                        LOCATION_CENTER
                    ]
            obj.RadialReference = LOCATION_SURFACE
        else:
            obj.RadialReference = [
                        LOCATION_SURFACE,
                        LOCATION_CENTER
                    ]

        if not hasattr(obj, 'RadialOffset'):
            obj.addProperty('App::PropertyDistance', 'RadialOffset', 'RocketComponent', translate('App::Property', 'Radial offset from the reference')).RadialOffset = 0.0

        # Basic scaling options
        if not hasattr(obj, 'Scale'):
            obj.addProperty('App::PropertyBool', 'Scale', 'RocketComponent', translate('App::Property', 'Scale the object')).Scale = False
        if not hasattr(obj, 'ScaleOverride'):
            obj.addProperty('App::PropertyBool', 'ScaleOverride', 'RocketComponent', translate('App::Property', 'Overriding the scale set by the parent')).ScaleOverride = False
        if not hasattr(obj, 'ScaleByValue'):
            obj.addProperty('App::PropertyBool', 'ScaleByValue', 'RocketComponent', translate('App::Property', 'Scale the object by value')).ScaleByValue = True
        if not hasattr(obj, 'ScaleValue'):
            obj.addProperty('App::PropertyLength', 'ScaleValue', 'RocketComponent', translate('App::Property', 'Scaling value or dimension')).ScaleValue = 1.0

        if not hasattr(obj,"Group"):
            obj.addExtension("App::GroupExtensionPython")

    def __getstate__(self) -> tuple:
        return self.Type, self.version

    def __setstate__(self, state : tuple) -> None:
        if state:
            self.Type = state[0]
            self.version = state[1]

    def setScratch(self, name : str, value : str) -> None:
        self._scratch[name] = value

    def getScratch(self, name : str) -> str:
        return self._scratch[name]

    def isScratch(self, name : str) -> bool:
        return name in self._scratch

    def setDefaults(self) -> None:
        pass

    def setEdited(self, event=None) -> None:
        self.notifyComponentChanged()

    def eligibleChild(self, childType : str) -> bool:
        return False

    def getType(self) -> str:
        return self.Type

    def isAfter(self) -> bool:
        return isinstance(self.getAxialMethod(), AxialMethod.AfterAxialMethod)

    def isRocketAssembly(self) -> bool:
        parent = None
        if self.hasParent():
            parent = self.getParent()
        while parent:
            if parent.Type == FEATURE_ROCKET:
                return True

            if parent.hasParent():
                parent = parent.getParent()
            else:
                parent = None

        return False

    def getName(self) -> str:
        return self._obj.Label

    def setName(self, name : str) -> None:
        self._obj.Label = name

    def getComment(self) -> str:
        return self._obj.Comment

    def setComment(self, comment : str) -> None:
        self._obj.Comment = comment

    def setParent(self, obj : Any) -> None:
        if hasattr(obj, "Proxy"):
            parent = obj.Proxy
        else:
            parent = obj

        if self._parent == parent:
            return

        self._parent = parent
        self.notifyComponentChanged()

    """
        recursively set the parents for all children
    """
    def setChildParent(self) -> None:
        for child in self.getChildren():
            child.Proxy.setParent(self)
            child.Proxy.setChildParent()

    def hasParent(self) -> bool:
        if not hasattr(self, "_parent") or self._parent is None:
            return False

        return True

    def getParent(self) -> Any:
        if not self.hasParent():
            raise ObjectNotFound()

        return self.getProxy(self._parent)

    def hasChildren(self) -> bool:
        if hasattr(self._obj, "Group") and len(self._obj.Group) > 0:
            return True
        return False

    def getChildren(self) -> list:
        if hasattr(self._obj, "Group"):
            return self._obj.Group
        return []

    def setChildren(self, list : list) -> None:
        self._obj.Group = list

    def _getChild(self, index : int) -> Any:
        try:
            return self._obj.Group[index]
        except IndexError:
            return None

    def _setChild(self, index : int, value : Any) -> None:
        list = self._obj.Group
        list.insert(index, value)
        self._obj.Group = list

    def _moveChild(self, index : int, value : Any) -> None:
        list = self._obj.Group
        list.remove(value)
        list.insert(index, value)
        self._obj.Group = list

    def _removeChild(self, value : Any) -> None:
        list = self._obj.Group
        list.remove(value)
        self._obj.Group = list

    def getProxy(self, obj : Any) -> Any:
        if hasattr(obj, "Proxy"):
            return obj.Proxy
        return obj

    def getPrevious(self, obj : Any = None) -> Any:
        "Previous item along the rocket axis"
        if obj is None:
            if self._parent:
                return self.getProxy(self._parent).getPrevious(self)
            else:
                return None

        if hasattr(self._obj, "Group"):
            for index in range(len(self._obj.Group)):
                if self._obj.Group[index].Proxy == obj:
                    if index > 0:
                        return self._obj.Group[index - 1]
            return self._obj

        if self._parent:
            return self.getProxy(self._parent).getPrevious(obj)

        return None

    def getNext(self, obj : Any = None) -> Any:
        "Next item along the rocket axis"
        if obj is None:
            if self._parent:
                return self.getProxy(self._parent).getNext(self)
            else:
                return None

        if hasattr(self._obj, "Group"):
            for index in range(len(self._obj.Group)):
                if self._obj.Group[index].Proxy == obj:
                    if index < len(self._obj.Group) - 1:
                        return self._obj.Group[index + 1]
            return self._obj

        if self._parent:
            return self.getProxy(self._parent).getNext(obj)

        return None

    def getMaxForwardPosition(self) -> float:
        # Return the length of this component along the central axis
        length = 0.0
        if hasattr(self._obj, "Group"):
            for child in self._obj.Group:
                length = max(length, float(child.Proxy.getMaxForwardPosition()))

        return length

    def getForeRadius(self) -> float:
        # For placing objects on the outer part of the parent
        return 0.0

    def getAftRadius(self) -> float:
        # For placing objects on the outer part of the parent
        return self.getForeRadius()

    def getRadius(self, pos : float) -> float:
        return self.getForeRadius()

    def setRadius(self) -> None:
        # Calculate any auto radii
        self.getRadius(0)

    def getOuterRadius(self, pos : float) -> float:
        return 0.0

    def getInnerRadius(self, pos : float) -> float:
        return 0.0

    def getRadialPositionOffset(self) -> float:
        return 0.0

    def _documentRocket(self) -> Any:
        for obj in FreeCAD.ActiveDocument.Objects:
            if hasattr(obj, "Proxy"):
                if hasattr(obj.Proxy, "getType"):
                    if obj.Proxy.getType() == FEATURE_ROCKET:
                        return obj.Proxy

        return None

    def moveUp(self) -> None:
        # Move the part up in the tree
        if self.hasParent():
            self.getParent()._moveChildUp(self._obj)

            self.notifyComponentChanged()
            Commands.CmdRocket.updateRocket()
        # else:
        #     Commands.CmdStage.addToStage(self)

    def _moveChildUp(self, obj : Any) -> None:
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
                        if self.hasParent():
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
                        while parent:
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
                                if eligible:
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

                                    if eligible:
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

                                    if eligible:
                                        self._obj.removeObject(obj)
                                        obj.Proxy.setParent(None)
                                        eligible.addChild(obj)
                                        return
                                    index -= 1
                                return
                            if parent.Proxy.hasParent():
                                parent = parent.Proxy.getParent()
                            else:
                                parent = None

    def moveDown(self) -> None:
        # Move the part up in the tree
        if self.hasParent():
            self.getParent()._moveChildDown(self._obj)

            self.notifyComponentChanged()
            Ui.Commands.CmdRocket.updateRocket()

    def _moveChildDown(self, obj : Any) -> None:
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
                        parent = None
                        if self.hasParent():
                            parent = self.getParent()._obj
                        while parent:
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
                                if eligible:
                                    self._obj.removeObject(obj)
                                    obj.Proxy.setParent(None)
                                    eligible.addChildPosition(obj, 0)
                                    return

                                break
                            current = parent
                            parent = parent._parent

        if self.hasParent():
            parent = self.getParent()
            if parent.Type == FEATURE_STAGE:
                index = parent.getParent().getChildIndex(parent)
                while index < (parent.getParent().getChildCount() - 1):
                    nextStage = parent.getParent().getChild(index + 1)
                    eligible = nextStage.Proxy.firstEligibleChild(obj)

                    if eligible:
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

                    if eligible:
                        self._obj.removeObject(obj)
                        obj.Proxy.setParent(None)
                        eligible.addChildPosition(obj, 0)
                        return
                    index += 1
        return

    def firstEligibleChild(self, obj : Any) -> Any:
        """ Find the first element eligiible to receive the child object """
        if self.eligibleChild(obj.Proxy.Type):
            return self

        for child in self._obj.Group:
            if child.Proxy.eligibleChild(obj.Proxy.Type):
                return child.Proxy
            # Check the children
            eligible = child.firstEligibleChild(obj)
            if eligible:
                return eligible

        return None

    def nextEligibleChild(self, current : Any, obj : Any) -> Any:
        """ Find the first element eligiible to receive the child object """
        currentFound = False
        for child in self._obj.Group:
            if currentFound:
                if child.Proxy.eligibleChild(obj.Proxy.Type):
                    return child.Proxy
                # Check the children
                eligible = child.firstEligibleChild(obj)
                if eligible:
                    return eligible
            elif child.Proxy == current:
                currentFound = True

        return None

    def lastEligibleChild(self, obj : Any) -> Any:
        """ Find the last element eligiible to receive the child object """
        eligible = None
        if self.eligibleChild(obj.Proxy.Type):
            eligible = self
        for child in self._obj.Group:
            if child.Proxy.eligibleChild(obj.Proxy.Type):
                eligible = child.Proxy
            # Check the children
            lastChild = child.Proxy.lastEligibleChild(obj)
            if lastChild:
                eligible = lastChild

        return eligible

    def previousEligibleChild(self, current : Any, obj : Any) -> Any:
        """ Find the last element eligiible to receive the child object """
        eligible = None
        for child in self._obj.Group:
            if child.Proxy == current:
                return eligible

            if child.Proxy.eligibleChild(obj.Proxy.Type):
                eligible = child.Proxy
            # Check the children
            lastChild = child.Proxy.lastEligibleChild(obj)
            if lastChild:
                eligible = lastChild

        return eligible

    def setLocationReference(self, reference : str) -> None:
        self.setAxialMethod(AXIAL_METHOD_MAP[reference])

    def getAxialOffsetFromMethod(self, method : AxialMethod.AxialMethod) -> float:
        parentLength = 0
        if self.hasParent():
            parent = self.getParent()
            if parent.Type in [FEATURE_PARALLEL_STAGE, FEATURE_POD]:
                parentLength = 0
            else:
                parentLength = self.getParent().getLength()

        if method == AxialMethod.ABSOLUTE:
            return float(self.getComponentLocations()[0].x)
        else:
            return method.getAsOffset(self._obj.Placement.Base.x, self.getLength(), parentLength)

    def getAxialOffset(self) -> float:
        return float(self._obj.AxialOffset)

    def _setAxialOffset(self, method : AxialMethod.AxialMethod, newAxialOffset : float) -> None:
        newX = math.nan

        if not self.hasParent():
            # best-effort approximation.  this should be corrected later on in the initialization process.
            newX = newAxialOffset
        elif method == AxialMethod.ABSOLUTE:
            # in this case, this is simply the intended result
            newX = float(newAxialOffset) - float(self.getParent().getComponentLocations()[0].x)
        else:
            parent = self.getParent()
            if self.isAfter() and (parent.getChildIndex(self) > 0 or parent.Type not in [FEATURE_PARALLEL_STAGE, FEATURE_POD]):
                self.setAfter()
                return
            else:
                newX = method.getAsPosition(float(newAxialOffset), float(self.getLength()), float(parent.getLength()))
                if parent.Type not in [FEATURE_PARALLEL_STAGE, FEATURE_POD]:
                    newX += float(parent.getPosition().x)

        # snap to zero if less than the threshold 'EPSILON'
        if EPSILON > math.fabs(newX):
            newX = 0.0
        elif math.isnan(newX):
            raise Exception(translate("Rocket", "setAxialOffset is broken -- attempted to update as NaN: ")) # + this.toDebugDetail());

        # store for later:
        self._obj.AxialMethod = method
        self._obj.AxialOffset = newAxialOffset
        self._obj.Placement.Base.x = newX

    # the default implementation is mostly a placeholder here, however in inheriting classes,
    # this function is useful to indicate adjacent placements and view sizes
    def updateBounds(self) -> None:
        return

    def setAxialOffset(self, newAxialOffset : float) -> None:
        self.updateBounds()
        self._setAxialOffset(self._obj.AxialMethod, newAxialOffset)
        self.notifyComponentChanged()

    """  Get the positioning of the component relative to its parent component. """
    def getAxialMethod(self) -> AxialMethod.AxialMethod:
        return self._obj.AxialMethod

    """
        Set the positioning of the component relative to its parent component.
        The actual position of the component is maintained to the best ability.

        The default implementation is of protected visibility, since many components
        do not support setting the relative position.  A component that does support
        it should override this with a public method that simply calls this
        supermethod AND fire a suitable event.
    """
    def setAxialMethod(self, newAxialMethod : AxialMethod.AxialMethod) -> None:
        if type(newAxialMethod) == type(self._obj.AxialMethod):
            # no change.
            return

        # this variable changes the internal representation, but not the physical position
        # the relativePosition (method) is just the lens through which external code may view this component's position.
        self._obj.AxialMethod = newAxialMethod
        self._obj.AxialOffset = self.getAxialOffsetFromMethod(newAxialMethod)

        # this doesn't cause any physical change-- just how it's described.
        # self.notifyComponentChanged()

    def update(self) -> None:
        self._setAxialOffset(self._obj.AxialMethod, self._obj.AxialOffset)
        self._setRotation()

        from Rocket.position.RadiusPositionable import RadiusPositionable # Avoid a circular import
        if self.hasParent() and isinstance(self, RadiusPositionable):
            try:
                radius = self._obj.RadiusMethod.getRadius(self.getParent(), self, self._obj.RadiusOffset.Value)	# Radius from the parent's center
                print(f"Radius: {radius}")
                self.setRadiusByMethod(self._obj.RadiusMethod, radius)
            except Exception as ex:
                print(ex)

    def updateChildren(self) -> None:
        if not self._updating:
            # print(f"updating {self.getName()}")
            self.update()
            self._updating = True
            self.execute(self._obj)
            for child in self._obj.Group:
                if hasattr(child, "Proxy"):
                    # Sketches for custom fins won't have a proxy
                    child.Proxy.updateChildren()
            self._updating = False

    #  Called when any component in the tree fires a component change notification.  This is by
    #  default a no-op, but subclasses may override this method to e.g. invalidate
    #  cached data.  The overriding method *must* call
    #  <code>super.componentChanged(e)</code> at some point.
    def componentChanged(self) -> None:
        self.updateChildren()

    def _setRotation(self) -> None:
        self._obj.Placement = FreeCAD.Placement(self._obj.Placement.Base, FreeCAD.Vector(1,0,0), self._obj.AngleOffset)

    # Adds a child to the rocket component tree.  The component is added to the end
    # of the component's child list.  This is a helper method that calls
    def addChild(self, component : Self) -> None:
        if hasattr(component, "_obj"):
            self.addChildPosition(component._obj, len(self._obj.Group))
        else:
            self.addChildPosition(component, len(self._obj.Group))

    # Adds a child to the rocket component tree.  The component is added to
    # the given position of the component's child list.
    # <p>
    # This method may be overridden to enforce more strict component addition rules.
    # The tests should be performed first and then this method called.
    def addChildPosition(self, component : Any, index : int) -> None:
        if component.Proxy.hasParent():
            raise Exception(translate("Rocket", "component {} is already in a tree").format(component.Proxy.getName()))

        # Ensure that the no loops are created in component tree [A -> X -> Y -> B, B.addChild(A)]
        if self.getRoot()._obj == component:
            raise Exception(translate("Rocket", "Component {} is a parent of {}, attempting to create cycle in tree.")
                            .format(component.Proxy.getName(), self.getName()))

        if not self.eligibleChild(component.Proxy.Type):
            raise UnsupportedConfiguration(translate("Rocket", "Unsupported configuration: {}  not currently compatible with component: {}")
                            .format(component.Proxy.getName(), self.getName()))

        self._setChild(index, component)
        component.Proxy.setParent(self)

        if component.Proxy.getType() == FEATURE_STAGE:
            rocket = self.getRocket()
            if rocket:
                rocket.trackStage(component.Proxy)

        self.checkComponentStructure()
        component.Proxy.checkComponentStructure()

        self.notifyComponentChanged()

    # Removes a child from the rocket component tree.
    # (redirect to the removed-by-component
    def removeChildPosition(self, n : int) -> None:
        component = self.getChildren()[n].Proxy
        self.removeChild(component)

    # Removes a child from the rocket component tree.  Does nothing if the component
    # is not present as a child.
    def removeChild(self, component : Any) -> bool:
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

            self.notifyComponentChanged()
            self.updateBounds()

            return True
        except ValueError:
            pass
        return False

    # Returns the position of the child in this components child list, or -1 if the
    # component is not a child of this component.
    def getChildIndex(self, child : Self) -> int:
        try:
            self.checkComponentStructure()
            return self.getChildren().index(child._obj)
        except ValueError:
            pass
        return -1

    def getChildPosition(self, child : Self) -> int:
        return self.getChildIndex(child)

    def getChildCount(self) -> int:
        self.checkComponentStructure()
        return len(self.getChildren())

    def getChild(self, n : int) -> Any:
        self.checkComponentStructure()
        return self._obj.Group[n]

    # Get the root component of the component tree.
    def getRoot(self) -> Any:
        gp = self
        if gp:
            while gp.hasParent():
                gp = gp.getParent()

        return gp

    # Returns the root Rocket component of this component tree.  Throws an
    # IllegalStateException if the root component is not a Rocket.
    def getRocket(self) -> Any:
        root = self.getRoot()
        if root is None or root == self:
            return None
        if root.getType() == FEATURE_ROCKET:
            return root

        raise Exception(translate("Rocket", "getRocket() called with root component {}").format(self.getRoot().getName()))

    # Return the Stage component that this component belongs to.  Throws an
    # IllegalStateException if a Stage is not in the parentage of this component.
    def getStage(self) -> Any:
        current = self
        while current:
            if current.Type == FEATURE_STAGE:
                return current
            if current.hasParent():
                current = current.getParent()
            else:
                raise Exception(translate("Rocket", "getStage() called on hierarchy without a FeatureStage component."))

    # Returns all the stages that are a child or sub-child of this component.
    def getSubStages(self) -> list[Any]:
        result = []
        for current in self.getChildren():
            proxy = self.getProxy(current)
            if proxy.Type == FEATURE_STAGE:
                result.append(proxy)

        return result

    # Check that the local component structure is correct.  This can be called after changing
    # the component structure in order to verify the integrity.
    def checkComponentStructure(self) -> None:
        if self.hasParent():
            # Test that this component is found in parent's children with == operator
            if not self.containsExact(self.getParent().getChildren(), self):
                raise Exception(translate("Rocket", "Inconsistent component structure detected, parent does not contain this " +
                        "component as a child, parent={} this={}").format(self.getParent().getName(), self.getName()))
        for child in self.getChildren():
            if child.isDerivedFrom('Sketcher::SketchObject'):
                continue

            if not child.Proxy.hasParent() or child.Proxy.getParent() != self:
                message = translate("Rocket", "Inconsistent component structure detected, child does not have this component " + \
                        "as the parent, this={} child={} child.parent={}")
                if not child.Proxy.hasParent() is None:
                    message = message.format(self.getName(), child.Proxy.getName(), "None")
                else:
                    message = message.format(self.getName(), child.Proxy.getName(), child.Proxy.getParent().getName())
                raise Exception(message)

    # Check whether the list contains exactly the searched-for component (with == operator)
    def containsExact(self, haystack : Any, needle : Any) -> bool:
        for c in haystack:
            if needle == c.Proxy:
                return True

        return False

    def notifyComponentChanged(self) -> None:
        if not self.hasParent():
            return

        root = self.getRoot()
        if root:
            root.notifyComponentChanged()

    def setAfter(self) -> None:
        if not self.hasParent():
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
        elif 0 < thisIndex:
            index = thisIndex - 1
            referenceComponent = self.getParent()._getChild( index )

            if referenceComponent is None:
                self._obj.Placement.Base.x = self.getParent()._obj.Placement.Base.x
                return

            refLength = float(referenceComponent.Proxy.getLength())
            refRelX = float(referenceComponent.Placement.Base.x)

            self._obj.Placement.Base.x = refRelX + refLength

    """
        Get the characteristic length of the component, for example the length of a body tube
        of the length of the root chord of a fin.  This is used in positioning the component
        relative to its parent.

        If the length of a component is settable, the class must define the setter method
        itself.
    """
    def getLength(self) -> float:
        # Return the length of this component along the central axis
        return 0

    def setAppearance(self, appearance) -> None:
        if hasattr(self._obj.ViewObject.Proxy, "setAppearance"):
            self._obj.ViewObject.Proxy.setAppearance(appearance)

    # This will be implemented in the derived class
    @abstractmethod
    def execute(self, obj : Any) -> None:
        ...

    def getSolidShape(self, obj : Any) -> Part.Solid:
        """ Return a filled version of the shape. Useful for CFD """
        return None

    def getScale(self) -> float:
        """
        Return the scale value

        In cases where the parent is scaled, that is the value returned. Otherwise
        the components are expected to calculate the scale based on their parameters.
        """
        if self.isParentScaled() and not self._obj.ScaleOverride:
            return self.getParent().getScale()

        scale = 1.0
        if self._obj.Scale:
            if self._obj.ScaleValue.Value > 0.0:
                scale = self._obj.ScaleValue.Value
        return float(scale)

    def getParentScale(self) -> float:
        """
        Return the parents scale value
        """
        if self.isParentScaled():
            return self.getParent().getScale()
        return 1.0

    def isScaled(self) -> bool:
        """ Return True if the object or any of its parental lineage is scaled """
        if self._obj.Scale:
            return True
        return self.isParentScaled() and not self._obj.ScaleOverride

    def isParentScaled(self) -> bool:
        """ Return True if the parent is scaled """
        if self.hasParent():
            return self.getParent().isScaled()
        return False

    def resetScale(self) -> None:
        self._obj.Scale = False
        self._obj.ScaleOverride = False
        self._obj.ScaleByValue = True
        self._obj.ScaleValue = FreeCAD.Units.Quantity("1.0")
        self.setEdited()

    def setScale(self, scale : float) -> None:
        self._obj.Scale = True
        self._obj.ScaleByValue = True
        self._obj.ScaleValue = FreeCAD.Units.Quantity(f"{scale}")
        self.setEdited()

    def setScaled(self, scaled : bool) -> None:
        self._obj.Scale = scaled
        self.setEdited()

    def setPartScale(self, scale : float) -> None:
        """ This will be overridden as required to scale a part by a value """
        self._obj.Scale = False
        self.setEdited()

    def setPartScaleRecursive(self, scale : float) -> None:
        if self._obj.ScaleOverride:
            scale = self._obj.Proxy.getScale()

        self.setPartScale(scale)
        for current in self.getChildren():
            proxy = current.Proxy
            proxy.setPartScaleRecursive(scale)

    def setStageScale(self, scale : float) -> None:
        stage = self.getStage()
        if stage:
            for current in stage.getChildren():
                proxy = current.Proxy
                proxy.setPartScaleRecursive(scale)

    def setRocketScale(self, scale : float) -> None:
        rocket = self.getRocket()
        if rocket:
            for current in rocket.getChildren():
                proxy = current.Proxy
                proxy.setPartScaleRecursive(scale)

    def getPosition(self) -> Any:
        return self._obj.Placement.Base

    def getPositionAsCoordinate(self) -> Coordinate:
        pos = self._obj.Placement.Base
        return Coordinate(pos.x, pos.y, pos.z)
