# SPDX-License-Identifier: LGPL-2.1-or-later
# SPDX-FileCopyrightText: 2021 David Carter <dcarter@davidcarter.ca>
# SPDX-File-Notice: Part of the Rocket addon.


"""Provides support for importing Open Rocket files."""

__title__ = "FreeCAD Open Rocket Importer Common Component"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

import FreeCAD

from Rocket.Importer.OpenRocket.SaxElement import Element

class AppearanceElement(Element):

    def __init__(self, parent, tag, attributes, parentObj, filename, line):
        super().__init__(parent, tag, attributes, parentObj, filename, line)

        self._componentTags = ["paint", "ambient", "diffuse", "specular", "shine", "decal", "center", "offset", "scale"]

    def handleTag(self, tag, attributes):
        _tag = tag.lower().strip()
        if _tag == "paint":
            self.onPaint(self.getColor(attributes))
        if _tag == "ambient":
            self.onAmbient(self.getColor(attributes))
        if _tag == "diffuse":
            self.onDiffuse(self.getColor(attributes))
        if _tag == "specular":
            self.onSpecular(self.getColor(attributes))
        else:
            super().handleTag(tag, attributes)

    def handleEndTag(self, tag, content):
        _tag = tag.lower().strip()
        if _tag == "shine":
            self.onShine(content)
        else:
            super().handleEndTag(tag, content)

    def getColor(self, attributes):
        red = int(attributes["red"])
        green = int(attributes["green"])
        blue = int(attributes["blue"])
        alpha = 255
        if "alpha" in attributes:
            alpha = int(attributes["alpha"])

        color = (red / 255.0, green / 255.0, blue / 255.0, alpha / 255.0)
        return color

    def createAppearance(self):
        if self._parent._deferredAppearance is None:
            self._parent._deferredAppearance = FreeCAD.Material()

    def onPaint(self, color):
        self.onDiffuse(color)

    def onAmbient(self, color):
        self.createAppearance()
        self._parent._deferredAppearance.AmbientColor = color

    def onDiffuse(self, color):
        self.createAppearance()
        self._parent._deferredAppearance.DiffuseColor = color

    def onSpecular(self, color):
        self.createAppearance()
        self._parent._deferredAppearance.SpecularColor = color

    def onShine(self, content):
        self.createAppearance()
        self._parent._deferredAppearance.Shininess = float(content)
