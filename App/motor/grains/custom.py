# ***************************************************************************
# *   Copyright (c) 2022 David Carter <dcarter@davidcarter.ca>              *
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
"""Class for rocket motors"""

__title__ = "FreeCAD Rocket Motors"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

import skimage.draw as draw

from App.motor.Grain import FmmGrain
from App.motor.simResult import SimAlert, SimAlertLevel, SimAlertType
from App.motor.units import getAllConversions, convert

from App.Constants import GRAIN_GEOMETRY_CUSTOM

from DraftTools import translate

class CustomGrain(FmmGrain):
    """Custom grains can have any core shape. They define their geometry using a polygon property, which tracks a list
    of polygons that each consist of a number of points. The polygons are scaled according to user specified units and
    drawn onto the core map."""
    def __init__(self, obj):
        super().__init__(obj)

        self._obj.GeometryName = GRAIN_GEOMETRY_CUSTOM

        if not hasattr(obj, 'Points'):
            obj.addProperty('App::PropertyVectorList', 'Points', 'Grain', translate('App::Property', 'Core geometry')).Points = None
        if not hasattr(obj, 'DfxUnit'):
            obj.addProperty('App::PropertyEnumeration', 'DfxUnit', 'Grain', translate('App::Property', 'Inhibited ends'))
            obj.DfxUnit = getAllConversions('m')
            obj.DfxUnit = 'm'

    def onDocumentRestored(self, obj):
        super().onDocumentRestored(obj)
        
        # Add any missing attributes
        CustomGrain(obj)

    def generateCoreMap(self):
        inUnit = self._obj.DfxUnit
        for polygon in self._obj.Points:
            row = [(self.mapDim/2) + (-self.normalize(convert(p[1], inUnit, 'm')) * (self.mapDim/2)) for p in polygon]
            col = [(self.mapDim/2) + (self.normalize(convert(p[0], inUnit, 'm')) * (self.mapDim/2)) for p in polygon]
            imageRow, imageCol = draw.polygon(row, col, self.coreMap.shape)
            self.coreMap[imageRow, imageCol] = 0

    def getGeometryErrors(self):
        errors = super().getGeometryErrors()

        if len(self._obj.Points) > 1:
            aText = 'Support for custom grains with multiple cores is experimental'
            errors.append(SimAlert(SimAlertLevel.WARNING, SimAlertType.GEOMETRY, aText))

        return errors
