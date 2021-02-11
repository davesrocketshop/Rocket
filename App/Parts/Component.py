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

class Component:

    def __init__(self):
        self._manufacturer = ""
        self._partNumber = ""
        self._description = ""
        self._material = ("", MATERIAL_TYPE_BULK)
        self._mass = (0.0, "")

    def validString(value):
        if value is None:
            return False
        return True

    def validNonEmptyString(value):
        if validString(value) and (str(value).strip().length() > 0):
            return True
        return False

    def isValid():
        if not validString(self._manufacturer):
            return False
        if not validNonEmptyString(self._partNumber):
            return False
        if not validString(self._description):
            return False
        if not validNonEmptyString(self._material[0]):
            return False
        if self._material[0] not in [MATERIAL_TYPE_BULK, MATERIAL_TYPE_SURFACE, MATERIAL_TYPE_LINE]:
            return False

        if self._mass[0] < 0.0:
            return False
        elif self._mass[0] > 0.0: # No units required for 0 mass
            if not validNonEmptyString(self._mass[1]):
                return False

        return True
