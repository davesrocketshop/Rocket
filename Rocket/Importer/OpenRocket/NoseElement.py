# SPDX-License-Identifier: LGPL-2.1-or-later

# ***************************************************************************
# *   Copyright (c) 2021-2025 David Carter <dcarter@davidcarter.ca>         *
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
from Rocket.Importer.OpenRocket.TransitionElement import TransitionElement
from Rocket.Utilities import _toBoolean
from Rocket.Constants import STYLE_CAPPED, STYLE_HOLLOW, STYLE_SOLID
from Rocket.Constants import TYPE_CONE, TYPE_ELLIPTICAL, TYPE_HAACK, TYPE_OGIVE, TYPE_PARABOLIC, TYPE_POWER

from Ui.Commands.CmdNoseCone import makeNoseCone

class NoseElement(TransitionElement):

    def __init__(self, parent, tag, attributes, parentObj, filename, line):
        super().__init__(parent, tag, attributes, parentObj, filename, line)

        self._shoulderCapped = False

        self._knownTags.remove("foreradius")
        self._knownTags.remove("foreshoulderradius")
        self._knownTags.remove("foreshoulderdiameter")
        self._knownTags.remove("foreshoulderlength")
        self._knownTags.remove("foreshoulderthickness")
        self._knownTags.remove("foreshouldercapped")

        self._knownTags.extend(["isflipped"])

    def makeObject(self):
        self._feature = makeNoseCone()
        if self._parentObj:
            self._parentObj.addChild(self._feature)

    def handleEndTag(self, tag, content):
        _tag = tag.lower().strip()
        if _tag == "shape":
            if content == 'conical':
                self._feature._obj.NoseType = TYPE_CONE
            elif content == 'ogive':
                self._feature._obj.NoseType = TYPE_OGIVE
            elif content == 'ellipsoid':
                self._feature._obj.NoseType = TYPE_ELLIPTICAL
            elif content == 'power':
                self._feature._obj.NoseType = TYPE_POWER
            elif content == 'parabolic':
                self._feature._obj.NoseType = TYPE_PARABOLIC
            elif content == 'haack':
                self._feature._obj.NoseType = TYPE_HAACK
            else:
                raise Exception("Unknown nose type " + content)
        elif _tag == "shapeclipped":
            # _err("Clipped element not supported") # This is meant for transitions
            # self._feature._obj.Clipped = _toBoolean(content)
            pass
        elif _tag == "shapeparameter":
            self._feature._obj.Coefficient = float(content)
        elif _tag == "aftradius":
            if self.isAuto(content):
                self._feature._obj.AutoDiameter = True
                # self._feature._obj.ShoulderAutoDiameter = True
            else:
                self._feature._obj.AutoDiameter = False
                # self._feature._obj.ShoulderAutoDiameter = False
                diameter = float(content) * 2.0
                self._feature._obj.Diameter = FreeCAD.Units.Quantity(str(diameter) + " m").Value
        elif _tag == "aftouterdiameter":
            self._feature._obj.Diameter = FreeCAD.Units.Quantity(content + " m").Value
        elif _tag == "aftshoulderradius":
            if self.isAuto(content):
                self._feature._obj.ShoulderAutoDiameter = True
            else:
                self._feature._obj.ShoulderAutoDiameter = False
                diameter = float(content) * 2.0
                self._feature._obj.ShoulderDiameter = FreeCAD.Units.Quantity(str(diameter) + " m").Value
        elif _tag == "aftshoulderdiameter":
            if self.isAuto(content):
                self._feature._obj.ShoulderAutoDiameter = True
            else:
                self._feature._obj.ShoulderAutoDiameter = False
                self._feature._obj.ShoulderDiameter = FreeCAD.Units.Quantity(content + " m").Value
        elif _tag == "aftshoulderlength":
            self._feature._obj.ShoulderLength = FreeCAD.Units.Quantity(content + " m").Value
        elif _tag == "aftshoulderthickness":
            self._feature._obj.ShoulderThickness = FreeCAD.Units.Quantity(content + " m").Value
        elif _tag == "aftshouldercapped":
            self._shoulderCapped = _toBoolean(content)
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
