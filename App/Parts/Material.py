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
from App.Constants import MATERIAL_TYPE_BULK, MATERIAL_TYPE_SURFACE, MATERIAL_TYPE_LINE
from App.Parts.Exceptions import InvalidError, MultipleEntryError

class Material:

    def __init__(self):
        self._manufacturer = ""
        self._name = ""
        self._type = MATERIAL_TYPE_BULK
        self._density = 0.0
        self._units = "g/cm3" # This should be changed?

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
        raise InvalidError(self._manufacturer, self._name, message)

    def validate(self):
        self.validateString(self._manufacturer, "Manufacturer invalid")
        self.validateNonEmptyString(self._name, "Name invalid")
        self.validateNonEmptyString(self._units, "Units invalid")
        if self._type not in [MATERIAL_TYPE_BULK, MATERIAL_TYPE_SURFACE, MATERIAL_TYPE_LINE]:
            self.raiseInvalid(message)
        self.validateNonNegative(self._density, "Material type invalid")

    def persist(self, connection):
        cursor = connection.cursor()

        # Check to see if an entry exists
        cursor.execute("SELECT * FROM material WHERE name = ? AND  type = ?",
                            (self._name, self._type))
        row = cursor.fetchone()
        if row is not None:
            # See if this is a complete duplicate
            if row['density'] == self._density and row['units'] == self._units:
                return row['material_index']

            raise MultipleEntryError("Material database contains multiple entries for name:'%s', type:'%s'" % (self._name, self._type))

        cursor.execute("INSERT INTO material(name, type, density, units) VALUES (:name,:type,:density,:units)",
                            {"name" : self._name, 
                             "type" : self._type,
                             "density" : self._density,
                             "units" : self._units})
        id = cursor.lastrowid

        connection.commit()
        return id

    def getMaterial(connection, name, type):
        cursor = connection.cursor()

        cursor.execute("SELECT material_index FROM material WHERE name = ? AND  type = ?",
                            (name, type))

        rows = cursor.fetchall()
        if len(rows) < 1:
            print("Material '%s' of type '%s' not found" % (name, type))
            return 0

        if len(rows) > 1:
            print("%d rows found!" % len(rows))        
            cursor.execute("SELECT * FROM material WHERE name = ? AND  type = ?",
                            (name, type))
            rows = cursor.fetchall()
            i = 0
            for row in rows:
                print("%d: %s" % (i, str(row)))
                i += 1

        return rows[0]['material_index']
