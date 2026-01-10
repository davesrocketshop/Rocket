# SPDX-License-Identifier: LGPL-2.1-or-later
# SPDX-FileCopyrightText: 2021 David Carter <dcarter@davidcarter.ca>
# SPDX-File-Notice: Part of the Rocket addon.


"""Class for angle positioned components"""

__title__ = "FreeCAD Rocket Components"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

from abc import ABC, abstractmethod

from Rocket.position.AngleMethod import AngleMethod

class AnglePositionable(ABC):

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
