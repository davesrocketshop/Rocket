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
from App.RocketComponentShapeless import RocketComponentShapeless

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

class RocketComponent(RocketComponentShapeless, ChangeSource):

    def __init__(self, obj):
        super().__init__(obj)

        # Attributes from presets
        if not hasattr(obj, 'Manufacturer'):
            obj.addProperty('App::PropertyString', 'Manufacturer', 'Rocket', translate('App::Property', 'Component manufacturer')).Manufacturer = ""
        if not hasattr(obj, 'PartNumber'):
            obj.addProperty('App::PropertyString', 'PartNumber', 'Rocket', translate('App::Property', 'Component manufacturer part number')).PartNumber = ""
        if not hasattr(obj, 'Material'):
            obj.addProperty('App::PropertyString', 'Material', 'Rocket', translate('App::Property', 'Component material')).Material = ""
        if not hasattr(obj, 'Description'):
            obj.addProperty('App::PropertyString', 'Description', 'RocketComponent', translate('App::Property', 'Component description')).Description = ""
        
        if not hasattr(obj, 'LocationReference'):
            obj.addProperty('App::PropertyEnumeration', 'LocationReference', 'Rocket', translate('App::Property', 'Reference location for the location'))
            obj.LocationReference = [
                        LOCATION_PARENT_TOP,
                        LOCATION_PARENT_MIDDLE,
                        LOCATION_PARENT_BOTTOM,
                        LOCATION_BASE
                    ]
            obj.LocationReference = LOCATION_PARENT_BOTTOM
       
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
        
        # if not hasattr(obj, 'AxialMethod'):
        #     obj.addProperty('App::PropertyPythonObject', 'AxialMethod', 'Rocket', translate('App::Property', 'Method for calculating axial offsets')).AxialMethod = AxialMethod.AFTER

        # From Rocket
        if not hasattr(obj,"Length"):
            obj.addProperty('App::PropertyLength', 'Length', 'Rocket', translate('App::Property', 'Length of the component')).Length = 0.0
        # if not hasattr(obj,"AxialOffset"):
        #     obj.addProperty('App::PropertyDistance', 'AxialOffset', 'Rocket', translate('App::Property', 'Offset from the reference point')).AxialOffset = 0.0
        if not hasattr(obj, 'Position'):
            obj.addProperty('App::PropertyPythonObject', 'Position', 'Rocket', translate('App::Property', 'Method for calculating axial offsets')).Position = Coordinate()

        # if not hasattr(obj, 'Texture'):
        #     obj.addProperty('App::PropertyFileIncluded', 'Texture', 'Rocket', translate('App::Property', 'Texture file')).Texture = ""

        if not hasattr(obj,"Shape"):
            obj.addProperty('Part::PropertyPartShape', 'Shape', 'Rocket', translate('App::Property', 'Shape of the component'))

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

    def isMotorMount(self):
        return False

    # Return true if the component may have an aerodynamic effect on the rocket.
    def isAerodynamic(self):
        return False
	
    # Return true if the component may have an effect on the rocket's mass.
    def isMassive(self):
        return False

    # the default implementation is mostly a placeholder here, however in inheriting classes, 
    # this function is useful to indicate adjacent placements and view sizes
    def updateBounds(self):
        return

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

    def setLocationReference(self, reference):
        self.setAxialMethod(AXIAL_METHOD_MAP[reference])

    def getPosition(self):
        return self._obj.Placement.Base

    def getPositionAsCoordinate(self):
        pos = self._obj.Placement.Base
        return Coordinate(pos.x, pos.y, pos.z)

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
