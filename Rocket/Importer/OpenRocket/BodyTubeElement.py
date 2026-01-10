# SPDX-License-Identifier: LGPL-2.1-or-later
# SPDX-FileCopyrightText: 2021 David Carter <dcarter@davidcarter.ca>
# SPDX-File-Notice: Part of the Rocket addon.


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
        if self._parentObj:
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
        if self._parentObj:
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
        if self._parentObj:
            self._parentObj.addChild(self._feature)

class EngineBlockElement(BodyTubeElement):

    def __init__(self, parent, tag, attributes, parentObj, filename, line):
        super().__init__(parent, tag, attributes, parentObj, filename, line)

        self._knownTags.extend(["radialposition", "radialdirection"])

    def makeObject(self):
        self._feature = makeEngineBlock()
        if self._parentObj:
            self._parentObj.addChild(self._feature)
