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
"""Base class for rocket components"""

__title__ = "FreeCAD Rocket Components"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

import FreeCAD
import math

from PySide.QtCore import Signal

from App.ShapeBase import ShapeBase, TRACE_POSITION
# from App.Utilities import _err

from App.Constants import PROP_HIDDEN, PROP_TRANSIENT, PROP_READONLY
from App.Constants import LOCATION_PARENT_TOP, LOCATION_PARENT_MIDDLE, LOCATION_PARENT_BOTTOM, LOCATION_BASE
from App.Constants import LOCATION_SURFACE, LOCATION_CENTER
from App.Constants import PLACEMENT_AXIAL #, PLACEMENT_RADIAL

from DraftTools import translate

class ShapeComponent(ShapeBase):

    def __init__(self, obj):
        super().__init__(obj)

        if not hasattr(obj, 'Manufacturer'):
            obj.addProperty('App::PropertyString', 'Manufacturer', 'RocketComponent', translate('App::Property', 'Component manufacturer')).Manufacturer = ""
        if not hasattr(obj, 'PartNumber'):
            obj.addProperty('App::PropertyString', 'PartNumber', 'RocketComponent', translate('App::Property', 'Component manufacturer part number')).PartNumber = ""
        if not hasattr(obj, 'Description'):
            obj.addProperty('App::PropertyString', 'Description', 'RocketComponent', translate('App::Property', 'Component description')).Description = ""
        if not hasattr(obj, 'Material'):
            obj.addProperty('App::PropertyString', 'Material', 'RocketComponent', translate('App::Property', 'Component material')).Material = ""
        if not hasattr(obj, 'PlacementType'):
            obj.addProperty('App::PropertyString', 'PlacementType', 'RocketComponent', translate('App::Property', 'Component placement type'), PROP_HIDDEN|PROP_TRANSIENT).PlacementType = PLACEMENT_AXIAL

        if not hasattr(obj,"MassOverride"):
            obj.addProperty('App::PropertyBool', 'MassOverride', 'RocketComponent', translate('App::Property', 'Override the calculated mass of this component')).MassOverride = False
        if not hasattr(obj, 'OverrideChildren'):
            obj.addProperty('App::PropertyBool', 'OverrideChildren', 'RocketComponent', translate('App::Property', 'True when the overridden mass includes the mass of the children')).OverrideChildren = False
        if not hasattr(obj,"OverrideMass"):
            obj.addProperty('App::PropertyQuantity', 'OverrideMass', 'RocketComponent', translate('App::Property', 'Override the calculated mass of this component')).OverrideMass = 0.0

        # Adhesive has non-zero mass and must be accounted for, especially on larger rockets
        if not hasattr(obj,"AdhesiveMass"):
            obj.addProperty('App::PropertyQuantity', 'AdhesiveMass', 'RocketComponent', translate('App::Property', 'Mass of the adhesive used to attach this component to the rocket. This includes fillet mass')).AdhesiveMass = 0.0

        # Mass of the component based either on its material and volume, or override
        if not hasattr(obj, 'Mass'):
            obj.addProperty('App::PropertyQuantity', 'Mass', 'RocketComponent', translate('App::Property', 'Calculated or overridden component mass'), PROP_READONLY|PROP_TRANSIENT).Mass = 0.0
            
        self._obj = obj
        obj.Proxy=self
        self.version = '2.2'

    def positionChild(self, obj, parent, parentBase, parentLength, parentRadius):
        if TRACE_POSITION:
            print("P: ShapeComponent::positionChild(%s, %s, %f, %f, %f)" % (self._obj.Label, parent.Label, parentBase, parentLength, parentRadius))

        # Calculate any auto radii
        obj.Proxy.setRadius()

        if not hasattr(obj, 'LocationReference'):
            partBase = parentBase
            roll = 0.0
        else:
            if obj.LocationReference == LOCATION_PARENT_TOP:
                partBase = (float(parentBase) + float(parentLength)) - float(obj.Location)
            elif obj.LocationReference == LOCATION_PARENT_MIDDLE:
                partBase = (float(parentBase) + (float(parentLength) / 2.0)) + float(obj.Location)
            elif obj.LocationReference == LOCATION_PARENT_BOTTOM:
                partBase = float(parentBase) + float(obj.Location)
            elif obj.LocationReference == LOCATION_BASE:
                partBase = float(obj.Location)

            roll = float(obj.AngleOffset)

        # base = obj.Placement.Base

        if self._obj.PlacementType == PLACEMENT_AXIAL:
            self._positionChildAxial(obj, partBase, roll)
        else:
            self._positionChildRadial(obj, parent, parentRadius, partBase, roll)

    def _positionChildAxial(self, obj, partBase, roll):
        if TRACE_POSITION:
            print("P: ShapeComponent::_positionChildAxial(%s, %f, %f)" % (self._obj.Label, partBase, roll))

        # newPlacement = FreeCAD.Placement(FreeCAD.Vector(partBase, 0, parentRadius), FreeCAD.Rotation(FreeCAD.Vector(1,0,0), roll), FreeCAD.Vector(0, 0, -parentRadius))
        newPlacement = FreeCAD.Placement(FreeCAD.Vector(partBase, 0, 0), FreeCAD.Rotation(FreeCAD.Vector(1,0,0), roll), FreeCAD.Vector(0, 0, 0))
        if obj.Placement != newPlacement:
            obj.Placement = newPlacement

    def _positionChildRadial(self, obj, parent, parentRadius, partBase, roll):
        if TRACE_POSITION:
            print("P: ShapeComponent::_positionChildRadial(%s, %s, %f, %f, %f)" % (self._obj.Label, parent.Label, parentRadius, partBase, parentRadius))

        radial = float(parentRadius) + float(obj.Proxy.getRadialPositionOffset()) # Need to add current parent radial
        if hasattr(obj, 'AngleOffset'):
            radial += float(obj.AngleOffset)

        # Use a matrix for transformations, otherwise it rotates around the part axis not the rocket axis
        matrix = FreeCAD.Matrix()
        matrix.move(FreeCAD.Vector(partBase, 0, radial))
        matrix.rotateX(math.radians(roll))
        newPlacement = FreeCAD.Placement(matrix)
        if obj.Placement != newPlacement:
            obj.Placement = newPlacement

