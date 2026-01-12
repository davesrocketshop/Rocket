# SPDX-License-Identifier: LGPL-2.1-or-later
# SPDX-File-Notice: Part of the Rocket addon.

################################################################################
#                                                                              #
#   © 2025 David Carter <dcarter@davidcarter.ca>                               #
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

class Observer(ABC):

    @abstractmethod
    def componentChanged(self) -> None:
        raise NotImplementedError("Subclass must implement abstract method")

class Subject(ABC):

    def __init__(self) -> None:
        self._observers = []  # List to hold observers

    def attach(self, observer : Observer) -> None:
        if not hasattr(self, "_observers"):
            self._observers = []

        if observer not in self._observers:
            self._observers.append(observer)

    def detach(self, observer : Observer) -> None:
        if not hasattr(self, "_observers"):
            return

        self._observers.remove(observer)

    def notifyComponentChanged(self) -> None:
        for observer in self._observers:
            observer.componentChanged(self)
