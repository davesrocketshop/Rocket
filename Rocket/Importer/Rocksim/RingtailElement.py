# ***************************************************************************
# *   Copyright (c) 2025 David Carter <dcarter@davidcarter.ca>              *
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
"""Provides support for importing Rocksim files."""

__title__ = "FreeCAD Rocksim Importer"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

from Rocket.Importer.Rocksim.FinsetElement import FinsetElement
from Rocket.Constants import FIN_TYPE_TRAPEZOID

from Ui.Commands.CmdFin import makeFin
from Ui.Commands.CmdRingtail import makeRingtail

class RingtailElement(FinsetElement):

    def __init__(self, parent, tag, attributes, parentObj, filename, line):
        super().__init__(parent, tag, attributes, parentObj, filename, line)

        self._knownTags.extend(["od", "id", "tubedensity", "tubedensitytype", "tubematerial"])

        self._innerDiameter = 0
        self._outerDiameter = 0
        self._length = 0
        self._tubeDensity = 0
        self._tubeDensityType = ""
        self._tubeMaterial = ""


    def makeObject(self):
        self._feature = makeFin()
        self._feature._obj.FinType = FIN_TYPE_TRAPEZOID

        if self._parentObj:
            self._parentObj.addChild(self._feature)


    def handleEndTag(self, tag, content):
        _tag = tag.lower().strip()
        # print("RingtailElement handle tag " + _tag)
        if _tag == "od":
            self._outerDiameter = float(content)
        elif _tag == "id":
            self._innerDiameter = float(content)
        elif _tag == "tubedensity":
            self._tubeDensity = float(content)
        elif _tag == "tubedensitytype":
            self._tubeDensityType = self.densityType(int(content))
        elif _tag == "tubematerial":
            self._tubeMaterial = content
        else:
            super().handleEndTag(tag, content)

    def end(self):
        self._feature2 = makeRingtail()

        if self._feature:
            self._feature.addChild(self._feature2)

        self._feature2._obj.Diameter = self._outerDiameter
        self._feature2._obj.AutoDiameter = False
        self._feature2._obj.Thickness = (self._outerDiameter - self._innerDiameter) / 2.0
        self._feature2._obj.AutoLength = True

        self.setMaterial(self._feature2, self._tubeMaterial, self._tubeDensityType)

        if hasattr(self._feature2._obj.ViewObject, "ShapeAppearance"):
            self._feature2._obj.ViewObject.ShapeAppearance = self._appearance

        return super().end()
