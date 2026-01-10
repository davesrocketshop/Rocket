# SPDX-License-Identifier: LGPL-2.1-or-later

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
"""Class for drawing fins"""

__title__ = "FreeCAD Fins"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

import math
from typing import Any

import FreeCAD

translate = FreeCAD.Qt.translate

from Rocket.position.AxialMethod import BOTTOM
from Rocket.ExternalComponent import ExternalComponent
from Rocket.SymmetricComponent import SymmetricComponent
from Rocket.FeatureInnerTube import FeatureInnerTube
from Rocket.util.Coordinate import Coordinate, NUL

from Rocket.Constants import FEATURE_FIN, FEATURE_LAUNCH_LUG, FEATURE_RAIL_BUTTON, FEATURE_POD, FEATURE_RINGTAIL
from Rocket.Constants import FIN_TYPE_TRAPEZOID, FIN_TYPE_TRIANGLE, FIN_TYPE_ELLIPSE, FIN_TYPE_TUBE, FIN_TYPE_SKETCH, FIN_TYPE_PROXY
from Rocket.Constants import FIN_CROSS_SAME, FIN_CROSS_SQUARE, FIN_CROSS_ROUND, FIN_CROSS_AIRFOIL, FIN_CROSS_WEDGE, \
    FIN_CROSS_DIAMOND, FIN_CROSS_TAPER_LE, FIN_CROSS_TAPER_TE, FIN_CROSS_TAPER_LETE, FIN_CROSS_ELLIPSE, FIN_CROSS_BICONVEX
from Rocket.Constants import FIN_DEBUG_FULL, FIN_DEBUG_PROFILE_ONLY, FIN_DEBUG_MASK_ONLY
from Rocket.Constants import PROP_TRANSIENT, PROP_HIDDEN

from Rocket.ShapeHandlers.FinTrapezoidShapeHandler import FinTrapezoidShapeHandler
from Rocket.ShapeHandlers.FinTriangleShapeHandler import FinTriangleShapeHandler
from Rocket.ShapeHandlers.FinEllipseShapeHandler import FinEllipseShapeHandler
from Rocket.ShapeHandlers.FinSketchShapeHandler import FinSketchShapeHandler
from Rocket.ShapeHandlers.FinTubeShapeHandler import FinTubeShapeHandler
from Rocket.ShapeHandlers.FinProxyShapeHandler import FinProxyShapeHandler

from Rocket.Utilities import _err, _toFloat

DEBUG_SKETCH_FINS = 0 # Set > 0 when debugging sketch based fins

