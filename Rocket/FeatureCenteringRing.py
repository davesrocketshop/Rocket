# SPDX-License-Identifier: LGPL-2.1-or-later
# SPDX-FileCopyrightText: 2021 David Carter <dcarter@davidcarter.ca>
# SPDX-File-Notice: Part of the Rocket addon.


"""Class for drawing centering rings"""

__title__ = "FreeCAD Centering Rings"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

from typing import Any

import FreeCAD

translate = FreeCAD.Qt.translate

from Rocket.FeatureBulkhead import FeatureBulkhead
from Rocket.FeatureInnerTube import FeatureInnerTube
from Rocket.util.Coordinate import Coordinate, NUL
from Rocket.Constants import FEATURE_CENTERING_RING

from Rocket.ShapeHandlers.CenteringRingShapeHandler import CenteringRingShapeHandler

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

                    pos1 = self.toRelative(NUL, sibling.Proxy)[0].x
                    pos2 = self.toRelative(Coordinate(self.getLength()), sibling.Proxy)[0].x
                    if pos2 < 0 or pos1 > sibling.Proxy.getLength():
                        continue

                    self._obj.CenterDiameter = max(self._obj.CenterDiameter, sibling.Proxy.getOuterDiameter(pos))

                self._obj.CenterDiameter = min(self._obj.CenterDiameter, self.getOuterDiameter(pos))

        return super().getInnerDiameter(pos)

    def execute(self, obj : Any) -> None:
        shape = CenteringRingShapeHandler(obj)
        if shape:
            shape.draw()
