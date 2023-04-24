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

from Rocket.Importer.Rocsim.BaseElement import BaseElement
from Rocket.Importer.Rocsim.AttachedPartsElement import AttachedPartsElement
from Rocket.Constants import STYLE_CAPPED, STYLE_HOLLOW, STYLE_SOLID
from Rocket.Constants import TYPE_CONE, TYPE_ELLIPTICAL, TYPE_HAACK, TYPE_OGIVE, TYPE_PARABOLA, TYPE_POWER

from Ui.Commands.CmdTransition import makeTransition

class TransitionElement(BaseElement):

    def __init__(self, parent, tag, attributes, parentObj, filename, line):
        super().__init__(parent, tag, attributes, parentObj, filename, line)

        self._shoulderCapped = False

        self._validChildren.update({ 'attachedparts' : AttachedPartsElement,
                              })
        self._knownTags.extend(["xb", "calcmass", "calccg", "radialloc", "radialangle", "locationmode", "len", 
                                "finishcode", "serialno", "shapecode", "constructiontype", "wallthickness", "shapeparameter", 
                                "attachedparts", "material", "frontshoulderlen", "rearshoulderlen", "frontshoulderdia", 
                                "rearshoulderdia", "frontdia", "reardia"])

    def makeObject(self):
        self._feature = makeTransition()
        if self._parentObj is not None:
            self._parentObj.addChild(self._feature)

    def handleEndTag(self, tag, content):
        _tag = tag.lower().strip()
        if _tag == "shapecode":
            self.setType(content.strip())
        elif _tag == "len":
            self.onLength(FreeCAD.Units.Quantity(content + " mm").Value)
        elif _tag == "frontdia":
            self._feature._obj.ForeAutoDiameter = False
            self._feature._obj.ForeDiameter = FreeCAD.Units.Quantity(content + " mm").Value
        elif _tag == "reardia":
            self._feature._obj.AftAutoDiameter = False
            self._feature._obj.AftDiameter = FreeCAD.Units.Quantity(content + " mm").Value
        elif _tag == "wallthickness":
            thickness = FreeCAD.Units.Quantity(content + " mm").Value
            self.onThickness(thickness)
        elif _tag == "frontshoulderdia":
            self._feature._obj.ForeShoulderAutoDiameter = False
            self._feature._obj.ForeShoulderDiameter = FreeCAD.Units.Quantity(content + " mm").Value
        elif _tag == "rearshoulderdia":
            self._feature._obj.AftShoulderAutoDiameter = False
            self._feature._obj.AftShoulderDiameter = FreeCAD.Units.Quantity(content + " mm").Value
        elif _tag == "frontshoulderlen":
            self._feature._obj.ForeShoulderLength = FreeCAD.Units.Quantity(content + " mm").Value
        elif _tag == "rearshoulderlen":
            self._feature._obj.AftShoulderLength = FreeCAD.Units.Quantity(content + " mm").Value
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
            self._feature._obj.TransitionType = TYPE_CONE
        elif type == '1':
            self._feature._obj.TransitionType = TYPE_OGIVE
        elif type == '2':
            self._feature._obj.TransitionType = TYPE_POWER
            self._feature._obj.Coefficient = 0.5
        elif type == '3':
            self._feature._obj.TransitionType = TYPE_ELLIPTICAL
        elif type == '4':
            self._feature._obj.TransitionType = TYPE_POWER
        elif type == '5':
            self._feature._obj.TransitionType = TYPE_PARABOLA
        elif type == '6':
            self._feature._obj.TransitionType = TYPE_HAACK
        else:
            self._feature._obj.TransitionType = TYPE_PARABOLA # default

    def onLength(self, length):
        self._feature._obj.Length = length

    def onThickness(self, thickness):
        self._feature._obj.Thickness = thickness
        self._feature._obj.ForeShoulderThickness = thickness
        self._feature._obj.AftShoulderThickness = thickness

    def onFilled(self, filled):
        if filled:
            self._feature._obj.TransitionStyle = STYLE_SOLID
            self._filled = True
        else:
            self._filled = False

    def end(self):
        # Skip if this is a nose cone (derived)
        if not hasattr(self._feature._obj, "NoseStyle"):
            if float(self._feature._obj.Thickness) > 0 and not self._filled:
                if float(self._feature._obj.ForeShoulderThickness) <= 0:
                    self._feature._obj.ForeShoulderThickness = self._feature._obj.Thickness
                if float(self._feature._obj.AftShoulderThickness) <= 0:
                    self._feature._obj.AftShoulderThickness = self._feature._obj.Thickness
                if self._shoulderCapped:
                    self._feature._obj.TransitionStyle = STYLE_CAPPED
                else:
                    self._feature._obj.TransitionStyle = STYLE_HOLLOW
            else:
                self._feature._obj.TransitionStyle = STYLE_SOLID

            if float(self._feature._obj.ForeShoulderDiameter) > 0 and float(self._feature._obj.ForeShoulderLength) > 0:
                self._feature._obj.ForeShoulder = True
            else:
                self._feature._obj.ForeShoulder = False


            if float(self._feature._obj.AftShoulderDiameter) > 0 and float(self._feature._obj.AftShoulderLength) > 0:
                self._feature._obj.AftShoulder = True
            else:
                self._feature._obj.AftShoulder = False

        return super().end()
