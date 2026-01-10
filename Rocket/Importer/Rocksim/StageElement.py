# SPDX-License-Identifier: LGPL-2.1-or-later
# SPDX-FileCopyrightText: 2025 David Carter <dcarter@davidcarter.ca>
# SPDX-File-Notice: Part of the Rocket addon.


"""Provides support for importing Rocksim files."""

__title__ = "FreeCAD Rocksim Importer"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

from Rocket.Importer.Rocksim.ComponentElement import ComponentElement
from Rocket.Importer.Rocksim.NoseElement import NoseElement
from Rocket.Importer.Rocksim.BodyTubeElement import BodyTubeElement
from Rocket.Importer.Rocksim.TransitionElement import TransitionElement

from Ui.Commands.CmdStage import makeStage

class StageElement(ComponentElement):

    def __init__(self, parent, tag, attributes, parentObj, filename, line):
        super().__init__(parent, tag, attributes, parentObj, filename, line)

        self._validChildren = { 'nosecone' : NoseElement,
                                'bodytube' : BodyTubeElement,
                                'transition' : TransitionElement,
                              }

        self._knownTags.extend(["nosecone", "bodytube", "transition", "attachedparts"])

    def makeObject(self):
        self._feature = makeStage()
        if self._parentObj:
            self._parentObj.addChild(self._feature)
