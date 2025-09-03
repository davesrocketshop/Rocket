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
"""Provides support for importing Open Rocket files."""

__title__ = "FreeCAD Open Rocket Importer"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

import FreeCAD

from Rocket.Importer.Rocksim.ComponentElement import ComponentElement
from Rocket.Importer.Rocksim.AttachedPartsElement import AttachedPartsElement
from Rocket.Constants import STYLE_HOLLOW, STYLE_SOLID
from Rocket.Constants import TYPE_CONE, TYPE_ELLIPTICAL, TYPE_HAACK, TYPE_OGIVE, TYPE_PARABOLA, TYPE_POWER

from Ui.Commands.CmdNoseCone import makeNoseCone

class NoseElement(ComponentElement):

    def __init__(self, parent, tag, attributes, parentObj, filename, line):
        super().__init__(parent, tag, attributes, parentObj, filename, line)

        self._validChildren = { 'attachedparts' : AttachedPartsElement }
        self._knownTags.extend(["attachedparts", "shapecode", "len", "basedia", "wallthickness", "shoulderod",
                           "shoulderlen", "shapeparameter", "constructiontype", "displayflags", "metricsflags",
                           "baseextensionlen", "coredia", "corelen", "attachedparts"])

    def makeObject(self):
        self._feature = makeNoseCone()
        if self._parentObj:
            self._parentObj.addChild(self._feature)

    def handleEndTag(self, tag, content):
        _tag = tag.lower().strip()
        # print("NoseElement handle tag " + _tag)
        if _tag == "shapecode":
            shapeCode = int(content)
            if shapeCode == 0: # CONICAL
                self._feature._obj.NoseType = TYPE_CONE
            elif shapeCode == 1: # OGIVE
                self._feature._obj.NoseType = TYPE_OGIVE
            elif shapeCode == 2: # PARABOLIC - closeest is elliptical in OR
                self._feature._obj.NoseType = TYPE_ELLIPTICAL
            elif shapeCode == 3: # ELLIPTICAL
                self._feature._obj.NoseType = TYPE_ELLIPTICAL
            elif shapeCode == 4: # POWER SERIES
                self._feature._obj.NoseType = TYPE_POWER
            elif shapeCode == 5: # PARABOLIC SERIES
                self._feature._obj.NoseType = TYPE_PARABOLA
            elif shapeCode == 6: # HAACK
                self._feature._obj.NoseType = TYPE_HAACK
            else:
                raise Exception("Unknown nose type " + content)
        elif _tag == "shapeparameter":
            self._feature._obj.Coefficient = float(content)
        elif _tag == "basedia":
            self._feature._obj.AutoDiameter = False
            self._feature._obj.Diameter = float(content)
        elif _tag == "wallthickness":
            self._feature._obj.Thickness = float(content)
            self._feature._obj.ShoulderThickness = float(content)
        elif _tag == "shoulderod":
            self._feature._obj.ShoulderDiameter = float(content)
        elif _tag == "shoulderlen":
            length = float(content)
            self._feature._obj.ShoulderLength = length
            self._feature._obj.Shoulder = (length > 0)
        elif _tag == "constructiontype":
            constructionType = int(content)
            if constructionType == 0:
                self._feature._obj.NoseStyle = STYLE_SOLID
            else:
                self._feature._obj.NoseStyle = STYLE_HOLLOW
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
