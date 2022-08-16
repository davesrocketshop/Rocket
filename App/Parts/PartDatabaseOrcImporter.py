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

from pathlib import PurePath

import xml.sax

from App.Parts.Utilities import _msg, _err, _toFloat, _toBoolean, _toInt
from App.Parts.BodyTube import BodyTube
from App.Parts.Bulkhead import Bulkhead
from App.Parts.CenteringRing import CenteringRing
from App.Parts.Coupler import Coupler
from App.Parts.EngineBlock import EngineBlock
from App.Parts.LaunchLug import LaunchLug
from App.Parts.Material import Material
from App.Parts.NoseCone import NoseCone
from App.Parts.Parachute import Parachute
from App.Parts.Streamer import Streamer
from App.Parts.Transition import Transition

from App.Parts.Exceptions import InvalidError, MultipleEntryError, UnknownManufacturerError

from App.Constants import TYPE_CONE, TYPE_ELLIPTICAL, TYPE_HAACK, TYPE_OGIVE, TYPE_PARABOLA, TYPE_POWER
from App.Constants import MATERIAL_TYPE_BULK, MATERIAL_TYPE_LINE

class Element:

    def __init__(self, parent, tag, attributes, connection, filename, line):
        self._tag = tag
        self._parent = parent
        self._connection = connection
        self._filename = filename
        self._line = line
        
        self._validChildren = {}
        self._knownTags = []
        # print("Start %s" % tag)

    def end(self):
        return self._parent

    def isChildElement(self, tag):
        return str(tag).lower().strip() in self._validChildren

    def isTag(self, tag):
        return str(tag).lower() == self._tag.lower()

    def handleTag(self, tag, attributes):
        _tag = tag.lower().strip()
        if _tag in self._knownTags:
            return
        else:
            _msg('\tUnknown tag %s' % tag)

    def handleEndTag(self, tag, content):
        _tag = tag.lower().strip()
        if _tag in self._knownTags:
            return
        else:
            _msg('\tUnknown tag /%s' % tag)

    def createChild(self, tag, attributes, filename, line):
        _tag = tag.lower().strip()
        if not _tag in self._validChildren:
            print("Invalid element %s" % tag)
            return None
        return self._validChildren[_tag](self, tag, attributes, self._connection, filename, line)

class RootElement(Element):

    def __init__(self, parent, tag, attributes, connection, filename, line):
        super().__init__(parent, tag, attributes, connection, filename, line)

        self._validChildren = {'openrocketcomponent' : OpenRocketComponentElement}

class OpenRocketComponentElement(Element):

    def __init__(self, parent, tag, attributes, connection, filename, line):
        super().__init__(parent, tag, attributes, connection, filename, line)

        self._validChildren = { 'materials' : MaterialsElement,
                                'components' : ComponentsElement
                              }
        self._knownTags = ["version", "creator"]
        self._supportedVersions = ["0.1"]

    def handleEndTag(self, tag, content):
        _tag = tag.lower().strip()
        if _tag == "version":
            if content.strip() not in self._supportedVersions:
                _err("unsupported version '%s'" % content)
                # throw exception
            return
        else:
            super().handleEndTag(tag, content)

class MaterialsElement(Element):

    def __init__(self, parent, tag, attributes, connection, filename, line):
        super().__init__(parent, tag, attributes, connection, filename, line)

        self._validChildren = { 'material' : MaterialElement,
                                'components' : ComponentsElement
                              }

    def validChildren(self):
        return ['material']

