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

import math
import os
import re

import xml.etree.ElementTree as ET
import xml.sax

from App.Tools.Utilities import _msg, _err, _trace, _toFloat, _toBoolean
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

from App.Constants import TYPE_CONE, TYPE_ELLIPTICAL, TYPE_HAACK, TYPE_OGIVE, TYPE_VON_KARMAN, TYPE_PARABOLA, TYPE_PARABOLIC, TYPE_POWER
from App.Constants import MATERIAL_TYPE_BULK

class Element:

    def __init__(self, parent, tag, attributes, connection):
        self._tag = tag
        self._parent = parent
        self._connection = connection
        
        self._validChildren = {}
        self._knownTags = []
        print("Start %s" % tag)

    def end(self):
        # print("End %s" % self._tag)
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

    def createChild(self, tag, attributes):
        _tag = tag.lower().strip()
        if not _tag in self._validChildren:
            print("Invalid element %s" % tag)
            return None
        return self._validChildren[_tag](self, tag, attributes, self._connection)

class RootElement(Element):

    def __init__(self, parent, tag, attributes, connection):
        super().__init__(parent, tag, attributes, connection)

        self._validChildren = {'openrocketcomponent' : OpenRocketComponentElement}

class OpenRocketComponentElement(Element):

    def __init__(self, parent, tag, attributes, connection):
        super().__init__(parent, tag, attributes, connection)

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

    def __init__(self, parent, tag, attributes, connection):
        super().__init__(parent, tag, attributes, connection)

        self._validChildren = { 'material' : MaterialElement,
                                'components' : ComponentsElement
                              }

    def validChildren(self):
        return ['material']

    # def createChild(self, tag, attributes):
    #     return MaterialElement(self, tag, attributes)

class MaterialElement(Element):

    def __init__(self, parent, tag, attributes, connection):
        super().__init__(parent, tag, attributes, connection)

        self._validChildren = {}
        self._knownTags = ["name", "type", "density"]
        self._supportedVersions = ["0.1"]

        self._manufacturer = ""
        self._name = ""
        self._type = None
        self._density = 0.0
        self._units = attributes["UnitsOfMeasure"]

    def handleEndTag(self, tag, content):
        _tag = tag.lower().strip()
        if _tag == "name":
            self._name = content
        elif _tag == "type":
            self._type = content
        elif _tag == "density":
            self._type = _toFloat(content.strip())
        else:
            super().handleEndTag(tag, content)

    def end(self):
        material = Material()

        # Manufacturer is unknown
        material._name = self._name
        material._type = self._type
        material._density = self._density
        material._units = self._units

        if not material.isValid():
            _err("Invalid material")

        return super().end()

class ComponentsElement(Element):

    def __init__(self, parent, tag, attributes, connection):
        super().__init__(parent, tag, attributes, connection)

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

    def __init__(self, parent, tag, attributes, connection):
        super().__init__(parent, tag, attributes, connection)

        self._validChildren = {}
        self._knownTags = ["manufacturer", "partnumber", "description", "material", "mass"]

        self._manufacturer = ""
        self._partNumber = ""
        self._description = ""
        self._material = ("", MATERIAL_TYPE_BULK)
        self._mass = (0.0, "")

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
            self._manufacturer = content
        elif _tag == "partnumber":
            self._partNumber = content
        elif _tag == "description":
            self._description = content
        elif _tag == "material":
            self._material = (content, self._material[1])
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

    def end(self):
        return super().end()

class BodyTubeElement(ComponentElement):

    def __init__(self, parent, tag, attributes, connection):
        super().__init__(parent, tag, attributes, connection)

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
            obj = LaunchLug()
        else:
            _err("Unable to close body tube object for %s" % self._tag)
            return super().end()

        super().setValues(obj)
        obj._ID = self._ID
        obj._OD = self._OD
        obj._length = self._length

        if not obj.isValid():
            _err("Invalid %s" % self._tag)

        return super().end()

class BulkheadElement(ComponentElement):
    pass

class TransitionElement(ComponentElement):

    def __init__(self, parent, tag, attributes, connection):
        super().__init__(parent, tag, attributes, connection)

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

    def end(self):
        obj = Transition()

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

        if not obj.isValid():
            _err("Invalid %s" % self._tag)

        return super().end()

class ParachuteElement(ComponentElement):
    pass

class StreamerElement(ComponentElement):
    pass

class NoseConeElement(ComponentElement):
    pass

