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
"""Base class for rocket components"""

__title__ = "FreeCAD Open Rocket Component"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

from App.OpenRocket import _msg, _err, _trace

class Component:

    def __init__(self, doc):
        _trace(self.__class__.__name__, "__init__")

        self._doc = doc

        self._name = ""
        self._color = None
        self._linestyle = None
        self._position = None
        self._axialOffset = None
        self._overrideMass = None
        self._overrideCG = None
        self._overrideCD = None
        self._overrideSubcomponents = None
        self._comment = None
        self._preset = None

        self._subComponents = []

        self._axialPosition = 0 # is this redundant to _position?

    def append(self, subComponent):
        _trace(self.__class__.__name__, "append")

        self._subComponents.append(subComponent)

    def create(self, parent):
        """ Create the objects from the imported model """
        _trace(self.__class__.__name__, "create")

        for sub in self._subComponents:
            sub.create(parent)
        
    def calculatePosition(self, parentBase):
        _trace(self.__class__.__name__, "calculatePosition")

        self._axialPosition = parentBase

    def _fromOrkLength(self, length):
        """ Convert from an ORK length to a FreeCAD length """

        # ORK internal units are meters
        return length * 1000.0