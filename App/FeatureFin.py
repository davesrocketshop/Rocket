# ***************************************************************************
# *   Copyright (c) 2021-2023 David Carter <dcarter@davidcarter.ca>         *
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

import FreeCAD
import math

from App.events.ComponentChangeEvent import ComponentChangeEvent

from App.position.AxialMethod import BOTTOM
from App.ExternalComponent import ExternalComponent
from App.SymmetricComponent import SymmetricComponent
from App.FeatureInnerTube import FeatureInnerTube
from App.util.Coordinate import Coordinate, NUL

from App.Constants import FEATURE_FIN, FEATURE_LAUNCH_LUG, FEATURE_RAIL_BUTTON, FEATURE_POD
from App.Constants import FIN_TYPE_TRAPEZOID, FIN_TYPE_TRIANGLE, FIN_TYPE_ELLIPSE, FIN_TYPE_TUBE, FIN_TYPE_SKETCH
from App.Constants import FIN_CROSS_SAME, FIN_CROSS_SQUARE, FIN_CROSS_ROUND, FIN_CROSS_AIRFOIL, FIN_CROSS_WEDGE, \
    FIN_CROSS_DIAMOND, FIN_CROSS_TAPER_LE, FIN_CROSS_TAPER_TE, FIN_CROSS_TAPER_LETE, FIN_CROSS_ELLIPSE, FIN_CROSS_BICONVEX
from App.Constants import FIN_DEBUG_FULL, FIN_DEBUG_PROFILE_ONLY, FIN_DEBUG_MASK_ONLY
from App.Constants import PROP_TRANSIENT, PROP_HIDDEN

from App.ShapeHandlers.FinTrapezoidShapeHandler import FinTrapezoidShapeHandler
from App.ShapeHandlers.FinTriangleShapeHandler import FinTriangleShapeHandler
from App.ShapeHandlers.FinEllipseShapeHandler import FinEllipseShapeHandler
from App.ShapeHandlers.FinSketchShapeHandler import FinSketchShapeHandler
from App.ShapeHandlers.FinTubeShapeHandler import FinTubeShapeHandler

from App.Utilities import _err, _toFloat

from DraftTools import translate

DEBUG_SKETCH_FINS = 0 # Set > 0 when debugging sketch based fins