class MaterialElement(Element):

    def __init__(self, parent, tag, attributes, connection, filename, line):
        super().__init__(parent, tag, attributes, connection, filename, line)

        self._validChildren = {}
        self._knownTags = ["name", "type", "density"]
        self._supportedVersions = ["0.1"]

        self._manufacturer = self._defaultManufacturer()
        self._name = ""
        self._type = None
        self._density = 0.0
        self._units = attributes["UnitsOfMeasure"]

    def _defaultManufacturer(self):
        # The default manufacturer is based on the filename
        manufacturers = {
            "preseed.orc" : "unspecified",
            "apogee.orc" : "Apogee",
            "competition_chutes.orc" : "Generic competition",
            "bluetube.orc" : "Always Ready Rocketry",
            "bms.orc" : "BalsaMachining.com",
            "estes_classic.orc" : "Estes",
            "estes_ps2.orc" : "Estes",
            "generic_materials.orc" : "unspecified",
            "giantleaprocketry.orc" : "Giant Leap",
            "loc_precision.orc" : "LOC Precision",
            "madcow.orc" : "Madcow",
            "mpc.orc" : "MPC",
            "publicmissiles.orc" : "Public Missiles",
            "quest.orc" : "Quest",
            "semroc.orc" : "SEMROC",
            "top_flight.orc" : "Top Flight Recovery"
        }

        name = PurePath(self._filename).name.lower()
        if name not in manufacturers:
            print("Unknown manufacturer for '%s'" % name)
            raise UnknownManufacturerError("Unknown manufacturer for '%s'" % name)
        return manufacturers[name]

    def _sanitizeName(self, content):
        # LOCPrecision data has [material:name...] format
        content = content.strip()
        while str(content).startswith('[material:'):
            content = content[10:].rstrip(']').strip()
        return content

    def handleEndTag(self, tag, content):
        _tag = tag.lower().strip()
        if _tag == "name":
            self._name = self._sanitizeName(content)
        elif _tag == "type":
            self._type = content
        elif _tag == "density":
            self._density = _toFloat(content.strip())
        else:
            super().handleEndTag(tag, content)

    def setValues(self, obj):
        # super().setValues(obj)

        obj._manufacturer = self._manufacturer
        obj._name = self._name
        obj._type = self._type
        obj._density = self._density
        obj._units = self._units

    def persist(self, obj):
        try:
            obj.validate()
            obj.persist(self._connection)
        except (InvalidError, MultipleEntryError) as e:
            print("Error in %s at line %s" % (self._filename, str(self._line)))
            #print ("Invalid %s: name %s %s" % (self.__class__.__name__, e._name, e._message))

    def end(self):
        obj = Material()

        self.setValues(obj)
        self.persist(obj)

        return super().end()

class ComponentsElement(Element):

    def __init__(self, parent, tag, attributes, connection, filename, line):
        super().__init__(parent, tag, attributes, connection, filename, line)

        self._validChildren = { 'bodytube' : BodyTubeElement,
                                'tubecoupler' : BodyTubeElement,
                                'transition' : TransitionElement,
                                'engineblock' : BodyTubeElement,
                                'parachute' : ParachuteElement,
                                'streamer' : StreamerElement,
                                'nosecone' : NoseConeElement,
                                'centeringring' : BodyTubeElement,
                                'bulkhead' : BulkheadElement,
                                'launchlug' : BodyTubeElement
                              }

