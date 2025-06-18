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

from typing import Any

import FreeCAD
import Materials
import Part

from Rocket.Parts.PartDatabase import PartDatabase
from Rocket.Parts.Material import getUuid
from Rocket.Parts.Exceptions import MaterialNotFoundError

from Rocket.util.Coordinate import Coordinate
from Rocket.RocketComponentShapeless import RocketComponentShapeless

from Rocket.Constants import LOCATION_PARENT_TOP, LOCATION_PARENT_MIDDLE, LOCATION_PARENT_BOTTOM, LOCATION_BASE
from Rocket.Constants import MATERIAL_TYPE_BULK

from Rocket.position.AxialMethod import AXIAL_METHOD_MAP
from Rocket.interfaces.ChangeSource import ChangeSource
from Rocket.interfaces.ComponentChangeListener import ComponentChangeListener
from Rocket.util.Coordinate import Coordinate, ZERO
from Rocket.events.ComponentChangeEvent import ComponentChangeEvent

from Rocket.Utilities import _err

from DraftTools import translate

class RocketComponent(RocketComponentShapeless, ChangeSource):

    def __init__(self, obj : Any) -> None:
        super().__init__(obj)

        # Attributes from presets
        if not hasattr(obj, 'Manufacturer'):
            obj.addProperty('App::PropertyString', 'Manufacturer', 'RocketComponent', translate('App::Property', 'Component manufacturer')).Manufacturer = ""
        if not hasattr(obj, 'PartNumber'):
            obj.addProperty('App::PropertyString', 'PartNumber', 'RocketComponent', translate('App::Property', 'Component manufacturer part number')).PartNumber = ""
        # if not hasattr(obj, 'Material'):
        #     obj.addProperty('App::PropertyString', 'Material', 'RocketComponent', translate('App::Property', 'Component material')).Material = "Cardboard"
        if not hasattr(obj, 'Description'):
            obj.addProperty('App::PropertyString', 'Description', 'RocketComponent', translate('App::Property', 'Component description')).Description = ""

        if not hasattr(obj, 'LocationReference'):
            obj.addProperty('App::PropertyEnumeration', 'LocationReference', 'RocketComponent', translate('App::Property', 'Reference location for the location'))
            obj.LocationReference = [
                        LOCATION_PARENT_TOP,
                        LOCATION_PARENT_MIDDLE,
                        LOCATION_PARENT_BOTTOM,
                        LOCATION_BASE
                    ]
            obj.LocationReference = LOCATION_PARENT_BOTTOM
        else:
            obj.LocationReference = [
                        LOCATION_PARENT_TOP,
                        LOCATION_PARENT_MIDDLE,
                        LOCATION_PARENT_BOTTOM,
                        LOCATION_BASE
                    ]

        # From Rocket
        if not hasattr(obj,"Length"):
            obj.addProperty('App::PropertyLength', 'Length', 'RocketComponent', translate('App::Property', 'Length of the component')).Length = 0.0
        if not hasattr(obj, 'Position'):
            obj.addProperty('App::PropertyPythonObject', 'Position', 'RocketComponent', translate('App::Property', 'Method for calculating axial offsets')).Position = Coordinate()

        if not hasattr(obj, 'Scale'):
            obj.addProperty('App::PropertyBool', 'Scale', 'RocketComponent', translate('App::Property', 'Scale the object')).Scale = False
        if not hasattr(obj, 'ScaleByValue'):
            obj.addProperty('App::PropertyBool', 'ScaleByValue', 'RocketComponent', translate('App::Property', 'Scale the object by value')).ScaleByValue = True
        if not hasattr(obj, 'ScaleByDiameter'):
            obj.addProperty('App::PropertyBool', 'ScaleByDiameter', 'RocketComponent', translate('App::Property', 'Scale the object by body diameter')).ScaleByDiameter = False
        if not hasattr(obj, 'AutoScaleDiameter'):
            obj.addProperty('App::PropertyBool', 'AutoScaleDiameter', 'RocketComponent', translate('App::Property', 'Automatically scale the object by body diameter')).AutoScaleDiameter = False
        if not hasattr(obj, 'ScaleValue'):
            obj.addProperty('App::PropertyLength', 'ScaleValue', 'RocketComponent', translate('App::Property', 'Scaling value or dimension')).ScaleValue = 1.0

        if not hasattr(obj, 'Texture'):
            obj.addProperty('App::PropertyFileIncluded', 'Texture', 'RocketComponent', translate('App::Property', 'Texture file')).Texture = ""

        if not hasattr(obj,"Shape"):
            obj.addProperty('Part::PropertyPartShape', 'Shape', 'RocketComponent', translate('App::Property', 'Shape of the component'))

    def convertMaterialAndAppearance(self, obj : Any) -> None:
        if hasattr(obj, "Material"):
            self.convertMaterial(obj, obj.Material)
            obj.removeProperty("Material")
        if hasattr(obj, "ViewObject"):
            mat = FreeCAD.Material()
            if hasattr(obj.ViewObject, "ShapeMaterial"):
                mat = obj.ViewObject.ShapeMaterial
            if hasattr(obj.ViewObject, "ShapeColor"):
                mat.DiffuseColor = obj.ViewObject.ShapeColor
            obj.ViewObject.ShapeAppearance = (
                mat
            )
            obj.ViewObject.LineColor = mat.DiffuseColor

    def convertMaterial(self, obj : Any, old : Any) -> None:
        database = PartDatabase(FreeCAD.getUserAppDataDir() + "Mod/Rocket/")
        connection = database.getConnection()
        try:
            uuid = getUuid(connection, old, MATERIAL_TYPE_BULK)

            materialManager = Materials.MaterialManager()
            obj.ShapeMaterial = materialManager.getMaterial(uuid)
        except MaterialNotFoundError:
            _err(translate("Rocket", "Material '{}' not found - using default material").format(old))

    """
        Get the characteristic length of the component, for example the length of a body tube
        of the length of the root chord of a fin.  This is used in positioning the component
        relative to its parent.

        If the length of a component is settable, the class must define the setter method
        itself.
    """
    def getLength(self) -> float:
        # Return the length of this component along the central axis
        return self._obj.Length

    def isMotorMount(self) -> bool:
        return False

    # Return true if the component may have an aerodynamic effect on the rocket.
    def isAerodynamic(self) -> bool:
        return False

    # Return true if the component may have an effect on the rocket's mass.
    def isMassive(self) -> bool:
        return False

    # the default implementation is mostly a placeholder here, however in inheriting classes,
    # this function is useful to indicate adjacent placements and view sizes
    def updateBounds(self) -> None:
        return

    # Move a child to another position.
    def moveChild(self, component : Any, index : int) -> None:
        try:
            self._moveChild(index, component)

            self.checkComponentStructure()
            component.Proxy.checkComponentStructure()

            self.updateBounds()
            self.fireAddRemoveEvent(component)
        except ValueError:
            pass

    def setLocationReference(self, reference : str) -> None:
        self.setAxialMethod(AXIAL_METHOD_MAP[reference])

    def getPosition(self) -> Any:
        return self._obj.Placement.Base

    def getPositionAsCoordinate(self) -> Coordinate:
        pos = self._obj.Placement.Base
        return Coordinate(pos.x, pos.y, pos.z)

    def addConfigListener(self, listener : Any) -> bool:
        if listener is None or listener in self._configListeners or listener == self:
            return False

        self._configListeners.append(listener)
        listener.setBypassChangeEvent(True)

        return True

    def removeConfigListener(self, listener : Any) -> None:
        self._configListeners.remove(listener)
        listener.setBypassChangeEvent(False)

    def clearConfigListeners(self) -> None:
        for listener in self._configListeners:
            listener.setBypassChangeEvent(False)

        self._configListeners.clear()

    def getConfigListeners(self) -> list:
        return self._configListeners

    # Adds a ComponentChangeListener to the rocket tree.  The listener is added to the root
    # component, which must be of type Rocket (which overrides this method).  Events of all
    # subcomponents are sent to all listeners.
    def addComponentChangeListener(self, listener : ComponentChangeListener) -> None:
        self.getRocket().addComponentChangeListener(listener)

    # Removes a ComponentChangeListener from the rocket tree.  The listener is removed from
    # the root component, which must be of type Rocket (which overrides this method).
    # Does nothing if the root component is not a Rocket.  (The asymmetry is so
    # that listeners can always be removed just in case.)
    def removeComponentChangeListener(self, listener : ComponentChangeListener) -> None:
        if self.hasParent():
            self.getRoot().removeComponentChangeListener(listener)

    # Adds a <code>ChangeListener</code> to the rocket tree.  This is identical to
    # <code>addComponentChangeListener()</code> except that it uses a
    # <code>ChangeListener</code>.  The same events are dispatched to the
    # <code>ChangeListener</code>, as <code>ComponentChangeEvent</code> is a subclass
    # of <code>ChangeEvent</code>.
    def addChangeListener(self, listener : ComponentChangeListener) -> None:
        self.addComponentChangeListener(listener)

    # Removes a ChangeListener from the rocket tree.  This is identical to
    # removeComponentChangeListener() except it uses a ChangeListener.
    # Does nothing if the root component is not a Rocket.  (The asymmetry is so
    # that listeners can always be removed just in case.)
    def removeChangeListener(self, listener : ComponentChangeListener) -> None:
        self.removeComponentChangeListener(listener)

    """
         Returns coordinates of this component's instances in relation to this.parent.

        For example, the absolute position of any given instance is the parent's position
        plus the instance position returned by this method

        NOTE: the length of this array returned always equals this.getInstanceCount()
    """
    def getInstanceLocations(self) -> list:
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
    def clearPreset(self) -> None:
        for listener in self._configListeners:
            listener.clearPreset()

        self.fireComponentChangeEvent(ComponentChangeEvent.NONFUNCTIONAL_CHANGE)

    """
        Provides locations of all instances of component relative to this component's reference point
    """
    def getInstanceOffsets(self) -> list:
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
    def toRelative(self, c : Coordinate, dest : Any) -> list:
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
    def getComponentLocations(self) -> list:
        if not self.hasParent() or not hasattr(self.getParent(), "getComponentLocations"):
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

    def getSolidShape(self, obj : Any) -> Part.Solid:
        """ Return a filled version of the shape. Useful for CFD """
        if hasattr(obj, "Shape") and obj.Shape.isValid():
            return obj.Shape
        return None
