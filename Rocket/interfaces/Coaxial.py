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

from abc import ABC, abstractmethod

# This interface defines the API for components that are axially
# symmetric.  It differs from RadialParent in that RadialParent applies
# to axially symmetric components whose radius varies with position, while
# this interface is for components that have a constant radius over it's length.

class Coaxial(ABC):

    # Get the length of the radius of the inside dimension, in standard units.
    @abstractmethod
    def getInnerRadius(self, pos : float) -> float:
        pass

    # Set the length of the radius of the inside dimension, in standard units.
    @abstractmethod
    def setInnerRadius(self, radius : float):
        pass

    # Get the length of the radius of the outside dimension, in standard units.
    @abstractmethod
    def getOuterRadius(self, pos) -> float:
        pass

    # Set the length of the radius of the outside dimension, in standard units.
    @abstractmethod
    def setOuterRadius(self, radius : float):
        pass

    # Get the wall thickness of the component.  Typically this is just
    # the outer radius - inner radius.
    @abstractmethod
    def getThickness(self) -> float:
        pass
