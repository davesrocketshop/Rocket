# ***************************************************************************
# *   Copyright (c) 2021 David Carter <dcarter@davidcarter.ca>              *
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
import Part
import Sketcher

from App.Importer.SaxElement import NullElement
from App.Importer.ComponentElement import ComponentElement
from App.Utilities import _toBoolean, _err
from App.Constants import FIN_TYPE_TRAPEZOID
from App.Constants import FIN_CROSS_SAME, FIN_CROSS_SQUARE, FIN_CROSS_ROUND, FIN_CROSS_AIRFOIL

from Ui.Commands.CmdFin import makeFin
from Ui.Commands.CmdSketcher import newSketchNoEdit

class TrapezoidalFinset(ComponentElement):

    def __init__(self, parent, tag, attributes, parentObj, filename, line):
        super().__init__(parent, tag, attributes, parentObj, filename, line)

        self._shoulderCapped = False

        self._validChildren = { 'appearance' : NullElement,
                                'finish' : NullElement,
                                'material' : NullElement,
                              }
        self._knownTags = ["position", "fincount", "instancecount", "rotation", "angleoffset", "radiusoffset", "thickness", "crosssection", "cant",
                                "tabheight", "tablength", "tabposition", "filletradius", "filletmaterial", "rootchord", "tipchord", "sweeplength", "height"]

        self._obj = makeFin()
        self._obj.FinType = FIN_TYPE_TRAPEZOID

        if self._parentObj is not None:
            self._parentObj.addObject(self._obj)


    def handleEndTag(self, tag, content):
        _tag = tag.lower().strip()
        if _tag == "fincount":
            if int(content) > 1:
                self._obj.FinSet = True
                self._obj.FinCount = int(content)
            else:
                self._obj.FinSet = False
        elif _tag == "thickness":
            thickness = FreeCAD.Units.Quantity(content + " m").Value
            self._obj.RootThickness = thickness
            self._obj.TipThickness = thickness
        elif _tag == "crosssection":
            if content == 'square':
                self._obj.RootCrossSection = FIN_CROSS_SQUARE
            elif content == 'rounded':
                self._obj.RootCrossSection = FIN_CROSS_ROUND
            elif content == 'airfoil':
                self._obj.RootCrossSection = FIN_CROSS_AIRFOIL
            else:
                _err("Unrecognized fin cross section %s" % content)
                self._obj.RootCrossSection = FIN_CROSS_SQUARE
            self._obj.TipCrossSection = FIN_CROSS_SAME
        elif _tag == "tabheight":
            self._obj.Ttw = True # Should we check that height is greater than 0.0001?
            self._obj.TtwHeight = FreeCAD.Units.Quantity(content + " m").Value
        elif _tag == "tablength":
            self._obj.TtwLength = FreeCAD.Units.Quantity(content + " m").Value
        elif _tag == "tabposition":
            self._obj.TtwOffset = FreeCAD.Units.Quantity(content + " m").Value
        elif _tag == "rootchord":
            self._obj.RootChord = FreeCAD.Units.Quantity(content + " m").Value
        elif _tag == "tipchord":
            self._obj.TipChord = FreeCAD.Units.Quantity(content + " m").Value
        elif _tag == "sweeplength":
            self._obj.SweepLength = FreeCAD.Units.Quantity(content + " m").Value
        elif _tag == "height":
            self._obj.Height = FreeCAD.Units.Quantity(content + " m").Value
        else:
            super().handleEndTag(tag, content)

    def onName(self, content):
        self._obj.Label = content

    def end(self):
        return super().end()
