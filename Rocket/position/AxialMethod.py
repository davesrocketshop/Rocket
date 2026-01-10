# SPDX-License-Identifier: LGPL-2.1-or-later

# ***************************************************************************
# *   Copyright (c) 2021-2025 David Carter <dcarter@davidcarter.ca>         *
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
"""Class for axial placement strategies"""

__title__ = "FreeCAD Rocket Components"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

from abc import abstractmethod

import FreeCAD
translate = FreeCAD.Qt.translate

from Rocket.Constants import LOCATION_PARENT_TOP, LOCATION_PARENT_MIDDLE, LOCATION_PARENT_BOTTOM, \
    LOCATION_BASE, LOCATION_AFTER

from Rocket.position.DistanceMethod import DistanceMethod

class AxialMethod(DistanceMethod):

    _description : str = ""

    def __init__(self, newDescription):
        self._description : str = newDescription

    def __str__(self) -> str:
        return self._description

    def clampToZero(self):
        return False

    def getAsOffset(self, position, innerLength, outerLength):
        return 0.0

    def getAsPosition(self, offset, innerLength, outerLength):
        return 0.0

    @abstractmethod
    def getMethodName(self) -> str:
        ...

class AbsoluteAxialMethod(AxialMethod):

    def __init__(self):
        super().__init__(translate('App::Property', 'Tip of the nose cone'))

    def getAsOffset(self, position, innerLength, outerLength):
        return float(position)

    def getAsPosition(self, offset, innerLength, outerLength):
        return float(offset)

    def getMethodName(self) -> str:
        return LOCATION_BASE

class AfterAxialMethod(AxialMethod):

    def __init__(self):
        super().__init__(translate('App::Property', 'After the sibling component'))

    def getAsOffset(self, position, innerLength, outerLength):
        return float(position) - float(outerLength)

    def getAsPosition(self, offset, innerLength, outerLength):
        return float(outerLength) + float(offset)

    def getMethodName(self) -> str:
        return LOCATION_AFTER


class BottomAxialMethod(AxialMethod):

    def __init__(self):
        super().__init__(translate('App::Property', 'Bottom of the parent component'))

    def getAsOffset(self, position, innerLength, outerLength):
        return float(position) + (float(outerLength) - float(innerLength))

    def getAsPosition(self, offset, innerLength, outerLength):
        return float(offset) + (float(outerLength) - float(innerLength))

    def getMethodName(self) -> str:
        return LOCATION_PARENT_BOTTOM

class MiddleAxialMethod(AxialMethod):

    def __init__(self):
        super().__init__(translate('App::Property', 'Middle of the parent component'))

    def getAsOffset(self, position, innerLength, outerLength):
        return float(position) + (float(innerLength) - float(outerLength)) / 2

    def getAsPosition(self, offset, innerLength, outerLength):
        return float(offset) + (float(outerLength) - float(innerLength)) / 2

    def getMethodName(self) -> str:
        return LOCATION_PARENT_MIDDLE

class TopAxialMethod(AxialMethod):

    def __init__(self):
        super().__init__(translate('App::Property', 'Top of the parent component'))

    def getAsOffset(self, position, innerLength, outerLength):
        return float(position)

    def getAsPosition(self, offset, innerLength, outerLength):
        return float(offset)

    def getMethodName(self) -> str:
        return LOCATION_PARENT_TOP

ABSOLUTE = AbsoluteAxialMethod()
AFTER = AfterAxialMethod()
TOP = TopAxialMethod()
MIDDLE = MiddleAxialMethod()
BOTTOM = BottomAxialMethod()

AXIAL_METHOD_MAP = {
    LOCATION_PARENT_TOP : TOP,
    LOCATION_PARENT_MIDDLE : MIDDLE,
    LOCATION_PARENT_BOTTOM : BOTTOM,
    LOCATION_BASE : ABSOLUTE,
    LOCATION_AFTER : AFTER
}
