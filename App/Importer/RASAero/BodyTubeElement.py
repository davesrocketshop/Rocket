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
"""Provides support for importing RASAero files."""

__title__ = "FreeCAD RASAero Importer"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

import FreeCAD

from App.Importer.OpenRocket.SaxElement import NullElement, Element
from App.Importer.RASAero.FinElement import FinElement

from App.Constants import TYPE_CONE

from Ui.Commands.CmdBodyTube import makeBodyTube
from Ui.Commands.CmdTransition import makeTransition

class BodyTubeElement(Element):

    def __init__(self, parent, tag, attributes, parentObj, filename, line):
        super().__init__(parent, tag, attributes, parentObj, filename, line)

        self._validChildren.update({ 'fin' : FinElement,
                                # 'motormount' : MotorMountElement,
                              })
        self._knownTags.extend(["parttype", "length", "diameter", "launchlugdiameter", "launchluglength",
            "railguidediameter", "railguideheight", "launchshoearea", "location", "color",
            "boattaillength", "boattailreardiameter", "boattailoffset", "overhang"])

        self._boatTailLength = 0.0
        self._boatTailRearDiameter = 0.0

    #   <PartType>BodyTube</PartType>
    #   <Length>48</Length>
    #   <Diameter>3.08</Diameter>
    #   <LaunchLugDiameter>0</LaunchLugDiameter>
    #   <LaunchLugLength>0</LaunchLugLength>
    #   <RailGuideDiameter>0</RailGuideDiameter>
    #   <RailGuideHeight>0</RailGuideHeight>
    #   <LaunchShoeArea>0</LaunchShoeArea>
    #   <Location>15</Location>
    #   <Color>Black</Color>
    #   <BoattailLength>5.5</BoattailLength>
    #   <BoattailRearDiameter>3.07</BoattailRearDiameter>
    #   <BoattailOffset>0</BoattailOffset>
    #   <Overhang>0</Overhang>

    def makeObject(self):
        self._feature = makeBodyTube()
        if self._parentObj is not None:
            self._parentObj.addChild(self._feature)

    def handleEndTag(self, tag, content):
        _tag = tag.lower().strip()
        if _tag == "diameter":
            self._feature._obj.Diameter = FreeCAD.Units.Quantity(content + " in").Value
            self._feature._obj.AutoDiameter = False 
        elif _tag == "length":
            self._feature._obj.Length = FreeCAD.Units.Quantity(content + " in").Value
        elif _tag == "color":
            pass # Not yet implemented
        elif _tag == "boattaillength":
            self._boatTailLength = FreeCAD.Units.Quantity(content + " in").Value
        elif _tag == "boattailreardiameter":
            self._boatTailRearDiameter = FreeCAD.Units.Quantity(content + " in").Value
        elif _tag == "boattailoffset":
            pass # Not yet implemented
        elif _tag == "overhang":
            pass # Not yet implemented
        else:
            super().handleEndTag(tag, content)

    def end(self):

        return super().end()
