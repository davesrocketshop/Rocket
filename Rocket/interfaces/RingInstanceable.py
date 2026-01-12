# SPDX-License-Identifier: LGPL-2.1-or-later
# SPDX-File-Notice: Part of the Rocket addon.

################################################################################
#                                                                              #
#   © 2022 David Carter <dcarter@davidcarter.ca>                               #
#                                                                              #
#   This addon is free software: you can redistribute it and/or modify         #
#   it under the terms of the GNU Lesser General Public License as             #
#   published by the Free Software Foundation, either version 2.1              #
#   of the License, or (at your option) any later version.                     #
#                                                                              #
#   This addon is distributed in the hope that it will be useful,              #
#   but WITHOUT ANY WARRANTY; without even the implied warranty                #
#   of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.                    #
#   See the GNU Lesser General Public License for more details.                #
#                                                                              #
#   You should have received a copy of the GNU Lesser General Public           #
#   License along with this addon. If not, see https://www.gnu.org/licenses    #
#                                                                              #
################################################################################


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
    def setRadiusMethod(self, method : RadiusMethod) -> None:
        ...

