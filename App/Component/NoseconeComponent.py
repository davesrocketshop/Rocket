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
import FreeCADGui

from App.Component.Component import Component
from App.ShapeNoseCone import ShapeNoseCone
from Ui.ViewNoseCone import ViewProviderNoseCone

from App.Utilities import _msg, _err, _trace

from App.Constants import TYPE_CONE, TYPE_ELLIPTICAL, TYPE_HAACK, TYPE_OGIVE, TYPE_VON_KARMAN, TYPE_PARABOLA, TYPE_PARABOLIC, TYPE_POWER
from App.Constants import STYLE_CAPPED, STYLE_HOLLOW, STYLE_SOLID

class NoseconeComponent(Component):

    def __init__(self, doc):
        super().__init__(doc)
        _trace(self.__class__.__name__, "__init__")

        self._manufacturer = ""
        self._partNo = None
        self._description = None
        self._shape = None
        self._shapeClipped = None
        self._shapeParameter = None
        self._aftRadius = None
        self._aftOuterDiameter = None
        self._aftShoulderRadius = None
        self._aftShoulderLength = None
        self._aftShoulderThickness = None
        self._aftShoulderCapped = None
        self._length = None

    def create(self, parent):
        _trace(self.__class__.__name__, "create")

        obj = self._doc.addObject('Part::FeaturePython', 'NoseCone')
        obj.Label= self._name

        noseCone = ShapeNoseCone(obj)

        obj.NoseType = self._shape
        if (self._thickness > 0) and (self._thickness < self._aftShoulderRadius):
            if self._aftShoulderCapped:
                obj.NoseStyle = STYLE_CAPPED
            else:
                obj.NoseStyle = STYLE_HOLLOW
        else:
            obj.NoseStyle = STYLE_SOLID
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
