# SPDX-License-Identifier: LGPL-2.1-or-later
# SPDX-File-Notice: Part of the Rocket addon.

################################################################################
#                                                                              #
#   © 2021 David Carter <dcarter@davidcarter.ca>                               #
#                                                                              #
#   This addon is free software: you can redistribute it and/or modify         #
#   it under the terms of the GNU Lesser General Public License as             #
#   published by the Free Software Foundation, either version 2.1              #
#   of the License, or (at your option) any later version.                     #
#                                                                              #
#   This addon is distributed in the hope that it will be useful,              #
#   but WITHOUT ANY WARRANTY; without even the implied warranty                #
#   of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.                    #
#   See the GNU Lesser General Public License for more details.                #
#                                                                              #
#   You should have received a copy of the GNU Lesser General Public           #
#   License along with this addon. If not, see https://www.gnu.org/licenses    #
#                                                                              #
################################################################################


"""Class for drawing fins"""

__title__ = "FreeCAD Fins"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

from typing import Any

import FreeCAD
import Part
from Part import Shape, Wire, BSplineCurve, Vertex

translate = FreeCAD.Qt.translate

from Rocket.Constants import FIN_CROSS_SQUARE, FIN_CROSS_WEDGE, \
    FIN_CROSS_DIAMOND, FIN_CROSS_TAPER_LE, FIN_CROSS_TAPER_TE, FIN_CROSS_TAPER_LETE

from Rocket.ShapeHandlers.FinShapeHandler import FinShapeHandler
from Rocket.Utilities import _err, validationError, unsupportedError

