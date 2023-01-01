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
from App.Importer.ComponentElement import ComponentElement, BodyComponentElement
from App.Importer.SymmetricComponentElement import SymmetricComponentElement
import App.Importer as Importer

from Ui.Commands.CmdBodyTube import makeBodyTube, makeInnerTube, makeEngineBlock

class MotorMountElement(BodyComponentElement):

    def __init__(self, parent, tag, attributes, parentObj, filename, line):
        super().__init__(parent, tag, attributes, parentObj, filename, line)

        self._validChildren.update({ 'motor' : NullElement,
                              })
        self._knownTags.extend(["overhang", "ignitionevent", "ignitiondelay"])

    def makeObject(self):
        if self._parentObj is not None:
            self._feature = self._parentObj
            # print("MotorMount parent %s" % (self._parentObj.Label))
            self._feature._obj.MotorMount = True

    def handleEndTag(self, tag, content):
        _tag = tag.lower().strip()
        if _tag == "overhang":
            self._feature._obj.Overhang = content + "m"
        else:
            super().handleEndTag(tag, content)

class BodyTubeElement(SymmetricComponentElement):

    def __init__(self, parent, tag, attributes, parentObj, filename, line):
        super().__init__(parent, tag, attributes, parentObj, filename, line)

        self._validChildren.update({ 'subcomponents' : Importer.SubElement.SubElement,
                                'motormount' : MotorMountElement,
                              })
        self._knownTags.extend(["radius", "outerradius"]) #, "motormount"]

    def makeObject(self):
        self._feature = makeBodyTube()
        if self._parentObj is not None:
            self._parentObj.addChild(self._feature)

    def handleEndTag(self, tag, content):
        _tag = tag.lower().strip()
        if _tag == "radius" or _tag == "outerradius":
            if str(content).lower() == "auto":
                # self._obj.OuterDiameter = "0.0 m" - use the object default
                self._feature._obj.AutoDiameter = True 
            else:
                diameter = float(content) * 2.0
                self._feature._obj.OuterDiameter = str(diameter) + "m"
                self._feature._obj.AutoDiameter = False 
        else:
            super().handleEndTag(tag, content)

    def onThickness(self, length):
        self._feature._obj.Thickness = length

    def onLength(self, length):
        self._feature._obj.Length = length

class InnerTubeElement(BodyTubeElement):

    def makeObject(self):
        self._feature = makeInnerTube()
        if self._parentObj is not None:
            self._parentObj.addChild(self._feature)

class EngineBlockElement(BodyTubeElement):

    def makeObject(self):
        self._feature = makeEngineBlock()
        if self._parentObj is not None:
            self._parentObj.addChild(self._feature)
