# SPDX-License-Identifier: LGPL-2.1-or-later
# SPDX-FileCopyrightText: 2025 David Carter <dcarter@davidcarter.ca>
# SPDX-File-Notice: Part of the Rocket addon.


"""Provides support for importing Rocksim files."""

__title__ = "FreeCAD Rocksim Importer"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

import FreeCAD

from Rocket.Importer.Rocksim.FinsetElement import FinsetElement
from Rocket.Constants import FIN_TYPE_TUBE

from Ui.Commands.CmdFin import makeFin

class TubeFinsetElement(FinsetElement):

    def __init__(self, parent, tag, attributes, parentObj, filename, line):
        super().__init__(parent, tag, attributes, parentObj, filename, line)

        self._knownTags.extend(["tubecount", "od", "id", "mintubeangle", "maxtubesallowed"])

        self._innerDiameter = 0

    def makeObject(self):
        self._feature = makeFin()
        self._feature._obj.FinType = FIN_TYPE_TUBE

        if self._parentObj:
            self._parentObj.addChild(self._feature)


    def handleEndTag(self, tag, content):
        _tag = tag.lower().strip()
        # print("TubeFinsetElement handle tag " + _tag)
        if _tag == "tubecount":
            if int(content) > 1:
                self._feature._obj.FinSet = True
                self._feature._obj.FinCount = int(content)
                self._feature._obj.FinSpacing = 360.0 / int(content)
            else:
                self._feature._obj.FinSet = False
        elif _tag == "od":
            self._feature._obj.TubeAutoOuterDiameter = False
            self._feature._obj.TubeOuterDiameter = float(content)
        elif _tag == "id":
            self._innerDiameter = float(content)
        else:
            super().handleEndTag(tag, content)

    def end(self):
        if self._innerDiameter > 0:
            thickness = (float(self._feature._obj.TubeOuterDiameter.Value) - self._innerDiameter) / 2.0
            if thickness > 0:
                self._feature._obj.TubeThickness = thickness
        return super().end()
