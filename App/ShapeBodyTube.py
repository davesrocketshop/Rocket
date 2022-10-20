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
"""Class for drawing body tubes"""

__title__ = "FreeCAD Body Tubes"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

from PySide import QtCore
    
from App.interfaces.BoxBounded import BoxBounded
from App.interfaces.Coaxial import Coaxial

from App.ShapeBase import TRACE_POSITION, TRACE_EXECUTION
from App.SymetricComponent import SymetricComponent
from App.Constants import FEATURE_BODY_TUBE, FEATURE_BULKHEAD, FEATURE_CENTERING_RING, FEATURE_FIN, FEATURE_FINCAN, FEATURE_LAUNCH_LUG, \
    FEATURE_PARALLEL_STAGE, FEATURE_POD, FEATURE_RAIL_BUTTON, FEATURE_RAIL_GUIDE

from App.BodyTubeShapeHandler import BodyTubeShapeHandler
from App.Utilities import _wrn

from DraftTools import translate

def _migrate_from_1_0(obj):
    _wrn("Body tube migrating object from 1.0")

    old = {}
    old["InnerDiameter"] = obj.InnerDiameter

    obj.removeProperty("InnerDiameter")

    ShapeBodyTube(obj)

    od = float(obj.OuterDiameter)
    if od > 0.0:
        thickness = (od - float(old["InnerDiameter"])) / 2.0
        obj.Thickness = thickness

class ShapeBodyTube(SymetricComponent, BoxBounded, Coaxial):

    def __init__(self, obj):
        super().__init__(obj)
        self.Type = FEATURE_BODY_TUBE

        # self.AxialMethod = AxialMethod.AFTER

        # Default set to a BT-50
        if not hasattr(obj,"OuterDiameter"):
            obj.addProperty('App::PropertyLength', 'OuterDiameter', 'BodyTube', translate('App::Property', 'Diameter of the outside of the body tube')).OuterDiameter = 24.79
        if not hasattr(obj, 'AutoDiameter'):
            obj.addProperty('App::PropertyBool', 'AutoDiameter', 'BodyTube', translate('App::Property', 'Automatically set the outer diameter when possible')).AutoDiameter = False
        if not hasattr(obj,"Thickness"):
            obj.addProperty('App::PropertyLength', 'Thickness', 'BodyTube', translate('App::Property', 'Diameter of the inside of the body tube')).Thickness = 0.33
        if not hasattr(obj,"Length"):
            obj.addProperty('App::PropertyLength', 'Length', 'BodyTube', translate('App::Property', 'Length of the body tube')).Length = 457.0

        if not hasattr(obj, 'MotorMount'):
            obj.addProperty('App::PropertyBool', 'MotorMount', 'BodyTube', translate('App::Property', 'This component is a motor mount')).MotorMount = False
        if not hasattr(obj,"Overhang"):
            obj.addProperty('App::PropertyDistance', 'Overhang', 'BodyTube', translate('App::Property', 'Motor overhang')).Overhang = 3.0

        if not hasattr(obj,"Shape"):
            obj.addProperty('Part::PropertyPartShape', 'Shape', 'BodyTube', translate('App::Property', 'Shape of the body tube'))

        # if not hasattr(obj,"Group"):
        #     obj.addExtension("App::GroupExtensionPython")

    def onDocumentRestored(self, obj):
        super().onDocumentRestored(obj)

        if hasattr(obj, "InnerDiameter"):
            _migrate_from_1_0(obj)
        else:
            ShapeBodyTube(obj)

    def getLength(self):
        if TRACE_POSITION:
            print("P: ShapeBodyTube::getLength(%s)" % (self._obj.Label))

        # Return the length of this component along the central axis
        return self._obj.Length

    def getMaxForwardPosition(self):
        if TRACE_POSITION:
            print("P: ShapeBodyTube::getMaxForwardPosition(%s)" % (self._obj.Label))

        return float(self._obj.Length) + float(self._obj.Placement.Base.x)

    def _setAutoDiameter(self):
        if TRACE_POSITION:
            print("P: ShapeBodyTube::_setAutoDiameter(%s)" % (self._obj.Label))

        # For placing objects on the outer part of the parent
        if self._obj.AutoDiameter:
            radius = 0.0
            previous = self.getPrevious()
            if previous is not None:
                radius = previous.Proxy.getAftRadius()
            if radius <= 0.0:
                next = self.getNext()
                if next is not None:
                    radius = next.Proxy.getForeRadius()
            if radius <= 0.0:
                radius = (24.79 / 2.0) # Default to BT50
            diameter = 2.0 * radius
            if self._obj.OuterDiameter != diameter:
                self._obj.OuterDiameter = diameter
                self.setEdited()

    def getForeRadius(self):
        if TRACE_POSITION:
            print("P: ShapeBodyTube::getForeRadius(%s)" % (self._obj.Label))

        # For placing objects on the outer part of the parent
        self._setAutoDiameter()
        return self._obj.OuterDiameter / 2.0

    def getInnerRadius(self):
        if TRACE_POSITION:
            print("P: ShapeBase::getInnerRadius(%s)" % (self._obj.Label))

        # Set any autodiameter first
        self._setAutoDiameter()
        return float(self._obj.OuterDiameter) / 2.0 - float(self._obj.Thickness)

    def execute(self, obj):
        if TRACE_EXECUTION:
            print("E: ShapeBodyTube::execute(%s)" % (self._obj.Label))

        shape = BodyTubeShapeHandler(obj)
        if shape is not None:
            shape.draw()

    def eligibleChild(self, childType):
        return childType in [
            FEATURE_BULKHEAD, 
            FEATURE_BODY_TUBE, 
            FEATURE_CENTERING_RING, 
            FEATURE_FIN, 
            FEATURE_FINCAN, 
            FEATURE_LAUNCH_LUG,
            # FEATURE_PARALLEL_STAGE, 
            # FEATURE_POD,
            FEATURE_RAIL_BUTTON, 
            FEATURE_RAIL_GUIDE]

    def onChildEdited(self):
        try:
            # print("%s: onChildEdited()" % (self.__class__.__name__))
            self._obj.Proxy.setEdited()
        except ReferenceError:
            # Already deleted object
            pass

def hookChildren(obj, group, oldGroup):
    # print("hookChildren()")
    # changed = False
    # for child in group:
    #     if child not in oldGroup:
    #         # print("%s: hookChildren added" % (child.__class__.__name__))
    #         child.Proxy.resetPlacement()
    #         # child.Proxy.edited.connect(obj.Proxy.onChildEdited, QtCore.Qt.QueuedConnection)
    #         child.Proxy.connect(obj.Proxy.onChildEdited, QtCore.Qt.QueuedConnection)
    #         changed = True

    # for child in oldGroup:
    #     if child not in group:
    #         # print("%s: hookChildren removed" % (child.__class__.__name__))
    #         # child.Proxy.edited.connect(None)
    #         try:
    #             child.Proxy.disconnect()
    #             changed = True
    #         except ReferenceError:
    #             pass # object may be deleted

    # if changed:
    #     obj.Proxy.setEdited()
    pass

