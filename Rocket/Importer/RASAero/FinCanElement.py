# SPDX-License-Identifier: LGPL-2.1-or-later

# ***************************************************************************
# *   Copyright (c) 2021-2025 David Carter <dcarter@davidcarter.ca>         *
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

from Rocket.Importer.OpenRocket.SaxElement import NullElement, Element
from Rocket.Importer.RASAero.BodyTubeElement import BodyTubeElement

from Rocket.Constants import TYPE_CONE

from Ui.Commands.CmdBodyTube import makeBodyTube
from Ui.Commands.CmdTransition import makeTransition
from Ui.Commands.CmdStage import makeStage, addToStage

class FinCanElement(BodyTubeElement):

    def __init__(self, parent, tag, attributes, parentObj, filename, line):
        super().__init__(parent, tag, attributes, parentObj, filename, line)

        self._knownTags.extend(["insidediameter", "shoulderlength", "nozzleexitdiameter"])

        self._transitionFore = 0.0
        self._transitionLength = 0.0

    #   <PartType>Booster</PartType>
    #   <Length>62</Length>
    #   <Diameter>4.05</Diameter>
    #   <InsideDiameter>3.08</InsideDiameter>
    #   <LaunchLugDiameter>0</LaunchLugDiameter>
    #   <LaunchLugLength>0</LaunchLugLength>
    #   <RailGuideDiameter>0</RailGuideDiameter>
    #   <RailGuideHeight>0</RailGuideHeight>
    #   <LaunchShoeArea>0.0331</LaunchShoeArea>
    #   <Location>63</Location>
    #   <ShoulderLength>1.75</ShoulderLength>
    #   <Color>Black</Color>
    #   <NozzleExitDiameter>0</NozzleExitDiameter>
    #   <BoattailLength>0</BoattailLength>
    #   <BoattailRearDiameter>0</BoattailRearDiameter>

    def makeObject(self):
        stage = makeStage()
        self._feature = makeBodyTube()
        if stage:
            addToStage(stage)
            self._parentObj = stage
            # stage.addChild(self._feature)

    def handleEndTag(self, tag, content):
        _tag = tag.lower().strip()
        if _tag == "insidediameter":
            self._transitionFore = FreeCAD.Units.Quantity(content + " in").Value
        elif _tag == "shoulderlength":
            self._transitionLength = FreeCAD.Units.Quantity(content + " in").Value
        elif _tag == "nozzleexitdiameter":
            pass # Not yet implemented
        else:
            super().handleEndTag(tag, content)

    def end(self):
        if self._transitionLength > 0:
            # Add a boat tail
            transition = makeTransition()
            transition._obj.TransitionType = TYPE_CONE
            transition._obj.ForeShoulder = False
            transition._obj.AftShoulder = False
            transition._obj.ForeDiameter = self._transitionFore
            transition._obj.AftDiameter = self._feature._obj.Diameter
            transition._obj.Length = self._transitionLength

            self._parentObj.addChild(transition)

        if self._parentObj:
            self._parentObj.addChild(self._feature)

        if self._boatTailLength > 0:
            # Add a boat tail
            boattail = makeTransition()
            boattail._obj.TransitionType = TYPE_CONE
            boattail._obj.ForeShoulder = False
            boattail._obj.AftShoulder = False
            boattail._obj.ForeDiameter = self._feature._obj.Diameter
            boattail._obj.AftDiameter = self._boatTailRearDiameter
            boattail._obj.Length = self._boatTailLength

            self._parentObj.addChild(boattail)

        return super().end()
