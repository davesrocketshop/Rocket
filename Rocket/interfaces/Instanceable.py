# SPDX-License-Identifier: LGPL-2.1-or-later
# SPDX-FileCopyrightText: 2022 David Carter <dcarter@davidcarter.ca>
# SPDX-File-Notice: Part of the Rocket addon.


"""Interface for rocket components"""

__title__ = "FreeCAD Rocket Components"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

from abc import ABC, abstractmethod

from Rocket.util.Coordinate import Coordinate

class Instanceable(ABC):

    """
        Returns vector coordinates of each instance of this component relative to this component's parent

        Note: <code> this.getOffsets().length == this.getInstanceCount() </code> should ALWAYS be true.
        If getInstanceCount() returns anything besides 1 this function should be overridden as well.
    """
    @abstractmethod
    def getInstanceLocations(self) -> list[Coordinate]:
        ...

    """
        Returns vector coordinates of each instance of this component relative to this component's reference point (typically front center)

        Note: <code> this.getOffsets().length == this.getInstanceCount() </code> should ALWAYS be true.
        If getInstanceCount() returns anything besides 1 this function should be overridden as well.
    """
    @abstractmethod
    def getInstanceOffsets(self) -> list[Coordinate]:
        ...

    """
        How many instances of this component are represented.  This should generally be editable.
    """
    @abstractmethod
    def setInstanceCount(self, newCount : int) -> None:
        ...

    """
         How many instances of this component are represented.  This should generally be editable.
    """
    @abstractmethod
    def getInstanceCount(self) -> int:
        ...

    """
        Get a human-readable name for this instance arrangement.
        Note: the same instance count may have different pattern names
    """
    @abstractmethod
    def getPatternName(self) -> str:
        ...
