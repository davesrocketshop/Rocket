# SPDX-License-Identifier: LGPL-2.1-or-later
# SPDX-FileCopyrightText: 2022 David Carter <dcarter@davidcarter.ca>
# SPDX-File-Notice: Part of the Rocket addon.


"""Interface for rocket components"""

__title__ = "FreeCAD Rocket Components"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

from abc import abstractmethod

from Rocket.position.AxialPositionable import AxialPositionable
from Rocket.interfaces.Instanceable import Instanceable

class LineInstanceable(Instanceable, AxialPositionable):

    @abstractmethod
    def getInstanceSeparation(self) -> float:
        pass

    @abstractmethod
    def setInstanceSeparation(self, separation : float) -> None:
        pass
