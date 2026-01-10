# SPDX-License-Identifier: LGPL-2.1-or-later
# SPDX-FileCopyrightText: 2021 David Carter <dcarter@davidcarter.ca>
# SPDX-File-Notice: Part of the Rocket addon.


"""Provides support for importing Open Rocket files."""

__title__ = "FreeCAD Open Rocket Importer"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

from Rocket.Importer.OpenRocket.SaxElement import NullElement
from Rocket.Importer.OpenRocket.RadiusRingComponentElement import RadiusRingComponentElement

from Ui.Commands.CmdBulkhead import makeBulkhead
from Ui.Commands.CmdCenteringRing import makeCenteringRing

class BulkheadElement(RadiusRingComponentElement):

    def __init__(self, parent, tag, attributes, parentObj, filename, line):
        super().__init__(parent, tag, attributes, parentObj, filename, line)

        self._shoulderCapped = False
        self._validChildren.update({ 'appearance' : NullElement, # Shouldn't be in there but it is
                              })

        self._knownTags.extend(["outerradius", "innerradius"])

    def makeObject(self):
        self._feature = makeBulkhead()
        if self._parentObj:
            self._parentObj.addChild(self._feature)

    def handleEndTag(self, tag, content):
        _tag = tag.lower().strip()
        if _tag == "outerradius":
            self._feature.setScratch("outerradius", content)
            if self.isAuto(content):
                diameter = "0.0"
                self._feature._obj.AutoDiameter = True
            else:
                diameter = float(content) * 2.0
                self._feature._obj.AutoDiameter = False
                self._feature._obj.Diameter = str(diameter) + "m"
        elif _tag == "innerradius":
            self._feature.setScratch("innerradius", content)
            if self.isAuto(content):
                diameter = "0.0"
                self._feature._obj.CenterAutoDiameter = True
            else:
                diameter = float(content) * 2.0
                self._feature._obj.CenterAutoDiameter = False
                self._feature._obj.CenterDiameter = str(diameter) + "m"
        else:
            super().handleEndTag(tag, content)

    def onName(self, content):
        self._feature.setName(content)

    def onLength(self, length):
        self._feature.setLength(length)

    def end(self):
        # Validate the shape here

        return super().end()

class CenteringRingElement(BulkheadElement):

    def makeObject(self):
        self._feature = makeCenteringRing()
        if self._parentObj:
            self._parentObj.addChild(self._feature)