class ComponentElement(Element):

    def __init__(self, parent, tag, attributes, connection, filename, line):
        super().__init__(parent, tag, attributes, connection, filename, line)

        self._validChildren = {}
        self._knownTags = ["manufacturer", "partnumber", "description", "material", "mass"]

        self._manufacturer = self._defaultManufacturer()
        self._partNumber = ""
        self._description = ""
        self._material = ("", MATERIAL_TYPE_BULK)
        self._mass = (0.0, "")

    def _defaultManufacturer(self):
        # The default manufacturer is based on the filename
        manufacturers = {
            "preseed.orc" : "unspecified",
            "apogee.orc" : "Apogee",
            "competition_chutes.orc" : "Generic competition",
            "bluetube.orc" : "Always Ready Rocketry",
            "bms.orc" : "BalsaMachining.com",
            "estes_classic.orc" : "Estes",
            "estes_ps2.orc" : "Estes",
            "generic_materials.orc" : "unspecified",
            "giantleaprocketry.orc" : "Giant Leap",
            "loc_precision.orc" : "LOC Precision",
            "madcow.orc" : "Madcow",
            "mpc.orc" : "MPC",
            "publicmissiles.orc" : "Public Missiles",
            "quest.orc" : "Quest",
            "semroc.orc" : "SEMROC",
            "top_flight.orc" : "Top Flight Recovery"
        }

        name = PurePath(self._filename).name.lower()
        if name not in manufacturers:
            print("Unknown manufacturer for '%s'" % name)
            raise UnknownManufacturerError("Unknown manufacturer for '%s'" % name)
        return manufacturers[name]

    def _unaliasManufacturer(self, content):
        # Ensure manufacturer names are consistent
        manufacturers = {
            "loc" : "LOC/Precision"
        }

        name = content.strip().lower()
        if name in manufacturers:
            return manufacturers[name]

        return content

    def _sanitizeName(self, content):
        # LOCPrecision data has [material:name...] format
        while str(content).startswith('[material:'):
            content = content[10:len(content) - 1]
        return content

    def handleTag(self, tag, attributes):
        _tag = tag.lower().strip()
        if _tag == "material":
            self._material = (self._material[0], attributes['Type'])
        elif _tag == "mass":
            self._mass = (self._mass[0], attributes['Unit'])
        else:
            super().handleTag(tag, attributes)

    def handleEndTag(self, tag, content):
        _tag = tag.lower().strip()
        if _tag == "manufacturer":
            self._manufacturer = self._unaliasManufacturer(content)
        elif _tag == "partnumber":
            self._partNumber = content
        elif _tag == "description":
            self._description = content
        elif _tag == "material":
            self._material = (self._sanitizeName(content), self._material[1])
        elif _tag == "mass":
            self._mass = (_toFloat(content.strip()), self._mass[1])
        else:
            super().handleEndTag(tag, content)

    def setValues(self, obj):
        obj._manufacturer = self._manufacturer
        obj._partNumber = self._partNumber
        obj._description = self._description
        obj._material = self._material
        obj._mass = self._mass

    def validate(self, obj):
        try:
            obj.validate()
        except InvalidError as e:
            print ("Invalid %s: manufacturer %s, part number %s %s" % (self.__class__.__name__, e._manufacturer, e._name, e._message))

    def end(self):
        return super().end()

    def persist(self, obj, connection):
        obj.persist(connection)

class BodyTubeElement(ComponentElement):

    def __init__(self, parent, tag, attributes, connection, filename, line):
        super().__init__(parent, tag, attributes, connection, filename, line)

        self._knownTags = self._knownTags + ["insidediameter", "outsidediameter", "length"]

        self._ID = (0.0, "")
        self._OD = (0.0, "")
        self._length = (0.0, "")

    def handleTag(self, tag, attributes):
        _tag = tag.lower().strip()
        if _tag == "insidediameter":
            self._ID = (self._ID[0], attributes['Unit'])
        elif _tag == "outsidediameter":
            self._OD = (self._OD[0], attributes['Unit'])
        elif _tag == "length":
            self._length = (self._length[0], attributes['Unit'])
        else:
            super().handleTag(tag, attributes)

    def handleEndTag(self, tag, content):
        _tag = tag.lower().strip()
        if _tag == "insidediameter":
            self._ID = (_toFloat(content), self._ID[1])
        elif _tag == "outsidediameter":
            self._OD = (_toFloat(content), self._OD[1])
        elif _tag == "length":
            self._length = (_toFloat(content), self._length[1])
        else:
            super().handleEndTag(tag, content)

    def setValues(self, obj):
        super().setValues(obj)

        obj._ID = self._ID
        obj._OD = self._OD
        obj._length = self._length

    def end(self):
        if self._tag.lower() == "bodytube":
            obj = BodyTube()
        elif self._tag.lower() == "tubecoupler":
            obj = Coupler()
        elif self._tag.lower() == "engineblock":
            obj = EngineBlock()
        elif self._tag.lower() == "launchlug":
            obj = LaunchLug()
        elif self._tag.lower() == "centeringring":
            obj = CenteringRing()
        else:
            _err("Unable to close body tube object for %s" % self._tag)
            return super().end()

        self.setValues(obj)
        self.validate(obj)
        self.persist(obj, self._connection)

        return super().end()

