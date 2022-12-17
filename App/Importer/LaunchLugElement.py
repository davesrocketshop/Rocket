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

from App.Importer.ComponentElement import ExternalComponentElement
import App.Importer as Importer

from Ui.Commands.CmdBodyTube import makeBodyTube

class LaunchLugElement(ExternalComponentElement):

    def __init__(self, parent, tag, attributes, parentObj, filename, line):
        super().__init__(parent, tag, attributes, parentObj, filename, line)

        # self._validChildren.update({ 'subcomponents' : Importer.SubElement.SubElement,
        #                         'motormount' : MotorMountElement,
        #                       })
        self._knownTags.extend(["instancecount", "instanceseparation", "radialdirection", "angleoffset", "radius", "outerradius", "length", "thickness"])

    def makeObject(self):
        self._obj = makeBodyTube()
        if self._parentObj is not None:
            self._parentObj.addObject(self._obj)

    def handleEndTag(self, tag, content):
        _tag = tag.lower().strip()
        if _tag == "instancecount":
            pass
        elif tag == "instanceseparation":
            pass
        elif tag == "radialdirection":
            pass
        elif tag == "angleoffset":
            pass
        elif _tag == "radius" or _tag == "outerradius":
            if str(content).lower() == "auto":
                # self._obj.OuterDiameter = "0.0 m" - use the object default
                if hasattr(self._obj.Proxy, "setOuterRadiusAutomatic"):
                    self._obj.Proxy.setOuterRadiusAutomatic(True)
            else:
                diameter = float(content) * 2.0
                if hasattr(self._obj.Proxy, "setOuterRadius"):
                    self._obj.Proxy.setOuterRadius(FreeCAD.Units.Quantity(str(diameter) + " m").Value)
                if hasattr(self._obj.Proxy, "setOuterRadiusAutomatic"):
                    self._obj.Proxy.setOuterRadiusAutomatic(False)
        elif _tag == "length":
            self.onLength(FreeCAD.Units.Quantity(content + " m").Value)
        elif _tag == "thickness":
            self.onThickness(FreeCAD.Units.Quantity(content + " m").Value)
        else:
            super().handleEndTag(tag, content)

    def onPositionType(self, value):
        self._obj.LocationReference = value

    def onPosition(self, position):
        self._obj.Location = position

    def onThickness(self, length):
        self._obj.Thickness = length

    def onLength(self, content):
        if hasattr(self._obj.Proxy, "setLength"):
            self._obj.Proxy.setLength(content)

    def onThickness(self, content):
        if hasattr(self._obj.Proxy, "setThickness"):
            self._obj.Proxy.setThickness(content)
