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

from Rocket.Importer.OpenRocket.SaxElement import NullElement
from Rocket.Importer.OpenRocket.ComponentElement import BodyComponentElement
from Rocket.Importer.OpenRocket.SymmetricComponentElement import SymmetricComponentElement
import Rocket.Importer.OpenRocket as OpenRocket

from Ui.Commands.CmdBodyTube import makeBodyTube, makeCoupler, makeEngineBlock

class MotorMountElement(BodyComponentElement):

    def __init__(self, parent, tag, attributes, parentObj, filename, line):
        super().__init__(parent, tag, attributes, parentObj, filename, line)

        self._validChildren.update({ 'motor' : NullElement,
                              })
        self._knownTags.extend(["overhang", "ignitionevent", "ignitiondelay", "ignitionconfiguration"])

    def makeObject(self):
        if self._parentObj is not None:
            self._feature = self._parentObj
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

        self._validChildren.update({ 'subcomponents' : OpenRocket.SubElement.SubElement,
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
            if self.isAuto(content):
                self._feature._obj.AutoDiameter = True
            else:
                diameter = float(content) * 2.0
                self._feature._obj.Diameter = str(diameter) + "m"
                self._feature._obj.AutoDiameter = False
        else:
            super().handleEndTag(tag, content)

    def onThickness(self, length):
        self._feature._obj.Thickness = length

    def onLength(self, length):
        self._feature._obj.Length = length

class TubeCouplerElement(BodyTubeElement):

    def __init__(self, parent, tag, attributes, parentObj, filename, line):
        super().__init__(parent, tag, attributes, parentObj, filename, line)

        self._knownTags.extend(["radialposition", "radialdirection"])

    def makeObject(self):
        self._feature = makeCoupler()
        if self._parentObj is not None:
            self._parentObj.addChild(self._feature)

class EngineBlockElement(BodyTubeElement):

    def __init__(self, parent, tag, attributes, parentObj, filename, line):
        super().__init__(parent, tag, attributes, parentObj, filename, line)

        self._knownTags.extend(["radialposition", "radialdirection"])

    def makeObject(self):
        self._feature = makeEngineBlock()
        if self._parentObj is not None:
            self._parentObj.addChild(self._feature)
