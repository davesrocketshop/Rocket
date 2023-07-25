# ***************************************************************************
# *   Copyright (c) 2021-2023 David Carter <dcarter@davidcarter.ca>         *
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
"""Provides support for importing Rocsim files."""

__title__ = "FreeCAD Rocsim Importer"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

import FreeCAD
import Part
import Sketcher

from Rocket.Importer.Rocsim.BaseElement import BaseElement
from Rocket.Importer.Rocsim.Utilities import getAxialMethodFromCode
from Rocket.position import AxialMethod
from Rocket.Constants import FIN_TYPE_TRAPEZOID, FIN_TYPE_ELLIPSE, FIN_TYPE_SKETCH
from Rocket.Constants import FIN_CROSS_SAME, FIN_CROSS_SQUARE, FIN_CROSS_ROUND, FIN_CROSS_AIRFOIL

from Ui.Commands.CmdFin import makeFin
from Ui.Commands.CmdSketcher import newSketchNoEdit

from DraftTools import translate

class FinSetElement(BaseElement):

    def __init__(self, parent, tag, attributes, parentObj, filename, line):
        super().__init__(parent, tag, attributes, parentObj, filename, line)

        # self._validChildren.update({ 'attachedparts' : AttachedPartsElement,
        #                       })
        self._knownTags.extend(["xb", "calcmass", "calccg", "radialloc", "radialangle", "locationmode", "len", 
                                "finishcode", "serialno", "fincount", "rootchord", "tipchord", "semispan", "midchordlen",
                                "sweepdistance", "thickness", "tipshapecode", "tablength", "tabdepth", "taboffset", 
                                "shapecode", "pointlist", "calcmass", "calccg", "material", "sweepmode", "cantangle"
                                ])
        
        self._id = -1
        self._innerTube = False
        self._locationLoaded = False
        self._location = 0
        self.sketch = None

    def makeObject(self):
        self._feature = makeFin()
        if self._parentObj is not None:
            self._parentObj.addChild(self._feature)

    def handleEndTag(self, tag, content):
        _tag = tag.lower().strip()
        if _tag == "material":
            self._feature._obj.Material = content
        elif _tag == "finishcode":
            pass
        elif _tag == "xb":
            self._location = float(FreeCAD.Units.Quantity(content + " mm").Value)
            if isinstance(self._feature.getAxialMethod(), AxialMethod.BottomAxialMethod):
                self._feature._obj.AxialOffset = -self._location
            else:
                self._feature._obj.AxialOffset = self._location
            self._locationLoaded = True
        elif _tag == "locationmode":
            self._feature._obj.AxialMethod = getAxialMethodFromCode(int(content))
            # If the location is loaded before the axialMethod, we still need to correct for the different relative distance direction
            if self._locationLoaded:
                if isinstance(self._feature.getAxialMethod(), AxialMethod.BottomAxialMethod):
                    self._feature._obj.AxialOffset = -self._location
                else:
                    self._feature._obj.AxialOffset = self._location
        elif _tag == "fincount":
            self._feature._obj.FinCount = int(content)
            self._feature._obj.FinSpacing = 360.0 / int(content)
            self._feature._obj.FinSet = (self._feature._obj.FinCount > 1)
        elif _tag == "rootchord":
            self._feature._obj.RootChord = FreeCAD.Units.Quantity(content + " mm").Value
        elif _tag == "tipchord":
            self._feature._obj.TipChord = FreeCAD.Units.Quantity(content + " mm").Value
        elif _tag == "semispan":
            self._feature._obj.Height = FreeCAD.Units.Quantity(content + " mm").Value
        elif _tag == "sweepdistance":
            self._feature._obj.SweepLength = FreeCAD.Units.Quantity(content + " mm").Value
        elif _tag == "thickness":
            thickness = FreeCAD.Units.Quantity(content + " mm").Value
            self._feature._obj.RootThickness = thickness
            self._feature._obj.TipThickness = thickness
        elif _tag == "tipshapecode":
            shapeCode = int(content)
            if shapeCode == 1:
                self._feature._obj.RootCrossSection = FIN_CROSS_ROUND
            elif shapeCode == 2:
                self._feature._obj.RootCrossSection = FIN_CROSS_AIRFOIL
            else:
                self._feature._obj.RootCrossSection = FIN_CROSS_SQUARE
            self._feature._obj.TipCrossSection = FIN_CROSS_SAME
        elif _tag == "tablength":
            self._feature._obj.TtwLength = FreeCAD.Units.Quantity(content + " mm").Value
        elif _tag == "tabdepth":
            self._feature._obj.TtwHeight = FreeCAD.Units.Quantity(content + " mm").Value
            self._feature._obj.Ttw = (self._feature._obj.TtwHeight > 0.0001)
        elif _tag == "taboffset":
            self._feature._obj.TtwOffset = FreeCAD.Units.Quantity(content + " mm").Value
        elif _tag == "radialangle":
            rotation = FreeCAD.Units.Quantity(content + " rad").Value
            self._feature._obj.AngleOffset = rotation
        elif _tag == "shapecode":
            shapeCode = int(content)
            if shapeCode == 0:
                self._feature._obj.FinType = FIN_TYPE_TRAPEZOID
            elif shapeCode == 1:
                self._feature._obj.FinType = FIN_TYPE_ELLIPSE
            elif shapeCode == 2:
                self._feature._obj.FinType = FIN_TYPE_SKETCH
            else:
                raise Exception(translate("Exception", "Unknown fin type {0}").format(content))
        elif _tag == "pointlist":
            self.makeSketch(content)
        else:
            super().handleEndTag(tag, content)

    def end(self):
        # Validate the nose shape here
        if not self._feature._obj.AutoDiameter and self._id > 0:
            thickness = (float(self._feature._obj.Diameter) - float(self._id)) / 2.0
            self._feature._obj.Thickness = thickness

        return super().end()

    def drawLines(self, points):
        # First reverse the X direction of the points
        newPoints = []
        for point in points:
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
    
    def makeSketch(self, points):
        if len(points) <= 0:
            return

        self.sketch = newSketchNoEdit()
        self._feature._obj.Profile = self.sketch

        pointList = []
        pairs = points.split('|')
        for pair in pairs:
            if len(pair) > 0:
                point = pair.split(',')
                pointList.append((float(point[0]), float(point[1])))

        self.drawLines(pointList)
        FreeCAD.ActiveDocument.recompute([self.sketch]) # Compute the sketch
        self.sketch.Visibility = False
   

