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
from App.Constants import STYLE_CAPPED, STYLE_HOLLOW, STYLE_SOLID
from App.Constants import FIN_TYPE_SKETCH
from App.Constants import FIN_CROSS_SAME, FIN_CROSS_SQUARE, FIN_CROSS_ROUND, FIN_CROSS_AIRFOIL

from Ui.Commands.CmdFin import makeFin
from Ui.Commands.CmdSketcher import newSketchNoEdit

class FreeformFinpoints(ComponentElement):

    def __init__(self, parent, tag, attributes, parentObj, filename, line):
        super().__init__(parent, tag, attributes, parentObj, filename, line)

        self._validChildren = {}
        self._knownTags = ["point"]

        self.sketch = parent.sketch
        self.points = []


    def handleTag(self, tag, attributes):
        _tag = tag.lower().strip()
        if _tag == "point":
            x = FreeCAD.Units.Quantity(attributes["x"] + " m").Value 
            y = FreeCAD.Units.Quantity(attributes["y"] + " m").Value
            self.points.append((x,y))
        else:
            super().handleTag(tag, attributes)

    def drawLines(self):
        # First reverse the X direction of the points
        max_x = 0
        for point in self.points:
            if point[0] > max_x:
                max_x = point[0]

        newPoints = []
        for point in self.points:
            newPoints.append((max_x - point[0], point[1]))
        self.points = newPoints

        last = self.points[-1]
        for index, point in enumerate(self.points):
            # print("draw (%s,%s)->(%s,%s)" % (last[0], last[1], point[0], point[1]))
            self.sketch.addGeometry(Part.LineSegment(FreeCAD.Vector(float(last[0]), float(last[1]), 0),
                                                        FreeCAD.Vector(float(point[0]), float(point[1]), 0)))
            self.sketch.addConstraint(Sketcher.Constraint("DistanceX", index, 2, point[0]))
            self.sketch.addConstraint(Sketcher.Constraint("DistanceY", index, 2, point[1]))
            last = point

        count = len(self.points)
        for index in range(count):
            if index == 0:
                self.sketch.addConstraint(Sketcher.Constraint("Coincident", count-1, 2, index, 1))
            else:
                self.sketch.addConstraint(Sketcher.Constraint("Coincident", index-1, 2, index, 1))

    def end(self):
        self.drawLines()
        return super().end()

class FreeformFinset(ComponentElement):

    def __init__(self, parent, tag, attributes, parentObj, filename, line):
        super().__init__(parent, tag, attributes, parentObj, filename, line)

        self._shoulderCapped = False

        self._validChildren = { 'appearance' : NullElement,
                                'finish' : NullElement,
                                'material' : NullElement,
                                'finpoints' : FreeformFinpoints,
                              }
        self._knownTags = ["position", "fincount", "rotation", "thickness", "crosssection", "cant", "finpoints"]

        self.sketch = newSketchNoEdit()
        # self._obj = makeFin()
        # self._obj.FinType = FIN_TYPE_SKETCH
        # self._obj.Profile = self.sketch
        # self.sketch.Visibility = False

        # if self._parentObj is not None:
        #     self._parentObj.addObject(self._obj)


    def handleEndTag(self, tag, content):
        _tag = tag.lower().strip()
        if _tag == "position":
            pass
        elif _tag == "fincount":
            if int(content) > 1:
                # self._obj.FinSet = True
                # self._obj.FinCount = int(content)
                pass
            else:
                # self._obj.FinSet = False
                pass
        elif _tag == "rotation":
            pass
        elif _tag == "thickness":
            thickness = float(content)
            # self._obj.RootThickness = thickness
            # self._obj.TipThickness = thickness
            pass
        elif _tag == "crosssection":
            # if content == 'Square':
            #     self._obj.RootCrossSection = FIN_CROSS_SQUARE
            # elif content == 'Rounded':
            #     self._obj.RootCrossSection = FIN_CROSS_ROUND
            # elif content == 'Airfoil':
            #     self._obj.RootCrossSection = FIN_CROSS_AIRFOIL
            # else:
            #     _err("Unrecognized fin cross section %s" % content)
            #     self._obj.RootCrossSection = FIN_CROSS_SQUARE
            # self._obj.TipCrossSection = FIN_CROSS_SAME
            pass
        elif _tag == "cant":
            pass
        else:
            super().handleEndTag(tag, content)

    def onName(self, content):
        # self._obj.Label = content
        pass

    def end(self):
        return super().end()
