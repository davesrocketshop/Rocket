# SPDX-License-Identifier: LGPL-2.1-or-later
# SPDX-FileCopyrightText: 2025 David Carter <dcarter@davidcarter.ca>
# SPDX-File-Notice: Part of the Rocket addon.


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
