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

from App.ShapeBase import TRACE_POSITION, TRACE_EXECUTION
from App.ShapeComponent import ShapeComponent
from App.Constants import FEATURE_ROCKET, FEATURE_STAGE

class ShapeRocket(ShapeComponent):

    def __init__(self, obj):
        super().__init__(obj)
        self.Type = FEATURE_ROCKET
        
        # if not hasattr(obj,"Group"):
        #     obj.addExtension("App::GroupExtensionPython")

    def execute(self,obj):
        if TRACE_EXECUTION:
            print("E: ShapeRocket::execute(%s)" % (self._obj.Label))

        if not hasattr(obj,'Shape'):
            return

    def reposition(self):
        if TRACE_POSITION:
            print("P: ShapeRocket::reposition(%s)" % (self._obj.Label))

        self.positionChildren()
        FreeCAD.ActiveDocument.recompute()

    def eligibleChild(self, childType):
        return childType == FEATURE_STAGE

    def positionChildren(self):
        if TRACE_POSITION:
            print("P: ShapeRocket::positionChildren(%s)" % (self._obj.Label))

        # Dynamic placements
        try:
            base = FreeCAD.Vector(0, 0, 0)
            counter = 1
            for child in reversed(self._obj.Group):
                child.Proxy.positionChild(self._obj, base, 0, 0, 0)
                base.x = max(base.x, float(child.Proxy.getMaxForwardPosition() ))

        except ReferenceError:
            # Deleted object
            pass

def hookChildren(obj, group, oldGroup):
    # for child in group:
    #     if child not in oldGroup:
    #         # child.Proxy.resetPlacement()
    #         # child.Proxy.edited.connect(obj.Proxy.reposition, QtCore.Qt.QueuedConnection)
    #         child.Proxy.connect(obj.Proxy.reposition, QtCore.Qt.QueuedConnection)

    # for child in oldGroup:
    #     if child not in group:
    #         try:
    #             # child.Proxy.edited.connect(None)
    #             child.Proxy.disconnect()
    #         except ReferenceError:
    #             pass # object may be deleted

    # obj.Proxy.reposition()
    pass

