# ***************************************************************************
# *   Copyright (c) 2022-2025 David Carter <dcarter@davidcarter.ca>         *
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
"""Base class for rocket finishes"""

__title__ = "FreeCAD Rocket Components"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

class Finish():
    roughnessSize = None
    name = None

    def __init__(self, _name, _roughness):
        self.roughnessSize = _roughness
        self.name = _name

    def getRoughnessSize(self):
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
