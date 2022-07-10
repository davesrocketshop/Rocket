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

from App.ShapeFin import ShapeFin
from App.Constants import FIN_TYPE_TRAPEZOID, FIN_TYPE_ELLIPSE, FIN_TYPE_SKETCH, \
                            FINCAN_CROSS_SQUARE, FINCAN_CROSS_ROUND, FINCAN_CROSS_TAPER

from App.FinCanShapeHandler import FinCanTrapezoidShapeHandler
from App.FinCanShapeHandler import FinCanEllipseShapeHandler
from App.FinCanShapeHandler import FinCanSketchShapeHandler

from DraftTools import translate

class ShapeFinCan(ShapeFin):

    def __init__(self, obj):
        super().__init__(obj)

        # Fin cans aren't TTW and are a fin set
        obj.Ttw = False
        obj.FinSet = True

        # Default set to fit on a BT-50
        if not hasattr(obj,"InnerDiameter"):
            obj.addProperty('App::PropertyLength', 'InnerDiameter', 'Fin', translate('App::Property', 'Diameter of the inside of the fin can')).InnerDiameter = 24.8
        if not hasattr(obj,"Thickness"):
            obj.addProperty('App::PropertyLength', 'Thickness', 'Fin', translate('App::Property', 'Thickness of the fin can')).Thickness = 1.5
        if not hasattr(obj,"Length"):
            obj.addProperty('App::PropertyLength', 'Length', 'Fin', translate('App::Property', 'Length of the fin can')).Length = 60.0
        if not hasattr(obj,"LeadingEdgeOffset"):
            obj.addProperty('App::PropertyDistance', 'LeadingEdgeOffset', 'Fin', translate('App::Property', 'Distance between the fin can leading edge and the fin leading edge')).LeadingEdgeOffset = 0.0

        if not hasattr(obj,"LeadingEdge"):
            obj.addProperty('App::PropertyEnumeration', 'LeadingEdge', 'Fin', translate('App::Property', 'Leading Edge'))
        obj.LeadingEdge = [FINCAN_CROSS_SQUARE, FINCAN_CROSS_ROUND, FINCAN_CROSS_TAPER]
        obj.LeadingEdge = FINCAN_CROSS_SQUARE
        if not hasattr(obj,"LeadingLength"):
            obj.addProperty('App::PropertyLength', 'LeadingLength', 'Fin', translate('App::Property', 'Leading Edge Length')).LeadingLength = 5.0

        if not hasattr(obj,"TrailingEdge"):
            obj.addProperty('App::PropertyEnumeration', 'TrailingEdge', 'Fin', translate('App::Property', 'Trailing Edge'))
        obj.TrailingEdge = [FINCAN_CROSS_SQUARE, FINCAN_CROSS_ROUND, FINCAN_CROSS_TAPER]
        obj.TrailingEdge = FINCAN_CROSS_SQUARE
        if not hasattr(obj,"TrailingLength"):
            obj.addProperty('App::PropertyLength', 'TrailingLength', 'Fin', translate('App::Property', 'Trailing Edge Length')).TrailingLength = 5.0

        if not hasattr(obj,"LaunchLug"):
            obj.addProperty('App::PropertyBool', 'LaunchLug', 'Fin', translate('App::Property', 'Fin can includes a launch lug')).LaunchLug = True
        if not hasattr(obj,"LugInnerDiameter"):
            obj.addProperty('App::PropertyLength', 'LugInnerDiameter', 'Fin', translate('App::Property', 'Diameter of the inside of the launch lug')).LugInnerDiameter = 3.56
        if not hasattr(obj,"LugThickness"):
            obj.addProperty('App::PropertyLength', 'LugThickness', 'Fin', translate('App::Property', 'Thickness of the launch lug')).LugThickness = 1.0
        if not hasattr(obj,"LugLength"):
            obj.addProperty('App::PropertyLength', 'LugLength', 'Fin', translate('App::Property', 'Length of the launch')).LugLength = 60.0
        if not hasattr(obj,"LugAutoLength"):
            obj.addProperty('App::PropertyBool', 'LugAutoLength', 'Fin', translate('App::Property', 'Automatically adjust the length of the launch lug')).LugAutoLength = True

        # Set the Parent Radius to the ID
        obj.ParentRadius = (obj.InnerDiameter / 2.0)



    def execute(self, obj):

        if obj.FinType == FIN_TYPE_TRAPEZOID:
            shape = FinCanTrapezoidShapeHandler(obj)
        elif obj.FinType == FIN_TYPE_ELLIPSE:
            shape = FinCanEllipseShapeHandler(obj)
        elif obj.FinType == FIN_TYPE_SKETCH:
            shape = FinCanSketchShapeHandler(obj)

        if shape is not None:
            shape.draw()
