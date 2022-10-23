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
import FreeCADGui
import copy

from PySide.QtCore import QObject, Signal
from App.Utilities import _err
from App.Constants import PROP_NORECOMPUTE

# Set to True when debugging
TRACE_POSITION = True
TRACE_EXECUTION = True

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

class ShapeBase():

    edited = EditedShape()

    def __init__(self, obj):
        super().__init__()
        self.Type = "RocketComponent"
        self.version = '3.0'

        self._obj = obj
        self._parent = None
        obj.Proxy=self
        self._scratch = {} # None persistent property storage, for import properties and similar

    def onDocumentRestored(self, obj):
        obj.Proxy=self
        self._obj = obj
        self._parent = None
    
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

    def setEdited(self, event=None):
        self.edited.setEdited(event)

    def connect(self, fn, type):
        self.edited.doConnect(fn, type)

    def disconnect(self):
        self.edited.doDisconnect()

    def eligibleChild(self, childType):
        return False

    def setParent(self, obj):
        if hasattr(obj, "Proxy"):
            self._parent = obj.Proxy
        else:
            self._parent = obj

    def getParent(self):
        if hasattr(self._parent, "Proxy"):
            return self._parent.Proxy
        return self._parent

    def getChildren(self):
        return self._obj.Group

    def setChildren(self, list):
        self._obj.Group = list

    def _getChild(self, index):
        return self._obj.Group[index]

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
        if TRACE_POSITION:
            print("P: ShapeBase::getPrevious(%s)" % (self._obj.Label))

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
        if TRACE_POSITION:
            print("P: ShapeBase::getNext(%s)" % (self._obj.Label))

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

    def getLength(self):
        if TRACE_POSITION:
            print("P: ShapeBase::getLength(%s)" % (self._obj.Label))

        # Return the length of this component along the central axis
        length = 0.0
        if hasattr(self._obj, "Group"):
            for child in self._obj.Group:
                length += float(child.Proxy.getLength())

        print("Length = %f" %(length))
        return length

    def getMaxForwardPosition(self):
        if TRACE_POSITION:
            print("P: ShapeBase::getMaxForwardPosition(%s)" % (self._obj.Label))

        # Return the length of this component along the central axis
        length = 0.0
        if hasattr(self._obj, "Group"):
            for child in self._obj.Group:
                length = max(length, float(child.Proxy.getMaxForwardPosition()))

        # print("Length = %f" %(length))
        return length

    def getForeRadius(self):
        if TRACE_POSITION:
            print("P: ShapeBase::getForeRadius(%s)" % (self._obj.Label))

        # For placing objects on the outer part of the parent
        return 0.0

    def getAftRadius(self):
        if TRACE_POSITION:
            print("P: ShapeBase::getAftRadius(%s)" % (self._obj.Label))

        # For placing objects on the outer part of the parent
        return self.getForeRadius()

    def getRadius(self):
        if TRACE_POSITION:
            print("P: ShapeBase::getRadius(%s)" % (self._obj.Label))

        return self.getForeRadius()

    def setRadius(self):
        if TRACE_POSITION:
            print("P: ShapeBase::setRadius(%s)" % (self._obj.Label))

        # Calculate any auto radii
        self.getRadius()

    def resetPlacement(self):
        if TRACE_POSITION:
            print("P: ShapeBase::resetPlacement(%s)" % (self._obj.Label))

        self._obj.Placement = FreeCAD.Placement()

    def reposition(self):
        if TRACE_POSITION:
            print("P: ShapeBase::reposition(%s)" % (self._obj.Label))

        # if self.getParent() is not None:
        #     if TRACE_POSITION:
        #         print("P: ShapeBase::reposition(%s)._parent(%s)" % (self._obj.Label, self.getParent()._obj.Label))
        #     self.getParent().reposition()
        # else:
        #     rocket=FreeCADGui.ActiveDocument.ActiveView.getActiveObject("rocket")
        #     if rocket:
        #         rocket.Proxy.reposition()
        #     elif TRACE_POSITION:
        #         print("P: ShapeBase::reposition(%s) - NO PARENT" % (self._obj.Label))

    def setAxialPosition(self, partBase, roll=0.0):
        if TRACE_POSITION:
            print("P: ShapeBase::setAxialPosition(%s, (%f,%f,%f), %f)" % (self._obj.Label, partBase.x, partBase.y, partBase.z, roll))

        base = self._obj.Placement.Base
        self._obj.Placement = FreeCAD.Placement(FreeCAD.Vector(partBase.x, base.y, base.z), FreeCAD.Rotation(FreeCAD.Vector(1,0,0), roll))

        self.positionChildren(partBase)

    def positionChildren(self, partBase):
        if TRACE_POSITION:
            print("P: ShapeBase::positionChildren(%s, (%f,%f,%f))" % (self._obj.Label, partBase.x, partBase.y, partBase.z))

        # Dynamic placements
        if hasattr(self._obj, "Group"):
            base = FreeCAD.Vector(partBase)
            # base = FreeCAD.Vector(0,0,0)
            for child in reversed(self._obj.Group):
                child.Proxy.positionChild(self._obj, base, self.getLength(), self.getForeRadius(), 0.0)
                # base.x += float(child.Proxy.getLength())

    def positionChild(self, parent, parentBase, parentLength, parentRadius, rotation):
        if TRACE_POSITION:
            print("P: ShapeBase::positionChild(%s, %s, (%f,%f,%f), %f, %f, %f)" % (self._obj.Label, parent.Label, parentBase.x, parentBase.y, parentBase.z, parentLength, parentRadius, rotation))

        base = FreeCAD.Vector(parentBase)
        self.setAxialPosition(base)

        self.positionChildren(base)


    def getOuterRadius(self):
        if TRACE_POSITION:
            print("P: ShapeBase::getOuterRadius(%s)" % (self._obj.Label))

        return 0.0

    def getInnerRadius(self):
        if TRACE_POSITION:
            print("P: ShapeBase::getInnerRadius(%s)" % (self._obj.Label))

        return 0.0

    def setRadialPosition(self, outerRadius, innerRadius):
        if TRACE_POSITION:
            print("P: ShapeBase::setRadialPosition(%s, %f, %f)" % (self._obj.Label, outerRadius, innerRadius))


    def getRadialPositionOffset(self):
        if TRACE_POSITION:
            print("P: ShapeBase::getRadialPositionOffset(%s)" % (self._obj.Label))

        return 0.0

    def moveUp(self):
        # Move the part up in the tree
        if self.getParent() is not None:
            self.getParent()._moveChildUp(self._obj)
            self.reposition()

    def _moveChildUp(self, obj):
        if hasattr(self._obj, "Group"):
            index = 0
            for child in self._obj.Group:
                if child.Proxy == obj.Proxy:
                    if index > 0:
                        # print("\t2")
                        if self._obj.Group[index - 1].Proxy.eligibleChild(obj.Proxy.Type):
                            # Append to the end of the previous entry
                            self._obj.removeObject(obj)
                            parent = self._obj.Group[index - 1]
                            obj.Proxy.setParent(parent)
                            parent.addObject(obj)
                        else:
                            # Swap with the previous entry
                            group = self._obj.Group
                            temp = group[index - 1]
                            group[index - 1] = obj
                            group[index] = temp
                            self._obj.Group = group
                            return
                    else:
                        # Add to the grandparent ahead of the parent, or add to the next greater parent
                        if self.getParent() is not None:
                            grandparent = self.getParent()._obj
                            parent = self
                            index = 0
                            for child in grandparent.Group:
                                if child.Proxy == parent and grandparent.Proxy.eligibleChild(obj.Proxy.Type):
                                    parent._obj.removeObject(obj)
                                    obj.Proxy.setParent(grandparent)
                                    group = grandparent.Group
                                    group.insert(index, obj)
                                    grandparent.Group = group
                                    return
                                index += 1
                        else:
                            grandparent = None

                        parent = grandparent
                        while parent is not None:
                            if parent.Proxy.eligibleChild(obj.Proxy.Type):
                                self._obj.removeObject(obj)
                                obj.Proxy.setParent(parent)
                                parent.addObject(obj)
                                return
                            parent = parent.Proxy._parent
                index += 1

        if self.getParent() is not None:
            self.getParent()._moveChildUp(self._obj)
        return

    def moveDown(self):
        # Move the part up in the tree
        if self.getParent() is not None:
            self.getParent()._moveChildDown(self._obj)
            self.reposition()

    def _moveChildDown(self, obj):
        if hasattr(self._obj, "Group"):
            index = 0
            last = len(self._obj.Group) - 1
            for child in self._obj.Group:
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
                            # Swap with the next entrysetParent
                            group = self._obj.Group
                            temp = group[index + 1]
                            group[index + 1] = obj
                            group[index] = temp
                            self._obj.Group = group
                            return
                    else:
                        current = self
                        parent = self.getParent()
                        if parent is not None:
                            parent = parent._obj
                        while parent is not None:
                            if parent.Proxy.eligibleChild(obj.Proxy.Type):
                                # parentLen = len(parent.Group)
                                index1 = 0
                                for child in parent.Group:
                                    if child.Proxy == current:
                                        self._obj.removeObject(obj)
                                        obj.Proxy.setParent(parent)
                                        group = parent.Group
                                        group.insert(index1 + 1, obj)
                                        parent.Group = group
                                        return
                                    index1 += 1
                            else:
                                break
                            current = parent
                            parent = parent._parent
                index += 1

        if self.getParent() is not None:
            self.getParent()._moveChildDown(self._obj)
        return

    # This will be implemented in the derived class
    def execute(self, obj):
        _err("No execute method defined for %s" % (self.__class__.__name__))
