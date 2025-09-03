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
"""Class for drawing centering rings"""

__title__ = "FreeCAD Centering Rings"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

from typing import Any

from Rocket.FeatureBulkhead import FeatureBulkhead
from Rocket.FeatureInnerTube import FeatureInnerTube
from Rocket.util.Coordinate import Coordinate, NUL
from Rocket.Constants import FEATURE_CENTERING_RING

from Rocket.ShapeHandlers.CenteringRingShapeHandler import CenteringRingShapeHandler

from Rocket.Utilities import translate

#
# Centering rings are an extension of bulkheads
#
class FeatureCenteringRing(FeatureBulkhead):

    def __init__(self, obj : Any):
        super().__init__(obj)
        self.Type = FEATURE_CENTERING_RING

        if not hasattr(obj, 'Notched'):
            obj.addProperty('App::PropertyBool', 'Notched', 'RocketComponent', translate('App::Property', 'Include a notch for an engine hook')).Notched = False
        if not hasattr(obj, 'NotchWidth'):
            obj.addProperty('App::PropertyLength', 'NotchWidth', 'RocketComponent', translate('App::Property', 'Width of the engine hook notch')).NotchWidth = 3.0
        if not hasattr(obj, 'NotchHeight'):
            obj.addProperty('App::PropertyLength', 'NotchHeight', 'RocketComponent', translate('App::Property', 'Height of the engine hook notch')).NotchHeight = 3.0

    def setDefaults(self) -> None:
        super().setDefaults()

        self.setOuterDiameterAutomatic(True)
        self.setInnerDiameterAutomatic(True)
        self.setLength(2.0)
        self._obj.HoleDiameter = 2.0
        self._obj.HoleCenter = 7.0

    def onDocumentRestored(self, obj : Any) -> None:
        FeatureCenteringRing(obj)

        # Convert from the pre-1.0 material system if required
        self.convertMaterialAndAppearance(obj)

        self._obj = obj

    def update(self) -> None:
        super().update()

        # Ensure any automatic variables are set
        self.getInnerDiameter(0)

    def getInnerRadius(self, pos : float) -> float:
        return self.getInnerDiameter(pos) / 2.0

    def getInnerDiameter(self, pos : float) -> float:
        # Implement sibling inner radius automation
        if self.isInnerDiameterAutomatic():
            self._obj.CenterDiameter = 0
            # Component can be parentless if detached from rocket
            if self.hasParent():
                for sibling in self.getParent().getChildren():
                    # Only InnerTubes are considered when determining the automatic
                    # inner radius (for now).
                    if not isinstance(sibling.Proxy, FeatureInnerTube): # Excludes itself
                        continue

                    pos1 = self.toRelative(NUL, sibling.Proxy)[0]._x
                    pos2 = self.toRelative(Coordinate(self.getLength()), sibling.Proxy)[0]._x
                    if pos2 < 0 or pos1 > sibling.Proxy.getLength():
                        continue

                    self._obj.CenterDiameter = max(self._obj.CenterDiameter, sibling.Proxy.getOuterDiameter(pos))

                self._obj.CenterDiameter = min(self._obj.CenterDiameter, self.getOuterDiameter(pos))

        return super().getInnerDiameter(pos)

    def execute(self, obj : Any) -> None:
        shape = CenteringRingShapeHandler(obj)
        if shape:
            shape.draw()
