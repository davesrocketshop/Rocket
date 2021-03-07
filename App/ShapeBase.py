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

from PySide.QtCore import QObject, Signal
from App.Utilities import _err

class ShapeBase(QObject):

    edited = Signal()

    def __init__(self, obj):
        super().__init__()
        self.Type = "RocketComponent"
        self.version = '3.0'

        self._obj = obj
        self._parent = None
        obj.Proxy=self
        self._scratch = {} # None persistent property storage, for import properties and similar

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

    def setEdited(self):
        self.edited.emit()

    def eligibleChild(self, childType):
        return False

    def setParent(self, obj):
        self._parent = obj

    def getParent(self):
        return self._parent

    def getAxialLength(self):
        # Return the length of this component along the central axis
        return 0.0

    def getRadius(self):
        # For placing objects on the outer part of the parent
        return 0.0

    def resetPlacement(self):
        self._obj.Placement = FreeCAD.Placement()

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
        pass

    def getOuterRadius(self):
        return 0.0

    def getInnerRadius(self):
        return 0.0

    def setRadialPosition(self, outerRadius, innerRadius):
        pass

    # This will be implemented in the derived class
    def execute(self, obj):
        _err("No execute method defined for %s" % (self.__class__.__name__))
