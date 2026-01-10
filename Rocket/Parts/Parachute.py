# SPDX-License-Identifier: LGPL-2.1-or-later
# SPDX-FileCopyrightText: 2021 David Carter <dcarter@davidcarter.ca>
# SPDX-File-Notice: Part of the Rocket addon.


"""Class for rocket part components"""

__title__ = "FreeCAD Open Rocket Part Parachute"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

from Rocket.Parts.Component import Component
from Rocket.Parts.Material import getMaterial, getMaterialAnyType
from Rocket.Parts.Exceptions import MaterialNotFoundError

from Rocket.Constants import MATERIAL_TYPE_LINE

class Parachute(Component):

    def __init__(self):
        super().__init__()

        self._diameter = (0.0, "")
        self._sides = 0
        self._lineCount = 0
        self._lineLength = (0.0, "")
        self._lineMaterial = ("", MATERIAL_TYPE_LINE)

    def validate(self):
        super().validate()

        self.validatePositive(self._diameter[0], "Diameter invalid")
        self.validateNonNegative(self._sides, "Sides invalid")  # Circular has zero sides
        self.validatePositive(self._lineCount, "Line Count invalid")
        self.validateNonNegative(self._lineLength[0], "Line Length invalid")

        self.validateNonEmptyString(self._lineMaterial[0], "Line Material invalid")
        self.validateNonEmptyString(self._diameter[1], "Diameter Units invalid '%s" % self._diameter[1])
        self.validateNonEmptyString(self._lineLength[1], "Line Length Units invalid '%s" % self._lineLength[1])
        if self._lineMaterial[1].lower() != MATERIAL_TYPE_LINE.lower():
            self.raiseInvalid("Line Material Units invalid '%s" % self._lineMaterial[1])

    def _getLineMaterial(self, connection):
        try:
            material_index = getMaterial(connection, self._manufacturer, self._lineMaterial[0], self._lineMaterial[1])
        except MaterialNotFoundError:
            try:
                print("Unable to find material for '%s':'%s' - setting to any type" % (self._manufacturer, self._lineMaterial[0]))
                material_index = getMaterialAnyType(connection, self._manufacturer, self._lineMaterial[0])
            except MaterialNotFoundError:
                print("Unable to find material for '%s':'%s' - setting to unspecified" % (self._manufacturer, self._lineMaterial[0]))
                material_index = getMaterial(connection, 'unspecified', 'unspecified', self._lineMaterial[1])

        return material_index

    def persist(self, connection):
        component_id = super().persist(connection)
        material_id = self._getLineMaterial(connection)

        cursor = connection.cursor()

        cursor.execute("INSERT INTO parachute (component_index, line_material_index, sides, lines, diameter, diameter_units, line_length, line_length_units) VALUES (?,?,?,?,?,?,?,?)",
                            (component_id, material_id, self._sides, self._lineCount, self._diameter[0], self._diameter[1], self._lineLength[0], self._lineLength[1]))
        id = cursor.lastrowid

        connection.commit()

        return id
