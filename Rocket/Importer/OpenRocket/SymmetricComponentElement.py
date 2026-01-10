# SPDX-License-Identifier: LGPL-2.1-or-later
# SPDX-FileCopyrightText: 2021 David Carter <dcarter@davidcarter.ca>
# SPDX-File-Notice: Part of the Rocket addon.


"""Provides support for importing Open Rocket files."""

__title__ = "FreeCAD Open Rocket Importer Common Component"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

import FreeCAD

from Rocket.Importer.OpenRocket.ComponentElement import BodyComponentElement
from Rocket.SymmetricComponent import SymmetricComponent

class SymmetricComponentElement(BodyComponentElement):

    def __init__(self, parent, tag, attributes, parentObj, filename, line):
        super().__init__(parent, tag, attributes, parentObj, filename, line)

        self._knownTags.extend(["thickness"])


    def handleEndTag(self, tag, content):
        _tag = tag.lower().strip()
        if _tag == "thickness":
            if content == 'filled':
                self.onFilled(True)
            else:
                self.onFilled(False)
                thickness = FreeCAD.Units.Quantity(content + " m").Value
                if thickness <= 0:
                    thickness = SymmetricComponent.DEFAULT_THICKNESS
                self.onThickness(thickness)
        else:
            super().handleEndTag(tag, content)

    def onThickness(self, thickness):
        pass

    def onFilled(self, filled):
        pass
