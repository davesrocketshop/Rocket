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

import FreeCAD

from PySide import QtCore
from DraftTools import translate

from App.ShapeBase import ShapeBase, TRACE_POSITION, TRACE_EXECUTION
from App.Constants import FEATURE_ROCKET, FEATURE_STAGE
from App.Constants import PROP_TRANSIENT, PROP_HIDDEN, PROP_NORECOMPUTE

class ShapeStage(ShapeBase):

    def __init__(self, obj):
        super().__init__(obj)

        self._initShapeStage(obj)

    def _initShapeStage(self, obj):
        self.Type = FEATURE_STAGE
        
        if not hasattr(obj,"Group"):
            obj.addExtension("App::GroupExtensionPython")
        if not hasattr(obj, 'AxialOffset'):
            obj.addProperty('App::PropertyDistance', 'AxialOffset', 'RocketComponent', translate('App::Property', 'Axial offset from the center line'), PROP_TRANSIENT|PROP_HIDDEN|PROP_NORECOMPUTE).AxialOffset = 0.0

    def execute(self,obj):
        if TRACE_EXECUTION:
            print("E: ShapeStage::execute(%s)" % (self._obj.Label))

        # print("TypeNoRecompute %d" % (self.TypeNoRecompute))
        self.positionChildren(self._obj.AxialOffset)
        if not hasattr(obj,'Shape'):
            return

    def eligibleChild(self, childType):
        return childType not in [FEATURE_ROCKET, FEATURE_STAGE]

    def setAxialPosition(self, partBase):
        if TRACE_POSITION:
            print("P: ShapeStage::setAxialPosition(%s, %f)" % (self._obj.Label, partBase))

        base = self._obj.Placement.Base
        newBase = FreeCAD.Placement(FreeCAD.Vector(partBase, base.y, base.z), FreeCAD.Rotation(0,0,0))
        # self._obj.Placement = FreeCAD.Placement(FreeCAD.Vector(0.0, base.y, base.z), FreeCAD.Rotation(0,0,0))
        if newBase != self._obj.Placement:
            self._obj.Placement = newBase

        # self.positionChildren(partBase)
        # self.positionChildren(0.0)

    def positionChildren(self, partBase=0.0):
        if TRACE_POSITION:
            print("P: ShapeStage::positionChildren(%s, %f)" % (self._obj.Label, partBase))
        
        # Dynamic placements
        try:
            if self._obj.AxialOffset != partBase:
                self._obj.AxialOffset = partBase

            length = float(partBase)
            i = len(self._obj.Group) - 1
            while i >= 0:
                child = self._obj.Group[i]
                child.Proxy.setAxialPosition(length)

                length += float(child.Proxy.getAxialLength())
                i -= 1

            # FreeCAD.ActiveDocument.recompute()
        except ReferenceError:
            # Deleted object
            pass

def hookChild(obj, child, oldGroup):
    if child not in oldGroup:
        child.Proxy.resetPlacement()
        child.Proxy.connect(obj.Proxy.positionChildren, QtCore.Qt.QueuedConnection)


def unhookChild(obj, child, group):
    if child not in group:
        try:
            child.Proxy.disconnect()
        except ReferenceError:
            # Object may be deleted
            pass

def hookChildren(obj, group, oldGroup):
    # for child in group:
    #     hookChild(obj, child, oldGroup)

    # for child in oldGroup:
    #     unhookChild(obj, child, group)

    # obj.Proxy.positionChildren(float(obj.AxialOffset))
    pass

