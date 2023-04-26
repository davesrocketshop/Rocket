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

from Rocket.Importer.Rocsim.PositionDependentElement import PositionDependentElement

from Ui.Commands.CmdCenteringRing import makeCenteringRing
from Ui.Commands.CmdBulkhead import makeBulkhead
from Ui.Commands.CmdBodyTube import makeEngineBlock, makeCoupler

class RingElement(PositionDependentElement):

    def __init__(self, parent, tag, attributes, parentObj, filename, line):
        super().__init__(parent, tag, attributes, parentObj, filename, line)

        self._knownTags.extend(["len", "material", "od", "id", "usagecode", "calcmass", "calccg", "radialloc", 
                                "radialangle", "finishcode", "serialno", "autosize"])
        
        self._id = -1
        self._innerTube = False
        self._locationLoaded = False
        self._usageCode = 0

    def makeObject(self):
        self._feature = makeCenteringRing()
        # Attach after converting to the appropriate component as required

    def handleEndTag(self, tag, content):
        _tag = tag.lower().strip()
        if _tag == "len":
            self._feature._obj.Length = FreeCAD.Units.Quantity(content + " mm").Value
        elif _tag == "id":
            self._feature._obj.CenterDiameter = FreeCAD.Units.Quantity(content + " mm").Value
        elif _tag == "od":
            self._feature._obj.Diameter = FreeCAD.Units.Quantity(content + " mm").Value
        elif _tag == "usagecode":
            self._usageCode = int(content)
        elif _tag == "material":
            self._feature._obj.Material = content
        else:
            super().handleEndTag(tag, content)
    
    def asBulkhead(self, ring):
        bulkhead = makeBulkhead()
        bulkhead.fromCenteringRing(ring)
        
        return bulkhead

    def asEngineBlock(self, ring):
        engineBlock = makeEngineBlock()
        engineBlock.fromCenteringRing(ring)
        
        return engineBlock

    def asTubeCoupler(self, ring):
        coupler = makeCoupler()
        coupler.fromCenteringRing(ring)
        
        return coupler

    def end(self):
        # Validate the nose shape here

        ring = self._feature
        if self._usageCode == 1:
            # Bulkhead
            self._feature = self.asBulkhead(ring)
            FreeCAD.ActiveDocument.removeObject(ring._obj.Name)
        elif self._usageCode == 2:
            # Engine block
            self._feature = self.asEngineBlock(ring)
            FreeCAD.ActiveDocument.removeObject(ring._obj.Name)
        elif self._usageCode == 3:
            # Sleeve
            pass
        elif self._usageCode == 4:
            # Tube coupler
            self._feature = self.asTubeCoupler(ring)
            FreeCAD.ActiveDocument.removeObject(ring._obj.Name)
        else:
            # 0, default - centering ring
            pass

        # Now ready to attach
        if self._parentObj is not None:
            self._parentObj.addChild(self._feature)

        return super().end()
