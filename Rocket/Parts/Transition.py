# ***************************************************************************
# *   Copyright (c) 2021-2024 David Carter <dcarter@davidcarter.ca>         *
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

from Rocket.Parts.Component import Component
from Rocket.Constants import TYPE_CONE, TYPE_ELLIPTICAL, TYPE_HAACK, TYPE_OGIVE, TYPE_VON_KARMAN, TYPE_PARABOLA, TYPE_PARABOLIC, TYPE_POWER
from Rocket.Constants import STYLE_SOLID, STYLE_CAPPED
from Rocket.Parts.Exceptions import MultipleEntryError, NotFoundError

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

    def validate(self):
        super().validate()

        if self._noseType not in [TYPE_CONE.lower(), TYPE_ELLIPTICAL.lower(), TYPE_HAACK.lower(), TYPE_OGIVE.lower(), TYPE_VON_KARMAN.lower(), TYPE_PARABOLA.lower(), TYPE_PARABOLIC.lower(), TYPE_POWER.lower()]:
            self.raiseInvalid("Shape is invalid '%s'" % self._noseType)

        self.validateNonNegative(self._foreOutsideDiameter[0], "Fore Outside Diameter invalid")
        self.validateNonNegative(self._foreShoulderDiameter[0], "Fore Shoulder Diameter invalid")
        self.validateNonNegative(self._foreShoulderLength[0], "Fore Shoulder Length invalid")
        self.validateNonNegative(self._aftOutsideDiameter[0], "Aft Outside Diameter invalid")
        self.validateNonNegative(self._aftShoulderDiameter[0], "Aft Shoulder Diameter invalid")
        self.validateNonNegative(self._aftShoulderLength[0], "Aft Shoulder Length invalid")
        self.validatePositive(self._length[0], "Length invalid")

        if self._thickness[0] == 0.0:
            self._filled = True
        elif not self._filled:
            self.validatePositive(self._thickness[0], "Thickness invalid")

        self.validateNonEmptyString(self._foreOutsideDiameter[1], "Fore Outside Diameter Units invalid '%s" % self._foreOutsideDiameter[1])
        self.validateNonEmptyString(self._foreShoulderDiameter[1], "Fore Shoulder Diameter Units invalid '%s" % self._foreShoulderDiameter[1])
        self.validateNonEmptyString(self._foreShoulderLength[1], "Fore Shoulder Length Units invalid '%s" % self._foreShoulderLength[1])
        self.validateNonEmptyString(self._aftOutsideDiameter[1], "Aft Outside Diameter Units invalid '%s" % self._aftOutsideDiameter[1])
        self.validateNonEmptyString(self._aftShoulderDiameter[1], "Aft Shoulder Diameter Units invalid '%s" % self._aftShoulderDiameter[1])
        self.validateNonEmptyString(self._aftShoulderLength[1], "Aft Shoulder Length Units invalid '%s" % self._aftShoulderLength[1])
        self.validateNonEmptyString(self._length[1], "Length Units invalid '%s" % self._length[1])
        if not self._filled:
            self.validateNonEmptyString(self._thickness[1], "Thickness Units invalid '%s" % self._thickness[1])

    def _tranStyle(self):
        # Not enough information to fully determine core or hollow
        if self._filled or self._thickness == 0.0:
            return STYLE_SOLID
        return STYLE_CAPPED

    def persist(self, connection):
        style = self._tranStyle()

        component_id = super().persist(connection)

        cursor = connection.cursor()

        cursor.execute("""INSERT INTO transition (component_index, shape, style, 
                fore_outside_diameter, fore_outside_diameter_units, fore_shoulder_diameter, fore_shoulder_diameter_units, fore_shoulder_length, fore_shoulder_length_units,
                aft_outside_diameter, aft_outside_diameter_units, aft_shoulder_diameter, aft_shoulder_diameter_units, aft_shoulder_length, aft_shoulder_length_units,
                length, length_units, thickness, thickness_units)
            VALUES
                (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                    (component_id, self._noseType, style,
                    self._foreOutsideDiameter[0], self._foreOutsideDiameter[1], self._foreShoulderDiameter[0], self._foreShoulderDiameter[1], self._foreShoulderLength[0], self._foreShoulderLength[1],
                    self._aftOutsideDiameter[0], self._aftOutsideDiameter[1], self._aftShoulderDiameter[0], self._aftShoulderDiameter[1], self._aftShoulderLength[0], self._aftShoulderLength[1],
                    self._length[0], self._length[1], self._thickness[0], self._thickness[1]))
        id = cursor.lastrowid

        connection.commit()

        return id

def listTransitions(connection):
    cursor = connection.cursor()

    cursor.execute("""SELECT transition_index, manufacturer, part_number, description,
                        shape, length, length_units, 
                        fore_outside_diameter, fore_outside_diameter_units, fore_shoulder_diameter, fore_shoulder_diameter_units, fore_shoulder_length, fore_shoulder_length_units,
                        aft_outside_diameter, aft_outside_diameter_units, aft_shoulder_diameter, aft_shoulder_diameter_units, aft_shoulder_length, aft_shoulder_length_units
                    FROM component c, transition t WHERE t.component_index = c.component_index""")

    rows = cursor.fetchall()
    return rows

def getTransition(connection, index):
    cursor = connection.cursor()

    cursor.execute("""SELECT transition_index, c.manufacturer, part_number, description, material_name, uuid, mass, mass_units,
                        shape, style, length, length_units, thickness, thickness_units,
                        fore_outside_diameter, fore_outside_diameter_units, fore_shoulder_diameter, fore_shoulder_diameter_units, fore_shoulder_length, fore_shoulder_length_units,
                        aft_outside_diameter, aft_outside_diameter_units, aft_shoulder_diameter, aft_shoulder_diameter_units, aft_shoulder_length, aft_shoulder_length_units
                    FROM component c, transition t, material m WHERE t.component_index = c.component_index AND c.material_index = m.material_index AND t.transition_index = :index""", {
                        "index" : index
                    })

    rows = cursor.fetchall()
    if len(rows) < 1:
        raise NotFoundError()

    if len(rows) > 1:
        raise MultipleEntryError()

    return rows[0]
