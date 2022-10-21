# ***************************************************************************
# *   Copyright (c) 2022 David Carter <dcarter@davidcarter.ca>              *
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
"""Class for rocket assemblies"""

__title__ = "FreeCAD Rocket Assembly"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

from uuid import UUID, uuid4

class FlightConfigurationId():

    _key = None

    # Keys are generated differently in Python, so use the strings for these 
    # Java equivalents
    #
    # DEFAULT_MOST_SIG_BITS = 0xF4F2F1F0
    # ERROR_UUID = UUID( DEFAULT_MOST_SIG_BITS, 2489)
    # DEFAULT_VALUE_UUID = UUID( DEFAULT_MOST_SIG_BITS, 5676)
    
    ERROR_UUID = UUID("ffffffff-f4f2-f1f0-0000-0000000009b9")
    ERROR_KEY_NAME = "ErrorKey"
    DEFAULT_VALUE_UUID = UUID("ffffffff-f4f2-f1f0-0000-00000000162c")
    DEFAULT_VALUE_NAME = "DefaultKey"

    # builds the id with the given UUID object
    def FlightConfigurationId(self, uuid=None):
        if uuid is None:
            self._key = uuid4()
        else:
            self._key = uuid

    def isDefaultId(self):
        return self._key == self.DEFAULT_VALUE_UUID

    def hasError(self):
        return self._key == self.ERROR_UUID

    def isValid(self):
        return not self.hasError()

ERROR_FCID = FlightConfigurationId( FlightConfigurationId.ERROR_UUID)
DEFAULT_VALUE_FCID = FlightConfigurationId( FlightConfigurationId.DEFAULT_VALUE_UUID )
	