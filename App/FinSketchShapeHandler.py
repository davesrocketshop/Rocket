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
"""Class for drawing fins"""

__title__ = "FreeCAD Fins"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"
    
import FreeCAD
import Part

from DraftTools import translate

from App.Constants import FIN_CROSS_SQUARE, FIN_CROSS_WEDGE, \
    FIN_CROSS_DIAMOND, FIN_CROSS_TAPER_LE, FIN_CROSS_TAPER_TE, FIN_CROSS_TAPER_LETE

from App.FinShapeHandler import FinShapeHandler
from App.Utilities import _err

class FinSketchShapeHandler(FinShapeHandler):

    def __init__(self, obj):
        super().__init__(obj)

    def verifyShape(self, shape):
        if shape is None:
            _err(translate('Rocket', "shape is empty"))
            return False

        if issubclass(type(shape), Part.Compound):
            _err(translate('Rocket', "Compound objects not supported"))
            return False

        # Verify the shape creates a closed face
        face = Part.Face(shape.Wires)
        if not face.isValid():
            _err(translate('Rocket', "Sketch must create a valid face"))
            return False
        return True

    def isCurved(self, shape):
        for edge in shape.Edges:
            if not issubclass(type(edge.Curve), Part.Line):
                return True
        return False

    def _pointOnLine(self, z, zmin, zmax):
        return (zmin <= z) and (zmax >= z)

    def _xOnLine(self, z, vertex1, vertex2):
        try:
            zRange = (z - vertex1.Point.z) / (vertex2.Point.z - vertex1.Point.z)

            x = (vertex2.Point.x - vertex1.Point.x) * zRange + vertex1.Point.x
        except ZeroDivisionError as ex:
            x = vertex1.Point.x
        return x

    def _zInVertex(self, z, vertexes, tolerance):
        if len(vertexes) != 2:
            _err(translate('Rocket', "Unable to handle shapes other than lines"))
            return False

        return self._pointOnLine(z, vertexes[0].Point.z - tolerance, vertexes[1].Point.z + tolerance) or \
                self._pointOnLine(z, vertexes[1].Point.z - tolerance, vertexes[0].Point.z + tolerance)

    def findChords(self, shape):
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
        for z in zArray:
            # Find the endpoints for z
            ends = []
            for edge in shape.Edges:
                if self._zInVertex(z, edge.Vertexes, tolerance):
                    # Get the x,y for z
                    x = self._xOnLine(z, edge.Vertexes[0], edge.Vertexes[1])
                    ends.append(FreeCAD.Vector(x, 0, z))

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

    def findRootChord(self, shape):
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

    def getFace(self):
        profile = self._obj.Profile
        shape = profile.Shape

        if not self.verifyShape(shape):
            return None
        else:
            return Part.Wire(shape)

    def getOffsetFace(self):
        profile = self._obj.Profile
        shape = profile.Shape

        if not self.verifyShape(shape):
            return None
        else:
            # tolerance = 10 * shape.getTolerance(1, Part.Shape)
            tolerance = 1e-3 # Small, but many orders of magnitude larger than the tolerance
            shape = shape.makeOffset2D(tolerance)

            return Part.Wire(shape)


    def curvedProfiles(self, shape):
        halfThickness = float(self._obj.RootThickness) / 2.0

        face1 = shape.copy()
        if face1 is not None:
            face1.translate(FreeCAD.Vector(0, -halfThickness, 0))

            face2 = shape.copy()
            face2.translate(FreeCAD.Vector(0,  halfThickness, 0))

            profiles = [face1, face2]
        else:
            profiles = []
        return profiles

    def _makeChord(self, chord, rootLength2, tolerance):
        height = float(chord[0].z)

        if len(chord) > 1:
            chordLength = float(chord[1].x - chord[0].x)
            offset = float(chord[1].x)
            profile = self._makeChordProfile(self._obj.RootCrossSection, offset, chordLength, float(self._obj.RootThickness), height, self._obj.RootPerCent, float(self._obj.RootLength1), rootLength2)
        elif self._obj.RootCrossSection in [FIN_CROSS_SQUARE, FIN_CROSS_WEDGE, FIN_CROSS_DIAMOND, FIN_CROSS_TAPER_LE, FIN_CROSS_TAPER_TE, FIN_CROSS_TAPER_LETE]:
            chordLength = 1e-3  # Very small chord length
            # chordLength = 2.0 * tolerance # Very small chord length
            offset = float(chord[0].x)
            profile = self._makeChordProfile(self._obj.RootCrossSection, offset, chordLength, float(self._obj.RootThickness), height, self._obj.RootPerCent, float(self._obj.RootLength1), rootLength2)
        else:
            profile = Part.Vertex(FreeCAD.Vector(float(chord[0].x), 0.0, float(chord[0].z)))

        return profile

    def straightProfiles(self, shape, tolerance):
        chords = self.findChords(shape)
        profiles = []
        rootLength2 = float(self._obj.RootLength2)

        for index in range(len(chords) - 1):
            profile1 = self._makeChord(chords[index], rootLength2, tolerance)
            profile2 = self._makeChord(chords[index + 1], rootLength2, tolerance)
            profiles.append([profile1, profile2])

        return profiles

    def _makeProfiles(self):
        shape = self.getFace()
        if shape is None:
            return []

        # print("Global Tolerance")
        # print(shape.globalTolerance(1))
        if self.isCurved(shape):
            return self.curvedProfiles(shape)
        return self.straightProfiles(shape, shape.globalTolerance(1))

    def _makeCommon(self):
        # The mask will be the fin outline, scaled very slightly
        shape = self.getOffsetFace()

        face = Part.Shape(shape) # Make copies
        face.translate(FreeCAD.Vector(0, -float(self._obj.RootThickness), 0))

        mask = Part.Face(face).extrude(FreeCAD.Vector(0, 2.0 * float(self._obj.RootThickness), 0))
        return mask

    def _makeTtw(self):
        # Create the Ttw tab - No clear root chord like regular fins
        shape = self.getFace()
        if shape is None:
            return []

        xmin, xmax = self.findRootChord(shape)

        origin = FreeCAD.Vector(float(xmax) - float(self._obj.TtwOffset) - float(self._obj.TtwLength), -0.5 * self._obj.TtwThickness, -1.0 * self._obj.TtwHeight)
        return Part.makeBox(self._obj.TtwLength, self._obj.TtwThickness, self._obj.TtwHeight, origin)
