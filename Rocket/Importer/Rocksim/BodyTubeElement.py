# SPDX-License-Identifier: LGPL-2.1-or-later

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

from Rocket.Importer.OpenRocket.SaxElement import NullElement
from Rocket.Importer.Rocksim.ComponentElement import ComponentElement

from Ui.Commands.CmdBodyTube import makeBodyTube, makeInnerTube

class MotorMountElement(ComponentElement):

    def __init__(self, parent, tag, attributes, parentObj, filename, line):
        super().__init__(parent, tag, attributes, parentObj, filename, line)

        self._validChildren.update({ 'motor' : NullElement,
                              })
        self._knownTags.extend(["overhang", "ignitionevent", "ignitiondelay", "ignitionconfiguration"])

    def makeObject(self):
        if self._parentObj:
            self._feature = self._parentObj
            self._feature._obj.MotorMount = True

    def handleEndTag(self, tag, content):
        _tag = tag.lower().strip()
        if _tag == "overhang":
            self._feature._obj.Overhang = content + "m"
        else:
            super().handleEndTag(tag, content)

class BodyTubeElement(ComponentElement):

    def __init__(self, parent, tag, attributes, parentObj, filename, line):
        super().__init__(parent, tag, attributes, parentObj, filename, line)

        # avoid circular import
        from Rocket.Importer.Rocksim.AttachedPartsElement import AttachedPartsElement

        self._validChildren.update({ 'attachedparts' : AttachedPartsElement })
        self._knownTags.extend(["od", "id", "finishcode", "ismotormount", "engineoverhang", "motordia", "frontextension",
                                "rearextension", "isinsidetube", "isstrapontube", "finset", "attachedparts", "bodytube",
                                "usagecode", "autosize", "ring"])
        self._innerDiameter = 0

    def makeObject(self):
        self._feature = makeBodyTube()
        if self._parentObj:
            self._parentObj.addChild(self._feature)

    def handleEndTag(self, tag, content):
        _tag = tag.lower().strip()
        # print("BodyTubeElement handle tag " + _tag)
        if _tag == "od":
            self._feature._obj.Diameter = float(content)
        elif _tag == "id":
            self._innerDiameter = float(content)
        elif _tag == "autosize":
            if int(content) != 0:
                self._feature._obj.AutoDiameter = True
            else:
                self._feature._obj.AutoDiameter = False
        elif _tag == "ismotormount":
            if int(content) != 0:
                self._feature._obj.MotorMount = True
            else:
                self._feature._obj.MotorMount = False
        elif _tag == "engineoverhang":
            self._feature._obj.Overhang = float(content)
        else:
            super().handleEndTag(tag, content)

    def onThickness(self, length):
        self._feature._obj.Thickness = length

    def onLength(self, length):
        self._feature._obj.Length = length

    def end(self):
        if self._innerDiameter > 0:
            thickness = (float(self._feature._obj.Diameter.Value) - self._innerDiameter) / 2.0
            if thickness > 0:
                self.onThickness(thickness)
        return super().end()

class InnerTubeElement(BodyTubeElement):

    def __init__(self, parent, tag, attributes, parentObj, filename, line):
        super().__init__(parent, tag, attributes, parentObj, filename, line)

    def makeObject(self):
        self._feature = makeInnerTube()
        if self._parentObj:
            self._parentObj.addChild(self._feature)
