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

from App.ShapeBase import ShapeBase
from App.ShapeStage import ShapeStage
from App.ShapeComponent import ShapeRadialLocation
from App.Constants import FEATURE_ROCKET, FEATURE_STAGE, FEATURE_PARALLEL_STAGE
from App.Constants import PROP_TRANSIENT, PROP_HIDDEN, PROP_NORECOMPUTE
from App.Constants import PLACEMENT_RADIAL


class ShapeParallelStage(ShapeRadialLocation, ShapeStage):

    def __init__(self, obj):
        super().__init__(obj)
        self._initShapeStage(obj)

        self.Type = FEATURE_PARALLEL_STAGE
        self._obj.PlacementType = PLACEMENT_RADIAL

        if not hasattr(obj,"StageCount"):
            obj.addProperty('App::PropertyInteger', 'StageCount', 'Stage', translate('App::Property', 'Number of stages in a radial pattern')).StageCount = 2
        if not hasattr(obj,"StageSpacing"):
            obj.addProperty('App::PropertyAngle', 'StageSpacing', 'Stage', translate('App::Property', 'Angle between consecutive stages')).StageSpacing = 180

    def eligibleChild(self, childType):
        return childType not in [FEATURE_ROCKET, FEATURE_STAGE, FEATURE_PARALLEL_STAGE]

def hookChild(obj, child, oldGroup):
    if child not in oldGroup:
        child.Proxy.resetPlacement()
        # child.Proxy.edited.connect(obj.Proxy.positionChildren, QtCore.Qt.QueuedConnection)
        child.Proxy.connect(obj.Proxy.positionChildren, QtCore.Qt.QueuedConnection)


def unhookChild(obj, child, group):
    if child not in group:
        try:
            # child.Proxy.edited.connect(None)
            child.Proxy.disconnect()
        except ReferenceError:
            # Object may be deleted
            pass

def hookChildren(obj, group, oldGroup):
    for child in group:
        hookChild(obj, child, oldGroup)

    for child in oldGroup:
        unhookChild(obj, child, group)

    # obj.Proxy.positionChildren(float(obj.RadialOffset))

