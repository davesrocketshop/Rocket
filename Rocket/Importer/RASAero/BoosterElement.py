# SPDX-License-Identifier: LGPL-2.1-or-later
# SPDX-FileCopyrightText: 2021 David Carter <dcarter@davidcarter.ca>
# SPDX-File-Notice: Part of the Rocket addon.


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

class BoosterElement(BodyTubeElement):

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
