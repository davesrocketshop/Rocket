# SPDX-License-Identifier: LGPL-2.1-or-later
# SPDX-FileCopyrightText: 2021 David Carter <dcarter@davidcarter.ca>
# SPDX-File-Notice: Part of the Rocket addon.


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
