# ***************************************************************************
# *   Copyright (c) 2021-2025 David Carter <dcarter@davidcarter.ca>         *
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

from Rocket.Constants import MATERIAL_TYPE_BULK, MATERIAL_TYPE_SURFACE, MATERIAL_TYPE_LINE
from Rocket.Parts.Exceptions import InvalidError, MaterialNotFoundError, NotFoundError
from Rocket.Parts.Material import getMaterial, getMaterialAnyType

class Component:

    def __init__(self):
        self._manufacturer = ""
        self._partNumber = ""
        self._description = ""
        self._material = ("", MATERIAL_TYPE_BULK)
        self._mass = (0.0, "")

    def validateString(self, value, message):
        if value is None:
            self.raiseInvalid(message)

    def validateNonEmptyString(self, value, message):
        self.validateString(value, message)
        if len(str(value).strip()) <= 0:
            self.raiseInvalid(message)

    def validatePositive(self, value, message):
        if value <= 0.0:
            self.raiseInvalid(message)

    def validateNonNegative(self, value, message):
        if value < 0.0:
            self.raiseInvalid(message)

    def raiseInvalid(self, message):
        raise InvalidError(self._manufacturer, self._partNumber, message)

    def validate(self):
        self.validateString(self._manufacturer, "Manufacturer invalid")
        self.validateNonEmptyString(self._partNumber, "Part Number invalid")
        self.validateString(self._description, "Description invalid")

        if len(str(self._material[0]).strip()) == 0:
            self._material = ("Generic", self._material[1])
        if self._material[1] not in [MATERIAL_TYPE_BULK, MATERIAL_TYPE_SURFACE, MATERIAL_TYPE_LINE]:
            self.raiseInvalid("Material type invalid")

        self.validateNonNegative(self._mass[0], "_mass invalid")
        if self._mass[0] > 0.0: # No units required for 0 mass
            self.validateNonEmptyString(self._mass[1], "_mass units invalid")

    def persist(self, connection):
        material_index = -1
        try:
            # material_index = Materials.getMaterial(connection, self._manufacturer, self._material[0], self._material[1])
            material_index = getMaterial(connection, self._manufacturer, self._material[0], self._material[1])
        except MaterialNotFoundError:
            pass
        if material_index < 0:
            try:
                print("Unable to find material for '%s':'%s' - setting to any type" % (self._manufacturer, self._partNumber))
                material_index = getMaterialAnyType(connection, self._manufacturer, self._material[0])
            except MaterialNotFoundError:
                pass
        print(f"Material not found - using generic '{self._manufacturer}' '{self._material[0]}' '{self._material[1]}' ")
        if material_index < 0:
            try:
                print("Unable to find material for '%s':'%s' - setting to Generic" % (self._manufacturer, self._partNumber))
                material_index = getMaterial(connection, 'Generic', self._material[0], self._material[1])
            except MaterialNotFoundError:
                pass
        if material_index < 0:
            try:
                print("Unable to find material for '%s':'%s' - setting to Generic any type" % (self._manufacturer, self._partNumber))
                material_index = getMaterialAnyType(connection, 'Generic', self._material[1])
            except MaterialNotFoundError:
                pass

        cursor = connection.cursor()

        cursor.execute("INSERT INTO component (manufacturer, part_number, description, material_index, mass, mass_units) VALUES (?,?,?,?,?,?)",
                            (self._manufacturer, self._partNumber, self._description, material_index, self._mass[0], self._mass[1]))
        id = cursor.lastrowid

        connection.commit()

        return id

def getManufacturers(connection):
    cursor = connection.cursor()

    cursor.execute("SELECT DISTINCT manufacturer FROM component")

    rows = cursor.fetchall()
    if len(rows) < 1:
        raise NotFoundError()

    manufacturers = [row[0] for row in rows]
    return manufacturers
