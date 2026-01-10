# SPDX-License-Identifier: LGPL-2.1-or-later
# SPDX-File-Notice: Part of the Rocket addon.

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

from Rocket.Importer.OpenRocket.SaxElement import Element

from Rocket.Constants import TYPE_CONE

from Ui.Commands.CmdTransition import makeTransition

class BoatTailElement(Element):

    def __init__(self, parent, tag, attributes, parentObj, filename, line):
        super().__init__(parent, tag, attributes, parentObj, filename, line)

        self._shoulderCapped = False

        # self._validChildren.update({ 'subcomponents' : OpenRocket.SubElement.SubElement,
        #                       })
        self._knownTags.extend(["parttype", "length", "diameter",
                "reardiameter", "location", "color"])
    # <BoatTail>
    #   <PartType>BoatTail</PartType>
    #   <Length>5.5</Length>
    #   <Diameter>3.08</Diameter>
    #   <RearDiameter>3.07</RearDiameter>
    #   <Location>63</Location>
    #   <Color>Black</Color>
    # </BoatTail>

    def makeObject(self):
        self._feature = makeTransition()
        if self._parentObj:
            self._parentObj.addChild(self._feature)

    def handleEndTag(self, tag, content):
        _tag = tag.lower().strip()
        if _tag == "diameter":
            self._feature._obj.ForeDiameter = FreeCAD.Units.Quantity(content + " in").Value
        elif _tag == "reardiameter":
            self._feature._obj.AftDiameter = FreeCAD.Units.Quantity(content + " in").Value
        elif _tag == "length":
            self._feature._obj.Length = FreeCAD.Units.Quantity(content + " in").Value
        elif _tag == "color":
            pass # Not yet implemented
        else:
            super().handleEndTag(tag, content)

    def end(self):
        self._feature._obj.TransitionType = TYPE_CONE
        self._feature._obj.ForeShoulder = False
        self._feature._obj.AftShoulder = False

        return super().end()