class BulkheadElement(ComponentElement):

    def __init__(self, parent, tag, attributes, connection, filename, line):
        super().__init__(parent, tag, attributes, connection, filename, line)

        # The 'filled' tag is recognized but not used
        self._knownTags = self._knownTags + ["filled", "outsidediameter", "length"]

        self._OD = (0.0, "")
        self._length = (0.0, "")

    def handleTag(self, tag, attributes):
        _tag = tag.lower().strip()
        if _tag == "outsidediameter":
            self._OD = (self._OD[0], attributes['Unit'])
        elif _tag == "length":
            self._length = (self._length[0], attributes['Unit'])
        else:
            super().handleTag(tag, attributes)

    def handleEndTag(self, tag, content):
        _tag = tag.lower().strip()
        if _tag == "outsidediameter":
            self._OD = (_toFloat(content), self._OD[1])
        elif _tag == "length":
            self._length = (_toFloat(content), self._length[1])
        else:
            super().handleEndTag(tag, content)

    def setValues(self, obj):
        super().setValues(obj)

        obj._OD = self._OD
        obj._length = self._length

    def end(self):
        obj = Bulkhead()

        self.setValues(obj)
        self.validate(obj)
        self.persist(obj, self._connection)

        return super().end()

class TransitionElement(ComponentElement):

    def __init__(self, parent, tag, attributes, connection, filename, line):
        super().__init__(parent, tag, attributes, connection, filename, line)

        self._knownTags = self._knownTags + ["filled", "shape", "foreoutsidediameter", "foreshoulderdiameter", "foreshoulderlength", 
            "aftoutsidediameter", "aftshoulderdiameter", "aftshoulderlength", "length", "thickness"]

        # Map import shape names to internal names. There may be multiple entries for the same type
        self._shapeMap = { "conical" : TYPE_CONE.lower(),
                           "ellipsoid" : TYPE_ELLIPTICAL.lower(),
                           "ogive" : TYPE_OGIVE.lower()
                         }
        
        self._noseType = "" # Shape
        self._filled = False

        self._foreOutsideDiameter = (0.0, "")
        self._foreShoulderDiameter = (0.0, "")
        self._foreShoulderLength = (0.0, "")
        self._aftOutsideDiameter = (0.0, "")
        self._aftShoulderDiameter = (0.0, "")
        self._aftShoulderLength = (0.0, "")
        self._length = (0.0, "")
        self._thickness = (0.0, "")

    def handleTag(self, tag, attributes):
        _tag = tag.lower().strip()
        if _tag == "foreoutsidediameter":
            self._foreOutsideDiameter = (self._foreOutsideDiameter[0], attributes['Unit'])
        elif _tag == "foreshoulderdiameter":
            self._foreShoulderDiameter = (self._foreShoulderDiameter[0], attributes['Unit'])
        elif _tag == "foreshoulderlength":
            self._foreShoulderLength = (self._foreShoulderLength[0], attributes['Unit'])
        elif _tag == "aftoutsidediameter":
            self._aftOutsideDiameter = (self._aftOutsideDiameter[0], attributes['Unit'])
        elif _tag == "aftshoulderdiameter":
            self._aftShoulderDiameter = (self._aftShoulderDiameter[0], attributes['Unit'])
        elif _tag == "aftshoulderlength":
            self._aftShoulderLength = (self._aftShoulderLength[0], attributes['Unit'])
        elif _tag == "length":
            self._length = (self._length[0], attributes['Unit'])
        else:
            super().handleTag(tag, attributes)

    def _mapShape(self, shape):
        _shape = shape.lower()
        if _shape in self._shapeMap:
            return self._shapeMap[_shape]
        return shape

    def handleEndTag(self, tag, content):
        _tag = tag.lower().strip()
        if _tag == "filled":
            self._filled = _toBoolean(content)
        elif _tag == "shape":
            self._noseType = self._mapShape(content)
        elif _tag == "foreoutsidediameter":
            self._foreOutsideDiameter = (_toFloat(content), self._foreOutsideDiameter[1])
        elif _tag == "foreshoulderdiameter":
            self._foreShoulderDiameter = (_toFloat(content), self._foreShoulderDiameter[1])
        elif _tag == "foreshoulderlength":
            self._foreShoulderLength = (_toFloat(content), self._foreShoulderLength[1])
        elif _tag == "aftoutsidediameter":
            self._aftOutsideDiameter = (_toFloat(content), self._aftOutsideDiameter[1])
        elif _tag == "aftshoulderdiameter":
            self._aftShoulderDiameter = (_toFloat(content), self._aftShoulderDiameter[1])
        elif _tag == "aftshoulderlength":
            self._aftShoulderLength = (_toFloat(content), self._aftShoulderLength[1])
        elif _tag == "length":
            self._length = (_toFloat(content), self._length[1])
        else:
            super().handleEndTag(tag, content)

    def setValues(self, obj):
        super().setValues(obj)

        obj._noseType = self._noseType
        obj._filled = self._filled

        obj._foreOutsideDiameter = self._foreOutsideDiameter
        obj._foreShoulderDiameter = self._foreShoulderDiameter
        obj._foreShoulderLength = self._foreShoulderLength
        obj._aftOutsideDiameter = self._aftOutsideDiameter
        obj._aftShoulderDiameter = self._aftShoulderDiameter
        obj._aftShoulderLength = self._aftShoulderLength
        obj._length = self._length
        obj._thickness = self._thickness

    def end(self):
        obj = Transition()

        self.setValues(obj)
        self.validate(obj)
        self.persist(obj, self._connection)

        return super().end()

