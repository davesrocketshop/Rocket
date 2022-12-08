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

from App.Importer.ComponentElement import ComponentElement

from Ui.Commands.CmdCenteringRing import makeCenteringRing

class CenteringRingElement(ComponentElement):

    def __init__(self, parent, tag, attributes, parentObj, filename, line):
        super().__init__(parent, tag, attributes, parentObj, filename, line)

        self._shoulderCapped = False

        self._knownTags = ["length", "radialposition", "radialdirection", "outerradius", "innerradius"]

        self._obj = makeCenteringRing()
        if self._parentObj is not None:
            self._parentObj.addObject(self._obj)

    def handleEndTag(self, tag, content):
        _tag = tag.lower().strip()
        if _tag == "length":
            self._obj.Thickness = content + "m"
        elif _tag == "outerradius":
            self._obj.Proxy.setScratch("outerradius", content)
            if str(content).lower() == "auto":
                diameter = "0.0"
            else:
                diameter = float(content) * 2.0
            self._obj.Diameter = str(diameter) + "m"
        elif _tag == "innerradius":
            self._obj.Proxy.setScratch("innerradius", content)
            if str(content).lower() == "auto":
                diameter = "0.0"
            else:
                diameter = float(content) * 2.0
            self._obj.CenterDiameter = str(diameter) + "m"
        else:
            super().handleEndTag(tag, content)

    def onName(self, content):
        self._obj.Label = content

    def end(self):
        # Validate the shape here

        return super().end()
