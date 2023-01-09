# ***************************************************************************
# *   Copyright (c) 2022-2023 David Carter <dcarter@davidcarter.ca>         *
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
"""Interface for rocket components"""

__title__ = "FreeCAD Rocket Components"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

from abc import ABC, abstractmethod

class RadialParent(ABC):

    # Return the outer radius of the component at local coordinate <code>x</code>.
    # Values for <code>x < 0</code> and <code>x > getLengthAerodynamic()</code> are undefined.
    @abstractmethod
    def getOuterRadius(self, x):
        pass

    # Return the inner radius of the component at local coordinate <code>x</code>.
    # Values for <code>x < 0</code> and <code>x > getLengthAerodynamic()</code> are undefined.
    @abstractmethod
    def getInnerRadius(self, x):
        pass

    # Return the length of this component.
    @abstractmethod
    def getLength(self):
        pass