class FeatureFin(ExternalComponent):

    def __init__(self, obj):
        super().__init__(obj, BOTTOM)
        self.Type = FEATURE_FIN

        if not hasattr(obj,"FinType"):
            obj.addProperty('App::PropertyEnumeration', 'FinType', 'RocketComponent', translate('App::Property', 'Fin type'))
            obj.FinType = [FIN_TYPE_TRAPEZOID,
                    FIN_TYPE_TRIANGLE, 
                    FIN_TYPE_ELLIPSE, 
                    FIN_TYPE_TUBE, 
                    FIN_TYPE_SKETCH
                    ]
            obj.FinType = FIN_TYPE_TRAPEZOID
        else:
            obj.FinType = [FIN_TYPE_TRAPEZOID, 
                    FIN_TYPE_TRIANGLE, 
                    FIN_TYPE_ELLIPSE, 
                    FIN_TYPE_TUBE, 
                    FIN_TYPE_SKETCH
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

        # Hidden properties used for calculation
        if not hasattr(obj,"ParentRadius"):
            obj.addProperty('App::PropertyLength', 'ParentRadius', 'RocketComponent', 'Parent radius', PROP_TRANSIENT | PROP_HIDDEN).ParentRadius = 20.0 # No translation required for a hidden parameter
        if not hasattr(obj,"AutoDiameter"):
            obj.addProperty('App::PropertyBool', 'AutoDiameter', 'RocketComponent', translate('App::Property', 'Automatically set diameter')).AutoDiameter = True
        obj.setEditorMode('AutoDiameter', PROP_HIDDEN)  # hide

        if not hasattr(obj, "Profile"):
            obj.addProperty('App::PropertyLink', 'Profile', 'RocketComponent', translate('App::Property', 'Custom fin sketch')).Profile = None

        if not hasattr(obj,"Group"):
            obj.addExtension("App::GroupExtensionPython")

        # A transient property for debugging sketch based fins
        if DEBUG_SKETCH_FINS > 0:
            if not hasattr(obj,"DebugSketch"):
                obj.addProperty('App::PropertyEnumeration', 'DebugSketch', 'RocketComponent', translate('App::Property', 'Sketch based fin debugging options'), PROP_TRANSIENT)
                obj.DebugSketch = [FIN_DEBUG_FULL, FIN_DEBUG_PROFILE_ONLY, FIN_DEBUG_MASK_ONLY]
                obj.DebugSketch = FIN_DEBUG_FULL

        self._setFinEditorVisibility()

    def setDefaults(self):
        super().setDefaults()

    def _setFinEditorVisibility(self):
        # self._obj.setEditorMode('FinSet', EDITOR_HIDDEN)  # hide
        # self._obj.setEditorMode('FinCount', EDITOR_HIDDEN)  # show
        # self._obj.setEditorMode('FinSpacing', EDITOR_HIDDEN)  # show
        pass

    def onDocumentRestored(self, obj):
        if obj is not None:
            FeatureFin(obj) # Update any properties

            self._obj = obj
            
        self._setFinEditorVisibility()

    def update(self):
        super().update()

        # Ensure any automatic variables are set
        self.setParentDiameter()
        self.getTubeOuterDiameter()
        self._setTtwAutoHeight()

    def isAfter(self):
        return False

    def setParentRadius(self):
        self.setParentDiameter()

    def setParentDiameter(self):
        if self._obj.AutoDiameter:
            parent = self.getParent()
            if parent is not None and hasattr(parent, "getOuterDiameter"):
                self._obj.ParentRadius = parent.getOuterDiameter() / 2.0
            else:
                self._obj.ParentRadius = SymmetricComponent.DEFAULT_RADIUS
        
    def _setTtwAutoHeight(self, pos=0):
        if self._obj.TtwAutoHeight:
            centerDiameter = 0
            # Component can be parentless if detached from rocket
            if self.getParent() is not None:
                for sibling in self.getParent().getChildren():
                    # Only InnerTubes are considered when determining the automatic
                    # inner radius (for now).
                    if not isinstance(sibling.Proxy, FeatureInnerTube): # Excludes itself
                        continue

                    pos1 = self.toRelative(NUL, sibling.Proxy)[0]._x
                    pos2 = self.toRelative(Coordinate(self.getLength()), sibling.Proxy)[0]._x
                    if pos2 < 0 or pos1 > sibling.Proxy.getLength():
                        continue

                    centerDiameter = max(centerDiameter, float(sibling.Proxy.getOuterDiameter()))

                centerDiameter = min(centerDiameter, 2.0 * float(self._obj.ParentRadius))

                self._obj.TtwHeight = float(self._obj.ParentRadius) - (centerDiameter / 2.0)

    def getForeRadius(self):
        # For placing objects on the outer part of the parent
        return float(self._obj.ParentRadius + self._obj.Height)

    def getLength(self):
        # Return the length of this component along the central axis
        if self._obj.Length <= 0:
            self._obj.Length = self.getRootChord()
        return self._obj.Length

    def isFinSet(self):
        return self._obj.FinSet

    def getFinCount(self):
        return int(self._obj.FinCount)

    def setFinCount(self, count):
        self._obj.FinCount = count

    def getRootChord(self):
        if self._obj.FinType == FIN_TYPE_SKETCH:
            if self._obj.RootChord <= 0 or self._obj.Length <= 0:
                handler = FinSketchShapeHandler(self._obj)
                shape = handler.getFace()
                if shape is None:
                    return 0
                xmin,xmax = handler.findRootChord(shape)
                self._obj.RootChord = float(xmax - xmin)
                self._obj.Length = self._obj.RootChord

        return self._obj.RootChord

    def setRootChord(self, chord):
        self._obj.RootChord = chord

    def getRootThickness(self):
        return self._obj.RootThickness

    def setRootThickness(self, thickness):
        self._obj.RootThickness = thickness

    def getTipChord(self):
        return self._obj.TipChord

    def setTipChord(self, chord):
        self._obj.TipChord = chord

    def getTipThickness(self):
        return self._obj.TipThickness

    def setTipThickness(self, thickness):
        self._obj.TipThickness = thickness

    def getThickness(self):
        return self._obj.RootThickness

    def setThickness(self, thickness):
        self._obj.RootThickness = thickness
        self._obj.TipThickness = thickness

    def getHeight(self):
        return self._obj.Height

    def setHeight(self, height):
        self._obj.Height = height

    def getSweepLength(self):
        return self._obj.SweepLength

    def setSweepLength(self, length):
        self._obj.SweepLength = length
        self.sweepAngleFromLength()

    def sweepAngleFromLength(self):
        length = float(self._obj.SweepLength)
        theta = 90.0 - math.degrees(math.atan2(float(self._obj.Height), length))
        self._obj.SweepAngle = theta

    def getSweepAngle(self):
        return self._obj.SweepAngle

    def setSweepAngle(self, angle):
        self._obj.SweepAngle = angle
        self.sweepLengthFromAngle()

    def sweepLengthFromAngle(self):
        theta = _toFloat(self._obj.SweepAngle)
        if theta <= -90.0 or theta >= 90.0:
            _err("Sweep angle must be greater than -90 and less than +90")
            return
        theta = math.radians(-1.0 * (theta + 90.0))
        length = _toFloat(self._obj.Height) / math.tan(theta)
        self._obj.SweepLength = length

    def execute(self, obj):
        if obj.FinType == FIN_TYPE_TRAPEZOID:
            if self.getTipChord() > 0.0:
                shape = FinTrapezoidShapeHandler(obj)
            else:
                shape = FinTriangleShapeHandler(obj)
        elif obj.FinType == FIN_TYPE_TRIANGLE:
                shape = FinTriangleShapeHandler(obj)
        elif obj.FinType == FIN_TYPE_ELLIPSE:
            shape = FinEllipseShapeHandler(obj)
        elif obj.FinType == FIN_TYPE_TUBE:
            shape = FinTubeShapeHandler(obj)
        elif obj.FinType == FIN_TYPE_SKETCH:
            shape = FinSketchShapeHandler(obj)

        if shape is not None:
            shape.draw()

    def eligibleChild(self, childType):
        return childType in [
            FEATURE_POD, 
            FEATURE_LAUNCH_LUG, 
            FEATURE_RAIL_BUTTON
            # FEATURE_RAIL_GUIDE - this doesn't make sense on a fin
            ]

    """ Returns the geometry of a trapezoidal fin. """
    def getFinPoints(self):
        list = []
        
        list.append(Coordinate.NUL)
        list.append(Coordinate(self._obj.SweepLength, self._obj.Height))
        if self._obj.TipChord > 0.0001:
            list.append(Coordinate(self._obj.SweepLength + self._obj.TipChord, self._obj.Height));
        list.append(Coordinate(math.max(self._obj.RootChord, 0.0001), 0));
        
        return list

    def isTubeOuterRadiusAutomatic(self):
        return self._obj.TubeAutoOuterDiameter

    """
        Return the outer radius of the tube-fin
    """
    def getTubeOuterRadius(self):
        return (float(self.getTubeOuterDiameter()) / 2.0)

    def getTubeOuterDiameter(self):
        if self._obj.TubeAutoOuterDiameter:
            if self._obj.FinCount < 3:
                self._obj.TubeOuterDiameter = 2.0 * float(self._obj.ParentRadius)
            else:
                self._obj.TubeOuterDiameter = 2.0 * self.getTouchingRadius()

        return float(self._obj.TubeOuterDiameter)

    """
         Return distance between tubes.
    """
    def getTubeSeparation(self):
        return 2.0 * (self.getTouchingRadius() - self.getTubeOuterRadius())

    """
        Return the required radius for the fins to be touching
    """
    def getTouchingRadius(self):
        r = self._obj.ParentRadius
        finSep = math.pi / self._obj.FinCount
        
        r *= math.sin(finSep)/(1.0 - math.sin(finSep))
        
        return r

    """
        Set the outer radius of the tube-fin.  If the radius is less than the wall thickness,
        the wall thickness is decreased accordingly of the value of the radius.
        This method sets the automatic radius off.
    """
    def setTubeOuterRadius(self, radius):
        self.setTubeOuterDiameter(2.0 * radius)

    def setTubeOuterDiameter(self, radius):
        for listener in self._configListeners:
            if isinstance(listener, FeatureFin):
                listener.setTubeOuterDiameter(radius)

        if self._obj.TubeOuterDiameter == radius and not self._obj.TubeAutoOuterDiameter:
            return
        
        self._obj.TubeAutoOuterDiameter = False
        self._obj.TubeOuterDiameter = max(radius, 0)
        
        if self._obj.TubeThickness > (self._obj.TubeOuterDiameter / 2.0):
            self._obj.TubeThickness = (self._obj.TubeOuterDiameter / 2.0)
        self.fireComponentChangeEvent(ComponentChangeEvent.BOTH_CHANGE)
        self.clearPreset()

    """
        Sets whether the radius is selected automatically or not.
    """
    def setTubeOuterRadiusAutomatic(self, auto):
        self.setTubeOuterDiameterAutomatic(auto)

    def setTubeOuterDiameterAutomatic(self, auto):
        for listener in self._configListeners:
            if isinstance(listener, FeatureFin):
                listener.setTubeOuterDiameterAutomatic(auto)

        if self._obj.TubeAutoOuterDiameter == auto:
            return
        
        self._obj.TubeAutoOuterDiameter = auto
        self.fireComponentChangeEvent(ComponentChangeEvent.BOTH_CHANGE)
        self.clearPreset()
