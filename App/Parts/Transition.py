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

__title__ = "FreeCAD Open Rocket Part Transition"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

from App.Parts.Component import Component
from App.Constants import TYPE_CONE, TYPE_ELLIPTICAL, TYPE_HAACK, TYPE_OGIVE, TYPE_VON_KARMAN, TYPE_PARABOLA, TYPE_PARABOLIC, TYPE_POWER
from App.Tools.Utilities import _err

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

    def isValid(self):
        if not super().isValid():
            _err("Transition: super invalid")
            return False

        if self._noseType not in [TYPE_CONE.lower(), TYPE_ELLIPTICAL.lower(), TYPE_HAACK.lower(), TYPE_OGIVE.lower(), TYPE_VON_KARMAN.lower(), TYPE_PARABOLA.lower(), TYPE_PARABOLIC.lower(), TYPE_POWER.lower()]:
            _err("Transition: Shape is invalid '%s'" % self._noseType)
            return False

        if self._foreOutsideDiameter[0] <= 0.0:
            _err("Transition: _foreOutsideDiameter invalid")
            return False
        if self._foreShoulderDiameter[0] <= 0.0:
            _err("Transition: _foreShoulderDiameter invalid")
            return False
        if self._foreShoulderLength[0] <= 0.0:
            _err("Transition: _foreShoulderLength invalid")
            return False
        if self._aftOutsideDiameter[0] <= 0.0:
            _err("Transition: _aftOutsideDiameter invalid")
            return False
        if self._aftShoulderDiameter[0] <= 0.0:
            _err("Transition: _aftShoulderDiameter invalid")
            return False
        if self._aftShoulderLength[0] <= 0.0:
            _err("Transition: _aftShoulderLength invalid")
            return False
        if self._length[0] <= 0.0:
            _err("Transition: _length invalid")
            return False
        if self._thickness[0] <= 0.0 and not self._filled:
            _err("Transition: _thickness invalid")
            return False
        if not self.validNonEmptyString(self._foreOutsideDiameter[1]):
            _err("Transition: _foreOutsideDiameter Units invalid '%s" % self._foreOutsideDiameter[1])
            return False
        if not self.validNonEmptyString(self._foreShoulderDiameter[1]):
            _err("Transition: _foreShoulderDiameter Units invalid '%s" % self._foreShoulderDiameter[1])
            return False
        if not self.validNonEmptyString(self._foreShoulderLength[1]):
            _err("Transition: _foreShoulderLength Units invalid '%s" % self._foreShoulderLength[1])
            return False
        if not self.validNonEmptyString(self._aftOutsideDiameter[1]):
            _err("Transition: _aftOutsideDiameter Units invalid '%s" % self._aftOutsideDiameter[1])
            return False
        if not self.validNonEmptyString(self._aftShoulderDiameter[1]):
            _err("Transition: _aftShoulderDiameter Units invalid '%s" % self._aftShoulderDiameter[1])
            return False
        if not self.validNonEmptyString(self._aftShoulderLength[1]):
            _err("Transition: _aftShoulderLength Units invalid '%s" % self._aftShoulderLength[1])
            return False
        if not self.validNonEmptyString(self._length[1]):
            _err("Transition: _length Units invalid '%s" % self._length[1])
            return False
        if not self.validNonEmptyString(self._thickness[1]) and not self._filled:
            _err("Transition: _thickness Units invalid '%s" % self._thickness[1])
            return False

        return True
