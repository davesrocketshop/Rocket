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

__title__ = "FreeCAD Open Rocket Part Body Tube"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

from App.Parts.Component import Component
from App.Constants import TYPE_CONE, TYPE_ELLIPTICAL, TYPE_HAACK, TYPE_OGIVE, TYPE_VON_KARMAN, TYPE_PARABOLA, TYPE_PARABOLIC, TYPE_POWER
from App.Constants import STYLE_SOLID, STYLE_CAPPED
from App.Parts.Utilities import _err
from App.Parts.Exceptions import MultipleEntryError, NotFoundError

class NoseCone(Component):

    def __init__(self):
        super().__init__()

        self._noseType = "" # Shape
        self._filled = False

        self._outsideDiameter = (0.0, "")
        self._shoulderDiameter = (0.0, "")
        self._shoulderLength = (0.0, "")
        self._length = (0.0, "")
        self._thickness = (0.0, "")

    def validate(self):
        super().validate()

        if self._noseType not in [TYPE_CONE.lower(), TYPE_ELLIPTICAL.lower(), TYPE_HAACK.lower(), TYPE_OGIVE.lower(), TYPE_VON_KARMAN.lower(), TYPE_PARABOLA.lower(), TYPE_PARABOLIC.lower(), TYPE_POWER.lower()]:
            _err("NoseCone: Shape is invalid '%s'" % self._noseType)
            return False

        self.validatePositive(self._outsideDiameter[0], "Outside Diameter invalid")
        self.validateNonNegative(self._shoulderDiameter[0], "Shoulder Diameter invalid")
        self.validateNonNegative(self._shoulderLength[0], "Shoulder Length invalid")
        self.validatePositive(self._length[0], "Length invalid")
        if not self._filled:
            self.validatePositive(self._thickness[0], "Thickness invalid")

        self.validateNonEmptyString(self._outsideDiameter[1], "Outside Diameter Units invalid '%s" % self._outsideDiameter[1])
        self.validateNonEmptyString(self._shoulderDiameter[1], "Shoulder Diameter Units invalid '%s" % self._shoulderDiameter[1])
        self.validateNonEmptyString(self._shoulderLength[1], "Shoulder Length Units invalid '%s" % self._shoulderLength[1])
        self.validateNonEmptyString(self._length[1], "Length Units invalid '%s" % self._length[1])
        if not self._filled:
            self.validateNonEmptyString(self._thickness[1], "Thickness Units invalid '%s" % self._thickness[1])

    def _noseStyle(self):
        # Not enough information to fully determine core or hollow
        if self._filled or self._thickness == 0.0:
            return STYLE_SOLID
        return STYLE_CAPPED

    def persist(self, connection):
        style = self._noseStyle()

        component_id = super().persist(connection)

        cursor = connection.cursor()

        cursor.execute("""INSERT INTO nose (component_index, shape, style, diameter, diameter_units,
                length, length_units, thickness, thickness_units, shoulder_diameter, shoulder_diameter_units, shoulder_length, shoulder_length_units)
            VALUES
                (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                            (component_id, self._noseType, style, self._outsideDiameter[0], self._outsideDiameter[1], 
                            self._length[0], self._length[1], self._thickness[0], self._thickness[1],
                            self._shoulderDiameter[0], self._shoulderDiameter[1], self._shoulderLength[0], self._shoulderLength[1]))
        id = cursor.lastrowid

        connection.commit()

        return id

def listNoseCones(connection):
    cursor = connection.cursor()

    cursor.execute("""SELECT nose_index, manufacturer, part_number, description, shape, diameter, diameter_units, length, length_units, 
                        shoulder_diameter, shoulder_diameter_units, shoulder_length, shoulder_length_units
                    FROM component c, nose n WHERE n.component_index = c.component_index""")

    rows = cursor.fetchall()
    return rows

def getNoseCone(connection, index):
    cursor = connection.cursor()

    cursor.execute("""SELECT nose_index, c.manufacturer, part_number, description, material_name, mass, mass_units,
                        shape, style, diameter, diameter_units, length, length_units, thickness, thickness_units,
                        shoulder_diameter, shoulder_diameter_units, shoulder_length, shoulder_length_units
                    FROM component c, nose n, material m WHERE n.component_index = c.component_index AND c.material_index = m.material_index AND n.nose_index = :index""", {
                        "index" : index
                    })

    rows = cursor.fetchall()
    if len(rows) < 1:
        raise NotFoundError()

    if len(rows) > 1:
        raise MultipleEntryError()

    return rows[0]
