# ***************************************************************************
# *   Copyright (c) 2021-2023 David Carter <dcarter@davidcarter.ca>         *
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

__title__ = "FreeCAD Open Rocket Part Body Tube"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

from Rocket.Parts.Component import Component
from Rocket.Constants import STYLE_SOLID, STYLE_CAPPED
from Rocket.Parts.Exceptions import MultipleEntryError, NotFoundError

class RailButton(Component):

    def __init__(self):
        super().__init__()

        self._finish = ""

        self._outerDiameter = (0.0, "")
        self._innerDiameter = (0.0, "")
        self._height = (0.0, "")
        self._baseHeight = (0.0, "")
        self._flangeHeight = (0.0, "")
        self._screwHeight = (0.0, "")
        self._dragCoefficient = (0.0, "")
        self._screwMass = (0.0, "")
        self._nutMass = (0.0, "")
        self._screwDiameter = (0.0, "")
        self._countersinkDiameter = (0.0, "")
        self._countersinkAngle = (0.0, "")

    def validate(self):
        super().validate()

        # self._finish = ""

        self.validatePositive(self._outerDiameter[0], "Outer Diameter invalid")
        self.validatePositive(self._innerDiameter[0], "Inner Diameter invalid")
        self.validatePositive(self._height[0], "Height invalid")
        self.validatePositive(self._baseHeight[0], "Base Height invalid")
        self.validateNonNegative(self._flangeHeight[0], "Flange Height invalid")
        self.validateNonNegative(self._screwHeight[0], "Screw Height invalid")
        # self._dragCoefficient = (0.0, "")
        self.validateNonNegative(self._screwMass[0], "Srew Mass invalid")
        self.validateNonNegative(self._nutMass[0], "Nut Mass invalid")
        self.validateNonNegative(self._screwDiameter[0], "Screw Diameter invalid")
        self.validateNonNegative(self._countersinkDiameter[0], "Countersink DIameter invalid")
        self.validateNonNegative(self._countersinkAngle[0], "Countersink Angle invalid")

        self.validateNonEmptyString(self._outerDiameter[1], "Outer Diameter Units invalid '%s" % self._outerDiameter[1])
        self.validateNonEmptyString(self._innerDiameter[1], "Inner Diameter Units invalid '%s" % self._innerDiameter[1])
        self.validateNonEmptyString(self._height[1], "Height Units invalid '%s" % self._height[1])
        self.validateNonEmptyString(self._baseHeight[1], "Base Height Units invalid '%s" % self._baseHeight[1])
        self.validateNonEmptyString(self._flangeHeight[1], "Flange Height Units invalid '%s" % self._flangeHeight[1])
        self.validateNonEmptyString(self._screwHeight[1], "Screw Height Units invalid '%s" % self._screwHeight[1])
        self.validateNonEmptyString(self._screwMass[1], "Srew Mass Units invalid '%s" % self._screwMass[1])
        self.validateNonEmptyString(self._nutMass[1], "Nut Mass Units invalid '%s" % self._nutMass[1])
        self.validateNonEmptyString(self._screwDiameter[1], "Screw Diameter Units invalid '%s" % self._screwDiameter[1])
        self.validateNonEmptyString(self._countersinkDiameter[1], "Screw Diameter Units invalid '%s" % self._countersinkDiameter[1])

    def _noseStyle(self):
        # Not enough information to fully determine core or hollow
        if self._filled or self._thickness == 0.0:
            return STYLE_SOLID
        return STYLE_CAPPED

    def persist(self, connection):
        component_id = super().persist(connection)

        cursor = connection.cursor()

        cursor.execute("""INSERT INTO rail_button (component_index, finish, outer_diameter, outer_diameter_units, inner_diameter, inner_diameter_units, height, height_units,
                base_height, base_height_units, flange_height, flange_height_units, screw_height, screw_height_units, drag_coefficient, screw_mass, screw_mass_units,
                nut_mass, nut_mass_units, screw_diameter, screw_diameter_units, countersink_diameter, countersink_diameter_units, countersink_angle)
            VALUES
                (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                            (component_id, self._finish,
                            self._outerDiameter[0], self._outerDiameter[1],
                            self._innerDiameter[0], self._innerDiameter[1],
                            self._height[0], self._height[1],
                            self._baseHeight[0], self._baseHeight[1],
                            self._flangeHeight[0], self._flangeHeight[1],
                            self._screwHeight[0], self._screwHeight[1],
                            self._dragCoefficient[0],
                            self._screwMass[0], self._screwMass[1],
                            self._nutMass[0], self._nutMass[1],
                            self._screwDiameter[0], self._screwDiameter[1],
                            self._countersinkDiameter[0], self._countersinkDiameter[1],
                            self._countersinkAngle[0]))
        id = cursor.lastrowid

        connection.commit()

        return id

def listRailButton(connection):
    cursor = connection.cursor()

    cursor.execute("""SELECT rail_button_index, manufacturer, part_number, description,
                        finish, outer_diameter, outer_diameter_units, inner_diameter, inner_diameter_units, height, height_units,
                        base_height, base_height_units, flange_height, flange_height_units, screw_height, screw_height_units, drag_coefficient, screw_mass, screw_mass_units,
                        nut_mass, nut_mass_units, screw_diameter, screw_diameter_units, countersink_diameter, countersink_diameter_units, countersink_angle
                    FROM component c, rail_button b WHERE b.component_index = c.component_index""")

    rows = cursor.fetchall()
    return rows

def getRailButton(connection, index):
    cursor = connection.cursor()

    cursor.execute("""SELECT rail_button_index, c.manufacturer, part_number, description, material_name, mass, mass_units,
                        finish, outer_diameter, outer_diameter_units, inner_diameter, inner_diameter_units, height, height_units,
                        base_height, base_height_units, flange_height, flange_height_units, screw_height, screw_height_units, drag_coefficient, screw_mass, screw_mass_units,
                        nut_mass, nut_mass_units, screw_diameter, screw_diameter_units, countersink_diameter, countersink_diameter_units, countersink_angle
                    FROM component c, rail_button b, material m WHERE b.component_index = c.component_index AND c.material_index = m.material_index AND b.rail_button_index = :index""", {
                        "index" : index
                    })

    rows = cursor.fetchall()
    if len(rows) < 1:
        raise NotFoundError()

    if len(rows) > 1:
        raise MultipleEntryError()

    return rows[0]
