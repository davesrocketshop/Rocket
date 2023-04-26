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
"""Provides support for importing Rocsim files."""

__title__ = "FreeCAD Rocsim Importer"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

import FreeCAD

from Rocket.Importer.Rocsim.BaseElement import BaseElement
from Rocket.Importer.Rocsim.AttachedPartsElement import AttachedPartsElement
from Rocket.Importer.Rocsim.Utilities import getAxialMethodFromCode
from Rocket.position import AxialMethod

from Ui.Commands.CmdBodyTube import makeBodyTube, makeInnerTube

class BodyTubeElement(BaseElement):

    def __init__(self, parent, tag, attributes, parentObj, filename, line):
        super().__init__(parent, tag, attributes, parentObj, filename, line)

        self._validChildren.update({ 'attachedparts' : AttachedPartsElement,
                              })
        self._knownTags.extend(["xb", "calcmass", "calccg", "radialloc", "radialangle", "locationmode", "len", 
                                "finishcode", "serialno", "shapecode", "constructiontype", "wallthickness", "shapeparameter", 
                                "attachedparts", "material", "od", "id", "ismotormount", "motordia", "engineoverhang", "isinsidetube"])
        
        self._id = -1
        self._innerTube = False
        self._locationLoaded = False

    def makeObject(self):
        self._feature = makeBodyTube()
        # Attach after converting to an inner tube, if required

    def handleEndTag(self, tag, content):
        _tag = tag.lower().strip()
        if _tag == "len":
            self.onLength(FreeCAD.Units.Quantity(content + " mm").Value)
        elif _tag == "id":
            self._id = FreeCAD.Units.Quantity(content + " mm").Value
        elif _tag == "od":
            self._feature._obj.AutoDiameter = False
            self._feature._obj.Diameter = FreeCAD.Units.Quantity(content + " mm").Value
        elif _tag == "ismotormount":
            self._feature._obj.MotorMount = (int(content) > 0)
        elif _tag == "engineoverhang":
            self._feature._obj.Overhang = FreeCAD.Units.Quantity(content + " mm").Value
        elif _tag == "isinsidetube":
            self._innerTube = (int(content) > 0)
        elif _tag == "xb":
            offset = float(FreeCAD.Units.Quantity(content + " mm").Value)
            if isinstance(self._feature.getAxialMethod(), AxialMethod.BottomAxialMethod):
                self._feature._obj.AxialOffset = -offset
            self._locationLoaded = True
        elif _tag == "locationmode":
            self._feature._obj.AxialMethod = getAxialMethodFromCode(int(content))
            # If the location is loaded before the axialMethod, we still need to correct for the different relative distance direction
            if self._locationLoaded:
                if isinstance(self._feature.getAxialMethod(), AxialMethod.BottomAxialMethod):
                    self._feature._obj.AxialOffset = -self._feature._obj.AxialOffset
        else:
            super().handleEndTag(tag, content)

    def onLength(self, length):
        self._feature._obj.Length = length

    def convertToInnerTube(self, bodyTube):
        inner = makeInnerTube()
        inner.fromBodyTube(bodyTube)

        return inner

    def end(self):
        # Validate the nose shape here
        if not self._feature._obj.AutoDiameter and self._id > 0:
            thickness = (float(self._feature._obj.Diameter) - float(self._id)) / 2.0
            self._feature._obj.Thickness = thickness

        if self._innerTube:
            bodyTube = self._feature
            self._feature = self.convertToInnerTube(bodyTube)
            FreeCAD.ActiveDocument.removeObject(bodyTube._obj.Name)

        # Now ready to attach
        if self._parentObj is not None:
            self._parentObj.addChild(self._feature)

        return super().end()
