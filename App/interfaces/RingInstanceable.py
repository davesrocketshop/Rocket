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

from abc import abstractmethod

from App.interfaces.Instanceable import Instanceable
from App.position.AnglePositionable import AnglePositionable
from App.position.RadiusPositionable import RadiusPositionable

class RingInstanceable(Instanceable, AnglePositionable, RadiusPositionable):

    @abstractmethod
    def getAngleOffset(self):
        pass

    @abstractmethod
    def setAngleOffset(self, angle):
        pass

    @abstractmethod
    def getAngleMethod(self):
        pass

    @abstractmethod
    def setAngleMethod(self, method):
        pass

    @abstractmethod
    def getInstanceAngleIncrement(self):
        pass

    @abstractmethod
    def getInstanceAngles(self):
        pass

    @abstractmethod
    def getRadiusOffset(self):
        pass

    @abstractmethod
    def setRadiusOffset(self, radius):
        pass

    @abstractmethod
    def getRadiusMethod(self):
        pass

    @abstractmethod
    def setRadiusMethod(self, method):
        pass