class ParachuteElement(ComponentElement):

    def __init__(self, parent, tag, attributes, connection, filename, line):
        super().__init__(parent, tag, attributes, connection, filename, line)

        self._knownTags = self._knownTags + ["diameter", "sides", "linecount", "linelength", "linematerial"]

        self._diameter = (0.0, "")
        self._sides = 0
        self._lineCount = 0
        self._lineLength = (0.0, "")
        self._lineMaterial = ("unspecified", MATERIAL_TYPE_LINE)

    def handleTag(self, tag, attributes):
        _tag = tag.lower().strip()
        if _tag == "diameter":
            self._diameter = (self._diameter[0], attributes['Unit'])
        elif _tag == "linelength":
            self._lineLength = (self._lineLength[0], attributes['Unit'])
        elif _tag == "linematerial":
            self._lineMaterial = (self._lineMaterial[0], attributes['Type'])
        else:
            super().handleTag(tag, attributes)

    def handleEndTag(self, tag, content):
        _tag = tag.lower().strip()
        if _tag == "diameter":
            self._diameter = (_toFloat(content), self._diameter[1])
        elif _tag == "sides":
            self._sides = _toInt(content)
        elif _tag == "linecount":
            self._lineCount = _toInt(content)
        elif _tag == "linelength":
            self._lineLength = (_toFloat(content), self._lineLength[1])
        elif _tag == "linematerial":
            self._lineMaterial = (self._sanitizeName(content), self._lineMaterial[1])
        else:
            super().handleEndTag(tag, content)

    def setValues(self, obj):
        super().setValues(obj)

        obj._diameter = self._diameter
        obj._sides = self._sides
        obj._lineCount = self._lineCount
        obj._lineLength = self._lineLength
        obj._lineMaterial = self._lineMaterial

    def end(self):
        obj = Parachute()

        self.setValues(obj)
        self.validate(obj)
        self.persist(obj, self._connection)

        return super().end()

class StreamerElement(ComponentElement):

    def __init__(self, parent, tag, attributes, connection, filename, line):
        super().__init__(parent, tag, attributes, connection, filename, line)

        self._knownTags = self._knownTags + ["length", "width", "thickness"]

        self._length = (0.0, "")
        self._width = (0.0, "")
        self._thickness = (0.0, "")

    def handleTag(self, tag, attributes):
        _tag = tag.lower().strip()
        if _tag == "length":
            self._length = (self._length[0], attributes['Unit'])
        elif _tag == "width":
            self._width = (self._width[0], attributes['Unit'])
        elif _tag == "thickness":
            self._thickness = (self._thickness[0], attributes['Unit'])
        else:
            super().handleTag(tag, attributes)

    def handleEndTag(self, tag, content):
        _tag = tag.lower().strip()
        if _tag == "length":
            self._length = (_toFloat(content), self._length[1])
        elif _tag == "width":
            self._width = (_toFloat(content), self._width[1])
        elif _tag == "thickness":
            self._thickness = (_toFloat(content), self._thickness[1])
        else:
            super().handleEndTag(tag, content)

    def setValues(self, obj):
        super().setValues(obj)

        obj._length = self._length
        obj._width = self._width
        obj._thickness = self._thickness

    def end(self):
        obj = Streamer()

        self.setValues(obj)
        self.validate(obj)
        self.persist(obj, self._connection)

        return super().end()