class FinSketchShapeHandler(FinShapeHandler):

    def __init__(self, obj : Any) -> None:
        super().__init__(obj)

    def verifyShape(self, shape : Shape) -> bool:
        if shape is None:
            validationError(translate('Rocket', "shape is empty"))
            return False

        if issubclass(type(shape), Part.Compound):
            unsupportedError(translate('Rocket', "Compound objects not supported"))
            return False

        # Verify the shape creates a closed face
        face = Part.Face(shape.Wires)
        if not face.isValid():
            validationError(translate('Rocket', "Sketch must create a valid face"))
            return False
        return True

    def isCurved(self, shape : Shape) -> bool:
        for edge in shape.Edges:
            if not issubclass(type(edge.Curve), Part.Line):
                return True
        return False

    def _pointOnLine(self, z : float, zmin : float, zmax : float) -> bool:
        return (zmin <= z) and (zmax >= z)

    def _xOnLine(self, z : float, vertex1 : Vertex, vertex2 : Vertex) -> float:
        try:
            zRange = (z - vertex1.Point.z) / (vertex2.Point.z - vertex1.Point.z)

            x = (vertex2.Point.x - vertex1.Point.x) * zRange + vertex1.Point.x
        except ZeroDivisionError as ex:
            x = vertex1.Point.x
        return float(x)

    def _zInVertex(self, z : float, vertexes : list[Vertex] , tolerance : float) -> bool:
        if len(vertexes) != 2:
            _err(translate('Rocket', "Unable to handle shapes other than lines"))
            return False

        return self._pointOnLine(z, vertexes[0].Point.z - tolerance, vertexes[1].Point.z + tolerance) or \
                self._pointOnLine(z, vertexes[1].Point.z - tolerance, vertexes[0].Point.z + tolerance)

    def findChords(self, shape : Shape) -> list:
        zArray = []

        tolerance = shape.getTolerance(1, Part.Shape) # Maximum tolerance
        for v in shape.Vertexes:
            if len(zArray) < 1:
                zArray.append(v.Point.z)
            else:
                found = False
                for existing in zArray:
                    if abs(existing - v.Point.z) <= tolerance:
                        found = True
                        break

                if not found:
                    zArray.append(v.Point.z)

        zArray.sort()

        # Find all x's associated with all z's
        index = 0
        endArray = []
        self._height = -1 # Determine the height from the sketch
        for z in zArray:
            # Find the endpoints for z
            ends = []
            for edge in shape.Edges:
                if self._zInVertex(z, edge.Vertexes, tolerance):
                    # Get the x,y for z
                    x = self._xOnLine(z, edge.Vertexes[0], edge.Vertexes[1])
                    ends.append(FreeCAD.Vector(x, 0, z))
                    self._height = max(self._height, z)

            endArray.append(ends)

            index += 1

        # Use the x's to find the chords
        chords = []
        for ends in endArray:
            xmin = ends[0].x
            xmax = ends[0].x
            z = ends[0].z
            for point in ends:
                if xmin > point.x:
                    xmin = point.x
                elif xmax < point.x:
                    xmax = point.x
            if xmin == xmax:
                chords.append([FreeCAD.Vector(xmin, 0, z)])
            else:
                chords.append([FreeCAD.Vector(xmin, 0, z), FreeCAD.Vector(xmax, 0, z)])

        return chords

    def findChord(self, height: float, shape : Shape) -> tuple[float, float]:
        tolerance = shape.getTolerance(1, Part.Shape) # Maximum tolerance

        # Find all x's associated with all z's
        ends = []
        for edge in shape.Edges:
            if self._zInVertex(height, edge.Vertexes, tolerance):
                # Get the x,y for z
                x = self._xOnLine(height, edge.Vertexes[0], edge.Vertexes[1])
                ends.append(x)

        # Use the x's to find the chord
        xmin = ends[0]
        xmax = ends[0]
        for x in ends:
            if xmin > x:
                xmin = x
            elif xmax < x:
                xmax = x
        return (xmin, xmax)

    def findRootChord(self, shape : Shape) -> tuple[float, float]:
        # return self.findChord(0.0, shape)
        tolerance = shape.getTolerance(1, Part.Shape) # Maximum tolerance

        # Find all x's associated with all z's
        ends = []
        z = 0.0
        for edge in shape.Edges:
            if self._zInVertex(z, edge.Vertexes, tolerance):
                # Get the x,y for z
                x = self._xOnLine(z, edge.Vertexes[0], edge.Vertexes[1])
                ends.append(x)

        # Use the x's to find the chord
        xmin = ends[0]
        xmax = ends[0]
        for x in ends:
            if xmin > x:
                xmin = x
            elif xmax < x:
                xmax = x
        return (xmin, xmax)

    def findHeight(self) -> float:
        profile = self._obj.Profile
        shape = profile.Shape

        return shape.BoundBox.ZMax

    def getFace(self) -> Any:
        profile = self._obj.Profile
        shape = profile.Shape

        if not self.verifyShape(shape):
            return None

        return Part.Wire(shape)

    def getOffsetFace(self) -> Wire:
        profile = self._obj.Profile
        shape = profile.Shape

        if not self.verifyShape(shape):
            return None

        # tolerance = 10 * shape.getTolerance(1, Part.Shape)
        tolerance = 1e-3 # Small, but many orders of magnitude larger than the tolerance
        shape = shape.makeOffset2D(tolerance)

        return Part.Wire(shape)


    def curvedProfiles(self, shape : Shape) -> list:
        halfThickness = self._rootThickness / 2.0

        face1 = shape.copy()
        if face1:
            face1.translate(FreeCAD.Vector(0, -halfThickness, 0))

            face2 = shape.copy()
            face2.translate(FreeCAD.Vector(0,  halfThickness, 0))

            profiles = [face1, face2]
        else:
            profiles = []
        return profiles
    
    def _thicknessAtHeight(self, height : float) -> float:
        if self._height > 0 and height > 0:
            thickness = self._rootThickness - ((self._rootThickness - self._tipThickness) / 2.0 * (height/ self._height))
            return thickness
        return self._rootThickness

    def _makeChord(self, chord : list) -> Shape:
        height = float(chord[0].z)
        thickness = self._thicknessAtHeight(height)

        if len(chord) > 1:
            chordLength = float(chord[1].x - chord[0].x)
            offset = float(chord[0].x)
            l1, l2 = self._lengthsFromPercent(chordLength, self._rootPerCent,
                                            self._rootLength1, self._rootLength2)
            profile = self._makeChordProfile(self._rootCrossSection, offset, chordLength, thickness, height, l1, l2)
        elif self._rootCrossSection in [FIN_CROSS_SQUARE, FIN_CROSS_WEDGE, FIN_CROSS_DIAMOND, FIN_CROSS_TAPER_LE, FIN_CROSS_TAPER_TE, FIN_CROSS_TAPER_LETE]:
            chordLength = 1e-3  # Very small chord length
            offset = float(chord[0].x)
            l1, l2 = self._lengthsFromPercent(chordLength, self._rootPerCent,
                                            self._rootLength1, self._rootLength2)
            profile = self._makeChordProfile(self._rootCrossSection, offset, chordLength, thickness, height, l1, l2)
        else:
            profile = Part.Vertex(FreeCAD.Vector(float(chord[0].x), 0.0, float(chord[0].z)))

        return profile

    def straightProfiles(self, shape : Shape) -> list:
        chords = self.findChords(shape)
        profiles = []

        for index in range(len(chords) - 1):
            profile1 = self._makeChord(chords[index])
            profile2 = self._makeChord(chords[index + 1])
            profiles.append([profile1, profile2])

        return profiles

    def _makeAtHeightProfile(self, crossSection : str, height : float = 0.0, offset : float = 0.0) -> Wire:
        shape = self.getFace()
        if shape is None:
            return None

        if height < 0:
            xmin, xmax = self.findRootChord(shape)
        else:
            xmin, xmax = self.findChord(height, shape)
        chord = abs(xmax - xmin) + 2 * offset
        l1, l2 = self._lengthsFromPercent(chord, self._rootPerCent,
                                          self._rootLength1, self._rootLength2)
        return self._makeChordProfile(crossSection, xmin - offset, chord,
            self._rootThickness + 2.0 * offset, height, l1, l2)


    def _makeRootProfile(self, height : float = 0.0) -> Wire:
        return self._makeAtHeightProfile(self._rootCrossSection, height)

    def _makeProfiles(self) -> list:
        shape = self.getFace()
        if shape is None:
            return []

        if self.isCurved(shape):
            return self.curvedProfiles(shape)
        return self.straightProfiles(shape)

    def _makeCommon(self) -> Shape:
        # The mask will be the fin outline, scaled very slightly
        shape = self.getOffsetFace()

        face = Part.Shape(shape) # Make copies
        face.translate(FreeCAD.Vector(0, -self._rootThickness, 0))

        mask = Part.Face(face).extrude(FreeCAD.Vector(0, 2.0 * self._rootThickness, 0))
        return mask

    # def _makeTtw(self) -> Shape:
    #     # Create the Ttw tab - No clear root chord like regular fins
    #     shape = self.getFace()
    #     if shape is None:
    #         return None

    #     # xmin, xmax = self.findRootChord(shape)

    #     # origin = FreeCAD.Vector(float(xmax) - self._ttwOffset - self._ttwLength, -0.5 * self._ttwThickness, -1.0 * self._ttwHeight)
    #     origin = FreeCAD.Vector(self._ttwOffset, -0.5 * self._ttwThickness, -1.0 * self._ttwHeight)
    #     return Part.makeBox(self._ttwLength, self._ttwThickness, self._ttwHeight, origin)

    def area(self) -> float:
        #
        # Returns the areaa of the sketch
        shape = self.getFace()
        if shape is None:
            return 0.0

        face = Part.Face(shape)
        return face.Area

    def rootChordLength(self) -> float:
        shape = self.getFace()
        if shape is None:
            return 0.0
        xmin, xmax = self.findRootChord(shape)
        print(f"xmin {xmin}, xmax {xmax}")
        return abs(xmax - xmin)
