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
"""Class for rocket motors"""

__title__ = "FreeCAD Rocket Motors"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"


from App.motor.Grain import Grain
from App.motor import geometry

from App.Constants import GRAIN_GEOMETRY_END

class EndBurningGrain(Grain):
    """Defines an end-burning grain, which is a simple cylinder that burns on one end."""

    def __init__(self, obj):
        super().__init__(obj)

        self._obj.GeometryName = GRAIN_GEOMETRY_END

    def onDocumentRestored(self, obj):
        super().onDocumentRestored(obj)
        
        # Add any missing attributes
        EndBurningGrain(obj)

    def getSurfaceAreaAtRegression(self, regDist):
        diameter = self._obj.Diameter
        return geometry.circleArea(diameter)

    def getVolumeAtRegression(self, regDist):
        bLength = self.getRegressedLength(regDist)
        diameter = self._obj.Diameter
        return geometry.cylinderVolume(diameter, bLength)

    def simulationSetup(self, config):
        pass

    def getWebLeft(self, regDist):
        return self.getRegressedLength(regDist)

    def getMassFlux(self, massIn, dTime, regDist, dRegDist, position, density):
        return 0

    def getPortArea(self, regDist):
        return None

    def getEndPositions(self, regDist):
        return (0, self._obj.Length - regDist)
