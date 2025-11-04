# ***************************************************************************
# *   Copyright (c) 2021-2025 David Carter <dcarter@davidcarter.ca>         *
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
"""Provides support for importing Rocket Workbench part files."""

__title__ = "FreeCAD Rocket Workbench Importer"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

import FreeCAD

from pathlib import PurePath

import xml.sax

from Rocket.Parts.Utilities import _msg, _err, _toFloat, _toBoolean, _toInt
from Rocket.Parts.PartDatabaseOrcImporter import Element, ComponentElement

from Rocket.Parts.Exceptions import InvalidError, MultipleEntryError, UnknownManufacturerError

from Rocket.Constants import TYPE_CONE, TYPE_ELLIPTICAL, TYPE_HAACK, TYPE_OGIVE, TYPE_PARABOLA, TYPE_POWER
from Rocket.Constants import MATERIAL_TYPE_BULK, MATERIAL_TYPE_LINE, MATERIAL_TYPE_SURFACE

class RootElement(Element):

    def __init__(self, parent, tag, attributes, connection, filename, line):
        super().__init__(parent, tag, attributes, connection, filename, line)

        self._validChildren = {'rocketcomponent' : RWBComponentElement}

class RWBComponentElement(Element):

    def __init__(self, parent, tag, attributes, connection, filename, line):
        super().__init__(parent, tag, attributes, connection, filename, line)

        self._validChildren = { 'components' : ComponentsElement
                              }
        self._knownTags = ["version", "creator", "legacy"]
        self._supportedVersions = ["0.1", "1.0"]

    def handleEndTag(self, tag, content):
        _tag = tag.lower().strip()
        if _tag == "version":
            if content.strip() not in self._supportedVersions:
                _err("unsupported version '%s'" % content)
                # throw exception
            return
        else:
            super().handleEndTag(tag, content)

class ComponentsElement(Element):

    def __init__(self, parent, tag, attributes, connection, filename, line):
        super().__init__(parent, tag, attributes, connection, filename, line)

        self._validChildren = { 'retainer' : RetainerElement,
                                'tailconeretainer' : TailconeRetainerElement
                              }

class RetainerElement(ComponentElement):

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
        # if self._tag.lower() == "bodytube":
        #     obj = BodyTube()
        # elif self._tag.lower() == "tubecoupler":
        #     obj = Coupler()
        # elif self._tag.lower() == "engineblock":
        #     obj = EngineBlock()
        # elif self._tag.lower() == "launchlug":
        #     obj = LaunchLug()
        # elif self._tag.lower() == "centeringring":
        #     obj = CenteringRing()
        # else:
        #     _err("Unable to close body tube object for %s" % self._tag)
        #     return super().end()

        # self.setValues(obj)
        # self.validate(obj)
        # self.persist(obj, self._connection)

        return super().end()

class TailconeRetainerElement(ComponentElement):

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
        # obj = Bulkhead()

        # self.setValues(obj)
        # self.validate(obj)
        # self.persist(obj, self._connection)

        return super().end()

class PartDatabaseRWBImporter(xml.sax.ContentHandler):
    def __init__(self, connection, filename):
        super().__init__()

        self._connection = connection
        self._filename = filename
        self._current = RootElement(None, "root", None, self._connection, filename, 0)
        self._content = ''

    # Call when an element starts
    def startElement(self, tag, attributes):
        loc = self._locator
        if loc:
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
