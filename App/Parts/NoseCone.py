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
from App.Tools.Utilities import _err

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

