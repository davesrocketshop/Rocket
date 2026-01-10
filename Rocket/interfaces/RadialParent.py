# SPDX-License-Identifier: LGPL-2.1-or-later
# SPDX-FileCopyrightText: 2022 David Carter <dcarter@davidcarter.ca>
# SPDX-File-Notice: Part of the Rocket addon.


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
