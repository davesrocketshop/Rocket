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
"""Class for rocket part materials"""

__title__ = "FreeCAD Open Rocket Part Material"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

# from App.OpenRocket import _msg, _err, _trace

class Material:

    def __init__(self):
        self._manufacturer = ""
        self._name = ""
        self._type = MATERIAL_TYPE_BULK
        self._density = 0.0
        self._units = "g/cm3" # This should be changed?

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
        if not validNonEmptyString(self._name):
            return False
        if not validNonEmptyString(self._units):
            return False
        if self._type not in [MATERIAL_TYPE_BULK, MATERIAL_TYPE_SURFACE, MATERIAL_TYPE_LINE]:
            return False
        if self._density < 0.0:
            return False

        return True