class NoseConeElement(ComponentElement):

    def __init__(self, parent, tag, attributes, connection, filename, line):
        super().__init__(parent, tag, attributes, connection, filename, line)

        self._knownTags = self._knownTags + ["filled", "shape", "foreoutsidediameter", "foreshoulderdiameter", "foreshoulderlength", 
            "aftoutsidediameter", "aftshoulderdiameter", "aftshoulderlength", "length", "thickness"]

        # Map import shape names to internal names. There may be multiple entries for the same type
        self._shapeMap = { "conical" : TYPE_CONE.lower(),
                           "ellipsoid" : TYPE_ELLIPTICAL.lower(),
                           "ogive" : TYPE_OGIVE.lower(),
                           "parabolic" : TYPE_PARABOLA.lower(),
                           "haack" : TYPE_HAACK.lower(),
                           "power" : TYPE_POWER.lower()
                         }
        
        self._noseType = "" # Shape
        self._filled = False

        self._outsideDiameter = (0.0, "")
        self._shoulderDiameter = (0.0, "")
        self._shoulderLength = (0.0, "")
        self._length = (0.0, "")
        self._thickness = (0.0, "")

    def handleTag(self, tag, attributes):
        _tag = tag.lower().strip()
        if _tag == "outsidediameter":
            self._outsideDiameter = (self._outsideDiameter[0], attributes['Unit'])
        elif _tag == "shoulderdiameter":
            self._shoulderDiameter = (self._shoulderDiameter[0], attributes['Unit'])
        elif _tag == "shoulderlength":
            self._shoulderLength = (self._shoulderLength[0], attributes['Unit'])
        elif _tag == "length":
            self._length = (self._length[0], attributes['Unit'])
        elif _tag == "thickness":
            try:
                self._thickness = (self._thickness[0], attributes['Unit'])
            except KeyError:
                self._thickness = (self._thickness[0], "in")
        else:
            super().handleTag(tag, attributes)

    def _mapShape(self, shape):
        _shape = shape.lower()
        if _shape in self._shapeMap:
            return self._shapeMap[_shape]
        return shape

    def handleEndTag(self, tag, content):
        _tag = tag.lower().strip()
        if _tag == "filled":
            self._filled = _toBoolean(content)
        elif _tag == "shape":
            self._noseType = self._mapShape(content)
        elif _tag == "outsidediameter":
            self._outsideDiameter = (_toFloat(content), self._outsideDiameter[1])
        elif _tag == "shoulderdiameter":
            self._shoulderDiameter = (_toFloat(content), self._shoulderDiameter[1])
        elif _tag == "shoulderlength":
            self._shoulderLength = (_toFloat(content), self._shoulderLength[1])
        elif _tag == "length":
            self._length = (_toFloat(content), self._length[1])
        elif _tag == "thickness":
            self._thickness = (_toFloat(content), self._thickness[1])
        else:
            super().handleEndTag(tag, content)

    def setValues(self, obj):
        super().setValues(obj)

        obj._noseType = self._noseType
        obj._filled = self._filled

        obj._outsideDiameter = self._outsideDiameter
        obj._shoulderDiameter = self._shoulderDiameter
        obj._shoulderLength = self._shoulderLength
        obj._length = self._length
        obj._thickness = self._thickness

    def end(self):
        obj = NoseCone()

        self.setValues(obj)
        self.validate(obj)
        self.persist(obj, self._connection)

        return super().end()

class PartDatabaseOrcImporter(xml.sax.ContentHandler):
    def __init__(self, connection, filename):
        super().__init__()
        
        self._connection = connection
        self._filename = filename
        self._current = RootElement(None, "root", None, self._connection, filename, 0)
        self._content = ''

    # Call when an element starts
    def startElement(self, tag, attributes):
        loc = self._locator
        if loc is not None:
            line = loc.getLineNumber()
        if self._current.isChildElement(tag):
            self._current = self._current.createChild(tag, attributes, self._filename, line)
            self._content = ''
        else:
            self._current.handleTag(tag, attributes)

    # Call when an elements ends
    def endElement(self, tag):
        if self._current.isTag(tag):
            self._current = self._current.end()
        else:
            self._current.handleEndTag(tag, self._content.strip())
        self._content = ''


    # Call when a character is read
    def characters(self, content):
        self._content += content
