# SPDX-License-Identifier: LGPL-2.1-or-later
# SPDX-FileCopyrightText: 2022 David Carter <dcarter@davidcarter.ca>
# SPDX-File-Notice: Part of the Rocket addon.


"""Class for axially positioned components"""

__title__ = "FreeCAD Rocket Components"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

from abc import ABC, abstractmethod

from Rocket.position.AxialMethod import AxialMethod

class AxialPositionable(ABC):

    @abstractmethod
    def getAxialOffset(self) -> float:
        ...

    @abstractmethod
    def setAxialOffset(self, newAxialOffset : float) -> None:
        ...

    @abstractmethod
    def getAxialMethod(self) -> AxialMethod:
        ...

    @abstractmethod
    def setAxialMethod(self, newAxialMethod : AxialMethod) -> None:
        ...
