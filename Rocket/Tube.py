# SPDX-License-Identifier: LGPL-2.1-or-later
# SPDX-FileCopyrightText: 2021 David Carter <dcarter@davidcarter.ca>
# SPDX-File-Notice: Part of the Rocket addon.


"""Class for rocket components"""

__title__ = "FreeCAD Rocket Components"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

from typing import Any

from Rocket.ExternalComponent import ExternalComponent
from Rocket.interfaces.Coaxial import Coaxial

class Tube(ExternalComponent, Coaxial):

    def __init__(self, obj : Any) -> None:
        super().__init__(obj)

    def setDefaults(self) -> None:
        super().setDefaults()
