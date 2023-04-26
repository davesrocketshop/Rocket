# ***************************************************************************
# *   Copyright (c) 2021-2023 David Carter <dcarter@davidcarter.ca>         *
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
"""Provides support for importing Rocsim files."""

__title__ = "FreeCAD Rocsim Importer"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

import FreeCAD

from Rocket.Importer.Rocsim.PositionDependentElement import PositionDependentElement
from Rocket.Constants import FIN_TYPE_TUBE

from Ui.Commands.CmdFin import makeFin

class TubeFinElement(PositionDependentElement):

    def __init__(self, parent, tag, attributes, parentObj, filename, line):
        super().__init__(parent, tag, attributes, parentObj, filename, line)

        self._knownTags.extend(["radialangle", "len", "finishcode", "material", "od", "id", "tubecount",
                                "calcmass", "calccg", "radialloc", "serialno"])
        
        self._id = -1
        self._innerTube = False
        self._locationLoaded = False

    def makeObject(self):
        self._feature = makeFin()
        self._feature._obj.FinType = FIN_TYPE_TUBE
        if self._parentObj is not None:
            self._parentObj.addChild(self._feature)

    def handleEndTag(self, tag, content):
        _tag = tag.lower().strip()
        if _tag == "len":
            self._feature._obj.Length = FreeCAD.Units.Quantity(content + " mm").Value
        elif _tag == "id":
            self._id = FreeCAD.Units.Quantity(content + " mm").Value
        elif _tag == "od":
            self._feature._obj.TubeOuterDiameter = FreeCAD.Units.Quantity(content + " mm").Value
            self._feature._obj.TubeAutoOuterDiameter = False
        elif _tag == "tubecount":
            self._feature._obj.FinCount = int(content)
        elif _tag == "radialangle":
            rotation = FreeCAD.Units.Quantity(content + " rad").Value
            self._feature._obj.AngleOffset = rotation
        else:
            super().handleEndTag(tag, content)

    def end(self):
        # Validate the nose shape here
        if self._id > 0:
            thickness = (float(self._feature._obj.TubeOuterDiameter) - float(self._id)) / 2.0
            self._feature._obj.TubeThickness = thickness

        return super().end()