class PartDatabaseOrcImporter(xml.sax.ContentHandler):
    def __init__(self, connection):
        self._connection = connection
        self._current = RootElement(None, "root", None, self._connection)
        self._content = ''

    # Call when an element starts
    def startElement(self, tag, attributes):
        if self._current.isChildElement(tag):
            self._current = self._current.createChild(tag, attributes)
            self._content = ''
        else:
            self._current.handleTag(tag, attributes)

    # Call when an elements ends
    def endElement(self, tag):
        if self._current.isTag(tag):
            self._current = self._current.end()
            self._content = ''
        else:
            self._current.handleEndTag(tag, self._content)


    # Call when a character is read
    def characters(self, content):
        self._content = content

class PartDatabaseOrcImporterX(object):

    def __init__(self, doc, connection):
        self._doc = doc
        self._connection = connection

    def processComponentTag(self, parent, child):
        # Tags common to all components
        SUPPORTED_TAGS = []

        tag = child.tag.strip().lower()
        if tag == "manufacturer":
            _trace("processComponentTag", "Processing '%s'" % child.tag)
            parent._manufacturer = child.text.strip()
            return True
        elif tag == "partnumber":
            _trace("processComponentTag", "Processing '%s'" % child.tag)
            parent._partNumber = child.text.strip()
            return True
        elif tag == "description":
            _trace("processComponentTag", "Processing '%s'" % child.tag)
            parent._description = child.text.strip()
            return True
        elif tag == "material":
            _trace("processComponentTag", "Processing '%s'" % child.tag)
            parent._material = (child.text, child.attrib['Type'])
            return True
        elif tag == "mass":
            _trace("processComponentTag", "Processing '%s'" % child.tag)
            parent._mass = (_toFloat(child.text), child.attrib['Unit'])
            return True
        elif tag in SUPPORTED_TAGS:
            _trace("processComponentTag", "unprocessed component tag '%s'" % (child.tag))
            return True

        return False # Tag was not handled

    # def processNosecone(self, parent, context):
    #     # Tags that are recognized but currently ignored
    #     SUPPORTED_TAGS = ["manufacturer", "partno", "description", "thickness", "shape", "shapeclipped", "shapeparameter", "aftradius", "aftouterdiameter", "aftshoulderradius", "aftshoulderdiameter", "aftshoulderlength", "aftshoulderthickness", "aftshouldercapped", "length"]

    #     nose = NoseconeComponent(self._doc)
    #     for child in context:
    #         tag = child.tag.strip().lower()
    #         if tag == "manufacturer":
    #             _trace("processNosecone", "Processing '%s'" % child.tag)
    #             nose._manufacturer = child.text
    #         elif tag == "partno":
    #             _trace("processNosecone", "Processing '%s'" % child.tag)
    #             nose._partNo = child.text
    #         elif tag == "description":
    #             _trace("processNosecone", "Processing '%s'" % child.tag)
    #             nose._description = child.text
    #         elif tag == "thickness":
    #             _trace("processNosecone", "Processing '%s'" % child.tag)
    #             nose._thickness = float(child.text)
    #         elif tag == "shape":
    #             _trace("processNosecone", "Processing '%s'" % child.tag)
    #             nose._shape = child.text
    #         elif tag == "shapeclipped":
    #             _trace("processNosecone", "Processing '%s'" % child.tag)
    #             nose._shapeClipped = _toBoolean(child.text)
    #         elif tag == "shapeparameter":
    #             _trace("processNosecone", "Processing '%s'" % child.tag)
    #             nose._shapeParameter = float(child.text)
    #         elif tag == "aftradius":
    #             _trace("processNosecone", "Processing '%s'" % child.tag)
    #             nose._aftRadius = float(child.text)
    #         elif tag == "aftouterdiameter":
    #             _trace("processNosecone", "Processing '%s'" % child.tag)
    #             nose._aftRadius = float(child.text) / 2.0
    #         elif tag == "aftshoulderradius":
    #             _trace("processNosecone", "Processing '%s'" % child.tag)
    #             nose._aftShoulderRadius = float(child.text)
    #         elif tag == "aftshoulderdiameter":
    #             _trace("processNosecone", "Processing '%s'" % child.tag)
    #             nose._aftShoulderRadius = 2.0 * float(child.text)
    #         elif tag == "aftshoulderlength":
    #             _trace("processNosecone", "Processing '%s'" % child.tag)
    #             nose._aftShoulderLength = float(child.text)
    #         elif tag == "aftshoulderthickness":
    #             _trace("processNosecone", "Processing '%s'" % child.tag)
    #             nose._aftShoulderThickness = float(child.text)
    #         elif tag == "aftshouldercapped":
    #             _trace("processNosecone", "Processing '%s'" % child.tag)
    #             nose._aftShoulderCapped = _toBoolean(child.text)
    #         elif tag == "length":
    #             _trace("processNosecone", "Processing '%s'" % child.tag)
    #             nose._length = float(child.text)
    #         elif tag in SUPPORTED_TAGS:
    #             _trace("processNosecone", "unprocessed tag '%s'" % (child.tag))
    #         elif not self.processComponentTag(nose, child):
    #             _trace("processNosecone", "unrecognized tag '%s'" % (child.tag))

    #     return nose

    # def processAxialStage(self, parent, context):
    #     # Tags that are recognized but currently ignored
    #     SUPPORTED_TAGS = []

    #     stage = AxialStageComponent(self._doc)
    #     for child in context:
    #         tag = child.tag.strip().lower()
    #         if tag == "subcomponents":
    #             _trace("processAxialStage", "Processing '%s'" % child.tag)
    #             self.processRocketSubComponents(stage, child)
    #         elif tag in SUPPORTED_TAGS:
    #             _trace("processAxialStage", "unprocessed tag '%s'" % (child.tag))
    #         elif not self.processComponentTag(stage, child):
    #             _trace("processAxialStage", "unrecognized tag '%s'" % (child.tag))

    #     return stage

    def processComponents(self, parent, context):
        # Tags that are recognized but currently ignored
        SUPPORTED_TAGS = ["bodytube", "transition", "trapezoidfinset", "ellipticalfinset", "freeformfinset", "tubefinset", "launchlug", "railbutton",
                "engineblock", "innertube", "tubecoupler", "bulkhead", "centeringring", "masscomponent", "shockcord", "parachute", "streamer", 
                "boosterset", "parallelstage", "podset"]

        for child in context:
            tag = child.tag.strip().lower()
            if tag == 'stage':
                _trace("processComponents", "Processing '%s'" % child.tag)
                stage = self.processAxialStage(parent, child)
                if stage is not None:
                    parent.append(stage)
            elif tag == 'nosecone':
                _trace("processComponents", "Processing '%s'" % child.tag)
                nose = self.processNosecone(parent, child)
                if nose is not None:
                    parent.append(nose)
            elif tag in SUPPORTED_TAGS:
                _trace("processComponents", "unprocessed tag '%s'" % (child.tag))
            #elif not self.processComponentTag(parent, child):
            else:
                _trace("processComponents", "unrecognized tag '%s'" % (child.tag))

    def processMaterials(self, context):
        # Tags that are recognized but currently ignored
        SUPPORTED_TAGS = []

        # Initialize material properties
        self._units = context.attrib['UnitsOfMeasure']
        for child in context:
            tag = child.tag.strip().lower()
            if tag == "name":
                _trace("processMaterials", "Processing '%s'" % child.tag)
                parent._name = child.text
            elif tag == "type":
                _trace("processMaterials", "Processing '%s'" % child.tag)
                parent._type = child.text
            elif tag == "density":
                parent._density = _toFloat(child.text)
            elif tag in SUPPORTED_TAGS:
                _trace("processMaterials", "unprocessed tag '%s'" % (child.tag))
            elif not self.processComponentTag(rocket, child):
                _trace("processMaterials", "unrecognized tag '%s'" % (child.tag))

        self._rocket = rocket

    def importParts(self):

        # Tags that are recognized but currently ignored
        SUPPORTED_TAGS = []
        SUPPORTED_VERSIONS = ["0.1"]

        root = self._doc.getroot()
        if root.tag != "openrocket":
            _err("unsupported root node %s" % (root.tag))
            return
        else:
            ork_version = root.get("version")
            ork_creator = root.get("creator")
            _trace("process", "process(%s, %s)" % (ork_version, ork_creator))
            if ork_version not in SUPPORTED_VERSIONS:
                _err("unsupported version")
                return

            for child in root:
                tag = child.tag.strip().lower()
                if tag == "materials":
                    _trace("process", "Processing '%s'" % child.tag)
                    self.processMaterials(child)
                if tag == "components":
                    _trace("process", "Processing '%s'" % child.tag)
                    # self.processComponents(child)
                elif tag in SUPPORTED_TAGS:
                    _trace("process", "unprocessed tag '%s'" % (child.tag))
                elif not self.processComponentTag(parent, context):
                    _trace("process", "unrecognized tag '%s'" % (child.tag))
