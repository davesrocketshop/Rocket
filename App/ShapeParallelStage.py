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

from App.ShapeBase import TRACE_POSITION
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

    def positionChild(self, parent, parentBase, parentLength, parentRadius, rotation):
        if TRACE_POSITION:
            print("P: ShapeParallelStage::positionChild(%s, %s, (%f,%f,%f), %f, %f, %f)" % (self._obj.Label, parent.Label, parentBase.x, parentBase.y, parentBase.z, parentLength, parentRadius, rotation))

        base = FreeCAD.Vector(parentBase)
        base.z = parentRadius

        # radius = 0.0

        # base = self._obj.Placement.Base
        roll = 0.0
        self._obj.Placement = FreeCAD.Placement(FreeCAD.Vector(base), FreeCAD.Rotation(FreeCAD.Vector(1,0,0), roll))

        self.positionChildren(base)

    def eligibleChild(self, childType):
        return childType not in [FEATURE_ROCKET, FEATURE_STAGE, FEATURE_PARALLEL_STAGE]