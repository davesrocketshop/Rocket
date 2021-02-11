# ***************************************************************************
# *   Copyright (c) 2021 David Carter <dcarter@davidcarter.ca>              *
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
"""Class for rocket part components"""

__title__ = "FreeCAD Open Rocket Part Transition"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

class Transition(Component):

    def __init__(self):
        super().__init__()

        self._noseType = "" # Shape
        self._filled = False

        self._foreOutsideDiameter = (0.0, "")
        self._foreShoulderDiameter = (0.0, "")
        self._foreShoulderLength = (0.0, "")
        self._aftOutsideDiameter = (0.0, "")
        self._aftShoulderDiameter = (0.0, "")
        self._aftShoulderLength = (0.0, "")
        self._length = (0.0, "")
        self._thickness = (0.0, "")
