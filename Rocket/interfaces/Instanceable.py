# SPDX-License-Identifier: LGPL-2.1-or-later
# SPDX-File-Notice: Part of the Rocket addon.

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
