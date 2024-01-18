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

__title__ = "FreeCAD Open Rocket Part Body Tube"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

from Rocket.Parts.Component import Component
from Rocket.Parts.Exceptions import MultipleEntryError, NotFoundError
from Rocket.Constants import COMPONENT_TYPE_ANY, COMPONENT_TYPE_BODYTUBE, COMPONENT_TYPE_COUPLER, \
    COMPONENT_TYPE_LAUNCHLUG, COMPONENT_TYPE_ENGINEBLOCK, COMPONENT_TYPE_CENTERINGRING, COMPONENT_TYPE_BULKHEAD

class BodyTube(Component):

    def __init__(self):
        super().__init__()

        self._ID = (0.0, "")
        self._OD = (0.0, "")
        self._length = (0.0, "")
        self._tubeType = "body tube" # Used to support multiple components

    def validate(self):
        super().validate()

        # This should be positive, but some tube couplers are actually thick bulkheads
        self.validateNonNegative(self._ID[0], "ID invalid")

        self.validatePositive(self._OD[0], "OD invalid")
        self.validatePositive(self._length[0], "Length invalid")

        self.validateNonEmptyString(self._ID[1], "ID Units invalid '%s" % self._ID[1])
        self.validateNonEmptyString(self._OD[1], "OD Units invalid '%s" % self._OD[1])
        self.validateNonEmptyString(self._length[1], "Length Units invalid '%s" % self._length[1])

    def persist(self, connection):
        component_id = super().persist(connection)

        # May throw a NotFoundError
        tube_id = getTubeType(connection, self._tubeType)

        cursor = connection.cursor()

        cursor.execute("INSERT INTO body_tube (component_index, tube_type_index, inner_diameter, inner_diameter_units, outer_diameter, outer_diameter_units, length, length_units) VALUES (?,?,?,?,?,?,?,?)",
                            (component_id, tube_id, self._ID[0], self._ID[1], self._OD[0], self._OD[1], self._length[0], self._length[1]))
        id = cursor.lastrowid

        connection.commit()

        return id

def getTubeType(connection, tubeType):
    cursor = connection.cursor()

    alias = {
        'body tube': COMPONENT_TYPE_BODYTUBE,
        'coupler': COMPONENT_TYPE_COUPLER,
        'launch lug': COMPONENT_TYPE_LAUNCHLUG,
        'engine block': COMPONENT_TYPE_ENGINEBLOCK,
        'centering ring': COMPONENT_TYPE_CENTERINGRING,
        'bulkhead' : COMPONENT_TYPE_BULKHEAD
    }

    cursor.execute("SELECT tube_type_index FROM tube_type WHERE type=:type", {
                        "type" : alias[tubeType]
                    })

    rows = cursor.fetchall()
    if len(rows) < 1:
        raise NotFoundError("Tube type %s not found" % tubeType)

    return rows[0]['tube_type_index']

def listBodyTubes(connection, tubeType=None):
    cursor = connection.cursor()

    if tubeType is None or tubeType == COMPONENT_TYPE_ANY:
        cursor.execute("""SELECT body_tube_index, type, manufacturer, part_number, description, inner_diameter, inner_diameter_units, 
                            outer_diameter, outer_diameter_units, length, length_units
                        FROM component c, body_tube b, tube_type t
                        WHERE b.component_index = c.component_index AND b.tube_type_index = t.tube_type_index
                            AND NOT t.type = 'Centering Ring' AND NOT t.type = 'Bulkhead'""")
    else:
        cursor.execute("""SELECT body_tube_index, type, manufacturer, part_number, description, inner_diameter, inner_diameter_units, 
                            outer_diameter, outer_diameter_units, length, length_units
                        FROM component c, body_tube b, tube_type t 
                        WHERE b.component_index = c.component_index AND b.tube_type_index = t.tube_type_index AND t.type = :type""", {
                            "type" : tubeType
                        })

    rows = cursor.fetchall()
    return rows

def getBodyTube(connection, index):
    cursor = connection.cursor()

    cursor.execute("""SELECT body_tube_index, c.manufacturer, part_number, description, material_name, mass, mass_units,
                        inner_diameter, inner_diameter_units, outer_diameter, outer_diameter_units, length, length_units
                    FROM component c, body_tube b, material m WHERE b.component_index = c.component_index AND c.material_index = m.material_index AND b.body_tube_index = :index""", {
                        "index" : index
                    })

    rows = cursor.fetchall()
    if len(rows) < 1:
        raise NotFoundError()

    if len(rows) > 1:
        raise MultipleEntryError()

    return rows[0]
