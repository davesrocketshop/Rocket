# SPDX-License-Identifier: LGPL-2.1-or-later
# SPDX-FileCopyrightText: 2021 David Carter <dcarter@davidcarter.ca>
# SPDX-File-Notice: Part of the Rocket addon.


"""Provides support for importing Open Rocket files."""

__title__ = "FreeCAD Open Rocket Importer"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

import FreeCAD

from Rocket.Importer.OpenRocket.FinsetElement import FinsetElement
from Rocket.Constants import FIN_TYPE_TRAPEZOID

from Ui.Commands.CmdFin import makeFin

class TrapezoidalFinsetElement(FinsetElement):

    def __init__(self, parent, tag, attributes, parentObj, filename, line):
        super().__init__(parent, tag, attributes, parentObj, filename, line)

        self._knownTags.extend(["rootchord", "tipchord", "sweeplength", "height"])

    def makeObject(self):
        self._feature = makeFin()
        self._feature._obj.FinType = FIN_TYPE_TRAPEZOID

        if self._parentObj:
            self._parentObj.addChild(self._feature)


    def handleEndTag(self, tag, content):
        _tag = tag.lower().strip()
        if _tag == "rootchord":
            self._feature._obj.RootChord = FreeCAD.Units.Quantity(content + " m").Value
        elif _tag == "tipchord":
            self._feature._obj.TipChord = FreeCAD.Units.Quantity(content + " m").Value
        elif _tag == "sweeplength":
            self._feature._obj.SweepLength = FreeCAD.Units.Quantity(content + " m").Value
        elif _tag == "height":
            self._feature._obj.Height = FreeCAD.Units.Quantity(content + " m").Value
        else:
            super().handleEndTag(tag, content)

    def end(self):
        # Set the sweep angle
        self._feature.sweepAngleFromLength()

        return super().end()
