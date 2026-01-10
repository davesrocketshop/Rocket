# SPDX-License-Identifier: LGPL-2.1-or-later
# SPDX-FileCopyrightText: 2022 David Carter <dcarter@davidcarter.ca>
# SPDX-File-Notice: Part of the Rocket addon.


"""Base class for rocket finishes"""

__title__ = "FreeCAD Rocket Components"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

class Finish():
    roughnessSize : float = 0.0
    name : str = ""

    def __init__(self, _name : str, _roughness : float) -> None:
        self.roughnessSize = _roughness
        self.name = _name

    def getRoughnessSize(self) -> float:
        return self.roughnessSize

# Rough
ROUGH = Finish("ExternalComponent.Rough", 500e-6)
# Unfinished
UNFINISHED = Finish("ExternalComponent.Unfinished", 150e-6)
# Regular paint
NORMAL = Finish("ExternalComponent.Regularpaint", 60e-6)
# Smooth paint
SMOOTH = Finish("ExternalComponent.Smoothpaint", 20e-6)
# Polished
POLISHED = Finish("ExternalComponent.Polished", 2e-6)
