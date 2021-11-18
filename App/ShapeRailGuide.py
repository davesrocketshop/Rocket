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

from App.ShapeComponent import ShapeLocation
from App.Constants import FEATURE_RAIL_GUIDE
from App.Constants import PLACEMENT_RADIAL

from App.RailGuideShapeHandler import RailGuideShapeHandler

from DraftTools import translate

class ShapeRailGuide(ShapeLocation):

    def __init__(self, obj):
        super().__init__(obj)
        self.Type = FEATURE_RAIL_GUIDE
        self._obj.PlacementType = PLACEMENT_RADIAL

        if not hasattr(obj,"TopWidth"):
            obj.addProperty('App::PropertyLength', 'TopWidth', 'LaunchGuide', translate('App::Property', 'Width of the top of the launch guide')).TopWidth = 9.462
        if not hasattr(obj, 'MiddleWidth'):
            obj.addProperty('App::PropertyLength', 'MiddleWidth', 'LaunchGuide', translate('App::Property', 'Width of the inside of the launch guide')).MiddleWidth = 6.2375
        if not hasattr(obj, 'BaseWidth'):
            obj.addProperty('App::PropertyLength', 'BaseWidth', 'LaunchGuide', translate('App::Property', 'Width of the base or bottom of the launch guide')).BaseWidth = 15.0
        if not hasattr(obj,"TopThickness"):
            obj.addProperty('App::PropertyLength', 'TopThickness', 'LaunchGuide', translate('App::Property', 'Thickness of the top part of the launch guide')).TopThickness = 2.096
        if not hasattr(obj,"BottomThickness"):
            obj.addProperty('App::PropertyLength', 'BottomThickness', 'LaunchGuide', translate('App::Property', 'Thickness of the inside part of the launch guide')).BottomThickness = 3.429
        if not hasattr(obj,"Thickness"):
            obj.addProperty('App::PropertyLength', 'Thickness', 'LaunchGuide', translate('App::Property', 'Total thickness of the launch guide')).Thickness = 7.62
        if not hasattr(obj,"Length"):
            obj.addProperty('App::PropertyLength', 'Length', 'LaunchGuide', translate('App::Property', 'Length of the launch guide')).Length = 20.0

        if not hasattr(obj,"Shape"):
            obj.addProperty('Part::PropertyPartShape', 'Shape', 'LaunchGuide', translate('App::Property', 'Shape of the launch guide'))

    def getAxialLength(self):
        # Return the length of this component along the central axis
        return self._obj.Length

    def execute(self, obj):
        shape = RailGuideShapeHandler(obj)
        if shape is not None:
            shape.draw()

    def eligibleChild(self, childType):
        return False

    def onChildEdited(self):
        # print("%s: onChildEdited()" % (self.__class__.__name__))
        self._obj.Proxy.setEdited()
