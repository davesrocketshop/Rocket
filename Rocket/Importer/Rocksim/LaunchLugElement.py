# SPDX-License-Identifier: LGPL-2.1-or-later
# SPDX-FileCopyrightText: 2025 David Carter <dcarter@davidcarter.ca>
# SPDX-File-Notice: Part of the Rocket addon.


"""Provides support for importing Rocksim files."""

__title__ = "FreeCAD Rocksim Importer"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

from Rocket.Importer.Rocksim.ComponentElement import ComponentElement

from Ui.Commands.CmdLaunchGuides import makeLaunchLug

class LaunchLugElement(ComponentElement):

    def __init__(self, parent, tag, attributes, parentObj, filename, line):
        super().__init__(parent, tag, attributes, parentObj, filename, line)

        self._knownTags.extend(["od", "id", "attachedparts"])

        self._innerDiameter = 0

    def makeObject(self):
        self._feature = makeLaunchLug()
        if self._parentObj:
            self._parentObj.addChild(self._feature)

    def handleEndTag(self, tag, content):
        _tag = tag.lower().strip()
        # print("LaunchLugElement handle tag " + _tag)
        if _tag == "od":
            self._feature._obj.Diameter = float(content)
        elif _tag == "id":
            self._innerDiameter = float(content)
        else:
            super().handleEndTag(tag, content)

    def onLength(self, content):
        if hasattr(self._feature, "setLength"):
            self._feature.setLength(content)

    def onThickness(self, content):
        if hasattr(self._feature, "setThickness"):
            self._feature.setThickness(content)

    def end(self):
        if self._innerDiameter > 0:
            thickness = (float(self._feature._obj.Diameter.Value) - self._innerDiameter) / 2.0
            if thickness > 0:
                self.onThickness(thickness)
        return super().end()