class ShapeLocation(ShapeComponent):

    def __init__(self, obj):
        super().__init__(obj)
        
        if not hasattr(obj, 'LocationReference'):
            obj.addProperty('App::PropertyEnumeration', 'LocationReference', 'RocketComponent', translate('App::Property', 'Reference location for the location'))
        obj.LocationReference = [
                    LOCATION_PARENT_TOP,
                    LOCATION_PARENT_MIDDLE,
                    LOCATION_PARENT_BOTTOM,
                    LOCATION_BASE
                ]
        obj.LocationReference = LOCATION_PARENT_BOTTOM
        if not hasattr(obj, 'Location'):
            obj.addProperty('App::PropertyDistance', 'Location', 'RocketComponent', translate('App::Property', 'Location offset from the reference')).Location = 0.0
        if not hasattr(obj, 'AngleOffset'):
            obj.addProperty('App::PropertyAngle', 'AngleOffset', 'RocketComponent', translate('App::Property', 'Angle of offset around the center axis')).AngleOffset = 0.0

class ShapeRadialLocation(ShapeLocation):

    def __init__(self, obj):
        super().__init__(obj)
        
        if not hasattr(obj, 'RadialReference'):
            obj.addProperty('App::PropertyEnumeration', 'RadialReference', 'RocketComponent', translate('App::Property', 'Reference location for the radial offset'))
        obj.RadialReference = [
                    LOCATION_SURFACE,
                    LOCATION_CENTER
                ]
        obj.RadialReference = LOCATION_SURFACE

        if not hasattr(obj, 'RadialOffset'):
            obj.addProperty('App::PropertyDistance', 'RadialOffset', 'RocketComponent', translate('App::Property', 'Radial offset from the reference')).RadialOffset = 0.0
