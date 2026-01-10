# SPDX-License-Identifier: LGPL-2.1-or-later
# SPDX-FileCopyrightText: 2021 David Carter <dcarter@davidcarter.ca>
# SPDX-File-Notice: Part of the Rocket addon.


"""Class for drawing fins"""

__title__ = "FreeCAD Fins"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

from typing import Any

import FreeCAD
import Part
from Part import Wire

translate = FreeCAD.Qt.translate

from Rocket.Utilities import validationError

from Rocket.ShapeHandlers.FinShapeHandler import FinShapeHandler

class FinTubeShapeHandler(FinShapeHandler):

    def __init__(self, obj : Any) -> None:
        super().__init__(obj)

    def isValidShape(self) -> bool:
        # Add error checking here
        if self._obj.Ttw:
            validationError(translate('Rocket', "Ttw tabs are not supported for tube fins"))
            return False
        return super().isValidShape()

    def _finOnlyShape(self, debug : str) -> Any:
        #
        # Return the shape of a single fin with no additions, such as fin tabs, fin cans, etc
        #
        # This can be used to determine characteristics such as mass, cg, and volume
        radius = self._obj.TubeOuterDiameter / 2.0
        outer = Part.makeCylinder(radius, self._obj.RootChord, FreeCAD.Vector(0,0,0), FreeCAD.Vector(1,0,0))
        inner = Part.makeCylinder(radius - self._obj.TubeThickness, self._obj.RootChord, FreeCAD.Vector(0,0,0), FreeCAD.Vector(1,0,0))
        return outer.cut(inner)

    def _drawFinSet(self, offset : float = 0) -> Any:
        fins = []
        base = self._drawSingleFin()
        for i in range(self._obj.FinCount):
            fin = Part.Shape(base) # Create a copy
            fin.translate(FreeCAD.Vector(0,0,float(self._obj.ParentRadius) + float(self._obj.TubeOuterDiameter / 2.0)))
            fin.rotate(FreeCAD.Vector(0, 0, 0), FreeCAD.Vector(1,0,0), i * float(self._obj.FinSpacing))
            fins.append(fin)

        return Part.makeCompound(fins)

    def _makeAtHeightProfile(self, crossSection : str, height : float = 0.0, offset : float = 0.0) -> Wire:
        return None

    def _makeRootProfile(self, height : float = 0.0) -> Wire:
        return None
