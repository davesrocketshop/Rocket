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

__title__ = "FreeCAD Open Rocket Part Parachute"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

from App.Parts.Component import Component
from App.Constants import MATERIAL_TYPE_BULK, MATERIAL_TYPE_SURFACE, MATERIAL_TYPE_LINE
from App.Tools.Utilities import _err

class Parachute(Component):

    def __init__(self):
        super().__init__()

        self._diameter = (0.0, "")
        self._sides = 0
        self._lineCount = 0
        self._lineLength = (0.0, "")
        self._lineMaterial = ("", MATERIAL_TYPE_LINE)

    def isValid(self):
        if not super().isValid():
            _err("Parachute: super invalid")
            return False

        if self._diameter[0] <= 0.0:
            _err("Parachute: _diameter invalid")
            return False
        if self._sides < 0:
            _err("Parachute: _sides invalid")
            return False
        if self._lineCount <= 0:
            _err("Parachute: _lineCount invalid")
            return False
        if self._lineLength[0] < 0.0:
            _err("Parachute: _lineLength invalid")
            return False
        # if self.validNonEmptyString(self._lineMaterial[0]):
        #     _err("Parachute: _lineMaterial invalid")
        #     return False
        if not self.validNonEmptyString(self._diameter[1]):
            _err("Parachute: _diameter Units invalid '%s" % self._diameter[1])
            return False
        if not self.validNonEmptyString(self._lineLength[1]):
            _err("Parachute: _lineLength Units invalid '%s" % self._lineLength[1])
            return False
        # if self._lineMaterial[1].lower() != MATERIAL_TYPE_LINE.lower():
        #     _err("Parachute: _lineMaterial Units invalid '%s" % self._lineMaterial[1])
        #     return False

        return True
