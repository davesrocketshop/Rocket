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
"""Base class for rocket part components"""

__title__ = "FreeCAD Open Rocket Part Component"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

from App.Constants import MATERIAL_TYPE_BULK, MATERIAL_TYPE_SURFACE, MATERIAL_TYPE_LINE
from App.Tools.Utilities import _err

class Component:

    def __init__(self):
        self._manufacturer = ""
        self._partNumber = ""
        self._description = ""
        self._material = ("", MATERIAL_TYPE_BULK)
        self._mass = (0.0, "")

    def validString(self, value):
        if value is None:
            return False
        return True

    def validNonEmptyString(self, value):
        if self.validString(value) and (len(str(value).strip()) > 0):
            return True
        return False

    def isValid(self):
        if not self.validString(self._manufacturer):
            _err("Component: _manufacturer invalid")
            return False
        if not self.validNonEmptyString(self._partNumber):
            _err("Component: _partNumber invalid")
            return False
        if not self.validString(self._description):
            _err("Component: _description invalid")
            return False
        if not self.validNonEmptyString(self._material[0]):
            _err("Component: _material invalid")
            return False
        if self._material[1] not in [MATERIAL_TYPE_BULK, MATERIAL_TYPE_SURFACE, MATERIAL_TYPE_LINE]:
            _err("Component: _material type invalid")
            return False

        if self._mass[0] < 0.0:
            _err("Component: _mass invalid")
            return False
        elif self._mass[0] > 0.0: # No units required for 0 mass
            if not self.validNonEmptyString(self._mass[1]):
                _err("Component: _mass units invalid")
                return False

        return True
