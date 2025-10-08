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
"""Class for radially positioned components"""

__title__ = "FreeCAD Rocket Components"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

from abc import ABC, abstractmethod

from Rocket.position.RadiusMethod import RadiusMethod

class RadiusPositionable(ABC):

    @abstractmethod
    def getBoundingRadius(self) -> float:
        ...

    @abstractmethod
    def getRadiusOffset(self) -> float:
        ...

    @abstractmethod
    def setRadiusOffset(self, radius : float) -> None:
        ...

    @abstractmethod
    def getRadiusMethod(self) -> RadiusMethod:
        ...

    @abstractmethod
    def setRadiusMethod(self, method : RadiusMethod) -> None:
        ...

    @abstractmethod
    def setRadiusByMethod(self, method : RadiusMethod, radius : float) -> None:
        ...
