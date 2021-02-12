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

__title__ = "FreeCAD Open Rocket Part Streamer"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

from App.Parts.Component import Component
from App.Tools.Utilities import _err

class Streamer(Component):

    def __init__(self):
        super().__init__()

        self._length = (0.0, "")
        self._width = (0.0, "")
        self._thickness = (0.0, "")

    def isValid(self):
        if not super().isValid():
            _err("Streamer: super invalid")
            return False

        if self._length[0] <= 0.0:
            _err("Streamer: _length invalid")
            return False
        if self._width[0] <= 0.0:
            _err("Streamer: _width invalid")
            return False
        if self._thickness[0] <= 0.0:
            _err("Streamer: _thickness invalid")
            return False
        if not self.validNonEmptyString(self._length[1]):
            _err("Streamer: _length units invalid '%s'" % self._length[1])
            return False
        if not self.validNonEmptyString(self._width[1]):
            _err("Streamer: _width Units invalid '%s'" % self._width[1])
            return False
        if not self.validNonEmptyString(self._thickness[1]):
            _err("Streamer: _thickness Units invalid '%s'" % self._lineLength[1])
            return False

        return True
