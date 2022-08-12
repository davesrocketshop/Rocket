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
"""Class for drawing fins"""

__title__ = "FreeCAD Fins"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"
    
import FreeCAD

from App.ShapeComponent import ShapeLocation
from App.Constants import FEATURE_FIN, FEATURE_LAUNCH_LUG, FEATURE_RAIL_BUTTON, FEATURE_RAIL_GUIDE, FEATURE_POD

from App.Constants import FIN_TYPE_TRAPEZOID, FIN_TYPE_ELLIPSE, FIN_TYPE_SKETCH
from App.Constants import FIN_CROSS_SAME, FIN_CROSS_SQUARE, FIN_CROSS_ROUND, FIN_CROSS_AIRFOIL, FIN_CROSS_WEDGE, \
    FIN_CROSS_DIAMOND, FIN_CROSS_TAPER_LE, FIN_CROSS_TAPER_TE, FIN_CROSS_TAPER_LETE
from App.Constants import FIN_DEBUG_FULL, FIN_DEBUG_PROFILE_ONLY, FIN_DEBUG_MASK_ONLY
from App.Constants import LOCATION_PARENT_TOP, LOCATION_PARENT_MIDDLE, LOCATION_PARENT_BOTTOM, LOCATION_BASE
from App.Constants import PROP_TRANSIENT, PROP_HIDDEN

from App.FinTrapezoidShapeHandler import FinTrapezoidShapeHandler
from App.FinEllipseShapeHandler import FinEllipseShapeHandler
from App.FinSketchShapeHandler import FinSketchShapeHandler

from DraftTools import translate

cDEBUG_SKETCH_FINS = 0 # Set > 0 when debugging sketch based fins

