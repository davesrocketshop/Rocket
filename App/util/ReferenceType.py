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
"""Class for rocket componentss"""

__title__ = "FreeCAD Rocket Components"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

from abc import ABC, abstractmethod
from App.Constants import DEFAULT_REFERENCE_LENGTH
from App.SymetricComponent import SymetricComponent

class ReferenceType(ABC):

    @abstractmethod
    def getReferenceLength(self, config):
        pass

class NoseConeReferenceType(ReferenceType):

    def getReferenceLength(self, config):
        for c in config.getActiveComponents():
            if isinstance(c, SymetricComponent):
                if c.getForeRadius() >= 0.0005:
                    return c.getForeRadius() * 2
                if c.getAftRadius() >= 0.0005:
                    return c.getAftRadius() * 2

        return DEFAULT_REFERENCE_LENGTH

class MaximumReferenceType(ReferenceType):

    def getReferenceLength(self, config):
        r = 0
        for c in config.getActiveComponents():
            if isinstance(c, SymetricComponent):
                r = max(r, c.getForeRadius())
                r = max(r, c.getAftRadius())

        r *= 2
        if r < 0.001:
            r = DEFAULT_REFERENCE_LENGTH
        
        return r

class CustomReferenceType(ReferenceType):

    def getReferenceLength(self, config):
        return config.getRocket().getCustomReferenceLength()

NOSECONE = NoseConeReferenceType()
MAXIMUM = MaximumReferenceType()
CUSTOM = CustomReferenceType()
