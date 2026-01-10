# SPDX-License-Identifier: LGPL-2.1-or-later
# SPDX-File-Notice: Part of the Rocket addon.

# ***************************************************************************
# *   Copyright (c) 2021-2025 David Carter <dcarter@davidcarter.ca>         *
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
"""Class for bulkheads"""

__title__ = "FreeCAD Bulkheads"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

from typing import Any

import FreeCAD

translate = FreeCAD.Qt.translate

from Rocket.RadiusRingComponent import RadiusRingComponent
from Rocket.Constants import FEATURE_BULKHEAD

from Rocket.ShapeHandlers.BulkheadShapeHandler import BulkheadShapeHandler

class FeatureBulkhead(RadiusRingComponent):

    def __init__(self, obj):
        super().__init__(obj)
        self.Type = FEATURE_BULKHEAD

        if not hasattr(obj, 'Thickness'):
            obj.addProperty('App::PropertyLength', 'Thickness', 'RocketComponent', translate('App::Property', 'Thickness of the bulkhead without any inner step')).Thickness = 2.0

        if not hasattr(obj, 'Step'):
            obj.addProperty('App::PropertyBool', 'Step', 'RocketComponent', translate('App::Property', 'Bulkheads may have a step that fits a smaller diameter')).Step = False
        if not hasattr(obj, 'StepReverse'):
            obj.addProperty('App::PropertyBool', 'StepReverse', 'RocketComponent', translate('App::Property', 'Bulkheads may have a step that fits a smaller diameter')).StepReverse = False
        if not hasattr(obj, 'StepDiameter'):
            obj.addProperty('App::PropertyLength', 'StepDiameter', 'RocketComponent', translate('App::Property', 'Outer diameter of the step')).StepDiameter = 21.0
        if not hasattr(obj, 'StepThickness'):
            obj.addProperty('App::PropertyLength', 'StepThickness', 'RocketComponent', translate('App::Property', 'Thickness of the step')).StepThickness = 2.0

        if not hasattr(obj, 'Holes'):
            obj.addProperty('App::PropertyBool', 'Holes', 'RocketComponent', translate('App::Property', 'Bulkheads may have holes for attaching eyebolts or retainers')).Holes = False
        if not hasattr(obj, 'HoleDiameter'):
            obj.addProperty('App::PropertyLength', 'HoleDiameter', 'RocketComponent', translate('App::Property', 'Hole diameter')).HoleDiameter = 5.0
        if not hasattr(obj, 'HoleCenter'):
            obj.addProperty('App::PropertyLength', 'HoleCenter', 'RocketComponent', translate('App::Property', 'Distance from the center of the bulkhead to the center of the hole')).HoleCenter = 6.25
        if not hasattr(obj, 'HoleCount'):
            obj.addProperty('App::PropertyInteger', 'HoleCount', 'RocketComponent', translate('App::Property', 'Number of holes in a radial pattern')).HoleCount = 1
        if not hasattr(obj, 'HoleOffset'):
            obj.addProperty('App::PropertyAngle', 'HoleOffset', 'RocketComponent', translate('App::Property', 'Outer diameter of the bulkhead')).HoleOffset = 0

    def setDefaults(self) -> None:
        super().setDefaults()

        self.setOuterDiameterAutomatic(True)
        self._obj.Diameter = 25.0

    def onDocumentRestored(self, obj : Any) -> None:
        FeatureBulkhead(obj)

        # Convert from the pre-1.0 material system if required
        self.convertMaterialAndAppearance(obj)

        self._obj = obj

    def getLength(self) -> float:
        # Return the length of this component along the central axis
        return float(self._obj.Thickness) / self.getScale()

    def setLength(self, length : float) -> None:
        self._obj.Thickness = length

    def execute(self, obj : Any) -> None:
        shape = BulkheadShapeHandler(obj)
        if shape:
            shape.draw()
