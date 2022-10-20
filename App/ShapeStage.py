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

from App.ShapeBase import TRACE_POSITION, TRACE_EXECUTION
from App.ShapeComponentAssembly import ShapeComponentAssembly
from App.Constants import FEATURE_ROCKET, FEATURE_STAGE, FEATURE_PARALLEL_STAGE
from App.Constants import PROP_TRANSIENT, PROP_HIDDEN, PROP_NORECOMPUTE

class ShapeStage(ShapeComponentAssembly):

    def __init__(self, obj):
        super().__init__(obj)

        self._initShapeStage(obj)

    def _initShapeStage(self, obj):
        self.Type = FEATURE_STAGE
        
        # if not hasattr(obj,"Group"):
        #     obj.addExtension("App::GroupExtensionPython")
        # if not hasattr(obj, 'AxialOffset'):
        #     obj.addProperty('App::PropertyDistance', 'AxialOffset', 'RocketComponent', translate('App::Property', 'Axial offset from the center line'), PROP_TRANSIENT|PROP_HIDDEN|PROP_NORECOMPUTE).AxialOffset = 0.0
        if not hasattr(obj,"StageNumber"):
            obj.addProperty('App::PropertyInteger', 'StageNumber', 'RocketComponent', translate('App::Property', 'Stage number')).StageNumber = 0
 
    def setStageNumber(self, newStageNumber):
        self._obj.StageNumber = newStageNumber
    
    def getStageNumber(self):
        return self._obj.StageNumber

    def execute(self,obj):
        if TRACE_EXECUTION:
            print("E: ShapeStage::execute(%s)" % (self._obj.Label))

        if not hasattr(obj,'Shape'):
            return

    def eligibleChild(self, childType):
        return childType not in [FEATURE_ROCKET, FEATURE_STAGE]

    # def setAxialPosition(self, partBase):
    #     if TRACE_POSITION:
    #         print("P: ShapeStage::setAxialPosition(%s, (%f,%f,%f))" % (self._obj.Label, partBase.x, partBase.y, partBase.z))

    #     # base = FreeCAD.Vector(self._obj.Placement.Base)
    #     base = FreeCAD.Vector(partBase)
    #     base.x = 0.0
    #     newPlacement = FreeCAD.Placement(base, FreeCAD.Rotation(0,0,0))
    #     # newPlacement = FreeCAD.Placement(FreeCAD.Vector(partBase), FreeCAD.Rotation(0,0,0))
    #     # newPlacement = FreeCAD.Placement(FreeCAD.Vector(0.0, base.y, base.z), FreeCAD.Rotation(0,0,0))
    #     if newPlacement != self._obj.Placement:
    #         self._obj.Placement = newPlacement

    #     # self.positionChildren(partBase)
    #     # self.positionChildren(0.0)

    # def positionChildren(self, partBase):
    #     if TRACE_POSITION:
    #         print("P: ShapeStage::positionChildren(%s, (%f,%f,%f))" % (self._obj.Label, partBase.x, partBase.y, partBase.z))
        
    #     # Dynamic placements
    #     try:
    #         base = FreeCAD.Vector(partBase)
    #         self.setAxialPosition(base)

    #         print("start base.x %f, partBase.x %f" % (base.x, partBase.x))
    #         # base = FreeCAD.Vector(0,0,0)
    #         for child in reversed(self._obj.Group):
    #             if child.Proxy.Type == FEATURE_PARALLEL_STAGE:
    #                 child.Proxy.positionChild(self._obj, partBase, self.getLength(), self.getForeRadius(), 0.0)
    #             else:
    #                 child.Proxy.positionChild(self._obj, base, self.getLength(), self.getForeRadius(), 0.0)
    #                 base.x = max(base.x, float(child.Proxy.getMaxForwardPosition() ))
    #         print("end base.x %f, partBase.x %f" % (base.x, partBase.x))
 
    #     except ReferenceError:
    #         # Deleted object
    #         pass

# def hookChild(obj, child, oldGroup):
#     if child not in oldGroup:
#         child.Proxy.resetPlacement()
#         child.Proxy.connect(obj.Proxy.positionChildren, QtCore.Qt.QueuedConnection)


# def unhookChild(obj, child, group):
#     if child not in group:
#         try:
#             child.Proxy.disconnect()
#         except ReferenceError:
#             # Object may be deleted
#             pass

def hookChildren(obj, group, oldGroup):
    # for child in group:
    #     hookChild(obj, child, oldGroup)

    # for child in oldGroup:
    #     unhookChild(obj, child, group)

    # obj.Proxy.positionChildren(float(obj.AxialOffset))
    pass

