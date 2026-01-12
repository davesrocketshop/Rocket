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

class RadialParent(ABC):

    # Return the outer radius of the component at local coordinate <code>x</code>.
    # Values for <code>x < 0</code> and <code>x > getLengthAerodynamic()</code> are undefined.
    @abstractmethod
    def getOuterRadius(self, pos : float) -> float:
        pass

    # Return the outer diameter of the component at local coordinate <code>x</code>.
    # Values for <code>x < 0</code> and <code>x > getLengthAerodynamic()</code> are undefined.
    @abstractmethod
    def getOuterDiameter(self, pos : float) -> float:
        pass

    # Return the inner radius of the component at local coordinate <code>x</code>.
    # Values for <code>x < 0</code> and <code>x > getLengthAerodynamic()</code> are undefined.
    @abstractmethod
    def getInnerRadius(self, pos : float) -> float:
        pass

    # Return the inner radius of the component at local coordinate <code>x</code>.
    # Values for <code>x < 0</code> and <code>x > getLengthAerodynamic()</code> are undefined.
    @abstractmethod
    def getInnerDiameter(self, pos : float) -> float:
        pass

    # Return the length of this component.
    @abstractmethod
    def getLength(self) -> float:
        pass
