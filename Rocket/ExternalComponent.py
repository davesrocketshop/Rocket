# SPDX-License-Identifier: LGPL-2.1-or-later
# SPDX-File-Notice: Part of the Rocket addon.

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
from Rocket.position.AxialMethod import AxialMethod
from Rocket.util import Finish

# Class of components with well-defined physical appearance and which have an effect on
# aerodynamic simulation.  They have material defined for them, and the mass of the component
# is calculated using the component's volume.

class ExternalComponent(RocketComponent):

    finish : Finish.Finish = Finish.NORMAL

    def __init__(self, obj : Any):
        super().__init__(obj)

    def setDefaults(self) -> None:
        super().setDefaults()

    def getFinish(self) -> Finish.Finish:
        return self.finish

    def setFinish(self, finish : Finish.Finish) -> None:
        if self.finish == finish:
            return
        self.finish = finish

        self.notifyComponentChanged()
