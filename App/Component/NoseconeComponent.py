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
"""Component class for rocket nose cones"""

__title__ = "FreeCAD Open Rocket Component"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

import FreeCAD

from App.Component.Component import Component
from App.ShapeNoseCone import ShapeNoseCone
from Ui.ViewNoseCone import ViewProviderNoseCone

from App.Utilities import _trace

from App.Constants import TYPE_CONE
from App.Constants import STYLE_CAPPED, STYLE_HOLLOW, STYLE_SOLID

class NoseconeComponent(Component):

    def __init__(self, doc):
        super().__init__(doc)
        _trace(self.__class__.__name__, "__init__")

        self._manufacturer = ""
        self._partNo = ""
        self._description = ""
        self._material = ""
        self._filled = False
        self._shape = TYPE_CONE
        self._shapeClipped = False
        self._shapeParameter = 1.0
        self._aftRadius = -1.0
        self._aftShoulderRadius = -1.0
        self._aftShoulderLength = -1.0
        self._aftShoulderThickness = -1.0
        self._aftShoulderCapped = False
        self._length = -1.0

    def create(self, parent):
        _trace(self.__class__.__name__, "create")

        obj = self._doc.addObject('Part::FeaturePython', 'NoseCone')
        obj.Label= self._name

        noseCone = ShapeNoseCone(obj) # lgtm [py/unused-local-variable]

        obj.NoseType = self._shape
        if self._filled:
            obj.NoseStyle = STYLE_SOLID
        else:
            if self._aftShoulderCapped:
                obj.NoseStyle = STYLE_CAPPED
            else:
                obj.NoseStyle = STYLE_HOLLOW
        # obj.Description = self._description

        obj.Length = self._fromOrkLength(self._length)
        obj.Radius = self._fromOrkLength(self._aftRadius)
        obj.Thickness = self._fromOrkLength(self._thickness)
        obj.Shoulder = (self._aftShoulderLength > 0)
        obj.ShoulderLength = self._fromOrkLength(self._aftShoulderLength)
        obj.ShoulderRadius = self._fromOrkLength(self._aftShoulderRadius)
        obj.ShoulderThickness = self._fromOrkLength(self._aftShoulderThickness)
        obj.Coefficient = self._shapeParameter

        if FreeCAD.GuiUp:
            ViewProviderNoseCone(obj.ViewObject)

        if parent is not None:
            parent.addObject(obj)

        super().create(obj)
