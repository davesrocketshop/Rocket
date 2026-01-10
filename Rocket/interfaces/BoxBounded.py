# SPDX-License-Identifier: LGPL-2.1-or-later
# SPDX-FileCopyrightText: 2022 David Carter <dcarter@davidcarter.ca>
# SPDX-File-Notice: Part of the Rocket addon.


"""Interface for rocket components"""

__title__ = "FreeCAD Rocket Components"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

from abc import ABC, abstractmethod

from Rocket.util.BoundingBox import BoundingBox

class BoxBounded(ABC):

    # Get a bounding box for a single instance of this component, from its own reference point.
    # This is expected to be combined with a InstanceContext for bounds in the global / rocket frame
    @abstractmethod
    def getInstanceBoundingBox(self) -> BoundingBox:
        pass
