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
"""Base class for rocket component assemblies"""

__title__ = "FreeCAD Rocket Components"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

# import FreeCAD
# import math

from tokenize import Double

from App.position import AxialMethod
from App.position.AxialPositionable import AxialPositionable
from App.ShapeComponent import ShapeComponent

# from DraftTools import translate

class ShapeComponentAssembly(ShapeComponent, AxialPositionable):

    def __init__(self, obj):
        super().__init__(obj)

    def getAxialOffset(self) -> Double:
        return self.getAxialOffsetFromMethod(self._obj.AxialMethod)
	
    def setAxialOffset(self, newAxialOffset) -> None:
        self._updateBounds()
        self.setAxialOffsetFromMethod(self._obj.AxialMethod, newAxialOffset)
	
    def getAxialMethod(self) -> AxialMethod:
        return self._obj.AxialMethod
	
    def setAxialMethod(self, newMethod) -> None:
        self._obj.AxialMethod = newMethod
