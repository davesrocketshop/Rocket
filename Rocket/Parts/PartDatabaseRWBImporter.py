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

import xml.sax

from Rocket.Parts.Retainer import Retainer

from Rocket.Parts.Utilities import _msg, _err, _toFloat, _toBoolean, _toInt
from Rocket.Parts.PartDatabaseOrcImporter import Element, ComponentElement, MaterialsElement

class RootElement(Element):

    def __init__(self, parent, tag, attributes, connection, filename, line):
        super().__init__(parent, tag, attributes, connection, filename, line)

        self._validChildren = {'rocketcomponent' : RWBComponentElement}

class RWBComponentElement(Element):

    def __init__(self, parent, tag, attributes, connection, filename, line):
        super().__init__(parent, tag, attributes, connection, filename, line)

        self._validChildren = { 'materials' : MaterialsElement,
                                'components' : ComponentsElement
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
                                'tailconeretainer' : RetainerElement
                              }

class RetainerElement(ComponentElement):

    def __init__(self, parent, tag, attributes, connection, filename, line):
        super().__init__(parent, tag, attributes, connection, filename, line)

        self._knownTags = self._knownTags + ["retainerid", "retainerod", "mmtdepth", "capdiameter", "capheight",
            "heightwithac", "heightwithsr", "flangediameter", "screwholepattern", "screwcount", "screwsize",
            "conediameterlarge", "conediametersmall", "opendiametersmall", "length", "airframetommt", "lip", "mass"]

        self._innerDiameter = (0.0, "")
        self._outerDiameter = (0.0, "")
        self._mmtDepth = (0.0, "")
        self._capDiameter = (0.0, "")
        self._capHeight = (0.0, "")
        self._heightWithAC = (0.0, "")
        self._heightWithSR = (0.0, "")
        self._flangeDiameter = (0.0, "")
        self._screwholePattern = (0.0, "")
        self._screwCount = 0
        self._screwSize = ""
        self._coneDiameterLarge = (0.0, "")
        self._coneDiameterSmall = (0.0, "")
        self._openDiameterSmall = (0.0, "")
        self._length = (0.0, "")
        self._airframeToMMT = (0.0, "")
        self._lip = (0.0, "")
        self._mass = (0.0, "")

    def handleTag(self, tag, attributes):
        _tag = tag.lower().strip()
        if _tag == "retainerid":
            self._innerDiameter = (self._innerDiameter[0], attributes['Unit'])
        elif _tag == "retainerod":
            self._outerDiameter = (self._outerDiameter[0], attributes['Unit'])
        elif _tag == "mmtdepth":
            self._mmtDepth = (self._mmtDepth[0], attributes['Unit'])
        elif _tag == "capdiameter":
            self._capDiameter = (self._capDiameter[0], attributes['Unit'])
        elif _tag == "capheight":
            self._capHeight = (self._capHeight[0], attributes['Unit'])
        elif _tag == "heightwithac":
            self._heightWithAC = (self._heightWithAC[0], attributes['Unit'])
        elif _tag == "heightwithsr":
            self._heightWithSR = (self._heightWithSR[0], attributes['Unit'])
        elif _tag == "flangediameter":
            self._flangeDiameter = (self._flangeDiameter[0], attributes['Unit'])
        elif _tag == "screwholepattern":
            self._screwholePattern = (self._screwholePattern[0], attributes['Unit'])
        elif _tag == "conediameterlarge":
            self._coneDiameterLarge = (self._coneDiameterLarge[0], attributes['Unit'])
        elif _tag == "conediametersmall":
            self._coneDiameterSmall = (self._coneDiameterSmall[0], attributes['Unit'])
        elif _tag == "opendiametersmall":
            self._openDiameterSmall = (self._openDiameterSmall[0], attributes['Unit'])
        elif _tag == "length":
            self._length = (self._length[0], attributes['Unit'])
        elif _tag == "airframetommt":
            self._airframeToMMT = (self._airframeToMMT[0], attributes['Unit'])
        elif _tag == "lip":
            self._lip = (self._lip[0], attributes['Unit'])
        elif _tag == "mass":
            self._mass = (self._mass[0], attributes['Unit'])
        else:
            super().handleTag(tag, attributes)

    def handleEndTag(self, tag, content):
        _tag = tag.lower().strip()
        if _tag == "retainerid":
            self._innerDiameter = (_toFloat(content), self._innerDiameter[1])
        elif _tag == "retainerod":
            self._outerDiameter = (_toFloat(content), self._outerDiameter[1])
        elif _tag == "mmtdepth":
            self._mmtDepth = (_toFloat(content), self._mmtDepth[1])
        elif _tag == "capdiameter":
            self._capDiameter = (_toFloat(content), self._capDiameter[1])
        elif _tag == "capheight":
            self._capHeight = (_toFloat(content), self._capHeight[1])
        elif _tag == "heightwithac":
            self._heightWithAC = (_toFloat(content), self._heightWithAC[1])
        elif _tag == "heightwithsr":
            self._heightWithSR = (_toFloat(content), self._heightWithSR[1])
        elif _tag == "flangediameter":
            self._flangeDiameter = (_toFloat(content), self._flangeDiameter[1])
        elif _tag == "screwholepattern":
            self._screwholePattern = (_toFloat(content), self._screwholePattern[1])
        elif _tag == "screwcount":
            self._screwCount = _toInt(content)
        elif _tag == "screwsize":
            self._screwSize = content.strip()
        elif _tag == "conediameterlarge":
            self._coneDiameterLarge = (_toFloat(content), self._coneDiameterLarge[1])
        elif _tag == "conediametersmall":
            self._coneDiameterSmall = (_toFloat(content), self._coneDiameterSmall[1])
        elif _tag == "opendiametersmall":
            self._openDiameterSmall = (_toFloat(content), self._openDiameterSmall[1])
        elif _tag == "length":
            self._length = (_toFloat(content), self._length[1])
        elif _tag == "airframetommt":
            self._airframeToMMT = (_toFloat(content), self._airframeToMMT[1])
        elif _tag == "lip":
            self._lip = (_toFloat(content), self._lip[1])
        elif _tag == "mass":
            self._mass =(_toFloat(content), self._mass[1])
        else:
            super().handleEndTag(tag, content)

    def setValues(self, obj):
        super().setValues(obj)

        obj._innerDiameter = self._innerDiameter
        obj._outerDiameter = self._outerDiameter
        obj._mmtDepth = self._mmtDepth
        obj._capDiameter = self._capDiameter
        obj._capHeight = self._capHeight
        obj._heightWithAC = self._heightWithAC
        obj._heightWithSR = self._heightWithSR
        obj._flangeDiameter = self._flangeDiameter
        obj._screwholePattern = self._screwholePattern
        obj._screwCount = self._screwCount
        obj._screwSize = self._screwSize
        obj._coneDiameterLarge = self._coneDiameterLarge
        obj._coneDiameterSmall = self._coneDiameterSmall
        obj._openDiameterSmall = self._openDiameterSmall
        obj._length = self._length
        obj._airframeToMMT = self._airframeToMMT
        obj._lip = self._lip
        obj._mass = self._mass

    def end(self):
        obj = Retainer()

        self.setValues(obj)
        self.validate(obj)
        self.persist(obj, self._connection)

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
