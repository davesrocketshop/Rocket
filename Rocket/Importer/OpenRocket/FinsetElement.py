# ***************************************************************************
# *   Copyright (c) 2021-2024 David Carter <dcarter@davidcarter.ca>         *
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
"""Provides support for importing Open Rocket files."""

__title__ = "FreeCAD Open Rocket Importer"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

import FreeCAD

from Rocket.Importer.OpenRocket.ComponentElement import ExternalComponentElement
from Rocket.Utilities import _err
from Rocket.Constants import FIN_CROSS_SAME, FIN_CROSS_SQUARE, FIN_CROSS_ROUND, FIN_CROSS_AIRFOIL

class FinsetElement(ExternalComponentElement):

    def __init__(self, parent, tag, attributes, parentObj, filename, line):
        super().__init__(parent, tag, attributes, parentObj, filename, line)

        self._knownTags.extend(["fincount", "instancecount", "rotation", "angleoffset", "radiusoffset", "thickness", "crosssection", "cant",
                                "tabheight", "tablength", "tabposition", "filletradius", "filletmaterial"])


    def handleEndTag(self, tag, content):
        _tag = tag.lower().strip()
        if _tag == "fincount":
            if int(content) > 1:
                self._feature._obj.FinSet = True
                self._feature._obj.FinCount = int(content)
                self._feature._obj.FinSpacing = 360.0 / int(content)
            else:
                self._feature._obj.FinSet = False
        elif _tag == "thickness":
            thickness = FreeCAD.Units.Quantity(content + " m").Value
            self._feature._obj.RootThickness = thickness
            self._feature._obj.TipThickness = thickness
        elif _tag == "rotation":
            rotation = FreeCAD.Units.Quantity(content + " deg").Value
            self._feature._obj.AngleOffset = rotation
        elif _tag == "cant":
            cant = FreeCAD.Units.Quantity(content + " deg").Value
            self._feature._obj.Cant = cant
        elif _tag == "crosssection":
            if content == 'square':
                self._feature._obj.RootCrossSection = FIN_CROSS_SQUARE
            elif content == 'rounded':
                self._feature._obj.RootCrossSection = FIN_CROSS_ROUND
            elif content == 'airfoil':
                self._feature._obj.RootCrossSection = FIN_CROSS_AIRFOIL
            else:
                _err("Unrecognized fin cross section %s" % content)
                self._feature._obj.RootCrossSection = FIN_CROSS_SQUARE
            self._feature._obj.TipCrossSection = FIN_CROSS_SAME
        elif _tag == "tabheight":
            self._feature._obj.Ttw = True # Should we check that height is greater than 0.0001?
            self._feature._obj.TtwHeight = FreeCAD.Units.Quantity(content + " m").Value
        elif _tag == "tablength":
            self._feature._obj.TtwLength = FreeCAD.Units.Quantity(content + " m").Value
        elif _tag == "tabposition":
            self._feature._obj.TtwOffset = FreeCAD.Units.Quantity(content + " m").Value
        else:
            super().handleEndTag(tag, content)

    def end(self):
        return super().end()
