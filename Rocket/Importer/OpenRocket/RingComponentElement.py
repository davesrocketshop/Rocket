# SPDX-License-Identifier: LGPL-2.1-or-later
# SPDX-FileCopyrightText: 2021 David Carter <dcarter@davidcarter.ca>
# SPDX-File-Notice: Part of the Rocket addon.


"""Provides support for importing Open Rocket files."""

__title__ = "FreeCAD Open Rocket Importer Common Component"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

import FreeCAD

from Rocket.Importer.OpenRocket.StructuralComponentElement import StructuralComponentElement

class RingComponentElement(StructuralComponentElement):

    def __init__(self, parent, tag, attributes, parentObj, filename, line):
        super().__init__(parent, tag, attributes, parentObj, filename, line)

        self._knownTags.extend(["length", "radialposition", "radialdirection"])


    def handleEndTag(self, tag, content):
        _tag = tag.lower().strip()
        if _tag == "length":
            self.onLength(FreeCAD.Units.Quantity(content + " m").Value)
        elif _tag == "radialposition":
            pass
        elif _tag == "radialdirection":
            pass
        else:
            super().handleEndTag(tag, content)

    def onLength(self, length):
        pass
