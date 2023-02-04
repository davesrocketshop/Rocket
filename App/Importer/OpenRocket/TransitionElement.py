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
"""Provides support for importing Open Rocket files."""

__title__ = "FreeCAD Open Rocket Importer"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

import FreeCAD

from App.Importer.OpenRocket.SaxElement import NullElement
from App.Importer.OpenRocket.SymmetricComponentElement import SymmetricComponentElement
from App.Utilities import _toBoolean, _err
from App.Constants import STYLE_CAPPED, STYLE_HOLLOW, STYLE_SOLID
from App.Constants import TYPE_CONE, TYPE_ELLIPTICAL, TYPE_HAACK, TYPE_OGIVE, TYPE_PARABOLA, TYPE_POWER

from Ui.Commands.CmdTransition import makeTransition

class TransitionElement(SymmetricComponentElement):

    def __init__(self, parent, tag, attributes, parentObj, filename, line):
        super().__init__(parent, tag, attributes, parentObj, filename, line)

        self._shoulderCapped = False

        self._knownTags.extend(["shape", "shapeclipped", "shapeparameter", 
                "foreradius", "aftradius", "aftouterdiameter", "foreshoulderradius", "foreshoulderdiameter", "foreshoulderlength", "foreshoulderthickness", "foreshouldercapped", 
                "aftshoulderradius", "aftshoulderdiameter", "aftshoulderlength", "aftshoulderthickness", "aftshouldercapped"])

        self._filled = False

    def makeObject(self):
        self._feature = makeTransition()
        if self._parentObj is not None:
            self._parentObj.addChild(self._feature)

    def handleEndTag(self, tag, content):
        _tag = tag.lower().strip()
        if _tag == "shape":
            if content == 'conical':
                self._feature._obj.TransitionType = TYPE_CONE
            elif content == 'ogive':
                self._feature._obj.TransitionType = TYPE_OGIVE
            elif content == 'ellipsoid':
                self._feature._obj.TransitionType = TYPE_ELLIPTICAL
            elif content == 'power':
                self._feature._obj.TransitionType = TYPE_POWER
            elif content == 'parabolic':
                self._feature._obj.TransitionType = TYPE_PARABOLA
            elif content == 'haack':
                self._feature._obj.TransitionType = TYPE_HAACK
            else:
                raise Exception("Unknown type " + content)
        elif _tag == "shapeclipped":
            self._feature._obj.Clipped = _toBoolean(content)
        elif _tag == "shapeparameter":
            self._feature._obj.Coefficient = float(content)
        elif _tag == "foreradius":
            if content == "auto":
                self._feature._obj.ForeAutoDiameter = True
            else:
                self._feature._obj.ForeAutoDiameter = False
                diameter = float(content) * 2.0
                self._feature._obj.ForeDiameter = str(diameter) + "m"
        elif _tag == "aftradius":
            if content == "auto":
                self._feature._obj.AftAutoDiameter = True
            else:
                self._feature._obj.AftAutoDiameter = False
                diameter = float(content) * 2.0
                self._feature._obj.AftDiameter = str(diameter) + "m"
        elif _tag == "aftouterdiameter":
            self._feature._obj.AftDiameter = FreeCAD.Units.Quantity(content + " m").Value

        elif _tag == "foreshoulderradius":
            diameter = float(content) * 2.0
            self._feature._obj.ForeShoulderDiameter = str(diameter) + "m"
        elif _tag == "foreshoulderdiameter":
            self._feature._obj.ForeShoulderDiameter = FreeCAD.Units.Quantity(content + " m").Value
        elif _tag == "foreshoulderlength":
            self._feature._obj.ForeShoulderLength = FreeCAD.Units.Quantity(content + " m").Value
        elif _tag == "foreshoulderthickness":
            self._feature._obj.ForeShoulderThickness = FreeCAD.Units.Quantity(content + " m").Value
        elif _tag == "foreshouldercapped":
            self._shoulderCapped = _toBoolean(content)

        elif _tag == "aftshoulderradius":
            diameter = float(content) * 2.0
            self._feature._obj.AftShoulderDiameter = str(diameter) + "m"
        elif _tag == "aftshoulderdiameter":
            self._feature._obj.AftShoulderDiameter = FreeCAD.Units.Quantity(content + " m").Value
        elif _tag == "aftshoulderlength":
            self._feature._obj.AftShoulderLength = FreeCAD.Units.Quantity(content + " m").Value
        elif _tag == "aftshoulderthickness":
            self._feature._obj.AftShoulderThickness = FreeCAD.Units.Quantity(content + " m").Value
        elif _tag == "aftshouldercapped":
            self._shoulderCapped = _toBoolean(content)

        # elif _tag == "manufacturer":
        #     self._feature._obj.Manufacturer = content
        # elif _tag == "partno":
        #     self._feature._obj.PartNumber = content
        # elif _tag == "description":
        #     self._feature._obj.Description = content
        else:
            super().handleEndTag(tag, content)

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
