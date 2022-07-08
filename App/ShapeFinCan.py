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
from App.Constants import FIN_TYPE_TRAPEZOID, FIN_TYPE_ELLIPSE, FIN_TYPE_SKETCH

from App.FinCanTrapezoidShapeHandler import FinCanTrapezoidShapeHandler
from App.FinEllipseShapeHandler import FinEllipseShapeHandler
from App.FinSketchShapeHandler import FinSketchShapeHandler

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

        # Set the Parent Radius to the OD
        obj.ParentRadius = (obj.InnerDiameter / 2.0) + obj.Thickness



    def execute(self, obj):

        if obj.FinType == FIN_TYPE_TRAPEZOID:
            shape = FinCanTrapezoidShapeHandler(obj)
        elif obj.FinType == FIN_TYPE_ELLIPSE:
            shape = FinEllipseShapeHandler(obj)
        elif obj.FinType == FIN_TYPE_SKETCH:
            shape = FinSketchShapeHandler(obj)

        if shape is not None:
            shape.draw()
