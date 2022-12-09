# ***************************************************************************
# *   Copyright (c) 2021 David Carter <dcarter@davidcarter.ca>              *
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

from App.Importer.SaxElement import NullElement
from App.Importer.ComponentElement import ComponentElement
from App.Utilities import _toBoolean, _err
from App.Constants import STYLE_CAPPED, STYLE_HOLLOW, STYLE_SOLID
from App.Constants import TYPE_CONE, TYPE_ELLIPTICAL, TYPE_HAACK, TYPE_OGIVE, TYPE_PARABOLA, TYPE_POWER

from Ui.Commands.CmdNoseCone import makeNoseCone

class NoseElement(ComponentElement):

    def __init__(self, parent, tag, attributes, parentObj, filename, line):
        super().__init__(parent, tag, attributes, parentObj, filename, line)

        self._shoulderCapped = False

        self._validChildren = { 'appearance' : NullElement,
                                'finish' : NullElement,
                                'material' : NullElement,
                              }
        self._knownTags = ["manufacturer", "partno", "description", "thickness", "shape", "shapeclipped", "shapeparameter", 
                "aftradius", "aftouterdiameter", "aftshoulderradius", "aftshoulderdiameter", "aftshoulderlength", "aftshoulderthickness", "aftshouldercapped", "length"]

        self._obj = makeNoseCone()
        if self._parentObj is not None:
            self._parentObj.addObject(self._obj)

    def handleEndTag(self, tag, content):
        _tag = tag.lower().strip()
        if _tag == "length":
            self._obj.Length = FreeCAD.Units.Quantity(content + " m").Value
        elif _tag == "thickness":
            if content == 'filled':
                self._obj.Thickness = 0
            else:
                self._obj.Thickness = FreeCAD.Units.Quantity(content + " m").Value
        elif _tag == "shape":
            if content == 'conical':
                self._obj.NoseType = TYPE_CONE
            elif content == 'ogive':
                self._obj.NoseType = TYPE_OGIVE
            elif content == 'ellipsoid':
                self._obj.NoseType = TYPE_ELLIPTICAL
            elif content == 'power':
                self._obj.NoseType = TYPE_POWER
            elif content == 'parabolic':
                self._obj.NoseType = TYPE_PARABOLA
            elif content == 'haack':
                self._obj.NoseType = TYPE_HAACK
            else:
                raise Exception("Unknow nose type " + content)
        elif _tag == "shapeclipped":
            # _err("Clipped element not supported") # This is meant for transitions
            # self._obj.Clipped = _toBoolean(content)
            pass
        elif _tag == "shapeparameter":
            self._obj.Coefficient = float(content)
        elif _tag == "aftradius":
            if content == "auto":
                self._obj.AutoDiameter = True
            else:
                self._obj.AutoDiameter = False
                diameter = float(content) * 2.0
                self._obj.Diameter = str(diameter) + "m"
        elif _tag == "aftouterdiameter":
            self._obj.Diameter = FreeCAD.Units.Quantity(content + " m").Value
        elif _tag == "aftshoulderradius":
            diameter = float(content) * 2.0
            self._obj.ShoulderDiameter = str(diameter) + "m"
        elif _tag == "aftshoulderdiameter":
            self._obj.ShoulderDiameter = FreeCAD.Units.Quantity(content + " m").Value
        elif _tag == "aftshoulderlength":
            self._obj.ShoulderLength = FreeCAD.Units.Quantity(content + " m").Value
        elif _tag == "aftshoulderthickness":
            self._obj.ShoulderThickness = FreeCAD.Units.Quantity(content + " m").Value
        elif _tag == "aftshouldercapped":
            self._shoulderCapped = _toBoolean(content)
        elif _tag == "manufacturer":
            self._obj.Manufacturer = content
        elif _tag == "partno":
            self._obj.PartNumber = content
        elif _tag == "description":
            self._obj.Description = content
        else:
            super().handleEndTag(tag, content)

    def onName(self, content):
        self._obj.Label = content

    def end(self):
        # Validate the nose shape here
        if float(self._obj.Thickness) > 0:
            if float(self._obj.ShoulderThickness) <= 0:
                self._obj.ShoulderThickness = self._obj.Thickness
            if self._shoulderCapped:
                self._obj.NoseStyle = STYLE_CAPPED
            else:
                self._obj.NoseStyle = STYLE_HOLLOW
        else:
            self._obj.NoseStyle = STYLE_SOLID

        if float(self._obj.ShoulderDiameter) > 0 and float(self._obj.ShoulderLength) > 0:
            self._obj.Shoulder = True
        else:
            self._obj.Shoulder = False

        return super().end()
