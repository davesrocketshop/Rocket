# ***************************************************************************
# *   Copyright (c) 2021-2024 David Carter <dcarter@davidcarter.ca>         *
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

from Rocket.Importer.OpenRocket.SaxElement import NullElement
from Rocket.Importer.Rocksim.ComponentElement import ComponentElement
from Rocket.Importer.OpenRocket.TransitionElement import TransitionElement
from Rocket.Utilities import _toBoolean
from Rocket.Constants import STYLE_CAPPED, STYLE_HOLLOW, STYLE_SOLID
from Rocket.Constants import TYPE_CONE, TYPE_ELLIPTICAL, TYPE_HAACK, TYPE_OGIVE, TYPE_PARABOLA, TYPE_POWER

from Ui.Commands.CmdNoseCone import makeNoseCone

class NoseElement(ComponentElement):

    def __init__(self, parent, tag, attributes, parentObj, filename, line):
        super().__init__(parent, tag, attributes, parentObj, filename, line)

        self._shoulderCapped = False
        self._validChildren = { 'attachedparts' : NullElement,
                                # 'material' : MaterialElement,
                                # 'appearance' : AppearanceElement,
                                # 'inside-appearance' : NullElement
                              }
        self._knownTags.extend(["attachedparts", "shapecode", "len", "basedia", "wallthickness", "shoulderod",
                           "shoulderlen", "shapeparameter", "constructiontype", "xb", "displayflags",
                           "metricsflags", "locationmode", "barrowmancna", "barrowmanxn", "rocksimcna", "rocksimxn",
                           "baseextensionlen", "coredia", "corelen", "attachedparts"])

    def makeObject(self):
        self._feature = makeNoseCone()
        if self._parentObj is not None:
            self._parentObj.addChild(self._feature)

    def handleEndTag(self, tag, content):
        _tag = tag.lower().strip()
        print("Handle tag " + _tag)
        if _tag == "shapecode":
            shapeCode = int(content)
            print("\tshapecode {}".format(shapeCode))
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
            print("\tbasedia {}".format(float(content)))
            self._feature._obj.AutoDiameter = False
            self._feature._obj.Diameter = float(content)
        elif _tag == "len":
            print("\tlen {}".format(float(content)))
            self.onLength(float(content))
        elif _tag == "wallthickness":
            print("\twallthickness {}".format(float(content)))
            self._feature._obj.Thickness = float(content)
            self._feature._obj.ShoulderThickness = float(content)
        elif _tag == "shoulderod":
            print("\tshoulderod {}".format(float(content)))
            self._feature._obj.ShoulderDiameter = float(content)
        elif _tag == "shoulderlen":
            length = float(content)
            print("\tshoulderlen {}".format(length))
            self._feature._obj.ShoulderLength = length
            if length > 0:
                self._feature._obj.Shoulder = True
        elif _tag == "constructiontype":
            constructionType = int(content)
            print("\tconstructiontype {}".format(constructionType))
            if constructionType == 0:
                self._feature._obj.NoseStyle = STYLE_SOLID
            else:
                self._feature._obj.NoseStyle = STYLE_HOLLOW
        # elif _tag == "aftouterdiameter":
        #     self._feature._obj.Diameter = FreeCAD.Units.Quantity(content + " m").Value
        # elif _tag == "aftshoulderradius":
        #     if self.isAuto(content):
        #         self._feature._obj.ShoulderAutoDiameter = True
        #     else:
        #         self._feature._obj.ShoulderAutoDiameter = False
        #         diameter = float(content) * 2.0
        #         self._feature._obj.ShoulderDiameter = FreeCAD.Units.Quantity(str(diameter) + " m").Value
        # elif _tag == "aftshoulderdiameter":
        #     if self.isAuto(content):
        #         self._feature._obj.ShoulderAutoDiameter = True
        #     else:
        #         self._feature._obj.ShoulderAutoDiameter = False
        #         self._feature._obj.ShoulderDiameter = FreeCAD.Units.Quantity(content + " m").Value
        # elif _tag == "aftshoulderlength":
        #     self._feature._obj.ShoulderLength = FreeCAD.Units.Quantity(content + " m").Value
        # elif _tag == "aftshoulderthickness":
        #     self._feature._obj.ShoulderThickness = FreeCAD.Units.Quantity(content + " m").Value
        # elif _tag == "aftshouldercapped":
        #     self._shoulderCapped = _toBoolean(content)
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

    def end(self):
        # Validate the nose shape here
        # if float(self._feature._obj.Thickness) > 0 and not self._filled:
        #     if float(self._feature._obj.ShoulderThickness) <= 0:
        #         self._feature._obj.ShoulderThickness = self._feature._obj.Thickness
        #     if self._shoulderCapped:
        #         self._feature._obj.NoseStyle = STYLE_CAPPED
        #     else:
        #         self._feature._obj.NoseStyle = STYLE_HOLLOW
        # else:
        #     self._feature._obj.NoseStyle = STYLE_SOLID

        # if float(self._feature._obj.ShoulderDiameter) > 0 and float(self._feature._obj.ShoulderLength) > 0:
        #     self._feature._obj.Shoulder = True
        # else:
        #     self._feature._obj.Shoulder = False

        return super().end()
