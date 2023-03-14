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
"""Provides support for importing Open Rocket files."""

__title__ = "FreeCAD Open Rocket Importer Common Component"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

from Rocket.Importer.OpenRocket.SaxElement import Element

class AppearanceElement(Element):

    def __init__(self, parent, tag, attributes, parentObj, filename, line):
        super().__init__(parent, tag, attributes, parentObj, filename, line)

        self._componentTags = ["paint", "ambient", "diffuse", "specular", "shine", "decal", "center", "offset", "scale"]

    def handleTag(self, tag, attributes):
        _tag = tag.lower().strip()
        if _tag == "paint":
            red, green, blue, alpha = self.getColor(attributes)
            self.onPaint(red, green, blue, alpha)
        if _tag == "ambient":
            red, green, blue, alpha = self.getColor(attributes)
            self.onAmbient(red, green, blue, alpha)
        if _tag == "diffuse":
            red, green, blue, alpha = self.getColor(attributes)
            self.onDiffuse(red, green, blue, alpha)
        if _tag == "specular":
            red, green, blue, alpha = self.getColor(attributes)
            self.onSpecular(red, green, blue, alpha)
        else:
            super().handleTag(tag, attributes)

    def handleEndTag(self, tag, content):
        _tag = tag.lower().strip()
        if _tag == "shine":
            self.onShine(content)
        else:
            super().handleEndTag(tag, content)

    def getColor(self, attributes):
        red = attributes["red"]
        green = attributes["green"]
        blue = attributes["blue"]
        alpha = 255
        if "alpha" in attributes:
            alpha = attributes["alpha"]

        return red, green, blue, alpha

    def onPaint(self, red, green, blue, alpha):
        if hasattr(self._parentObj, "setColor"):
            self._parentObj.setColor(int(red), int(green), int(blue), int(alpha))

    def onAmbient(self, red, green, blue, alpha):
        if hasattr(self._parentObj, "setAmbient"):
            self._parentObj.setAmbient(int(red), int(green), int(blue), int(alpha))

    def onDiffuse(self, red, green, blue, alpha):
        if hasattr(self._parentObj, "setDiffuse"):
            self._parentObj.setDiffuse(int(red), int(green), int(blue), int(alpha))

    def onSpecular(self, red, green, blue, alpha):
        if hasattr(self._parentObj, "setSpecular"):
            self._parentObj.setSpecular(int(red), int(green), int(blue), int(alpha))

    def onShine(self, content):
        if hasattr(self._parentObj, "setShininess"):
            self._parentObj.setShininess(float(content))
