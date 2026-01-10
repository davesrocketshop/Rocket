# SPDX-License-Identifier: LGPL-2.1-or-later
# SPDX-FileCopyrightText: 2021 David Carter <dcarter@davidcarter.ca>
# SPDX-File-Notice: Part of the Rocket addon.


"""Provides support for importing Open Rocket files."""

__title__ = "FreeCAD Open Rocket Importer"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

from Rocket.Importer.OpenRocket.SaxElement import NullElement
from Rocket.Importer.OpenRocket.ComponentElement import ComponentElement
import Rocket.Importer.OpenRocket as OpenRocket

from Ui.Commands.CmdStage import makeStage

class StageElement(ComponentElement):

    def __init__(self, parent, tag, attributes, parentObj, filename, line):
        super().__init__(parent, tag, attributes, parentObj, filename, line)

        self._validChildren = { 'subcomponents' : OpenRocket.SubElement.SubElement,
                                'separationconfiguration' : NullElement,
                              }

        self._knownTags.extend(["separationevent", "separationdelay"])

    def makeObject(self):
        self._feature = makeStage()
        if self._parentObj:
            self._parentObj.addChild(self._feature)
