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
    
from App.ShapeComponent import ShapeComponent

from App.Constants import FIN_TYPE_TRAPEZOID
from App.Constants import FIN_CROSS_SQUARE, FIN_CROSS_ROUND, FIN_CROSS_AIRFOIL, FIN_CROSS_WEDGE, \
    FIN_CROSS_DIAMOND, FIN_CROSS_TAPER_LE, FIN_CROSS_TAPER_TE, FIN_CROSS_TAPER_LETE

from App.FinTrapezoidShapeHandler import FinTrapezoidShapeHandler

from DraftTools import translate

class ShapeFin(ShapeComponent):

    def __init__(self, obj):
        super().__init__(obj)

        obj.addProperty('App::PropertyEnumeration', 'FinType', 'Fin', translate('App::Property', 'Fin type'))
        obj.FinType = [FIN_TYPE_TRAPEZOID, 
                # FIN_TYPE_ELLIPSE, 
                # FIN_TYPE_TUBE, 
                # FIN_TYPE_SKETCH
                ]
        obj.FinType = FIN_TYPE_TRAPEZOID

        obj.addProperty('App::PropertyEnumeration', 'RootCrossSection', 'Fin', translate('App::Property', 'Fin root cross section'))
        obj.RootCrossSection = [FIN_CROSS_SQUARE, FIN_CROSS_ROUND, FIN_CROSS_AIRFOIL, FIN_CROSS_WEDGE, 
            FIN_CROSS_DIAMOND, FIN_CROSS_TAPER_LE, FIN_CROSS_TAPER_TE, FIN_CROSS_TAPER_LETE]
        obj.RootCrossSection = FIN_CROSS_SQUARE

        obj.addProperty('App::PropertyLength', 'RootChord', 'Fin', translate('App::Property', 'Length of the base of the fin')).RootChord = 10.0
        obj.addProperty('App::PropertyLength', 'RootThickness', 'Fin', translate('App::Property', 'Fin root thickness')).RootThickness = 2.0
        obj.addProperty('App::PropertyBool', 'RootPerCent', 'Fin', translate('App::Property', 'Root chord lengths are percentages')).RootPerCent = True
        obj.addProperty('App::PropertyLength', 'RootLength1', 'Fin', translate('App::Property', 'Root chord length 1')).RootLength1 = 20.0
        obj.addProperty('App::PropertyLength', 'RootLength2', 'Fin', translate('App::Property', 'Root chord length 2')).RootLength2 = 80.0

        obj.addProperty('App::PropertyEnumeration', 'TipCrossSection', 'Fin', translate('App::Property', 'Fin tip cross section'))
        obj.TipCrossSection = [FIN_CROSS_SQUARE, FIN_CROSS_ROUND, FIN_CROSS_AIRFOIL, FIN_CROSS_WEDGE, 
            FIN_CROSS_DIAMOND, FIN_CROSS_TAPER_LE, FIN_CROSS_TAPER_TE, FIN_CROSS_TAPER_LETE]
        obj.TipCrossSection = FIN_CROSS_SQUARE

        obj.addProperty('App::PropertyLength', 'TipChord', 'Fin', translate('App::Property', 'Length of the tip of the fin')).TipChord = 5.0
        obj.addProperty('App::PropertyLength', 'TipThickness', 'Fin', translate('App::Property', 'Fin tip thickness')).TipThickness = 2.0
        obj.addProperty('App::PropertyBool', 'TipPerCent', 'Fin', translate('App::Property', 'Tip chord lengths are percentages')).TipPerCent = True
        obj.addProperty('App::PropertyLength', 'TipThickness', 'Fin', translate('App::Property', 'Fin tip thickness')).TipThickness = 2.0
        obj.addProperty('App::PropertyLength', 'TipLength1', 'Fin', translate('App::Property', 'Tip chord length 1')).TipLength1 = 20.0
        obj.addProperty('App::PropertyLength', 'TipLength2', 'Fin', translate('App::Property', 'Tip chord length 2')).TipLength2 = 80.0

        obj.addProperty('App::PropertyLength', 'Height', 'Fin', translate('App::Property', 'Fin semi-span')).Height = 10.0
        obj.addProperty('App::PropertyDistance', 'SweepLength', 'Fin', translate('App::Property', 'Sweep length')).SweepLength = 3.0 # Must be distance since it can be negative
        obj.addProperty('App::PropertyAngle', 'SweepAngle', 'Fin', translate('App::Property', 'Sweep angle')).SweepAngle = 0.0

        obj.addProperty('App::PropertyBool', 'Ttw', 'Fin', translate('App::Property', 'Through the wall (TTW) tab')).Ttw = False
        obj.addProperty('App::PropertyLength', 'TtwOffset', 'Fin', translate('App::Property', 'TTW Offset from fin root')).TtwOffset = 2.0
        obj.addProperty('App::PropertyLength', 'TtwLength', 'Fin', translate('App::Property', 'TTW Length')).TtwLength = 6.0
        obj.addProperty('App::PropertyLength', 'TtwHeight', 'Fin', translate('App::Property', 'TTW Height')).TtwHeight = 10.0
        obj.addProperty('App::PropertyLength', 'TtwThickness', 'Fin', translate('App::Property', 'TTW thickness')).TtwThickness = 1.0

        obj.addProperty('Part::PropertyPartShape', 'Shape', 'Fin', translate('App::Property', 'Shape of the fin'))

    def execute(self, obj):

        if obj.FinType == FIN_TYPE_TRAPEZOID:
            shape = FinTrapezoidShapeHandler(obj)

        if shape is not None:
            shape.draw()
