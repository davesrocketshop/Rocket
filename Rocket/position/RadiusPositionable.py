# SPDX-License-Identifier: LGPL-2.1-or-later
# SPDX-FileCopyrightText: 2021 David Carter <dcarter@davidcarter.ca>
# SPDX-File-Notice: Part of the Rocket addon.


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
