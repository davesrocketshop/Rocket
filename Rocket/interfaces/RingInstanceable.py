# SPDX-License-Identifier: LGPL-2.1-or-later
# SPDX-FileCopyrightText: 2022 David Carter <dcarter@davidcarter.ca>
# SPDX-File-Notice: Part of the Rocket addon.


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

