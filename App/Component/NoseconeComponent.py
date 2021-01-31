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

from App.OpenRocket import _msg, _err, _trace

from App.Component.Component import Component
from App.NoseCone import NoseCone, ViewProviderNoseCone

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

    def draw(self, parent):
        _trace(self.__class__.__name__, "draw")

        obj = self._doc.addObject('Part::FeaturePython', 'NoseCone')
        obj.Label= self._name

        #guiObj = Gui.ActiveDocument.getObject(self._name)
        noseCone = NoseCone(obj, self._shape, "solid",
            self._length, self._aftRadius, 2.0, self._shapeParameter, 100,
            (self._aftShoulderLength > 0), self._aftShoulderLength, self._aftShoulderRadius, self._aftShoulderThickness)
        if FreeCAD.GuiUp:
            ViewProviderNoseCone(noseCone.ViewObject)

        #noseCone.draw(obj)
        parent.addObject(obj)

        # draw any subcomponents
        super().draw(obj)