class ShapeFin(ShapeLocation):

    def __init__(self, obj):
        super().__init__(obj)
        self.Type = FEATURE_FIN

        if not hasattr(obj,"FinType"):
            obj.addProperty('App::PropertyEnumeration', 'FinType', 'Fin', translate('App::Property', 'Fin type'))
        obj.FinType = [FIN_TYPE_TRAPEZOID, 
                FIN_TYPE_ELLIPSE, 
                # FIN_TYPE_TUBE, 
                FIN_TYPE_SKETCH
                ]
        obj.FinType = FIN_TYPE_TRAPEZOID

        if not hasattr(obj,"RootCrossSection"):
            obj.addProperty('App::PropertyEnumeration', 'RootCrossSection', 'Fin', translate('App::Property', 'Fin root cross section'))
        obj.RootCrossSection = [FIN_CROSS_SQUARE, FIN_CROSS_ROUND, FIN_CROSS_AIRFOIL, FIN_CROSS_WEDGE, 
            FIN_CROSS_DIAMOND, FIN_CROSS_TAPER_LE, FIN_CROSS_TAPER_TE, FIN_CROSS_TAPER_LETE]
        obj.RootCrossSection = FIN_CROSS_SQUARE

        if not hasattr(obj,"RootChord"):
            obj.addProperty('App::PropertyLength', 'RootChord', 'Fin', translate('App::Property', 'Length of the base of the fin')).RootChord = 57.15
        if not hasattr(obj,"RootThickness"):
            obj.addProperty('App::PropertyLength', 'RootThickness', 'Fin', translate('App::Property', 'Fin root thickness')).RootThickness = 1.4
        if not hasattr(obj,"RootPerCent"):
            obj.addProperty('App::PropertyBool', 'RootPerCent', 'Fin', translate('App::Property', 'Root chord lengths are percentages')).RootPerCent = True
        if not hasattr(obj,"RootLength1"):
            obj.addProperty('App::PropertyLength', 'RootLength1', 'Fin', translate('App::Property', 'Root chord length 1')).RootLength1 = 20.0
        if not hasattr(obj,"RootLength2"):
            obj.addProperty('App::PropertyLength', 'RootLength2', 'Fin', translate('App::Property', 'Root chord length 2')).RootLength2 = 80.0

        if not hasattr(obj,"TipCrossSection"):
            obj.addProperty('App::PropertyEnumeration', 'TipCrossSection', 'Fin', translate('App::Property', 'Fin tip cross section'))
        obj.TipCrossSection = [FIN_CROSS_SAME, FIN_CROSS_SQUARE, FIN_CROSS_ROUND, FIN_CROSS_AIRFOIL, FIN_CROSS_WEDGE, 
            FIN_CROSS_DIAMOND, FIN_CROSS_TAPER_LE, FIN_CROSS_TAPER_TE, FIN_CROSS_TAPER_LETE]
        obj.TipCrossSection = FIN_CROSS_SAME

        if not hasattr(obj,"TipChord"):
            obj.addProperty('App::PropertyLength', 'TipChord', 'Fin', translate('App::Property', 'Length of the tip of the fin')).TipChord = 30.48
        if not hasattr(obj,"TipThickness"):
            obj.addProperty('App::PropertyLength', 'TipThickness', 'Fin', translate('App::Property', 'Fin tip thickness')).TipThickness = 1.4
        if not hasattr(obj,"TipPerCent"):
            obj.addProperty('App::PropertyBool', 'TipPerCent', 'Fin', translate('App::Property', 'Tip chord lengths are percentages')).TipPerCent = True
        if not hasattr(obj,"TipThickness"):
            obj.addProperty('App::PropertyLength', 'TipThickness', 'Fin', translate('App::Property', 'Fin tip thickness')).TipThickness = 2.0
        if not hasattr(obj,"TipLength1"):
            obj.addProperty('App::PropertyLength', 'TipLength1', 'Fin', translate('App::Property', 'Tip chord length 1')).TipLength1 = 20.0
        if not hasattr(obj,"TipLength2"):
            obj.addProperty('App::PropertyLength', 'TipLength2', 'Fin', translate('App::Property', 'Tip chord length 2')).TipLength2 = 80.0

        if not hasattr(obj,"Height"):
            obj.addProperty('App::PropertyLength', 'Height', 'Fin', translate('App::Property', 'Fin semi-span')).Height = 40.64
        if not hasattr(obj,"SweepLength"):
            obj.addProperty('App::PropertyDistance', 'SweepLength', 'Fin', translate('App::Property', 'Sweep length')).SweepLength = 69.86 # Must be distance since it can be negative
        if not hasattr(obj,"SweepAngle"):
            obj.addProperty('App::PropertyAngle', 'SweepAngle', 'Fin', translate('App::Property', 'Sweep angle')).SweepAngle = 0.0

        if not hasattr(obj,"Ttw"):
            obj.addProperty('App::PropertyBool', 'Ttw', 'Fin', translate('App::Property', 'Through the wall (TTW) tab')).Ttw = False
        if not hasattr(obj,"TtwOffset"):
            obj.addProperty('App::PropertyLength', 'TtwOffset', 'Fin', translate('App::Property', 'TTW Offset from fin root')).TtwOffset = 2.0
        if not hasattr(obj,"TtwLength"):
            obj.addProperty('App::PropertyLength', 'TtwLength', 'Fin', translate('App::Property', 'TTW Length')).TtwLength = 6.0
        if not hasattr(obj,"TtwHeight"):
            obj.addProperty('App::PropertyLength', 'TtwHeight', 'Fin', translate('App::Property', 'TTW Height')).TtwHeight = 10.0
        if not hasattr(obj,"TtwThickness"):
            obj.addProperty('App::PropertyLength', 'TtwThickness', 'Fin', translate('App::Property', 'TTW thickness')).TtwThickness = 1.0

        if not hasattr(obj,"FinSet"):
            obj.addProperty('App::PropertyBool', 'FinSet', 'Fin', translate('App::Property', 'True when describing a set of fins')).FinSet = True
        if not hasattr(obj,"FinCount"):
            obj.addProperty('App::PropertyInteger', 'FinCount', 'Fin', translate('App::Property', 'Number of fins in a radial pattern')).FinCount = 3
        if not hasattr(obj,"FinSpacing"):
            obj.addProperty('App::PropertyAngle', 'FinSpacing', 'Fin', translate('App::Property', 'Angle between consecutive fins')).FinSpacing = 120

        # Hidden properties used for calculation
        if not hasattr(obj,"ParentRadius"):
            obj.addProperty('App::PropertyLength', 'ParentRadius', 'Fin', translate('App::Property', 'Parent radius')).ParentRadius = 20.0
        obj.setEditorMode('ParentRadius', PROP_TRANSIENT | PROP_HIDDEN)  # hide

        if not hasattr(obj, "Profile"):
            obj.addProperty('App::PropertyLink', 'Profile', 'Fin', translate('App::Property', 'Custom fin sketch')).Profile = None

        if not hasattr(obj,"Group"):
            obj.addExtension("App::GroupExtensionPython")

        if not hasattr(obj,"Shape"):
            obj.addProperty('Part::PropertyPartShape', 'Shape', 'Fin', translate('App::Property', 'Shape of the fin'))

    def execute(self, obj):

        if obj.FinType == FIN_TYPE_TRAPEZOID:
            shape = FinTrapezoidShapeHandler(obj)
        elif obj.FinType == FIN_TYPE_ELLIPSE:
            shape = FinEllipseShapeHandler(obj)
        elif obj.FinType == FIN_TYPE_SKETCH:
            shape = FinSketchShapeHandler(obj)

        if shape is not None:
            shape.draw()

    def eligibleChild(self, childType):
        return childType in [
            FEATURE_POD, 
            FEATURE_LAUNCH_LUG, 
            FEATURE_RAIL_BUTTON, 
            FEATURE_RAIL_GUIDE]
