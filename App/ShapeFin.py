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
import FreeCADGui
import Part

from App.ShapeComponent import ShapeLocation

from App.Constants import FIN_TYPE_TRAPEZOID, FIN_TYPE_ELLIPSE, FIN_TYPE_TUBE, FIN_TYPE_SKETCH
from App.Constants import FIN_CROSS_SQUARE, FIN_CROSS_ROUND, FIN_CROSS_AIRFOIL, FIN_CROSS_WEDGE, \
    FIN_CROSS_DIAMOND, FIN_CROSS_TAPER_LE, FIN_CROSS_TAPER_TE, FIN_CROSS_TAPER_LETE

from App.FinTrapezoidShapeHandler import FinTrapezoidShapeHandler

def QT_TRANSLATE_NOOP(scope, text):
    return text

class ShapeFin(ShapeLocation):

    def __init__(self, obj):
        super().__init__(obj)

        if not hasattr(obj,"FinType"):
            obj.addProperty('App::PropertyEnumeration', 'FinType', 'Fin', QT_TRANSLATE_NOOP('App::Property', 'Fin type'))
        obj.FinType = [FIN_TYPE_TRAPEZOID, 
                # FIN_TYPE_ELLIPSE, 
                # FIN_TYPE_TUBE, 
                # FIN_TYPE_SKETCH
                ]
        obj.FinType = FIN_TYPE_TRAPEZOID

        if not hasattr(obj,"RootCrossSection"):
            obj.addProperty('App::PropertyEnumeration', 'RootCrossSection', 'Fin', QT_TRANSLATE_NOOP('App::Property', 'Fin root cross section'))
        obj.RootCrossSection = [FIN_CROSS_SQUARE, FIN_CROSS_ROUND, FIN_CROSS_AIRFOIL, FIN_CROSS_WEDGE, 
            FIN_CROSS_DIAMOND, FIN_CROSS_TAPER_LE, FIN_CROSS_TAPER_TE, FIN_CROSS_TAPER_LETE]
        obj.RootCrossSection = FIN_CROSS_SQUARE

        if not hasattr(obj,"RootChord"):
            obj.addProperty('App::PropertyLength', 'RootChord', 'Fin', QT_TRANSLATE_NOOP('App::Property', 'Length of the base of the fin')).RootChord = 10.0
        if not hasattr(obj,"RootThickness"):
            obj.addProperty('App::PropertyLength', 'RootThickness', 'Fin', QT_TRANSLATE_NOOP('App::Property', 'Fin root thickness')).RootThickness = 2.0
        if not hasattr(obj,"RootPerCent"):
            obj.addProperty('App::PropertyBool', 'RootPerCent', 'Fin', QT_TRANSLATE_NOOP('App::Property', 'Root chord lengths are percentages')).RootPerCent = True
        if not hasattr(obj,"RootLength1"):
            obj.addProperty('App::PropertyLength', 'RootLength1', 'Fin', QT_TRANSLATE_NOOP('App::Property', 'Root chord length 1')).RootLength1 = 20.0
        if not hasattr(obj,"RootLength2"):
            obj.addProperty('App::PropertyLength', 'RootLength2', 'Fin', QT_TRANSLATE_NOOP('App::Property', 'Root chord length 2')).RootLength2 = 80.0

        if not hasattr(obj,"TipCrossSection"):
            obj.addProperty('App::PropertyEnumeration', 'TipCrossSection', 'Fin', QT_TRANSLATE_NOOP('App::Property', 'Fin tip cross section'))
        obj.TipCrossSection = [FIN_CROSS_SQUARE, FIN_CROSS_ROUND, FIN_CROSS_AIRFOIL, FIN_CROSS_WEDGE, 
            FIN_CROSS_DIAMOND, FIN_CROSS_TAPER_LE, FIN_CROSS_TAPER_TE, FIN_CROSS_TAPER_LETE]
        obj.TipCrossSection = FIN_CROSS_SQUARE

        if not hasattr(obj,"TipChord"):
            obj.addProperty('App::PropertyLength', 'TipChord', 'Fin', QT_TRANSLATE_NOOP('App::Property', 'Length of the tip of the fin')).TipChord = 5.0
        if not hasattr(obj,"TipThickness"):
            obj.addProperty('App::PropertyLength', 'TipThickness', 'Fin', QT_TRANSLATE_NOOP('App::Property', 'Fin tip thickness')).TipThickness = 2.0
        if not hasattr(obj,"TipPerCent"):
            obj.addProperty('App::PropertyBool', 'TipPerCent', 'Fin', QT_TRANSLATE_NOOP('App::Property', 'Tip chord lengths are percentages')).TipPerCent = True
        if not hasattr(obj,"TipThickness"):
            obj.addProperty('App::PropertyLength', 'TipThickness', 'Fin', QT_TRANSLATE_NOOP('App::Property', 'Fin tip thickness')).TipThickness = 2.0
        if not hasattr(obj,"TipLength1"):
            obj.addProperty('App::PropertyLength', 'TipLength1', 'Fin', QT_TRANSLATE_NOOP('App::Property', 'Tip chord length 1')).TipLength1 = 20.0
        if not hasattr(obj,"TipLength2"):
            obj.addProperty('App::PropertyLength', 'TipLength2', 'Fin', QT_TRANSLATE_NOOP('App::Property', 'Tip chord length 2')).TipLength2 = 80.0

        if not hasattr(obj,"Height"):
            obj.addProperty('App::PropertyLength', 'Height', 'Fin', QT_TRANSLATE_NOOP('App::Property', 'Fin semi-span')).Height = 10.0
        if not hasattr(obj,"SweepLength"):
            obj.addProperty('App::PropertyDistance', 'SweepLength', 'Fin', QT_TRANSLATE_NOOP('App::Property', 'Sweep length')).SweepLength = 3.0 # Must be distance since it can be negative
        if not hasattr(obj,"SweepAngle"):
            obj.addProperty('App::PropertyAngle', 'SweepAngle', 'Fin', QT_TRANSLATE_NOOP('App::Property', 'Sweep angle')).SweepAngle = 0.0

        if not hasattr(obj,"Ttw"):
            obj.addProperty('App::PropertyBool', 'Ttw', 'Fin', QT_TRANSLATE_NOOP('App::Property', 'Through the wall (TTW) tab')).Ttw = False
        if not hasattr(obj,"TtwOffset"):
            obj.addProperty('App::PropertyLength', 'TtwOffset', 'Fin', QT_TRANSLATE_NOOP('App::Property', 'TTW Offset from fin root')).TtwOffset = 2.0
        if not hasattr(obj,"TtwLength"):
            obj.addProperty('App::PropertyLength', 'TtwLength', 'Fin', QT_TRANSLATE_NOOP('App::Property', 'TTW Length')).TtwLength = 6.0
        if not hasattr(obj,"TtwHeight"):
            obj.addProperty('App::PropertyLength', 'TtwHeight', 'Fin', QT_TRANSLATE_NOOP('App::Property', 'TTW Height')).TtwHeight = 10.0
        if not hasattr(obj,"TtwThickness"):
            obj.addProperty('App::PropertyLength', 'TtwThickness', 'Fin', QT_TRANSLATE_NOOP('App::Property', 'TTW thickness')).TtwThickness = 1.0

        if not hasattr(obj,"FinSet"):
            obj.addProperty('App::PropertyBool', 'FinSet', 'Fin', QT_TRANSLATE_NOOP('App::Property', 'True when describing a set of fins')).FinSet = False
        if not hasattr(obj,"FinCount"):
            obj.addProperty('App::PropertyInteger', 'FinCount', 'Fin', QT_TRANSLATE_NOOP('App::Property', 'Number of fins in a radial pattern')).FinCount = 3
        if not hasattr(obj,"FinSpacing"):
            obj.addProperty('App::PropertyAngle', 'FinSpacing', 'Fin', QT_TRANSLATE_NOOP('App::Property', 'Angle between consecutive fins')).FinSpacing = 120

        obj.addProperty('Part::PropertyPartShape', 'Shape', 'Fin', QT_TRANSLATE_NOOP('App::Property', 'Shape of the fin'))

    def execute(self, obj):

        if obj.FinType == FIN_TYPE_TRAPEZOID:
            shape = FinTrapezoidShapeHandler(obj)

        if shape is not None:
            shape.draw()
