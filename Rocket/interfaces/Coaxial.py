# SPDX-License-Identifier: LGPL-2.1-or-later
# SPDX-FileCopyrightText: 2022 David Carter <dcarter@davidcarter.ca>
# SPDX-File-Notice: Part of the Rocket addon.


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