class FeatureFin(ExternalComponent):

    def __init__(self, obj : Any) -> None:
        super().__init__(obj)
        self.Type = FEATURE_FIN
        self._shapeHandler = None

        if not hasattr(obj,"FinType"):
            obj.addProperty('App::PropertyEnumeration', 'FinType', 'RocketComponent', translate('App::Property', 'Fin type'))
            obj.FinType = [FIN_TYPE_TRAPEZOID,
                    FIN_TYPE_TRIANGLE,
                    FIN_TYPE_ELLIPSE,
                    FIN_TYPE_TUBE,
                    FIN_TYPE_SKETCH,
                    FIN_TYPE_PROXY
                    ]
            obj.FinType = FIN_TYPE_TRAPEZOID
        else:
            obj.FinType = [FIN_TYPE_TRAPEZOID,
                    FIN_TYPE_TRIANGLE,
                    FIN_TYPE_ELLIPSE,
                    FIN_TYPE_TUBE,
                    FIN_TYPE_SKETCH,
                    FIN_TYPE_PROXY
                    ]

        if not hasattr(obj,"RootCrossSection"):
            obj.addProperty('App::PropertyEnumeration', 'RootCrossSection', 'RocketComponent', translate('App::Property', 'Fin root cross section'))
            obj.RootCrossSection = [FIN_CROSS_SQUARE, FIN_CROSS_ROUND, FIN_CROSS_AIRFOIL, FIN_CROSS_WEDGE,
                FIN_CROSS_DIAMOND, FIN_CROSS_TAPER_LE, FIN_CROSS_TAPER_TE, FIN_CROSS_TAPER_LETE, FIN_CROSS_ELLIPSE, FIN_CROSS_BICONVEX]
            obj.RootCrossSection = FIN_CROSS_SQUARE
        else:
            obj.RootCrossSection = [FIN_CROSS_SQUARE, FIN_CROSS_ROUND, FIN_CROSS_AIRFOIL, FIN_CROSS_WEDGE,
                FIN_CROSS_DIAMOND, FIN_CROSS_TAPER_LE, FIN_CROSS_TAPER_TE, FIN_CROSS_TAPER_LETE, FIN_CROSS_ELLIPSE, FIN_CROSS_BICONVEX]

        if not hasattr(obj,"RootChord"):
            obj.addProperty('App::PropertyLength', 'RootChord', 'RocketComponent', translate('App::Property', 'Length of the base of the fin')).RootChord = 57.15
        if not hasattr(obj,"RootThickness"):
            obj.addProperty('App::PropertyLength', 'RootThickness', 'RocketComponent', translate('App::Property', 'Fin root thickness')).RootThickness = 1.4
        if not hasattr(obj,"RootPerCent"):
            obj.addProperty('App::PropertyBool', 'RootPerCent', 'RocketComponent', translate('App::Property', 'Root chord lengths are percentages')).RootPerCent = True
        if not hasattr(obj,"RootLength1"):
            obj.addProperty('App::PropertyLength', 'RootLength1', 'RocketComponent', translate('App::Property', 'Root chord length 1')).RootLength1 = 20.0
        if not hasattr(obj,"RootLength2"):
            obj.addProperty('App::PropertyLength', 'RootLength2', 'RocketComponent', translate('App::Property', 'Root chord length 2')).RootLength2 = 80.0

        if not hasattr(obj,"TipCrossSection"):
            obj.addProperty('App::PropertyEnumeration', 'TipCrossSection', 'RocketComponent', translate('App::Property', 'Fin tip cross section'))
            obj.TipCrossSection = [FIN_CROSS_SAME, FIN_CROSS_SQUARE, FIN_CROSS_ROUND, FIN_CROSS_AIRFOIL, FIN_CROSS_WEDGE,
                FIN_CROSS_DIAMOND, FIN_CROSS_TAPER_LE, FIN_CROSS_TAPER_TE, FIN_CROSS_TAPER_LETE, FIN_CROSS_ELLIPSE, FIN_CROSS_BICONVEX]
            obj.TipCrossSection = FIN_CROSS_SAME
        else:
            # Make sure these are up to date
            obj.TipCrossSection = [FIN_CROSS_SAME, FIN_CROSS_SQUARE, FIN_CROSS_ROUND, FIN_CROSS_AIRFOIL, FIN_CROSS_WEDGE,
                FIN_CROSS_DIAMOND, FIN_CROSS_TAPER_LE, FIN_CROSS_TAPER_TE, FIN_CROSS_TAPER_LETE, FIN_CROSS_ELLIPSE, FIN_CROSS_BICONVEX]

        if not hasattr(obj,"TipChord"):
            obj.addProperty('App::PropertyLength', 'TipChord', 'RocketComponent', translate('App::Property', 'Length of the tip of the fin')).TipChord = 30.48
        if not hasattr(obj,"TipThickness"):
            obj.addProperty('App::PropertyLength', 'TipThickness', 'RocketComponent', translate('App::Property', 'Fin tip thickness')).TipThickness = 1.4
        if not hasattr(obj,"TipSameThickness"):
            obj.addProperty('App::PropertyBool', 'TipSameThickness', 'RocketComponent', translate('App::Property', 'Fin tip thickness is the same as the root thickness')).TipSameThickness = True
        if not hasattr(obj,"TipPerCent"):
            obj.addProperty('App::PropertyBool', 'TipPerCent', 'RocketComponent', translate('App::Property', 'Tip chord lengths are percentages')).TipPerCent = True
        if not hasattr(obj,"TipLength1"):
            obj.addProperty('App::PropertyLength', 'TipLength1', 'RocketComponent', translate('App::Property', 'Tip chord length 1')).TipLength1 = 20.0
        if not hasattr(obj,"TipLength2"):
            obj.addProperty('App::PropertyLength', 'TipLength2', 'RocketComponent', translate('App::Property', 'Tip chord length 2')).TipLength2 = 80.0

        if not hasattr(obj,"Height"):
            obj.addProperty('App::PropertyLength', 'Height', 'RocketComponent', translate('App::Property', 'Fin semi-span')).Height = 40.64
        if not hasattr(obj,"SweepLength"):
            obj.addProperty('App::PropertyDistance', 'SweepLength', 'RocketComponent', translate('App::Property', 'Sweep length')).SweepLength = 69.86 # Must be distance since it can be negative
        if not hasattr(obj,"SweepAngle"):
            obj.addProperty('App::PropertyAngle', 'SweepAngle', 'RocketComponent', translate('App::Property', 'Sweep angle')).SweepAngle = 0.0
        if not hasattr(obj,"Cant"):
            obj.addProperty('App::PropertyAngle', 'Cant', 'RocketComponent', translate('App::Property', 'Fin cant')).Cant = 0.0

        if not hasattr(obj,"AutoHeight"):
            obj.addProperty('App::PropertyBool', 'AutoHeight', 'RocketComponent', translate('App::Property', 'Automatically set the fin height to reach the desired spans')).AutoHeight = False
        if not hasattr(obj,"Span"):
            obj.addProperty('App::PropertyLength', 'Span', 'RocketComponent', translate('App::Property', 'Fin total span')).Span = (2.0 * 40.64)

        if not hasattr(obj,"Ttw"):
            obj.addProperty('App::PropertyBool', 'Ttw', 'RocketComponent', translate('App::Property', 'Through the wall (TTW) tab')).Ttw = False
        if not hasattr(obj,"TtwOffset"):
            obj.addProperty('App::PropertyLength', 'TtwOffset', 'RocketComponent', translate('App::Property', 'TTW Offset from fin root')).TtwOffset = 2.0
        if not hasattr(obj,"TtwLength"):
            obj.addProperty('App::PropertyLength', 'TtwLength', 'RocketComponent', translate('App::Property', 'TTW Length')).TtwLength = 6.0
        if not hasattr(obj,"TtwHeight"):
            obj.addProperty('App::PropertyLength', 'TtwHeight', 'RocketComponent', translate('App::Property', 'TTW Height')).TtwHeight = 10.0
        if not hasattr(obj,"TtwAutoHeight"):
            obj.addProperty('App::PropertyBool', 'TtwAutoHeight', 'RocketComponent', translate('App::Property', 'Automatically set the TTW Height')).TtwAutoHeight = True
        if not hasattr(obj,"TtwThickness"):
            obj.addProperty('App::PropertyLength', 'TtwThickness', 'RocketComponent', translate('App::Property', 'TTW thickness')).TtwThickness = 1.0

        if not hasattr(obj,"FinSet"):
            obj.addProperty('App::PropertyBool', 'FinSet', 'RocketComponent', translate('App::Property', 'True when describing a set of fins')).FinSet = True
        if not hasattr(obj,"FinCount"):
            obj.addProperty('App::PropertyInteger', 'FinCount', 'RocketComponent', translate('App::Property', 'Number of fins in a radial pattern')).FinCount = 3
        if not hasattr(obj,"FinSpacing"):
            obj.addProperty('App::PropertyAngle', 'FinSpacing', 'RocketComponent', translate('App::Property', 'Angle between consecutive fins')).FinSpacing = 120

        if not hasattr(obj,"TubeOuterDiameter"):
            obj.addProperty('App::PropertyLength', 'TubeOuterDiameter', 'RocketComponent', translate('App::Property', 'Tube fin outer diameter')).TubeOuterDiameter = 30.0
        if not hasattr(obj,"TubeAutoOuterDiameter"):
            obj.addProperty('App::PropertyBool', 'TubeAutoOuterDiameter', 'RocketComponent', translate('App::Property', 'Tube fin auto outer diameter')).TubeAutoOuterDiameter = True
        if not hasattr(obj,"TubeThickness"):
            obj.addProperty('App::PropertyLength', 'TubeThickness', 'RocketComponent', translate('App::Property', 'Tube fin thickness')).TubeThickness = 1.0

        if not hasattr(obj,"MinimumEdge"):
            obj.addProperty('App::PropertyBool', 'MinimumEdge', 'RocketComponent', translate('App::Property', 'Set a minimum edge size for fins that would normally have a sharp edge')).MinimumEdge = False
        if not hasattr(obj,"MinimumEdgeSize"):
            obj.addProperty('App::PropertyLength', 'MinimumEdgeSize', 'RocketComponent', translate('App::Property', 'Minimum edge size')).MinimumEdgeSize = 0.2

        # Hidden properties used for calculation
        if not hasattr(obj,"ParentRadius"):
            obj.addProperty('App::PropertyLength', 'ParentRadius', 'RocketComponent', 'Parent radius', PROP_TRANSIENT | PROP_HIDDEN).ParentRadius = 20.0 # No translation required for a hidden parameter
        if not hasattr(obj,"AutoDiameter"):
            obj.addProperty('App::PropertyBool', 'AutoDiameter', 'RocketComponent', translate('App::Property', 'Automatically set diameter')).AutoDiameter = True
        obj.setEditorMode('AutoDiameter', PROP_HIDDEN)  # hide

        if not hasattr(obj,"FilletCrossSection"):
            obj.addProperty('App::PropertyEnumeration', 'FilletCrossSection', 'RocketComponent', translate('App::Property', 'Fin fillet cross section'))
            obj.FilletCrossSection = [FIN_CROSS_SAME, FIN_CROSS_SQUARE, FIN_CROSS_ROUND, FIN_CROSS_AIRFOIL, FIN_CROSS_WEDGE,
                FIN_CROSS_DIAMOND, FIN_CROSS_TAPER_LE, FIN_CROSS_TAPER_TE, FIN_CROSS_TAPER_LETE, FIN_CROSS_ELLIPSE, FIN_CROSS_BICONVEX]
            obj.FilletCrossSection = FIN_CROSS_ROUND
        else:
            # Make sure these are up to date
            obj.FilletCrossSection = [FIN_CROSS_SAME, FIN_CROSS_SQUARE, FIN_CROSS_ROUND, FIN_CROSS_AIRFOIL, FIN_CROSS_WEDGE,
                FIN_CROSS_DIAMOND, FIN_CROSS_TAPER_LE, FIN_CROSS_TAPER_TE, FIN_CROSS_TAPER_LETE, FIN_CROSS_ELLIPSE, FIN_CROSS_BICONVEX]
        if not hasattr(obj, 'Fillets'):
            obj.addProperty('App::PropertyBool', 'Fillets', 'RocketComponent', translate('App::Property', 'Apply fin fillets')).Fillets = False
        if not hasattr(obj,"FilletRadius"):
            obj.addProperty('App::PropertyLength', 'FilletRadius', 'RocketComponent', translate('App::Property', 'Fillet radius')).FilletRadius = 5

        if not hasattr(obj, 'ScaleByRootChord'):
            obj.addProperty('App::PropertyBool', 'ScaleByRootChord', 'RocketComponent', translate('App::Property', 'Scale the object by root chord')).ScaleByRootChord = False
        if not hasattr(obj, 'ScaleByHeight'):
            obj.addProperty('App::PropertyBool', 'ScaleByHeight', 'RocketComponent', translate('App::Property', 'Scale the object by fin height')).ScaleByHeight = False

        if not hasattr(obj, "Profile"):
            obj.addProperty('App::PropertyLink', 'Profile', 'RocketComponent', translate('App::Property', 'Custom fin sketch')).Profile = None

        if not hasattr(obj, 'ProxyPlacement'):
            obj.addProperty('App::PropertyPlacement', 'ProxyPlacement', 'RocketComponent', translate('App::Property', 'This is the local coordinate system within the rocket object that will be used for the proxy feature')).ProxyPlacement
        if not hasattr(obj, 'Base'):
            obj.addProperty('App::PropertyLink', 'Base', 'RocketComponent', translate('App::Property', 'The base object used to define the nose cone shape'))

        # A transient property for debugging sketch based fins
        if DEBUG_SKETCH_FINS > 0:
            if not hasattr(obj,"DebugSketch"):
                obj.addProperty('App::PropertyEnumeration', 'DebugSketch', 'RocketComponent', translate('App::Property', 'Sketch based fin debugging options'), PROP_TRANSIENT)
                obj.DebugSketch = [FIN_DEBUG_FULL, FIN_DEBUG_PROFILE_ONLY, FIN_DEBUG_MASK_ONLY]
                obj.DebugSketch = FIN_DEBUG_FULL

        self._setFinEditorVisibility()

    def setDefaults(self) -> None:
        self.sweepAngleFromLength()
        super().setDefaults()

        self._obj.AxialMethod = BOTTOM

    def _setFinEditorVisibility(self) -> None:
        # self._obj.setEditorMode('FinSet', EDITOR_HIDDEN)  # hide
        # self._obj.setEditorMode('FinCount', EDITOR_HIDDEN)  # show
        # self._obj.setEditorMode('FinSpacing', EDITOR_HIDDEN)  # show
        pass

    def onDocumentRestored(self, obj : Any) -> None:
        if obj:
            FeatureFin(obj) # Update any properties

            # Convert from the pre-1.0 material system if required
            self.convertMaterialAndAppearance(obj)

            self._obj = obj

        self._setFinEditorVisibility()

    def update(self) -> None:
        super().update()

        # Ensure any automatic variables are set
        self.setParentDiameter()
        self.getTubeOuterDiameter()
        self.setFinAutoHeight()
        self._setTtwAutoHeight(0)

    def _isDiameterScaled(self) -> bool:
        if self._obj.AutoDiameter:
            return False
        return self.isScaled()

    def getDiameterScale(self) -> float:
        if self._isDiameterScaled():
            return self.getScale()
        return 1.0

    def getScale(self) -> float:
        if self.hasParent() and not self._obj.ScaleOverride:
            if self.getParent().isScaled():
                return self.getParent().getScale()

        scale = 1.0
        if self._obj.Scale:
            if self._obj.ScaleByValue and self._obj.ScaleValue.Value > 0.0:
                scale = self._obj.ScaleValue.Value
            elif self._obj.ScaleByRootChord:
                chord = self._obj.RootChord.Value
                if chord > 0 and self._obj.ScaleValue > 0:
                    scale =  chord / self._obj.ScaleValue.Value
            elif self._obj.ScaleByHeight:
                height = self._obj.Height.Value
                if height > 0 and self._obj.ScaleValue > 0:
                    scale =  height / self._obj.ScaleValue.Value
        return float(scale)

    def getFinThickness(self) -> float:
        thickness = 0.0
        if self.getTipThickness() > 0.0:
            thickness = min(self.getTipThickness(), self.getRootThickness())
        else:
            thickness = self.getRootThickness()
        return thickness

    def isAfter(self) -> bool:
        return False

    def setParentRadius(self) -> None:
        self.setParentDiameter()

    def setParentDiameter(self) -> None:
        if self._obj.AutoDiameter:
            self._obj.ParentRadius = SymmetricComponent.DEFAULT_RADIUS
            if self.hasParent():
                parent = self.getParent()
                if hasattr(parent, "getOuterDiameter"):
                    self._obj.ParentRadius = parent.getOuterDiameter(0) / 2.0

    def setAutoHeight(self, auto : bool) -> None:
        if self._obj.AutoHeight != auto:
            self._obj.AutoHeight = auto
            self.setFinAutoHeight()

    def setFinAutoHeight(self) -> None:
        if self._obj.AutoHeight and self._obj.ParentRadius > 0 and self._obj.Span > 0:
            height = ((self._obj.Span - 2.0 * self._obj.ParentRadius) / 2.0)
            if height > 0:
                self.setHeight(height)

    def _setTtwAutoHeight(self, pos : float) -> None:
        if self._obj.TtwAutoHeight:
            centerDiameter = 0
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

                    centerDiameter = max(centerDiameter, float(sibling.Proxy.getOuterDiameter(pos)))

                centerDiameter = min(centerDiameter, 2.0 * float(self._obj.ParentRadius))

                self._obj.TtwHeight = float(self._obj.ParentRadius) - (centerDiameter / 2.0)

    def getForeRadius(self) -> float:
        # For placing objects on the outer part of the parent
        return float(self._obj.ParentRadius + self._obj.Height) / self.getDiameterScale()

    def getLength(self) -> float:
        # Return the length of this component along the central axis
        if self._obj.FinType == FIN_TYPE_PROXY:
            if self._shapeHandler == None:
                self._setShapeHandler()
            return self._shapeHandler.getLength() / self.getScale()

        if self._obj.Length <= 0:
            self._obj.Length = self.getRootChord()
        return float(self._obj.Length) / self.getScale()

    def isFinSet(self) -> bool:
        return self._obj.FinSet

    def getFinCount(self) -> int:
        return int(self._obj.FinCount)

    def setFinCount(self, count : int) -> None:
        self._obj.FinCount = count
        self.notifyComponentChanged()

    def getRootChord(self) -> float:
        if self._obj.FinType == FIN_TYPE_SKETCH:
            if self._obj.RootChord <= 0 or self._obj.Length <= 0:
                handler = FinSketchShapeHandler(self._obj)
                shape = handler.getFace()
                if shape is None:
                    return 0
                xmin,xmax = handler.findRootChord(shape)
                self._obj.RootChord = float(xmax - xmin)
                self._obj.Length = self._obj.RootChord

        return float(self._obj.RootChord) / self.getScale()

    def setRootChord(self, chord : float) -> None:
        self._obj.RootChord = chord
        self.notifyComponentChanged()

    def getRootThickness(self) -> float:
        return float(self._obj.RootThickness) / self.getScale()

    def setRootThickness(self, thickness : float) -> None:
        self._obj.RootThickness = thickness
        self.notifyComponentChanged()

    def getTipChord(self) -> float:
        return float(self._obj.TipChord) / self.getScale()

    def setTipChord(self, chord : float) -> None:
        self._obj.TipChord = chord
        self.notifyComponentChanged()

    def getTipThickness(self) -> float:
        return float(self._obj.TipThickness) / self.getScale()

    def setTipThickness(self, thickness : float) -> None:
        self._obj.TipThickness = thickness
        self.notifyComponentChanged()

    def getThickness(self) -> float:
        return float(self._obj.RootThickness) / self.getScale()

    def setThickness(self, thickness : float) -> None:
        self._obj.RootThickness = thickness
        self._obj.TipThickness = thickness
        self.notifyComponentChanged()

    def getHeight(self) -> float:
        return float(self._obj.Height) / self.getScale()

    def setHeight(self, height : float) -> None:
        self._obj.Height = height
        self.sweepAngleFromLength()
        self.notifyComponentChanged()

    def getSpan(self) -> float:
        return float(self._obj.Span) / self.getScale()

    def setSpan(self, span : float) -> None:
        self._obj.Span = span
        self.setFinAutoHeight()
        self.sweepAngleFromLength()
        self.notifyComponentChanged()

    def getSweepLength(self) -> float:
        return float(self._obj.SweepLength) / self.getScale()

    def setSweepLength(self, length : float) -> None:
        self._obj.SweepLength = length
        self.sweepAngleFromLength()
        self.notifyComponentChanged()

    def sweepAngleFromLength(self) -> None:
        length = float(self._obj.SweepLength)
        theta = 90.0 - math.degrees(math.atan2(float(self._obj.Height), length))
        self._obj.SweepAngle = theta

    def getSweepAngle(self) -> float:
        return float(self._obj.SweepAngle)

    def setSweepAngle(self, angle : float) -> None:
        self._obj.SweepAngle = angle
        self.sweepLengthFromAngle()
        self.notifyComponentChanged()

    def sweepLengthFromAngle(self) -> None:
        theta = _toFloat(self._obj.SweepAngle)
        if theta <= -90.0 or theta >= 90.0:
            _err("Sweep angle must be greater than -90 and less than +90")
            return
        theta = math.radians(-1.0 * (theta + 90.0))
        length = _toFloat(self._obj.Height) / math.tan(theta)
        self._obj.SweepLength = length

    def _setShapeHandler(self) -> None:
        obj = self._obj
        self._shapeHandler = None
        if obj.FinType == FIN_TYPE_TRAPEZOID:
            if self.getTipChord() > 0.0:
                self._shapeHandler = FinTrapezoidShapeHandler(obj)
            else:
                self._shapeHandler = FinTriangleShapeHandler(obj)
        elif obj.FinType == FIN_TYPE_TRIANGLE:
                self._shapeHandler = FinTriangleShapeHandler(obj)
        elif obj.FinType == FIN_TYPE_ELLIPSE:
            self._shapeHandler = FinEllipseShapeHandler(obj)
        elif obj.FinType == FIN_TYPE_TUBE:
            self._shapeHandler = FinTubeShapeHandler(obj)
        elif obj.FinType == FIN_TYPE_SKETCH:
            self._shapeHandler = FinSketchShapeHandler(obj)
        elif obj.FinType == FIN_TYPE_PROXY:
            self._shapeHandler = FinProxyShapeHandler(obj)

    def execute(self, obj : Any) -> None:
        self._setShapeHandler()

        if self._shapeHandler:
            self._shapeHandler.draw()

    def eligibleChild(self, childType : str) -> bool:
        return childType in [
            FEATURE_POD,
            FEATURE_LAUNCH_LUG,
            FEATURE_RAIL_BUTTON,
            FEATURE_RINGTAIL
            # FEATURE_RAIL_GUIDE - this doesn't make sense on a fin
            ]

    """ Returns the geometry of a trapezoidal fin. """
    def getFinPoints(self) -> list[Coordinate]:
        list = []

        list.append(NUL)
        list.append(Coordinate(self._obj.SweepLength, self._obj.Height))
        if self._obj.TipChord > 0.0001:
            list.append(Coordinate(self._obj.SweepLength + self._obj.TipChord, self._obj.Height));
        list.append(Coordinate(max(self._obj.RootChord, 0.0001), 0));

        return list

    def isTubeOuterRadiusAutomatic(self) -> bool:
        return self._obj.TubeAutoOuterDiameter

    """
        Return the outer radius of the tube-fin
    """
    def getTubeOuterRadius(self) -> float:
        return self.getTubeOuterDiameter() / 2.0

    def getTubeOuterDiameter(self) -> float:
        if self._obj.TubeAutoOuterDiameter:
            if self._obj.FinCount < 3:
                self._obj.TubeOuterDiameter = 2.0 * float(self._obj.ParentRadius)
            else:
                self._obj.TubeOuterDiameter = 2.0 * self.getTouchingRadius()

        return float(self._obj.TubeOuterDiameter)

    """
         Return distance between tubes.
    """
    def getTubeSeparation(self) -> float:
        return 2.0 * (self.getTouchingRadius() - self.getTubeOuterRadius())

    """
        Return the required radius for the fins to be touching
    """
    def getTouchingRadius(self) -> float:
        r = self._obj.ParentRadius
        finSep = math.pi / self._obj.FinCount

        r *= math.sin(finSep)/(1.0 - math.sin(finSep))

        return float(r)

    """
        Set the outer radius of the tube-fin.  If the radius is less than the wall thickness,
        the wall thickness is decreased accordingly of the value of the radius.
        This method sets the automatic radius off.
    """
    def setTubeOuterRadius(self, radius : float) -> None:
        self.setTubeOuterDiameter(2.0 * radius)

    def setTubeOuterDiameter(self, radius : float) -> None:
        if self._obj.TubeOuterDiameter == radius and not self._obj.TubeAutoOuterDiameter:
            return

        self._obj.TubeAutoOuterDiameter = False
        self._obj.TubeOuterDiameter = max(radius, 0)

        if self._obj.TubeThickness > (self._obj.TubeOuterDiameter / 2.0):
            self._obj.TubeThickness = (self._obj.TubeOuterDiameter / 2.0)
        self.notifyComponentChanged()
        self.clearPreset()

    """
        Sets whether the radius is selected automatically or not.
    """
    def setTubeOuterRadiusAutomatic(self, auto : bool) -> None:
        self.setTubeOuterDiameterAutomatic(auto)

    def setTubeOuterDiameterAutomatic(self, auto : bool) -> None:
        if self._obj.TubeAutoOuterDiameter == auto:
            return

        self._obj.TubeAutoOuterDiameter = auto
        self.notifyComponentChanged()
        self.clearPreset()

    def setPartScale(self, scale : float) -> None:
        if self._obj.ScaleOverride:
            scale = self._obj.Proxy.getScale()

        self._obj.Scale = False

        self._obj.Length /= scale

        self._obj.RootChord /= scale
        self._obj.RootThickness /= scale
        self._obj.RootLength1 /= scale
        self._obj.RootLength2 /= scale

        self._obj.TipChord /= scale
        self._obj.TipThickness /= scale
        self._obj.TipLength1 /= scale
        self._obj.TipLength2 /= scale

        self._obj.TubeOuterDiameter /= scale
        self._obj.TubeThickness /= scale

        self._obj.Height /= scale
        self._obj.Span /= scale
        self._obj.SweepLength /= scale

        self._obj.TtwOffset /= scale
        self._obj.TtwLength /= scale
        self._obj.TtwHeight /= scale
        self._obj.TtwThickness /= scale

        self._obj.FilletRadius /= scale
        self.setEdited()
