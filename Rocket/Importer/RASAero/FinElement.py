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
"""Provides support for importing RASAero files."""

__title__ = "FreeCAD RASAero Importer"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

import FreeCAD

from Rocket.Importer.OpenRocket.SaxElement import Element

from Rocket.Utilities import _err
from Rocket.Constants import FIN_CROSS_SAME, FIN_CROSS_SQUARE, FIN_CROSS_ROUND, FIN_CROSS_AIRFOIL, FIN_CROSS_DIAMOND, \
            FIN_CROSS_BICONVEX, FIN_CROSS_WEDGE, FIN_CROSS_TAPER_LE, FIN_CROSS_TAPER_LETE
from Rocket.Constants import FIN_TYPE_TRAPEZOID
from Rocket.Constants import LOCATION_PARENT_BOTTOM
from Rocket.position.AxialMethod import AXIAL_METHOD_MAP

from Ui.Commands.CmdFin import makeFin

class FinElement(Element):

    def __init__(self, parent, tag, attributes, parentObj, filename, line):
        super().__init__(parent, tag, attributes, parentObj, filename, line)

        self._knownTags.extend(["count", "chord", "span", "sweepdistance", "tipchord", "thickness", "leradius", "location",
                                "airfoilsection", "fx1", "fx3"])
        
        self._location = 0

    #   <Fin>
    #     <Count>3</Count>
    #     <Chord>7</Chord>
    #     <Span>2.5</Span>
    #     <SweepDistance>3.75</SweepDistance>
    #     <TipChord>1.75</TipChord>
    #     <Thickness>0.125</Thickness>
    #     <LERadius>0</LERadius>
    #     <Location>7</Location>
    #     <AirfoilSection>Hexagonal</AirfoilSection>
    #     <FX1>0.5</FX1>
    #     <FX3>0.5</FX3>
    #   </Fin>

    def makeObject(self):
        self._feature = makeFin()
        self._feature._obj.FinType = FIN_TYPE_TRAPEZOID

        if self._parentObj is not None:
            self._parentObj.addChild(self._feature)

    def handleEndTag(self, tag, content):
        _tag = tag.lower().strip()
        if _tag == "count":
            if int(content) > 1:
                self._feature._obj.FinSet = True
                self._feature._obj.FinCount = int(content)
                self._feature._obj.FinSpacing = 360.0 / int(content)
            else:
                self._feature._obj.FinSet = False
        elif _tag == "airfoilsection":
            _content = content.lower().strip()
            if _content == 'hexagonal':
                self._feature._obj.RootCrossSection = FIN_CROSS_TAPER_LETE
            elif _content == 'subsonic naca':
                self._feature._obj.RootCrossSection = FIN_CROSS_AIRFOIL
            elif _content == 'double wedge':
                self._feature._obj.RootCrossSection = FIN_CROSS_DIAMOND
            elif _content == 'biconvex':
                self._feature._obj.RootCrossSection = FIN_CROSS_BICONVEX
            elif _content == 'single wedge':
                self._feature._obj.RootCrossSection = FIN_CROSS_WEDGE
            elif _content == 'hexagonal blunt base':
                self._feature._obj.RootCrossSection = FIN_CROSS_TAPER_LE
            elif _content == 'rounded':
                self._feature._obj.RootCrossSection = FIN_CROSS_ROUND
            elif _content == 'square':
                self._feature._obj.RootCrossSection = FIN_CROSS_SQUARE
            else:
                _err("Unrecognized fin cross section %s" % content)
                self._feature._obj.RootCrossSection = FIN_CROSS_SQUARE
            self._feature._obj.TipCrossSection = FIN_CROSS_SAME
        elif _tag == "thickness":
            thickness = FreeCAD.Units.Quantity(content + " in").Value
            self._feature._obj.RootThickness = thickness
            self._feature._obj.TipThickness = thickness
        elif _tag == "chord":
            self._feature._obj.RootChord = FreeCAD.Units.Quantity(content + " in").Value
        elif _tag == "span":
            self._feature._obj.Height = FreeCAD.Units.Quantity(content + " in").Value
        elif _tag == "sweepdistance":
            self._feature._obj.SweepLength = FreeCAD.Units.Quantity(content + " in").Value
        elif _tag == "tipchord":
            self._feature._obj.TipChord = FreeCAD.Units.Quantity(content + " in").Value
        elif _tag == "leradius":
            #self._feature._obj.RootChord = FreeCAD.Units.Quantity(content + " in").Value
            pass
        elif _tag == "fx1":
            self._feature._obj.RootLength1 = FreeCAD.Units.Quantity(content + " in").Value
            self._feature._obj.TipLength1 = self._feature._obj.RootLength1
        elif _tag == "fx3":
            self._feature._obj.RootLength2 = FreeCAD.Units.Quantity(content + " in").Value
            self._feature._obj.TipLength2 = self._feature._obj.RootLength2
        elif _tag == "location":
            self._location = FreeCAD.Units.Quantity(content + " in").Value
        else:
            super().handleEndTag(tag, content)

    def onPositionType(self, value):
        if hasattr(self._feature._obj, "LocationReference"):
            self._feature._obj.LocationReference = value
        if hasattr(self._feature._obj, "AxialMethod"):
            self._feature._obj.AxialMethod = AXIAL_METHOD_MAP[value]

    def onAxialOffset(self, content):
        if hasattr(self._feature._obj, "Location"):
            self._feature._obj.Location = content
        if hasattr(self._feature._obj, "AxialOffset"):
            self._feature._obj.AxialOffset = content

    def end(self):
        self._feature._obj.TipSameThickness = True
        self._feature._obj.RootPerCent = False
        self._feature._obj.TipPerCent = False

        # Set the sweep angle
        self._feature.sweepAngleFromLength()

        if self._location != 0:
            self._location -= float(self._feature._obj.RootChord)
            self.onPositionType(LOCATION_PARENT_BOTTOM)
            self.onAxialOffset(self._location)

        return super().end()
