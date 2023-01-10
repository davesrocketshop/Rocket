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
import math

from abc import ABC, abstractmethod

from App.util.Coordinate import Coordinate
from App.ShapeBase import ShapeBase

from App.Constants import FEATURE_ROCKET, FEATURE_STAGE

from App.Constants import PROP_HIDDEN, PROP_TRANSIENT, PROP_READONLY
from App.Constants import LOCATION_PARENT_TOP, LOCATION_PARENT_MIDDLE, LOCATION_PARENT_BOTTOM, LOCATION_AFTER, LOCATION_BASE
from App.Constants import LOCATION_SURFACE, LOCATION_CENTER

from App.position import AxialMethod
from App.position.AxialMethod import AXIAL_METHOD_MAP
from App.interfaces.ChangeSource import ChangeSource
from App.util.Coordinate import Coordinate, ZERO
from App.events.ComponentChangeEvent import ComponentChangeEvent

from DraftTools import translate

class RocketComponent(ShapeBase, ChangeSource):

    def __init__(self, obj):
        super().__init__(obj)

        if not hasattr(obj, 'Manufacturer'):
            obj.addProperty('App::PropertyString', 'Manufacturer', 'Rocket', translate('App::Property', 'Component manufacturer')).Manufacturer = ""
        if not hasattr(obj, 'PartNumber'):
            obj.addProperty('App::PropertyString', 'PartNumber', 'Rocket', translate('App::Property', 'Component manufacturer part number')).PartNumber = ""
        if not hasattr(obj, 'Description'):
            obj.addProperty('App::PropertyString', 'Description', 'Rocket', translate('App::Property', 'Component description')).Description = ""
        if not hasattr(obj, 'Material'):
            obj.addProperty('App::PropertyString', 'Material', 'Rocket', translate('App::Property', 'Component material')).Material = ""
        
        if not hasattr(obj, 'LocationReference'):
            obj.addProperty('App::PropertyEnumeration', 'LocationReference', 'Rocket', translate('App::Property', 'Reference location for the location'))
            obj.LocationReference = [
                        LOCATION_PARENT_TOP,
                        LOCATION_PARENT_MIDDLE,
                        LOCATION_PARENT_BOTTOM,
                        LOCATION_BASE
                    ]
            obj.LocationReference = LOCATION_PARENT_BOTTOM
        if not hasattr(obj, 'AngleOffset'):
            obj.addProperty('App::PropertyAngle', 'AngleOffset', 'Rocket', translate('App::Property', 'Angle of offset around the center axis')).AngleOffset = 0.0
       
        if not hasattr(obj, 'RadialReference'):
            obj.addProperty('App::PropertyEnumeration', 'RadialReference', 'Rocket', translate('App::Property', 'Reference location for the radial offset'))
            obj.RadialReference = [
                        LOCATION_SURFACE,
                        LOCATION_CENTER
                    ]
            obj.RadialReference = LOCATION_SURFACE

        if not hasattr(obj, 'RadialOffset'):
            obj.addProperty('App::PropertyDistance', 'RadialOffset', 'Rocket', translate('App::Property', 'Radial offset from the reference')).RadialOffset = 0.0

        # if not hasattr(obj,"MassOverride"):
        #     obj.addProperty('App::PropertyBool', 'MassOverride', 'Rocket', translate('App::Property', 'Override the calculated mass of this component')).MassOverride = False
        # if not hasattr(obj, 'OverrideChildren'):
        #     obj.addProperty('App::PropertyBool', 'OverrideChildren', 'Rocket', translate('App::Property', 'True when the overridden mass includes the mass of the children')).OverrideChildren = False
        # if not hasattr(obj,"OverrideMass"):
        #     obj.addProperty('App::PropertyQuantity', 'OverrideMass', 'Rocket', translate('App::Property', 'Override the calculated mass of this component')).OverrideMass = 0.0

        # Adhesive has non-zero mass and must be accounted for, especially on larger rockets
        # if not hasattr(obj,"AdhesiveMass"):
        #     obj.addProperty('App::PropertyQuantity', 'AdhesiveMass', 'Rocket', translate('App::Property', 'Mass of the adhesive used to attach this component to the rocket. This includes fillet mass')).AdhesiveMass = 0.0

        # Mass of the component based either on its material and volume, or override
        # if not hasattr(obj, 'Mass'):
        #     obj.addProperty('App::PropertyQuantity', 'Mass', 'Rocket', translate('App::Property', 'Calculated or overridden component mass'), PROP_READONLY|PROP_TRANSIENT).Mass = 0.0
        
        if not hasattr(obj, 'AxialMethod'):
            obj.addProperty('App::PropertyPythonObject', 'AxialMethod', 'Rocket', translate('App::Property', 'Method for calculating axial offsets')).AxialMethod = AxialMethod.AFTER

        # From Rocket
        if not hasattr(obj,"Length"):
            obj.addProperty('App::PropertyLength', 'Length', 'Rocket', translate('App::Property', 'Length of the component')).Length = 0.0
        if not hasattr(obj,"AxialOffset"):
            obj.addProperty('App::PropertyDistance', 'AxialOffset', 'Rocket', translate('App::Property', 'Offset from the reference point')).AxialOffset = 0.0
        if not hasattr(obj, 'Position'):
            obj.addProperty('App::PropertyPythonObject', 'Position', 'Rocket', translate('App::Property', 'Method for calculating axial offsets')).Position = Coordinate()

        if not hasattr(obj,"Group"):
            obj.addExtension("App::GroupExtensionPython")

        self._configListeners = []

    def setDefaults(self):
        pass

    def isRocketAssembly(self):
        parent = self.getParent()
        while parent is not None:
            if parent.Type == FEATURE_ROCKET:
                return True

            parent = parent.getParent()

        return False

    def getComponentName(self):
        return self._obj.Label

    def getName(self):
        return self._obj.Label

    def setName(self, name):
        self._obj.Label = name

    """
        Get the characteristic length of the component, for example the length of a body tube
        of the length of the root chord of a fin.  This is used in positioning the component
        relative to its parent.
        
        If the length of a component is settable, the class must define the setter method
        itself.
    """
    def getLength(self):
        # Return the length of this component along the central axis
        return self._obj.Length

    """
        Test whether the given component type can be added to this component.  This type safety
        is enforced by the <code>addChild()</code> methods.  The return value of this method
        may change to reflect the current state of this component (e.g. two components of some
        type cannot be placed as children).

        DEPRECATED: use eligibleChild()
    """
    def isCompatible(self, type):
        return self.eligibleChild(type)

    def getType(self):
        return self.Type

    def isAfter(self):
        return AxialMethod.AFTER == self._obj.AxialMethod

    def isAxisymmetric(self):
        return True

    def isMotorMount(self):
        return False

    # Return true if the component may have an aerodynamic effect on the rocket.
    def isAerodynamic(self):
        return False
	
    # Return true if the component may have an effect on the rocket's mass.
    def isMassive(self):
        return False

    def update(self):
        self._setAxialOffset(self._obj.AxialMethod, self._obj.AxialOffset)
        self._setRotation()

    # the default implementation is mostly a placeholder here, however in inheriting classes, 
    # this function is useful to indicate adjacent placements and view sizes
    def updateBounds(self):
        return

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
            raise Exception("component " + component.Proxy.getComponentName() + " is already in a tree")

        # Ensure that the no loops are created in component tree [A -> X -> Y -> B, B.addChild(A)]
        if self.getRoot()._obj == component:
            raise Exception("Component " + component.Proxy.getComponentName() +
                    " is a parent of " + self.getComponentName() + ", attempting to create cycle in tree.")

        if not self.eligibleChild(component.Proxy.Type):
            raise Exception("Component: " + component.Proxy.getComponentName() +
                    " not currently compatible with component: " + self.getComponentName())

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
        component.checkComponentStructure()


        try:
            self._removeChild(component)
            component.Proxy.setParent(None)
            
            if component.Proxy.Type == FEATURE_STAGE:
                self.getRocket().forgetStage(component);

            # Remove sub-stages of the removed component
            for stage in component.getSubStages():
                self.getRocket().forgetStage(stage)
            
            self.checkComponentStructure()
            component.Proxy.checkComponentStructure()
            
            self.fireAddRemoveEvent(component)
            self.updateBounds()
            
            return True
        except ValueError:
            pass
        return False

    # Move a child to another position.
    def moveChild(self, component, index):
        try:
            self._moveChild(index, component)
            
            self.checkComponentStructure()
            component.Proxy.checkComponentStructure()
            
            self.updateBounds()
            self.fireAddRemoveEvent(component)
        except ValueError:
            pass

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

        if newAxialMethod == self._obj.AxialMethod:
            # no change.
            return

        # this variable changes the internal representation, but not the physical position
        # the relativePosition (method) is just the lens through which external code may view this component's position. 
        self._obj.AxialMethod = newAxialMethod
        self._obj.AxialOffset = self.getAxialOffsetFromMethod(newAxialMethod)

        # this doesn't cause any physical change-- just how it's described.
        # self.fireComponentChangeEvent(ComponentChangeEvent.BOTH_CHANGE)

    def setLocationReference(self, reference):
        self.setAxialMethod(AXIAL_METHOD_MAP[reference])

    # Fires an AERODYNAMIC_CHANGE, MASS_CHANGE or OTHER_CHANGE event depending on the
    # type of component removed.
    def fireAddRemoveEvent(self, component):
        type = ComponentChangeEvent.TREE_CHANGE
        for obj in component.Group:
            if not obj.isDerivedFrom('Sketcher::SketchObject'):
                proxy = obj.Proxy
                if proxy.isAeroDynamic():
                    type |= ComponentChangeEvent.AERODYNAMIC_CHANGE
                if proxy.isMassive():
                    type |= ComponentChangeEvent.MASS_CHANGE

        self.fireComponentChangeEvent(type);

    def fireComponentChangeEvent(self, event):
        if self.getParent() is None: # or self._bypassComponentChangeEvent:
            return

        self.getRoot().fireComponentChangeEvent(event)

    def getPosition(self):
        return self._obj.Placement.Base

    def getPositionAsCoordinate(self):
        pos = self._obj.Placement.Base
        return Coordinate(pos.x, pos.y, pos.z)

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

    def _setRotation(self):
        self._obj.Placement = FreeCAD.Placement(self._obj.Placement.Base, FreeCAD.Vector(1,0,0), self._obj.AngleOffset)

    def addConfigListener(self, listener):
        if listener is None or listener in self._configListeners or listener == self:
            return False

        self._configListeners.append(listener)
        listener.setBypassChangeEvent(True)

        return True

    def removeConfigListener(self, listener):
        self._configListeners.remove(listener)
        listener.setBypassChangeEvent(False)

    def clearConfigListeners(self):
        for listener in self._configListeners:
            listener.setBypassChangeEvent(False)

        self._configListeners.clear()

    def getConfigListeners(self):
        return self._configListeners

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

        raise Exception("getRocket() called with root component " + root.getComponentName())

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
            if proxy == FEATURE_STAGE:
                result.append(proxy)

        return result
	
    # Adds a ComponentChangeListener to the rocket tree.  The listener is added to the root
    # component, which must be of type Rocket (which overrides this method).  Events of all
    # subcomponents are sent to all listeners.
    def addComponentChangeListener(self, listener):
        self.getRocket().addComponentChangeListener(listener)
	
    # Removes a ComponentChangeListener from the rocket tree.  The listener is removed from
    # the root component, which must be of type Rocket (which overrides this method).
    # Does nothing if the root component is not a Rocket.  (The asymmetry is so
    # that listeners can always be removed just in case.)
    def removeComponentChangeListener(self, listener):
        if not self.getParent() is None:
            self.getRoot().removeComponentChangeListener(listener)

    # Adds a <code>ChangeListener</code> to the rocket tree.  This is identical to
    # <code>addComponentChangeListener()</code> except that it uses a
    # <code>ChangeListener</code>.  The same events are dispatched to the
    # <code>ChangeListener</code>, as <code>ComponentChangeEvent</code> is a subclass
    # of <code>ChangeEvent</code>.
    def addChangeListener(self, listener):
        self.addComponentChangeListener(listener)
	
    # Removes a ChangeListener from the rocket tree.  This is identical to
    # removeComponentChangeListener() except it uses a ChangeListener.
    # Does nothing if the root component is not a Rocket.  (The asymmetry is so
    # that listeners can always be removed just in case.)
    def removeChangeListener(self, listener):
        self.removeComponentChangeListener(listener)

    # Check that the local component structure is correct.  This can be called after changing
    # the component structure in order to verify the integrity.
    def checkComponentStructure(self):
        if self.getParent() is not None:
            # Test that this component is found in parent's children with == operator
            if not self.containsExact(self.getParent().getChildren(), self):
                raise Exception("Inconsistent component structure detected, parent does not contain this " +
                        "component as a child, parent=" + self.getParent().getComponentName() + " this=" + self.getComponentName())
        for child in self.getChildren():
            if child.isDerivedFrom('Sketcher::SketchObject'):
                continue

            if child.Proxy.getParent() != self:
                message = "Inconsistent component structure detected, child does not have this component " + \
                        "as the parent, this=" + self.getComponentName() + " child=" + child.Proxy.getComponentName() + \
                        " child.parent="
                if child.Proxy.getParent() is None:
                    message += "None"
                else:
                    message += child.Proxy.getParent().getComponentName()
                raise Exception(message)

    # Check whether the list contains exactly the searched-for component (with == operator)
    def containsExact(self, haystack, needle):
        for c in haystack:
            if needle == c.Proxy:
                return True

        return False

    def setAfter(self):
        if self.getParent() is None:
            # Probably initialization order issue.  Ignore for now.
            return
        
        self.AxialMethod = AxialMethod.AFTER
        self.AxialOffset = 0.0

        # Stages are reversed from OpenRocket
        count = self.getParent().getChildCount()
        
        # if first component in the stage. => position from the top of the parent
        thisIndex = self.getParent().getChildIndex(self)
        if thisIndex == (count - 1):
            self._obj.Placement.Base.x = self.getParent()._obj.Placement.Base.x
            # self._obj.Placement.Base.x = 0.0
        elif 0 <= thisIndex:
            index = thisIndex + 1
            referenceComponent = self.getParent()._getChild( index )
            while referenceComponent is not None:
                if referenceComponent.Proxy.isAfter():
                    break
                index = index + 1
                referenceComponent = self.getParent()._getChild( index )

            if referenceComponent is None:
                self._obj.Placement.Base.x = self.getParent()._obj.Placement.Base.x
                return
        
            refLength = float(referenceComponent.Proxy.getLength())
            refRelX = float(referenceComponent.Placement.Base.x)

            self._obj.Placement.Base.x = refRelX + refLength
            # self._obj.Placement.Base.x = refRelX - (refLength + float(self.getLength()))

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

    """
         Returns coordinates of this component's instances in relation to this.parent.
        
        For example, the absolute position of any given instance is the parent's position 
        plus the instance position returned by this method   
        
        NOTE: the length of this array returned always equals this.getInstanceCount()
    """
    def getInstanceLocations(self):
        base = self._obj.Placement.Base
        center = Coordinate(base.x, base.y, base.z)
        offsets = self.getInstanceOffsets()

        locations = []
        for instanceNumber in range(len(offsets)):
            locations.append(center.add(offsets[instanceNumber]))

        return locations

    """
        Clear the current component preset.  This does not affect the component properties
        otherwise.
    """
    def clearPreset(self):
        for listener in self._configListeners:
            listener.clearPreset()

        self.fireComponentChangeEvent(ComponentChangeEvent.NONFUNCTIONAL_CHANGE)

    """
        Provides locations of all instances of component relative to this component's reference point
    """
    def getInstanceOffsets(self):
        return [ZERO]

    """
        Return coordinate <code>c</code> described in the coordinate system of
        <code>dest</code>.  If <code>dest</code> is <code>null</code> returns
        absolute coordinates.
        
        This method returns an array of coordinates, each of which represents a
        position of the coordinate in clustered cases.  The array is guaranteed
        to contain at least one element.
        
        The current implementation does not support rotating components.
    """
    def toRelative(self, c, dest):
        if dest is None:
            raise Exception("calling toRelative(c,null) is being refactored. ")

        destLocs = dest.getInstanceLocations()
        toReturn = []
        for coordIndex in range(len(destLocs)):
            toReturn.append(self.getInstanceLocations()[0].add(c).sub(destLocs[coordIndex]))

        return toReturn

    """
        Provides locations of all instances of component *accounting for all parent instancing*
        
        
        NOTE: the length of this array MAY OR MAY NOT EQUAL this.getInstanceCount()
           --> RocketComponent::getInstanceCount() counts how many times this component replicates on its own
           --> vs. the total instance count due to parent assembly instancing

        DAC: This may not be correct as the Workbench already supplies absolute coordinates
    """
    def getComponentLocations(self):
        if self.getParent() is None:
            # == improperly initialized components OR the root Rocket instance 
            return self.getInstanceOffsets()
        else:
            parentPositions = self.getParent().getComponentLocations()
            parentCount = len(parentPositions)
            
            # override <instance>.getInstanceLocations() in each subclass
            instanceLocations = self.getInstanceLocations()
            instanceCount = len(instanceLocations)
            
            # usual case optimization
            if parentCount == 1 and instanceCount == 1:
                return [parentPositions[0].add(instanceLocations[0])]
            
            thisCount = instanceCount*parentCount
            thesePositions = [0] * thisCount
            for pi in range(parentCount):
                for ii in range(instanceCount):
                    thesePositions[pi + parentCount*ii] = parentPositions[pi].add(instanceLocations[ii])

            return thesePositions
