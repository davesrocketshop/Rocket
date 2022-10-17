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
"""Class for drawing launch guides"""

__title__ = "FreeCAD Launch Guide"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

from App.ShapeBase import TRACE_POSITION, TRACE_EXECUTION
from App.ShapeComponent import ShapeLocation
from App.Constants import FEATURE_RAIL_GUIDE
from App.Constants import PLACEMENT_RADIAL
from App.Constants import RAIL_GUIDE_BASE_FLAT, RAIL_GUIDE_BASE_CONFORMAL, RAIL_GUIDE_BASE_V

from App.RailGuideShapeHandler import RailGuideShapeHandler

from DraftTools import translate

class ShapeRailGuide(ShapeLocation):

    def __init__(self, obj):
        super().__init__(obj)
        self.Type = FEATURE_RAIL_GUIDE
        self._obj.PlacementType = PLACEMENT_RADIAL

        if not hasattr(obj,"RailGuideBaseType"):
            obj.addProperty('App::PropertyEnumeration', 'RailGuideBaseType', 'RailGuide', translate('App::Property', 'Rail guide base type'))
            obj.RailGuideBaseType = [RAIL_GUIDE_BASE_FLAT, 
                    RAIL_GUIDE_BASE_CONFORMAL,
                    RAIL_GUIDE_BASE_V
                    ]
            obj.RailGuideBaseType = RAIL_GUIDE_BASE_FLAT

        if not hasattr(obj,"TopWidth"):
            obj.addProperty('App::PropertyLength', 'TopWidth', 'RailGuide', translate('App::Property', 'Width of the top of the launch guide')).TopWidth = 9.462
        if not hasattr(obj, 'MiddleWidth'):
            obj.addProperty('App::PropertyLength', 'MiddleWidth', 'RailGuide', translate('App::Property', 'Width of the inside of the launch guide')).MiddleWidth = 6.2375
        if not hasattr(obj, 'BaseWidth'):
            obj.addProperty('App::PropertyLength', 'BaseWidth', 'RailGuide', translate('App::Property', 'Width of the base or bottom of the launch guide')).BaseWidth = 15.0
        if not hasattr(obj,"TopThickness"):
            obj.addProperty('App::PropertyLength', 'TopThickness', 'RailGuide', translate('App::Property', 'Thickness of the top part of the launch guide')).TopThickness = 2.096
        if not hasattr(obj,"BaseThickness"):
            obj.addProperty('App::PropertyLength', 'BaseThickness', 'RailGuide', translate('App::Property', 'Thickness of the inside part of the launch guide')).BaseThickness = 3.429
        if not hasattr(obj,"Thickness"):
            obj.addProperty('App::PropertyLength', 'Thickness', 'RailGuide', translate('App::Property', 'Total thickness of the launch guide')).Thickness = 7.62
        if not hasattr(obj,"Length"):
            obj.addProperty('App::PropertyLength', 'Length', 'RailGuide', translate('App::Property', 'Length of the launch guide')).Length = 20.0
        if not hasattr(obj,"Diameter"):
            obj.addProperty('App::PropertyLength', 'Diameter', 'RailGuide', translate('App::Property', 'Diameter of the outside of the body tube for conformal base type')).Diameter = 24.79
        if not hasattr(obj, 'AutoDiameter'):
            obj.addProperty('App::PropertyBool', 'AutoDiameter', 'RailGuide', translate('App::Property', 'Automatically set the diameter when possible')).AutoDiameter = True
        if not hasattr(obj,"VAngle"):
            obj.addProperty('App::PropertyAngle', 'VAngle', 'RailGuide', translate('App::Property', 'Angle for V base type')).VAngle = 135.0
        if not hasattr(obj, 'ForwardSweep'):
            obj.addProperty('App::PropertyBool', 'ForwardSweep', 'RailGuide', translate('App::Property', 'The component has a sweep at the forward end')).ForwardSweep = False
        if not hasattr(obj,"ForwardSweepAngle"):
            obj.addProperty('App::PropertyAngle', 'ForwardSweepAngle', 'RailGuide', translate('App::Property', 'Angle for the forward end sweep')).ForwardSweepAngle = 30.0
        if not hasattr(obj, 'AftSweep'):
            obj.addProperty('App::PropertyBool', 'AftSweep', 'RailGuide', translate('App::Property', 'The component has a sweep at the aft end')).AftSweep = False
        if not hasattr(obj,"AftSweepAngle"):
            obj.addProperty('App::PropertyAngle', 'AftSweepAngle', 'RailGuide', translate('App::Property', 'Angle for the aft end sweep')).AftSweepAngle = 30.0
        if not hasattr(obj, 'Notch'):
            obj.addProperty('App::PropertyBool', 'Notch', 'RailGuide', translate('App::Property', 'The component has a notch down the middle')).Notch = False
        if not hasattr(obj,"NotchWidth"):
            obj.addProperty('App::PropertyLength', 'NotchWidth', 'RailGuide', translate('App::Property', 'Width of the notch')).NotchWidth = 3.00
        if not hasattr(obj,"NotchDepth"):
            obj.addProperty('App::PropertyLength', 'NotchDepth', 'RailGuide', translate('App::Property', 'Depth of the notch')).NotchDepth = 4.20

        if not hasattr(obj,"Shape"):
            obj.addProperty('Part::PropertyPartShape', 'Shape', 'RailGuide', translate('App::Property', 'Shape of the launch guide'))

    def getAxialLength(self):
        if TRACE_POSITION:
            print("P: ShapeRailGuide::getAxialLength(%s)" % (self._obj.Label))

        # Return the length of this component along the central axis
        return self._obj.Length

    def execute(self, obj):
        if TRACE_EXECUTION:
            print("E: ShapeRailGuide::execute(%s)" % (self._obj.Label))

        shape = RailGuideShapeHandler(obj)
        if shape is not None:
            shape.draw()

    def onChildEdited(self):
        # print("%s: onChildEdited()" % (self.__class__.__name__))
        self._obj.Proxy.setEdited()
