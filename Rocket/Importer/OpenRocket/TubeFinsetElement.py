# SPDX-License-Identifier: LGPL-2.1-or-later

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
"""Provides support for importing Open Rocket files."""

__title__ = "FreeCAD Open Rocket Importer"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

import FreeCAD

from Rocket.Importer.OpenRocket.FinsetElement import FinsetElement
from Rocket.Constants import FIN_TYPE_TUBE

from Ui.Commands.CmdFin import makeFin

class TubeFinsetElement(FinsetElement):

    def __init__(self, parent, tag, attributes, parentObj, filename, line):
        super().__init__(parent, tag, attributes, parentObj, filename, line)

        self._knownTags = ["fincount", "rotation", "thickness", "length", "radius", "instancecount", "angleoffset", "radiusoffset"]

    def makeObject(self):
        self._feature = makeFin()
        self._feature._obj.FinType = FIN_TYPE_TUBE

        if self._parentObj:
            self._parentObj.addChild(self._feature)


    def handleEndTag(self, tag, content):
        _tag = tag.lower().strip()
        if _tag == "fincount":
            if int(content) > 1:
                self._feature._obj.FinSet = True
                self._feature._obj.FinCount = int(content)
                self._feature._obj.FinSpacing = 360.0 / int(content)
            else:
                self._feature._obj.FinSet = False
        elif _tag == "rotation":
            pass
        elif _tag == "thickness":
            thickness = FreeCAD.Units.Quantity(content + " m").Value
            self._feature._obj.TubeThickness = thickness
        elif _tag == "length":
            self._feature._obj.RootChord = FreeCAD.Units.Quantity(content + " m").Value
        elif _tag == "radius":
            if self.isAuto(content):
                self._feature._obj.TubeAutoOuterDiameter = True
            else:
                self._feature._obj.TubeAutoOuterDiameter = False
                radius = FreeCAD.Units.Quantity(content + " m").Value
                self._feature._obj.TubeOuterDiameter = 2.0 * radius
        elif _tag == "instancecount":
            pass
        elif _tag == "angleoffset":
            pass
        elif _tag == "radiusoffset":
            pass
        else:
            super().handleEndTag(tag, content)

    def end(self):
        return super().end()
