# ***************************************************************************
# *   Copyright (c) 2025 David Carter <dcarter@davidcarter.ca>              *
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

__title__ = "FreeCAD Open Rocket Part Retainer"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

from Rocket.Parts.Component import Component
from Rocket.Constants import RETAINER_TUBE_MOUNT, RETAINER_FLANGE_MOUNT, RETAINER_TAILCONE
from Rocket.Parts.Exceptions import MultipleEntryError, NotFoundError

class Retainer(Component):

    def __init__(self):
        super().__init__()

        self._innerDiameter = (0.0, "")
        self._outerDiameter = (0.0, "")
        self._mmtDepth = (0.0, "")
        self._capDiameter = (0.0, "")
        self._capHeight = (0.0, "")
        self._heightWithAC = (0.0, "")
        self._heightWithSR = (0.0, "")
        self._flangeDiameter = (0.0, "")
        self._screwholePattern = (0.0, "")
        self._screwCount = 0
        self._screwSize = ""
        self._coneDiameterLarge = (0.0, "")
        self._coneDiameterSmall = (0.0, "")
        self._openDiameterSmall = (0.0, "")
        self._length = (0.0, "")
        self._airframeToMMT = (0.0, "")
        self._lip = (0.0, "")
        self._mass = (0.0, "")

    def validate(self):
        super().validate()

        style = self._retainerStyle()
        if style == RETAINER_TUBE_MOUNT:
            self._validateTubeMount()
        elif style == RETAINER_FLANGE_MOUNT:
            self._validateFlangeMount()
        else:
            self._validateTailcone()

    def _validateTubeMount(self):
        self.validatePositive(self._innerDiameter[0], "Inside Diameter invalid")
        self.validatePositive(self._outerDiameter[0], "Outside Diameter invalid")
        self.validatePositive(self._mmtDepth[0], "Motor mount depth invalid")
        self.validatePositive(self._capDiameter[0], "Cap Diameter invalid")
        self.validatePositive(self._capHeight[0], "Cap height invalid")
        self.validatePositive(self._heightWithAC[0], "Height with aft closure invalid")

        self.validateNonEmptyString(self._innerDiameter[1], "Inside Diameter Units invalid '%s" % self._innerDiameter[1])
        self.validateNonEmptyString(self._outerDiameter[1], "Outside Diameter Units invalid '%s" % self._outerDiameter[1])
        self.validateNonEmptyString(self._mmtDepth[1], "Motor mount depth invalid '%s" % self._mmtDepth[1])
        self.validateNonEmptyString(self._capDiameter[1], "Cap Diameter Units invalid '%s" % self._capDiameter[1])
        self.validateNonEmptyString(self._capHeight[1], "Cap height Units invalid '%s" % self._capHeight[1])
        self.validateNonEmptyString(self._heightWithAC[1], "Height with aft closure Units invalid '%s" % self._heightWithAC[1])


    def _validateFlangeMount(self):
        self.validatePositive(self._outerDiameter[0], "Outside Diameter invalid")
        self.validatePositive(self._capDiameter[0], "Cap Diameter invalid")
        self.validatePositive(self._capHeight[0], "Cap height invalid")
        self.validatePositive(self._heightWithAC[0], "Height with aft closure invalid")
        self.validateNonNegative(self._heightWithSR[0], "Height with snap ring invalid")
        self.validatePositive(self._flangeDiameter[0], "Flange Diameter invalid")
        self.validatePositive(self._screwholePattern[0], "Screw hole pattern invalid")
        self.validatePositive(self._screwCount, "Screw count invalid")
        self.validateNonEmptyString(self._screwSize, "Screw size invalid")

        self.validateNonEmptyString(self._outerDiameter[1], "Outside Diameter Units invalid '%s" % self._outerDiameter[1])
        self.validateNonEmptyString(self._capDiameter[1], "Cap Diameter Units invalid '%s" % self._capDiameter[1])
        self.validateNonEmptyString(self._capHeight[1], "Cap height Units invalid '%s" % self._capHeight[1])
        self.validateNonEmptyString(self._heightWithAC[1], "Height with aft closure Units invalid '%s" % self._heightWithAC[1])
        # self.validateNonEmptyString(self._heightWithSR[1], "Height with snap ring Units invalid '%s" % self._heightWithSR[1])
        self.validateNonEmptyString(self._flangeDiameter[1], "Flang Diameter Units invalid '%s" % self._flangeDiameter[1])
        self.validateNonEmptyString(self._screwholePattern[1], "Screw hole pattern Units invalid '%s" % self._screwholePattern[1])

    def _validateTailcone(self):
        self.validatePositive(self._innerDiameter[0], "Inside Diameter invalid")
        self.validatePositive(self._mmtDepth[0], "Motor mount depth invalid")
        self.validatePositive(self._coneDiameterLarge[0], "Large cone diameter invalid")
        self.validatePositive(self._coneDiameterSmall[0], "Small cone diameter invalid")
        self.validatePositive(self._openDiameterSmall[0], "Small opening diameter invalid")
        self.validatePositive(self._length[0], "Length invalid")
        self.validatePositive(self._airframeToMMT[0], "Airframe to motor mount invalid")
        self.validatePositive(self._lip[0], "Lip invalid")

        self.validateNonEmptyString(self._innerDiameter[1], "Inside Diameter Units invalid '%s" % self._innerDiameter[1])
        self.validateNonEmptyString(self._mmtDepth[1], "Motor Mount Depth Units invalid '%s" % self._mmtDepth[1])
        self.validateNonEmptyString(self._coneDiameterLarge[1], "Large Cone Diameter Units invalid '%s" % self._coneDiameterLarge[1])
        self.validateNonEmptyString(self._coneDiameterSmall[1], "Small Cone Diameter Units invalid '%s" % self._coneDiameterSmall[1])
        self.validateNonEmptyString(self._openDiameterSmall[1], "Small Opening Diameter Units invalid '%s" % self._openDiameterSmall[1])
        self.validateNonEmptyString(self._length[1], "Length Units invalid '%s" % self._length[1])
        self.validateNonEmptyString(self._airframeToMMT[1], "Airfram to Motor Mount Units invalid '%s" % self._airframeToMMT[1])
        self.validateNonEmptyString(self._lip[1], "Lip Units invalid '%s" % self._lip[1])

    def _retainerStyle(self):
        # Not enough information to fully determine core or hollow
        if self._flangeDiameter[0] > 0:
            return RETAINER_FLANGE_MOUNT
        if self._coneDiameterLarge[0] > 0:
            return RETAINER_TAILCONE
        return RETAINER_TUBE_MOUNT

    def persist(self, connection):
        style = self._retainerStyle()

        component_id = super().persist(connection)

        cursor = connection.cursor()

        cursor.execute("""INSERT INTO retainer (component_index, style,
                inner_diameter, inner_diameter_units, outer_diameter, outer_diameter_units,
                mmt_depth, mmt_depth_units, cap_diameter, cap_diameter_units, cap_height, cap_height_units,
                height_with_ac, height_with_ac_units, height_with_sr, height_with_sr_units,
                flange_diameter, flange_diameter_units, screwhole_pattern, screwhole_pattern_units,
                screw_count, screw_size, cone_diameter_large, cone_diameter_large_units,
                cone_diameter_small, cone_diameter_small_units, open_diameter_small, open_diameter_small_units,
                length, length_units, airframe_to_mmt, airframe_to_mmt_units, lip, lip_units,
                mass, mass_units)
            VALUES
                (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                            (component_id, style,
                             self._innerDiameter[0], self._innerDiameter[1],
                             self._outerDiameter[0], self._outerDiameter[1],
                             self._mmtDepth[0], self._mmtDepth[1],
                             self._capDiameter[0], self._capDiameter[1],
                             self._capHeight[0], self._capHeight[1],
                             self._heightWithAC[0], self._heightWithAC[1],
                             self._heightWithSR[0], self._heightWithSR[1],
                             self._flangeDiameter[0], self._flangeDiameter[1],
                             self._screwholePattern[0], self._screwholePattern[1],
                             self._screwCount, self._screwSize,
                             self._coneDiameterLarge[0], self._coneDiameterLarge[1],
                             self._coneDiameterSmall[0], self._coneDiameterSmall[1],
                             self._openDiameterSmall[0], self._openDiameterSmall[1],
                             self._length[0], self._length[1],
                             self._airframeToMMT[0], self._airframeToMMT[1],
                             self._lip[0], self._lip[1],
                             self._mass[0], self._mass[1]))
        id = cursor.lastrowid

        connection.commit()

        return id

def listRetainers(connection):
    cursor = connection.cursor()

    cursor.execute("""SELECT retainer_index, manufacturer, part_number, description, style,
                        inner_diameter, inner_diameter_units, outer_diameter, outer_diameter_units,
                        mmt_depth, mmt_depth_units, cap_diameter, cap_diameter_units, cap_height, cap_height_units,
                        height_with_ac, height_with_ac_units, height_with_sr, height_with_sr_units,
                        flange_diameter, flange_diameter_units, screwhole_pattern, screwhole_pattern_units,
                        screw_count, screw_size, cone_diameter_large, cone_diameter_large_units,
                        cone_diameter_small, cone_diameter_small_units, open_diameter_small, open_diameter_small_units,
                        length, length_units, airframe_to_mmt, airframe_to_mmt_units, lip, lip_units,
                        mass, mass_units
                    FROM component c, retainer r WHERE r.component_index = c.component_index""")

    rows = cursor.fetchall()
    return rows

# def listNoseConesBySize(connection, minDiameter, maxDiameter, minLength, maxLength):
#     cursor = connection.cursor()

#     where = ""
#     if minDiameter:
#         where += f" AND n.normalized_diameter >= {minDiameter}"

#     if maxDiameter:
#         where += f" AND n.normalized_diameter <= {maxDiameter}"

#     if minLength:
#         where += f" AND n.normalized_length >= {minLength}"

#     if maxLength:
#         where += f" AND n.normalized_length <= {maxLength}"

#     cursor.execute("""SELECT nose_index, manufacturer, part_number, description, shape, diameter, diameter_units, length, length_units,
#                         shoulder_diameter, shoulder_diameter_units, shoulder_length, shoulder_length_units, normalized_diameter, normalized_length
#                     FROM component c, nose n WHERE n.component_index = c.component_index""" + where)

#     rows = cursor.fetchall()
#     return rows

def getRetainer(connection, index):
    cursor = connection.cursor()

    cursor.execute("""SELECT retainer_index, manufacturer, part_number, description, style,
                        inner_diameter, inner_diameter_units, outer_diameter, outer_diameter_units,
                        mmt_depth, mmt_depth_units, cap_diameter, cap_diameter_units, cap_height, cap_height_units,
                        height_with_ac, height_with_ac_units, height_with_sr, height_with_sr_units,
                        flange_diameter, flange_diameter_units, screwhole_pattern, screwhole_pattern_units,
                        screw_count, screw_size, cone_diameter_large, cone_diameter_large_units,
                        cone_diameter_small, cone_diameter_small_units, open_diameter_small, open_diameter_small_units,
                        length, length_units, airframe_to_mmt, airframe_to_mmt_units, lip, lip_units,
                        mass, mass_units
                    FROM component c, retainer r, material m WHERE r.component_index = c.component_index AND c.material_index = m.material_index AND r.retainer_index = :index""", {
                        "index" : index
                    })

    rows = cursor.fetchall()
    if len(rows) < 1:
        raise NotFoundError()

    if len(rows) > 1:
        raise MultipleEntryError()

    return rows[0]
