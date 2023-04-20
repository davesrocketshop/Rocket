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
"""Provides support for importing Rocsim files."""

__title__ = "FreeCAD Rocsim Importer"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

import FreeCAD

from Rocket.Importer.OpenRocket.SaxElement import NullElement
from Rocket.Importer.Rocsim.BaseElement import BaseElement
from Rocket.Utilities import _toBoolean
from Rocket.Constants import STYLE_CAPPED, STYLE_HOLLOW, STYLE_SOLID
from Rocket.Constants import TYPE_CONE, TYPE_ELLIPTICAL, TYPE_HAACK, TYPE_OGIVE, TYPE_PARABOLA, TYPE_POWER

from Ui.Commands.CmdNoseCone import makeNoseCone

class NoseElement(BaseElement):

    def __init__(self, parent, tag, attributes, parentObj, filename, line):
        super().__init__(parent, tag, attributes, parentObj, filename, line)

        self._shoulderCapped = False

        self._validChildren.update({ 'attachedparts' : NullElement,
                              })
        self._knownTags.extend(["xb", "calcmass", "calccg", "radialloc", "radialangle", "locationmode", "len", 
                                "finishcode", "serialno", "shapecode", "constructiontype", "wallthickness", "shapeparameter", 
                                "attachedparts", "basedia", "shoulderlen", "shoulderod", "material"])

    def makeObject(self):
        self._feature = makeNoseCone()
        self._feature._obj.ShoulderAutoDiameter = False
        if self._parentObj is not None:
            self._parentObj.addChild(self._feature)

    def handleEndTag(self, tag, content):
        _tag = tag.lower().strip()
        if _tag == "shapecode":
            self.setType(content.strip())
        elif _tag == "len":
            self.onLength(FreeCAD.Units.Quantity(content + " mm").Value)
        elif _tag == "basedia":
            self._feature._obj.AutoDiameter = False
            self._feature._obj.Diameter = FreeCAD.Units.Quantity(content + " mm").Value
        elif _tag == "wallthickness":
            thickness = FreeCAD.Units.Quantity(content + " mm").Value
            self.onThickness(thickness)
        elif _tag == "shoulderod":
            self._feature._obj.ShoulderAutoDiameter = False
            self._feature._obj.ShoulderDiameter = FreeCAD.Units.Quantity(content + " mm").Value
        elif _tag == "shoulderlen":
            self._feature._obj.ShoulderLength = FreeCAD.Units.Quantity(content + " mm").Value
        elif _tag == "shapeparameter":
            self._feature._obj.Coefficient = float(content)
        elif _tag == "constructiontype":
            typeCode = int(content)
            if typeCode == 0:
                self.onFilled(True)
            else:
                self.onFilled(False)
        elif _tag == "finishcode":
            # self._feature._obj.Coefficient = float(content)
            pass
        elif _tag == "material":
            self._feature._obj.Material = content
        else:
            super().handleEndTag(tag, content)

    def setType(self, type):
        if type == '0':
            self._feature._obj.NoseType = TYPE_CONE
        elif type == '1':
            self._feature._obj.NoseType = TYPE_OGIVE
        elif type == '2':
            self._feature._obj.NoseType = TYPE_POWER
            self._feature._obj.Coefficient = 0.5
        elif type == '3':
            self._feature._obj.NoseType = TYPE_ELLIPTICAL
        elif type == '4':
            self._feature._obj.NoseType = TYPE_POWER
        elif type == '5':
            self._feature._obj.NoseType = TYPE_PARABOLA
        elif type == '6':
            self._feature._obj.NoseType = TYPE_HAACK
        else:
            self._feature._obj.NoseType = TYPE_PARABOLA # default

    def onLength(self, length):
        self._feature._obj.Length = length

    def onThickness(self, thickness):
        self._feature._obj.Thickness = thickness
        self._feature._obj.ShoulderThickness = thickness

    def onFilled(self, filled):
        if filled:
            self._feature._obj.NoseStyle = STYLE_SOLID
            self._filled = True
        else:
            self._filled = False

    def end(self):
        # Validate the nose shape here
        if float(self._feature._obj.Thickness) > 0 and not self._filled:
            if float(self._feature._obj.ShoulderThickness) <= 0:
                self._feature._obj.ShoulderThickness = self._feature._obj.Thickness
            if self._shoulderCapped:
                self._feature._obj.NoseStyle = STYLE_CAPPED
            else:
                self._feature._obj.NoseStyle = STYLE_HOLLOW
        else:
            self._feature._obj.NoseStyle = STYLE_SOLID

        if float(self._feature._obj.ShoulderDiameter) > 0 and float(self._feature._obj.ShoulderLength) > 0:
            self._feature._obj.Shoulder = True
        else:
            self._feature._obj.Shoulder = False

        return super().end()
