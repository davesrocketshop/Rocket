# ***************************************************************************
# *   Copyright (c) 2021-2025 David Carter <dcarter@davidcarter.ca>         *
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
"""Class for drawing CFD Rockets"""

__title__ = "FreeCAD CFD Rocket"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

import FreeCAD
import MeshPart

from Rocket.Constants import FEATURE_CFD_ROCKET

from Rocket.cfd.parea import calculateProjectedArea

from DraftTools import translate

_linearDeflection = 0.5 # Linear deflection for a rough mesh with a fast calculation

def calcFrontalArea(shape):
    # Create a crude mesh and project it on to the YZ plane to caclulate the frontal area
    mesh = MeshPart.meshFromShape(shape, LinearDeflection=_linearDeflection)

    area = calculateProjectedArea(mesh)
    return area

class FeatureCFDRocket:

    def __init__(self, obj):
        # super().__init__(obj)
        self.Type = FEATURE_CFD_ROCKET
        self.version = '3.0'

        self._obj = obj
        obj.Proxy=self

        if not hasattr(obj,"Shape"):
            obj.addProperty('Part::PropertyPartShape', 'Shape', 'RocketComponent', translate('App::Property', 'Shape of the wind tunnel'))
        if not hasattr(obj,"AngleOfAttack"):
            obj.addProperty('App::PropertyAngle', 'AngleOfAttack', 'RocketComponent', translate('App::Property', 'Angle of attack in degrees')).AngleOfAttack = 0.0
        if not hasattr(obj,"AngleOfRotation"):
            obj.addProperty('App::PropertyAngle', 'AngleOfRotation', 'RocketComponent', translate('App::Property', 'Angle of rotation in degrees')).AngleOfRotation = 0.0

    def __getstate__(self):
        return self.Type, self.version

    def __setstate__(self, state):
        if state:
            self.Type = state[0]
            self.version = state[1]

    def onDocumentRestored(self, obj):
        FeatureCFDRocket(obj)
        self._obj = obj

    def calcFrontalArea(self):
        return calcFrontalArea(self._obj.Shape)

    def execute(self, obj):
        # shape = WindTunnelShapeHandler(obj)
        # if shape is not None:
        #     shape.draw()
        self.applyTranslations()

    def getCenter(self):
        box = self._obj.Shape.BoundBox
        center = box.XLength / 2.0

        return center

    def applyTranslations(self):
        center = self.getCenter()

        self._obj.Placement = FreeCAD.Placement()
        if self._obj.AngleOfRotation != 0.0:
            self._obj.Placement.rotate(FreeCAD.Vector(0, 0, 0),FreeCAD.Vector(1, 0, 0), self._obj.AngleOfRotation, comp=True)
        if self._obj.AngleOfAttack != 0.0:
            self._obj.Placement.rotate(FreeCAD.Vector(center, 0, 0),FreeCAD.Vector(0, 1, 0), self._obj.AngleOfAttack, comp=True)
        self._obj.Placement.move(FreeCAD.Vector(-center, 0, 0))
