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
"""Class for drawing body tubes"""

__title__ = "FreeCAD Body Tubes"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

from App.position.AxialPositionable import AxialPositionable

from App.ThicknessRingComponent import ThicknessRingComponent
from App.ShapeHandlers.BodyTubeShapeHandler import BodyTubeShapeHandler

from App.Constants import FEATURE_ENGINE_BLOCK

from DraftTools import translate

class FeatureEngineBlock(ThicknessRingComponent, AxialPositionable):

    def __init__(self, obj):
        super().__init__(obj)
        self.Type = FEATURE_ENGINE_BLOCK

        if not hasattr(obj,"Shape"):
            obj.addProperty('Part::PropertyPartShape', 'Shape', 'Rocket', translate('App::Property', 'Shape of the body tube'))

        # Set default values
        self._obj.AutoDiameter = True
        self._obj.Thickness = 5.0
        self._obj.Length = 5.0

    def onDocumentRestored(self, obj):
        super().onDocumentRestored(obj)

        FeatureEngineBlock(obj)

    def execute(self, obj):
        shape = BodyTubeShapeHandler(obj)
        if shape is not None:
            shape.draw()

    def isAfter(self):
        return False

    def eligibleChild(self, childType):
        return False
