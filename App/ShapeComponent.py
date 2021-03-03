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

from App.Utilities import _err

from App.Constants import LOCATION_PARENT_TOP, LOCATION_PARENT_MIDDLE, LOCATION_PARENT_BOTTOM, LOCATION_BASE

from DraftTools import translate

class ShapeComponent:

    def __init__(self, obj):
        self._obj = obj

        if not hasattr(obj, 'Manufacturer'):
            obj.addProperty('App::PropertyString', 'Manufacturer', 'RocketComponent', translate('App::Property', 'Component manufacturer')).Manufacturer = ""
        if not hasattr(obj, 'PartNumber'):
            obj.addProperty('App::PropertyString', 'PartNumber', 'RocketComponent', translate('App::Property', 'Component manufacturer part number')).PartNumber = ""
        if not hasattr(obj, 'Description'):
            obj.addProperty('App::PropertyString', 'Description', 'RocketComponent', translate('App::Property', 'Component description')).Description = ""
        if not hasattr(obj, 'Material'):
            obj.addProperty('App::PropertyString', 'Material', 'RocketComponent', translate('App::Property', 'Component material')).Material = ""

        obj.Proxy=self
        self.version = '3.0'
        self._scratch = {} # None persistent property storage, for import properties and similar

    def __getstate__(self):
        return self.version

    def __setstate__(self, state):
        if state:
            self.version = state

    def setScratch(self, name, value):
        self._scratch[name] = value

    def getScratch(self, name):
        return self._scratch[name]

    def isScratch(self, name):
        return name in self._scratch

    def getAxialLength(self):
        # Return the length of this component along the central axis
        return 0.0

    def getRadius(self):
        # For placing objects on the outer part of the parent
        return 0.0

    def setAxialPosition(self, partBase):
        base = self._obj.Placement.Base
        self._obj.Placement = FreeCAD.Placement(FreeCAD.Vector(partBase, base.y, base.z), FreeCAD.Rotation(0,0,0))

        self.positionChildren(partBase)

    def positionChildren(self, partBase):
        # Dynamic placements
        if hasattr(self._obj, "Group"):
            for child in self._obj.Group:
                child.Proxy.positionChild(child, self._obj, partBase, self.getAxialLength(), self.getRadius())

    def positionChild(self, obj, parent, parentBase, parentLength, parentRadius):
        print("ShapeComponent: positionChild")

        if not hasattr(obj, 'LocationReference'):
            partBase = parentBase
            roll = 0.0
        else:
            if obj.LocationReference == LOCATION_PARENT_TOP:
                partBase = (parentBase + parentLength) - float(obj.Location)
            elif obj.LocationReference == LOCATION_PARENT_MIDDLE:
                partBase = (parentBase + (parentLength / 2.0)) + float(obj.Location)
            elif obj.LocationReference == LOCATION_PARENT_BOTTOM:
                partBase = parentBase + float(obj.Location)
            elif obj.LocationReference == LOCATION_BASE:
                partBase = float(obj.Location)

            roll = float(obj.RadialOffset)

        base = obj.Placement.Base
        newPlacement = FreeCAD.Placement(FreeCAD.Vector(partBase, 0, parentRadius), FreeCAD.Rotation(FreeCAD.Vector(1,0,0), roll), FreeCAD.Vector(0, 0, -parentRadius))
        if obj.Placement != newPlacement:
            print("Placement changed")
            obj.Placement = newPlacement

    def getOuterRadius(self):
        return 0.0

    def getInnerRadius(self):
        return 0.0

    def setRadialPosition(self, outerRadius, innerRadius):
        pass

    # This will be implemented in the derived class
    def execute(self, obj):
        _err("No execute method defined for %s" % (self.__class__.__name__))

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
        if not hasattr(obj, 'RadialOffset'):
            obj.addProperty('App::PropertyAngle', 'RadialOffset', 'RocketComponent', translate('App::Property', 'Radial offset from the vertical')).RadialOffset = 0.0
