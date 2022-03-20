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
"""Class for drawing rail buttons"""

__title__ = "FreeCAD Rail Buttons"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

from App.ShapeComponent import ShapeComponent
from App.Constants import FEATURE_RAIL_BUTTON
from App.Constants import RAIL_BUTTON_ROUND, RAIL_BUTTON_AIRFOIL
from App.Constants import PLACEMENT_RADIAL
from App.Constants import CONTERSINK_ANGLE_60, CONTERSINK_ANGLE_82, CONTERSINK_ANGLE_90, CONTERSINK_ANGLE_100, \
                            CONTERSINK_ANGLE_110, CONTERSINK_ANGLE_120


from App.RailButtonShapeHandler import RailButtonShapeHandler

from DraftTools import translate

#
# Button dimensions were obtained here: https://www.rocketryforum.com/threads/rail-button-dimensions.30354/
# These have not been verified
#

class ShapeRailButton(ShapeComponent):

    def __init__(self, obj):
        super().__init__(obj)
        self.Type = FEATURE_RAIL_BUTTON

        # Default set to a BT-50
        if not hasattr(obj,"RailButtonType"):
            obj.addProperty('App::PropertyEnumeration', 'RailButtonType', 'RailButton', translate('App::Property', 'Rail button type'))
        obj.RailButtonType = [RAIL_BUTTON_ROUND, 
                RAIL_BUTTON_AIRFOIL
                ]
        obj.RailButtonType = RAIL_BUTTON_ROUND

        if not hasattr(obj,"OuterDiameter"):
            obj.addProperty('App::PropertyLength', 'OuterDiameter', 'RailButton', translate('App::Property', 'Diameter of the outside of the rail button')).OuterDiameter = 9.462
        if not hasattr(obj, 'InnerDiameter'):
            obj.addProperty('App::PropertyLength', 'InnerDiameter', 'RailButton', translate('App::Property', 'Diameter of the inside of the rail button')).InnerDiameter = 6.2375
        if not hasattr(obj,"TopThickness"):
            obj.addProperty('App::PropertyLength', 'TopThickness', 'RailButton', translate('App::Property', 'Thickness of the outboard part of the rail button')).TopThickness = 2.096
        if not hasattr(obj,"BaseThickness"):
            obj.addProperty('App::PropertyLength', 'BaseThickness', 'RailButton', translate('App::Property', 'Thickness of the inside part of the rail button')).BaseThickness = 3.429
        if not hasattr(obj,"Thickness"):
            obj.addProperty('App::PropertyLength', 'Thickness', 'RailButton', translate('App::Property', 'Total thickness of the rail button')).Thickness = 7.62
        if not hasattr(obj,"Length"):
            obj.addProperty('App::PropertyLength', 'Length', 'RailButton', translate('App::Property', 'Length of the rail button')).Length = 12.0

        # Default fastener is a #6 screw
        if not hasattr(obj, 'Fastener'):
            obj.addProperty('App::PropertyBool', 'Fastener', 'RailButton', translate('App::Property', 'Create a countersunk hole for the fastener')).Fastener = True
        if not hasattr(obj,"CountersinkAngle"):
            obj.addProperty('App::PropertyEnumeration', 'CountersinkAngle', 'RailButton', translate('App::Property', 'Fastener countersink angle'))
        obj.CountersinkAngle = [CONTERSINK_ANGLE_60,
                CONTERSINK_ANGLE_82,
                CONTERSINK_ANGLE_90,
                CONTERSINK_ANGLE_100,
                CONTERSINK_ANGLE_110,
                CONTERSINK_ANGLE_120
                ]
        obj.CountersinkAngle = CONTERSINK_ANGLE_82
        if not hasattr(obj,"ShankDiameter"):
            obj.addProperty('App::PropertyLength', 'ShankDiameter', 'RailButton', translate('App::Property', 'Fastener shank diameter')).ShankDiameter = 3.51
        if not hasattr(obj,"HeadDiameter"):
            obj.addProperty('App::PropertyLength', 'HeadDiameter', 'RailButton', translate('App::Property', 'Fastener head diameter')).HeadDiameter = 7.80

        if not hasattr(obj, 'FilletedTop'):
            obj.addProperty('App::PropertyBool', 'FilletedTop', 'RailButton', translate('App::Property', 'Apply a fillet to the top of the rail button')).FilletedTop = False
        if not hasattr(obj,"FilletRadius"):
            obj.addProperty('App::PropertyLength', 'FilletRadius', 'RailButton', translate('App::Property', 'Fillet radius')).FilletRadius = 0.5

        if not hasattr(obj,"Shape"):
            obj.addProperty('Part::PropertyPartShape', 'Shape', 'RailButton', translate('App::Property', 'Shape of the rail button'))

    def getAxialLength(self):
        # Return the length of this component along the central axis
        return self._obj.Length

    def execute(self, obj):
        shape = RailButtonShapeHandler(obj)
        if shape is not None:
            shape.draw()

    def eligibleChild(self, childType):
        return False

    def onChildEdited(self):
        # print("%s: onChildEdited()" % (self.__class__.__name__))
        self._obj.Proxy.setEdited()
