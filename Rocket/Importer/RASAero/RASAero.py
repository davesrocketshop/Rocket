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
"""Provides support for importing RASAero files."""

__title__ = "FreeCAD Open Rocket Importer"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

from io import TextIOWrapper
import re
import zipfile
from zipfile import ZipFile
import gzip

import xml.sax
import FreeCAD
import FreeCADGui

from Rocket.Exceptions import UnsupportedVersion

from Rocket.Importer.OpenRocket.SaxElement import Element, NullElement
from Rocket.Importer.RASAero.NoseElement import NoseElement
from Rocket.Importer.RASAero.BodyTubeElement import BodyTubeElement
from Rocket.Importer.RASAero.BoatTailElement import BoatTailElement
from Rocket.Importer.RASAero.BoosterElement import BoosterElement
from Rocket.Importer.RASAero.FinElement import FinElement

from Rocket.Utilities import _err

from Ui.Commands.CmdRocket import makeRocket
from Ui.Commands.CmdStage import makeStage

from DraftTools import translate

class RootElement(Element):

    def __init__(self, parent, tag, attributes, parentObj, filename, line):
        super().__init__(parent, tag, attributes, parentObj, filename, line)

        self._validChildren = {'rasaerodocument' : RASAeroElement}

class RASAeroElement(Element):

    def __init__(self, parent, tag, attributes, parentObj, filename, line):
        super().__init__(parent, tag, attributes, parentObj, filename, line)

        self.SUPPORTED_VERSIONS = ["2"]

        self._validChildren = { 'rocketdesign' : RocketElement,
                                'launchsite' : NullElement,
                                'recovery' : NullElement,
                                'machalt' : NullElement,
                                'simulationlist' : NullElement,
                              }
        self._knownTags = ["fileversion"]

    def handleEndTag(self, tag, content):
        _tag = tag.lower().strip()
        if _tag == "fileversion":
            if content not in self.SUPPORTED_VERSIONS:
                raise UnsupportedVersion(translate("Exception", "Unsupported version %s") % content)           
        else:
            super().handleEndTag(tag, content)

class RocketElement(Element):

    def __init__(self, parent, tag, attributes, parentObj, filename, line):
        super().__init__(parent, tag, attributes, parentObj, filename, line)

        self._validChildren = { 'nosecone' : NoseElement,
                                'bodytube' : BodyTubeElement,
                                'boattail' : BoatTailElement,
                                'booster' : BoosterElement,
                                'fincan' : FinElement,
                              }
        self._knownTags = ["surface", "cp", "modifiedbarrowman", "turbulence", "sustainernozzle", "booster1nozzle", 
                "booster2nozzle", "usebooster1", "usebooster2", "comments"]

        self._rocket = makeRocket(makeSustainer=False)
        self._feature = makeStage()
        if self._rocket is not None:
            self._rocket.addChild(self._feature)

    def handleEndTag(self, tag, content):
        _tag = tag.lower().strip()
        if _tag == "comments":
            self.onComment(content)
        # elif _tag == "revision":
        #     pass
        else:
            super().handleEndTag(tag, content)

    def onComment(self, content):
        if hasattr(self._rocket, "setComment"):
            self._rocket.setComment(content)

    def end(self):
        self._rocket.enableEvents()
        return self._parent

class RASAeroImporter(xml.sax.ContentHandler):
    def __init__(self, filename):
        self._filename = filename
        self._current = RootElement(None, "root", None, None, filename, 0)
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

    def importFile(doc, filename):
        try:
            with gzip.open(filename) as orc:
                orc.peek(10)
                OpenRocketImporter.importRocket(doc, orc, filename)
                doc.recompute(None,True,True)
                return
        except gzip.BadGzipFile:
            pass

        try:
            if zipfile.is_zipfile(filename):
                with ZipFile(filename) as orcZip:
                    for info in orcZip.infolist():
                        if re.match('.*\\.[oO][rR][kK]$', info.filename):
                            with orcZip.open(info.filename) as orc:
                                OpenRocketImporter.importRocket(doc, orc, info.filename)
                        elif re.match('.*\\.[rR][kK][tT]$', info.filename):
                            with orcZip.open(info.filename) as orc:
                                OpenRocketImporter.importRocket(doc, orc, info.filename)
                return
        except zipfile.BadZipFile:
            pass

        with open(filename, "rb") as orc:
            RASAeroImporter.importRocket(doc, orc, filename)

    def importRocket(doc, filestream, filename):
        # _msg("Importing %s..." % filename)
        orc = TextIOWrapper(filestream)

        # create an XMLReader
        parser = xml.sax.make_parser()

        # turn off namespaces
        parser.setFeature(xml.sax.handler.feature_namespaces, 0)

        # override the default ContextHandler
        handler = RASAeroImporter(filename)
        parser.setContentHandler(handler)
        parser.parse(orc)
