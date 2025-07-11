# ***************************************************************************
# *   Copyright (c) 2022-2025 David Carter <dcarter@davidcarter.ca>         *
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
"""Interface for rocket components"""

__title__ = "FreeCAD Rocket Components"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

from abc import abstractmethod

from Rocket.interfaces.Instanceable import Instanceable
from Rocket.position.AngleMethod import AngleMethod
from Rocket.position.AnglePositionable import AnglePositionable
from Rocket.position.RadiusMethod import RadiusMethod
from Rocket.position.RadiusPositionable import RadiusPositionable

class RingInstanceable(Instanceable, AnglePositionable, RadiusPositionable):

    @abstractmethod
    def getAngleOffset(self) -> float:
        ...

    @abstractmethod
    def setAngleOffset(self, angle : float) -> None:
        ...

    @abstractmethod
    def getAngleMethod(self) -> AngleMethod:
        ...

    @abstractmethod
    def setAngleMethod(self, newMethod : AngleMethod) -> None:
        ...

    @abstractmethod
    def getInstanceAngleIncrement(self) -> float:
        ...

    @abstractmethod
    def getInstanceAngles(self) -> list[float]:
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
    def setRadiusMethod(self, newMethod : RadiusMethod) -> None:
        ...

