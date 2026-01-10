# SPDX-License-Identifier: LGPL-2.1-or-later
# SPDX-FileCopyrightText: 2021 David Carter <dcarter@davidcarter.ca>
# SPDX-File-Notice: Part of the Rocket addon.


"""Provides support for importing Open Rocket files."""

__title__ = "FreeCAD Open Rocket Importer"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

import FreeCAD
import Part
import Sketcher

from Rocket.Importer.OpenRocket.SaxElement import Element
from Rocket.Importer.OpenRocket.FinsetElement import FinsetElement
from Rocket.Constants import FIN_TYPE_SKETCH

from Ui.Commands.CmdFin import makeFin
from Ui.Commands.CmdSketcher import newSketchNoEdit

class FreeformFinpoints(Element):

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
        newPoints = []
        for point in self.points:
            newPoints.append((point[0], point[1]))
        self.points = newPoints

        last = self.points[-1]
        for index, point in enumerate(self.points):
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
        FreeCAD.ActiveDocument.recompute([self.sketch]) # Compute the sketch
        return super().end()

class FreeformFinsetElement(FinsetElement):

    def __init__(self, parent, tag, attributes, parentObj, filename, line):
        super().__init__(parent, tag, attributes, parentObj, filename, line)

        self._shoulderCapped = False

        self._validChildren.update({ 'finpoints' : FreeformFinpoints,
                              })

    def makeObject(self):
        self.sketch = newSketchNoEdit()
        self._feature = makeFin()
        self._feature._obj.FinType = FIN_TYPE_SKETCH
        self._feature._obj.Profile = self.sketch
        # self._feature._obj.Group = [self.sketch]

        if self._parentObj:
            self._parentObj.addChild(self._feature)
        self.sketch.Visibility = False

    def end(self):
        self.sketch.Visibility = False

        return super().end()
