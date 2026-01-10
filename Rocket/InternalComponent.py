# SPDX-License-Identifier: LGPL-2.1-or-later
# SPDX-FileCopyrightText: 2021 David Carter <dcarter@davidcarter.ca>
# SPDX-File-Notice: Part of the Rocket addon.


"""Class for rocket components"""

__title__ = "FreeCAD Rocket Components"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

from typing import Any

from Rocket.RocketComponent import RocketComponent
from Rocket.position.AxialPositionable import AxialPositionable
from Rocket.position import AxialMethod


"""
    A component internal to the rocket.  Internal components have no effect on the
    the aerodynamics of a rocket, only its mass properties (though the location of the
    components is not enforced to be within external components).  Internal components
    are always attached relative to the parent component, which can be internal or
    external, or absolutely.
"""
class InternalComponent(RocketComponent, AxialPositionable):

    def __init__(self, obj : Any) -> None:
        super().__init__(obj)

    def setDefaults(self) -> None:
        super().setDefaults()

        self._obj.AxialMethod = AxialMethod.BOTTOM

    def setAxialMethod(self, newAxialMethod : AxialMethod.AxialMethod) -> None:
        super().setAxialMethod(newAxialMethod)
        self.notifyComponentChanged()
