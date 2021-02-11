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

import FreeCAD
from FreeCAD import Vector
from draftutils.translate import translate

from App.Utilities import _msg, _err, _trace, _toFloat, _toBoolean
from App.Parts.Material import Material

class Element:

    def __init__(self, parent, tag, attributes, connection):
        self._tag = tag
        self._parent = parent
        self._connection = connection
        
        self._validChildren = {}
        self._knownTags = []
        print("Start %s" % tag)

    def end(self):
        print("End %s" % self._tag)
        return self._parent

    def isChildElement(self, tag):
        return str(tag).lower().strip() in self._validChildren

    def isTag(self, tag):
        return str(tag).lower() == self._tag.lower()

    def handleTag(self, tag):
        _tag = tag.lower().strip()
        if _tag in self._knownTags:
            return
        else:
            _msg('Unknown tag %s' % tag)

    def handleEndTag(self, tag, content):
        _tag = tag.lower().strip()
        if _tag in self._knownTags:
            return
        else:
            _msg('Unknown tag %s' % tag)

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
            super().handleEndTag(content)

class MaterialsElement(Element):

    def __init__(self, parent, tag, attributes, connection):
        super().__init__(parent, tag, attributes, connection)

        self._validChildren = { 'materials' : MaterialsElement,
                                'components' : ComponentsElement
                              }

    def validChildren(self):
        return ['material']

    def createChild(self, tag, attributes):
        return MaterialElement(self, tag, attributes)

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
            super().handleEndTag(content)

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
                                'tubecoupler' : TubeCouplerElement
                              }

class BodyTubeElement(Element):
    pass

class TubeCouplerElement(Element):
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
            self._current.handleTag(tag)

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
