# ***************************************************************************
# *   Copyright (c) 2021-2025 David Carter <dcarter@davidcarter.ca>         *
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
"""Class for rocket components"""

__title__ = "FreeCAD Rocket Components"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

from typing import Any

from Rocket.RocketComponent import RocketComponent
from Rocket.events.ComponentChangeEvent import ComponentChangeEvent
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
        self.fireComponentChangeEvent(ComponentChangeEvent.NONFUNCTIONAL_CHANGE)

    """
        Non-aerodynamic components.
    """
    def isAerodynamic(self) -> bool:
        return False

    def isMassive(self) -> bool:
        return True
