# SPDX-License-Identifier: LGPL-2.1-or-later
# SPDX-FileCopyrightText: 2025 David Carter <dcarter@davidcarter.ca>
# SPDX-File-Notice: Part of the Rocket addon.


"""Provides support for importing Open Rocket files."""

__title__ = "FreeCAD Open Rocket Importer"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

from Rocket.Importer.Rocksim.ComponentElement import ComponentElement
from Rocket.Constants import STYLE_HOLLOW, STYLE_SOLID
from Rocket.Constants import TYPE_CONE, TYPE_ELLIPTICAL, TYPE_HAACK, TYPE_OGIVE, TYPE_PARABOLA, TYPE_POWER

from Ui.Commands.CmdTransition import makeTransition

class TransitionElement(ComponentElement):

    def __init__(self, parent, tag, attributes, parentObj, filename, line):
        super().__init__(parent, tag, attributes, parentObj, filename, line)

        # avoid circular import
        from Rocket.Importer.Rocksim.AttachedPartsElement import AttachedPartsElement

        self._validChildren = { 'attachedparts' : AttachedPartsElement }
        self._knownTags.extend(["attachedparts", "shapecode", "len", "basedia", "wallthickness", "shoulderod",
                           "shoulderlen", "shapeparameter", "constructiontype", "displayflags", "metricsflags",
                           "baseextensionlen", "coredia", "corelen", "attachedparts", "frontdia", "reardia",
                           "frontshoulderlen", "rearshoulderlen", "frontshoulderdia", "rearshoulderdia",
                           "equivnoselen", "equivnoseoffset"])

    def makeObject(self):
        self._feature = makeTransition()
        if self._parentObj:
            self._parentObj.addChild(self._feature)

    def handleEndTag(self, tag, content):
        _tag = tag.lower().strip()
        # print("TransitionElement handle tag " + _tag)
        if _tag == "shapecode":
            shapeCode = int(content)
            if shapeCode == 0: # CONICAL
                self._feature._obj.TransitionType = TYPE_CONE
            elif shapeCode == 1: # OGIVE
                self._feature._obj.TransitionType = TYPE_OGIVE
            elif shapeCode == 2: # PARABOLIC - closest is elliptical in OR
                self._feature._obj.TransitionType = TYPE_ELLIPTICAL
            elif shapeCode == 3: # ELLIPTICAL
                self._feature._obj.TransitionType = TYPE_ELLIPTICAL
            elif shapeCode == 4: # POWER SERIES
                self._feature._obj.TransitionType = TYPE_POWER
            elif shapeCode == 5: # PARABOLIC SERIES
                self._feature._obj.TransitionType = TYPE_PARABOLA
            elif shapeCode == 6: # HAACK
                self._feature._obj.TransitionType = TYPE_HAACK
            else:
                raise Exception("Unknown transition type " + content)
        elif _tag == "shapeparameter":
            self._feature._obj.Coefficient = float(content)
        elif _tag == "frontdia":
            self._feature._obj.ForeAutoDiameter = False
            self._feature._obj.ForeDiameter = float(content)
        elif _tag == "reardia":
            self._feature._obj.AftAutoDiameter = False
            self._feature._obj.AftDiameter = float(content)
        elif _tag == "wallthickness":
            self._feature._obj.Thickness = float(content)
            self._feature._obj.ForeShoulderThickness = float(content)
            self._feature._obj.AftShoulderThickness = float(content)
        elif _tag == "frontshoulderdia":
            self._feature._obj.ForeShoulderDiameter = float(content)
        elif _tag == "rearshoulderdia":
            self._feature._obj.AftShoulderDiameter = float(content)
        elif _tag == "frontshoulderlen":
            length = float(content)
            self._feature._obj.ForeShoulderLength = length
            if length > 0:
                self._feature._obj.ForeShoulder = True
        elif _tag == "rearshoulderlen":
            length = float(content)
            self._feature._obj.AftShoulderLength = length
            if length > 0:
                self._feature._obj.AftShoulder = True
        elif _tag == "constructiontype":
            constructionType = int(content)
            if constructionType == 0:
                self._feature._obj.TransitionStyle = STYLE_SOLID
            else:
                self._feature._obj.TransitionStyle = STYLE_HOLLOW
        else:
            super().handleEndTag(tag, content)

    def onLength(self, length):
        self._feature._obj.Length = length

    def onThickness(self, thickness):
        self._feature._obj.Thickness = thickness
        self._feature._obj.ShoulderThickness = thickness

    def onFilled(self, filled):
        if filled:
            self._feature._obj.NoseStyle = STYLE_SOLID
        else:
            self._feature._obj.NoseStyle = STYLE_HOLLOW
