# SPDX-License-Identifier: LGPL-2.1-or-later
# SPDX-FileCopyrightText: 2021 David Carter <dcarter@davidcarter.ca>
# SPDX-File-Notice: Part of the Rocket addon.


"""Provides support for importing Open Rocket files."""

__title__ = "FreeCAD Open Rocket Importer Common Component"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

import FreeCAD

from Rocket.Importer.OpenRocket.RingComponentElement import RingComponentElement

class RadiusRingComponentElement(RingComponentElement):

    def __init__(self, parent, tag, attributes, parentObj, filename, line):
        super().__init__(parent, tag, attributes, parentObj, filename, line)

        self._knownTags.extend(["instancecount", "instanceseparation"])


    def handleEndTag(self, tag, content):
        _tag = tag.lower().strip()
        if _tag == "instancecount":
            self.onInstanceCount(int(content))
        elif _tag == "instanceseparation":
            self.onInstanceSeparation(FreeCAD.Units.Quantity(content + " m").Value)
        else:
            super().handleEndTag(tag, content)

    def onInstanceCount(self, count):
        if hasattr(self._feature._obj, "InstanceCount"):
            self._feature._obj.InstanceCount = count

    def onInstanceSeparation(self, value):
        if hasattr(self._feature._obj, "InstanceSeparation"):
            self._feature._obj.InstanceSeparation = value
