# SPDX-License-Identifier: LGPL-2.1-or-later
# SPDX-File-Notice: Part of the Rocket addon.

################################################################################
#                                                                              #
#   © 2022 David Carter <dcarter@davidcarter.ca>                               #
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
