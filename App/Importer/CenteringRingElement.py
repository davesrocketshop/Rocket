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

from App.Importer.RingComponentElement import RingComponentElement

from Ui.Commands.CmdCenteringRing import makeCenteringRing

class CenteringRingElement(RingComponentElement):

    def __init__(self, parent, tag, attributes, parentObj, filename, line):
        super().__init__(parent, tag, attributes, parentObj, filename, line)

        self._shoulderCapped = False

        self._knownTags.extend(["outerradius", "innerradius"])

    def makeObject(self):
        self._feature = makeCenteringRing()
        if self._parentObj is not None:
            self._parentObj._obj.addObject(self._feature._obj)

    def handleEndTag(self, tag, content):
        _tag = tag.lower().strip()
        if _tag == "outerradius":
            self._feature.setScratch("outerradius", content)
            if str(content).lower() == "auto":
                diameter = "0.0"
                self._feature._obj.AutoDiameter = True
            else:
                diameter = float(content) * 2.0
                self._feature._obj.AutoDiameter = False
            self._feature._obj.Diameter = str(diameter) + "m"
        elif _tag == "innerradius":
            self._feature.setScratch("innerradius", content)
            if str(content).lower() == "auto":
                diameter = "0.0"
                self._feature._obj.CenterAutoDiameter = True
            else:
                diameter = float(content) * 2.0
                self._feature._obj.CenterAutoDiameter = False
            self._feature._obj.CenterDiameter = str(diameter) + "m"
        else:
            super().handleEndTag(tag, content)

    def onName(self, content):
        self._feature.setName(content)

    def onLength(self, length):
        self._feature.setThickness(length)

    def end(self):
        # Validate the shape here

        return super().end()
