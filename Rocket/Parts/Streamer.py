# SPDX-License-Identifier: LGPL-2.1-or-later

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
"""Class for rocket part components"""

__title__ = "FreeCAD Open Rocket Part Streamer"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

from Rocket.Parts.Component import Component

class Streamer(Component):

    def __init__(self):
        super().__init__()

        self._length = (0.0, "")
        self._width = (0.0, "")
        self._thickness = (0.0, "")

    def validate(self):
        super().validate()

        self.validatePositive(self._length[0], "Length invalid")
        self.validatePositive(self._width[0], "Width invalid")
        self.validatePositive(self._thickness[0], "Thickness invalid")

        self.validateNonEmptyString(self._length[1], "Length units invalid '%s'" % self._length[1])
        self.validateNonEmptyString(self._width[1], "Width Units invalid '%s'" % self._width[1])
        self.validateNonEmptyString(self._thickness[1], "Thickness Units invalid '%s'" % self._thickness[1])

    def persist(self, connection):
        component_id = super().persist(connection)

        cursor = connection.cursor()

        cursor.execute("INSERT INTO streamer (component_index, length, length_units, width, width_units, thickness, thickness_units) VALUES (?,?,?,?,?,?,?)",
                            (component_id, self._length[0], self._length[1], self._width[0], self._width[1], self._thickness[0], self._thickness[1]))
        id = cursor.lastrowid

        connection.commit()

        return id
