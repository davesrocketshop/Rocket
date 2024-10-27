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
"""Provides support for importing RASAero files."""

__title__ = "FreeCAD RASAero Importer"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

import FreeCAD

from Rocket.Importer.OpenRocket.SaxElement import Element

from Rocket.Constants import TYPE_CONE, TYPE_BLUNTED_CONE, TYPE_ELLIPTICAL, TYPE_HAACK, TYPE_OGIVE, TYPE_BLUNTED_OGIVE, TYPE_POWER

from Ui.Commands.CmdNoseCone import makeNoseCone

class NoseElement(Element):

    def __init__(self, parent, tag, attributes, parentObj, filename, line):
        super().__init__(parent, tag, attributes, parentObj, filename, line)

        self._knownTags.extend(["parttype", "length", "diameter",
                "shape", "bluntradius", "location", "color", "power law"])

        self._bluntRadius = 0.0

    def makeObject(self):
        self._feature = makeNoseCone()
        if self._parentObj is not None:
            self._parentObj.addChild(self._feature)

    def handleEndTag(self, tag, content):
        _tag = tag.lower().strip()
        if _tag == "shape":
            _content = content.lower().strip()
            if _content == 'conical':
                self._feature._obj.NoseType = TYPE_CONE
            elif _content == 'tangent ogive':
                self._feature._obj.NoseType = TYPE_OGIVE
            elif _content == 'von karman ogive':
                self._feature._obj.NoseType = TYPE_HAACK
                self._feature._obj.Coefficient = 0.0
            elif _content == 'power law':
                self._feature._obj.NoseType = TYPE_POWER
            elif _content == 'lv-haack':
                self._feature._obj.NoseType = TYPE_HAACK
                self._feature._obj.Coefficient = 1.0/3.0
            elif _content == 'parabolic':
                self._feature._obj.NoseType = TYPE_POWER
                self._feature._obj.Coefficient = 0.5
            elif _content == 'elliptical':
                self._feature._obj.NoseType = TYPE_ELLIPTICAL
            else:
                raise Exception("Unknown nose type " + content)
        elif _tag == "power law":
            self._feature._obj.Coefficient = float(content)
        elif _tag == "diameter":
            self._feature._obj.AutoDiameter = False
            self._feature._obj.Diameter = FreeCAD.Units.Quantity(content + " in").Value
        elif _tag == "length":
            self._feature._obj.Length = FreeCAD.Units.Quantity(content + " in").Value
        elif _tag == "bluntradius":
            self._bluntRadius = FreeCAD.Units.Quantity(content + " in").Value
        elif _tag == "color":
            pass # Not yet implemented
        else:
            super().handleEndTag(tag, content)

    def end(self):
        if self._bluntRadius > 0:
            self._feature._obj.BluntedDiameter = self._bluntRadius / 2.0
            if self._feature._obj.NoseType == TYPE_CONE:
                self._feature._obj.NoseType = TYPE_BLUNTED_CONE
            elif self._feature._obj.NoseType == TYPE_OGIVE:
                self._feature._obj.NoseType = TYPE_BLUNTED_OGIVE

        self._feature._obj.Shoulder = False

        return super().end()
