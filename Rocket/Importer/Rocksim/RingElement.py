# SPDX-License-Identifier: LGPL-2.1-or-later
# SPDX-FileCopyrightText: 2025 David Carter <dcarter@davidcarter.ca>
# SPDX-File-Notice: Part of the Rocket addon.


"""Provides support for importing Rocksim files."""

__title__ = "FreeCAD Rocksim Importer"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

from Rocket.Importer.Rocksim.ComponentElement import ComponentElement

from Ui.Commands.CmdBulkhead import makeBulkhead
from Ui.Commands.CmdCenteringRing import makeCenteringRing
from Ui.Commands.CmdBodyTube import makeCoupler, makeEngineBlock

class RingElement(ComponentElement):

    def __init__(self, parent, tag, attributes, parentObj, filename, line):
        super().__init__(parent, tag, attributes, parentObj, filename, line)

        self._knownTags.extend(["od", "id", "usagecode", "autosize", "attachedparts"])

        self._usageCode = 0
        self._outerDiameter = 0
        self._innerDiameter = 0
        self._length = 0
        self._thickness = 0
        self._locationMode = 0
        self._axialOffset = 0

        self._autoSize = False

    def makeObject(self):
        pass

    def handleEndTag(self, tag, content):
        _tag = tag.lower().strip()
        # print("RingElement handle tag " + _tag)
        if _tag == "od":
            self._outerDiameter = float(content)
        elif _tag == "id":
            self._innerDiameter = float(content)
        elif _tag == "usagecode":
            self._usageCode = int(content)
        elif _tag == "autosize":
            if int(content) != 0:
                self._autoSize = True
            else:
                self._autoSize = False
        else:
            super().handleEndTag(tag, content)

    def onLength(self, content):
        self._length = float(content)

    def onAxialOffset(self, content):
        self._axialOffset = float(content)

    def end(self):
        if self._innerDiameter > 0:
            self._thickness = (self._outerDiameter - self._innerDiameter) / 2.0

        # 0 == Centering Ring
		# 1 == Bulkhead
		# 2 == Engine Block
		# 3 == Sleeve
		# 4 == Tube Coupler
        if self._usageCode == 1:
            self.createBulkhead()
        elif self._usageCode == 2:
            self.createEngineBlock()
        # elif self._usageCode == 3:
        #     self.createSleeve()
        elif self._usageCode == 4:
            self.createTubeCoupler()
        else:
            self.createCenteringRing()

        return super().end()

    def onLocationMode(self, content):
        self._locationMode = int(content)

    def createBulkhead(self):
        self._feature = makeBulkhead()
        if self._parentObj:
            self._parentObj.addChild(self._feature)

        self._feature._obj.Diameter = self._outerDiameter
        self._feature._obj.AutoDiameter = self._autoSize
        self._feature._obj.Thickness = self._length

        self.setAxialOffset()
        super().onLocationMode(self._locationMode)

    def createEngineBlock(self):
        self._feature = makeEngineBlock()
        if self._parentObj:
            self._parentObj.addChild(self._feature)

        self._feature._obj.Diameter = self._outerDiameter
        self._feature._obj.AutoDiameter = self._autoSize
        self._feature._obj.Thickness = self._thickness
        self._feature._obj.Length = self._length

        self.setAxialOffset()
        super().onLocationMode(self._locationMode)

    def createTubeCoupler(self):
        self._feature = makeCoupler()
        if self._parentObj:
            self._parentObj.addChild(self._feature)

        self._feature._obj.Diameter = self._outerDiameter
        self._feature._obj.AutoDiameter = self._autoSize
        self._feature._obj.Thickness = self._thickness
        self._feature._obj.Length = self._length

        self.setAxialOffset()
        super().onLocationMode(self._locationMode)

    def createCenteringRing(self):
        self._feature = makeCenteringRing()
        if self._parentObj:
            self._parentObj.addChild(self._feature)

        self._feature._obj.Diameter = self._outerDiameter
        self._feature._obj.AutoDiameter = self._autoSize
        self._feature._obj.CenterDiameter = self._innerDiameter
        self._feature._obj.CenterAutoDiameter = self._autoSize
        self._feature._obj.Thickness = self._length

        self.setAxialOffset()
        super().onLocationMode(self._locationMode)

    def setAxialOffset(self):
        if hasattr(self._feature._obj, "Location"):
            self._feature._obj.Location = self._axialOffset
        if hasattr(self._feature._obj, "AxialOffset"):
            self._feature._obj.AxialOffset = self._axialOffset
