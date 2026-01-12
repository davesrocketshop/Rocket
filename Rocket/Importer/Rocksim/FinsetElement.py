# SPDX-License-Identifier: LGPL-2.1-or-later
# SPDX-File-Notice: Part of the Rocket addon.

# ***************************************************************************
# *   Copyright (c) 2025 David Carter <dcarter@davidcarter.ca>              *
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

from Rocket.Importer.Rocksim.ComponentElement import ComponentElement
from Rocket.Utilities import _err
from Rocket.Constants import FIN_CROSS_SAME, FIN_CROSS_SQUARE, FIN_CROSS_ROUND, FIN_CROSS_AIRFOIL
from Rocket.Constants import FIN_TYPE_TRAPEZOID, FIN_TYPE_ELLIPSE, FIN_TYPE_SKETCH

from Ui.Commands.CmdFin import makeFin
from Ui.Commands.CmdSketcher import newSketchNoEdit

class FinsetElement(ComponentElement):

    def __init__(self, parent, tag, attributes, parentObj, filename, line):
        super().__init__(parent, tag, attributes, parentObj, filename, line)

        # avoid circular import
        from Rocket.Importer.Rocksim.AttachedPartsElement import AttachedPartsElement

        self._validChildren = { 'attachedparts' : AttachedPartsElement }

        self._knownTags.extend(["fincount", "rootchord", "tipchord", "semispan", "midchordlen", "sweepdistance",
                                "thickness", "tipshapecode", "tablength", "tabdepth", "taboffset", "radialangle",
                                "shapecode", "pointlist", "sweepmode", "sweepangle", "rocksimxnperfin",
                                "rocksimradialxnperfin", "rocksimcnaperfin", "taperratio", "cantangle", "cantpivotpoint",
                                "useconstthickness", "locmaxthick", "attachedparts", "averagechord", "effectivetipchord",
                                "autocalcgridstepx", "gridstepcountx", "useabsolutegridstepsx", "gridstepsizex",
                                "snaptosizex", "autocalcgridstepy", "gridstepcounty", "useabsolutegridstepsy", "gridstepsizey",
                                "snaptosizey"])

        self._sketch = None

    def makeObject(self):
        self._feature = makeFin()
        self._feature._obj.FinType = FIN_TYPE_TRAPEZOID # Default fin type

        if self._parentObj:
            self._parentObj.addChild(self._feature)

    def handleEndTag(self, tag, content):
        _tag = tag.lower().strip()
        # print("FinsetElement handle tag " + _tag)
        if _tag == "fincount":
            if int(content) > 1:
                self._feature._obj.FinSet = True
                self._feature._obj.FinCount = int(content)
                self._feature._obj.FinSpacing = 360.0 / int(content)
            else:
                self._feature._obj.FinSet = False
        elif _tag == "thickness":
            thickness = float(content)
            self._feature._obj.RootThickness = thickness
            self._feature._obj.TipThickness = thickness
        elif _tag == "rootchord":
            self._feature._obj.RootChord = float(content)
        elif _tag == "tipchord":
            self._feature._obj.TipChord = float(content)
        elif _tag == "sweepdistance":
            self._feature._obj.SweepLength = float(content)
        elif _tag == "semispan":
            self._feature._obj.Height = float(content)
        elif _tag == "shapecode":
            shapeCode = int(content)
            if shapeCode == 0:
                self._feature._obj.FinType = FIN_TYPE_TRAPEZOID
            elif shapeCode == 1:
                self._feature._obj.FinType = FIN_TYPE_ELLIPSE
            elif shapeCode == 2:
                # self._feature._obj.FinType = FIN_TYPE_SKETCH
                # self.createSketch()
                pass
            else:
                _err("Unrecognized fin shape code %s" % content)
        elif _tag == "pointlist":
            self.setPoints(content)
        elif _tag == "radialangle":
            self._feature._obj.AngleOffset = FreeCAD.Units.Quantity(content + " rad").Value
        elif _tag == "cantangle":
            cant = FreeCAD.Units.Quantity(content + " rad").Value
            self._feature._obj.Cant = cant
        elif _tag == "tipshapecode":
            shapeCode = int(content)
            if shapeCode == 0:
                self._feature._obj.RootCrossSection = FIN_CROSS_SQUARE
            elif shapeCode == 1:
                self._feature._obj.RootCrossSection = FIN_CROSS_ROUND
            elif shapeCode == 2:
                self._feature._obj.RootCrossSection = FIN_CROSS_AIRFOIL
            else:
                _err("Unrecognized fin cross section %s" % content)
                self._feature._obj.RootCrossSection = FIN_CROSS_SQUARE
            self._feature._obj.TipCrossSection = FIN_CROSS_SAME
        elif _tag == "tabdepth":
            depth = float(content)
            if depth > 0:
                self._feature._obj.Ttw = True
            self._feature._obj.TtwHeight = depth
        elif _tag == "tablength":
            self._feature._obj.TtwLength = float(content)
        elif _tag == "taboffset":
            self._feature._obj.TtwOffset = float(content)
        else:
            super().handleEndTag(tag, content)

    def createSketch(self):
        if self._sketch is None:
            self._sketch = newSketchNoEdit()
            self._feature._obj.FinType = FIN_TYPE_SKETCH
            self._feature._obj.Profile = self._sketch

            self._sketch.Visibility = False

    def setPoints(self, content):
        self.createSketch()

        newPoints = []
        points = content.split("|")
        for point in points:
            dims = point.split(",")
            if len(dims) == 2:
                newPoints.append((float(dims[0]), float(dims[1])))
                # print("\tpoint ({}, {})".format(dims[0], dims[1]))

        last = newPoints[-1]
        for index, point in enumerate(newPoints):
            self._sketch.addGeometry(Part.LineSegment(FreeCAD.Vector(float(last[0]), float(last[1]), 0),
                                                        FreeCAD.Vector(float(point[0]), float(point[1]), 0)))
            self._sketch.addConstraint(Sketcher.Constraint("DistanceX", index, 2, point[0]))
            self._sketch.addConstraint(Sketcher.Constraint("DistanceY", index, 2, point[1]))
            last = point

        count = len(newPoints)
        for index in range(count):
            if index == 0:
                self._sketch.addConstraint(Sketcher.Constraint("Coincident", count-1, 2, index, 1))
            else:
                self._sketch.addConstraint(Sketcher.Constraint("Coincident", index-1, 2, index, 1))
        FreeCAD.ActiveDocument.recompute([self._sketch]) # Compute the sketch

    def onLength(self, length):
        self._feature._obj.Length = length

    def end(self):
        if self._sketch:
            self._sketch.Visibility = False

        return super().end()
