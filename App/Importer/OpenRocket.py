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

from io import TextIOWrapper
import re
import zipfile
from zipfile import ZipFile
import gzip
import xml.etree.ElementTree as ET

import xml.sax
import FreeCAD
import FreeCADGui

from App.Exceptions import UnsupportedVersion

from App.Importer.SaxElement import Element, NullElement
from App.Importer.ComponentElement import ComponentElement
from App.Importer.SubElement import SubElement
from App.Importer.NoseElement import NoseElement

from App.events.ComponentChangeEvent import ComponentChangeEvent

from App.Utilities import _msg

from Ui.Commands.CmdRocket import makeRocket

# import ptvsd
# print("Waiting for debugger attach")
# # 5678 is the default attach port in the VS Code debug configurations
# ptvsd.enable_attach(address=('localhost', 5678), redirect_output=True)
# ptvsd.wait_for_attach()

class RootElement(ComponentElement):

    def __init__(self, parent, tag, attributes, parentObj, filename, line):
        super().__init__(parent, tag, attributes, parentObj, filename, line)

        self._validChildren = {'openrocket' : OpenRocketElement}

class OpenRocketElement(ComponentElement):

    def __init__(self, parent, tag, attributes, parentObj, filename, line):
        super().__init__(parent, tag, attributes, parentObj, filename, line)

        SUPPORTED_VERSIONS = ["1.0", "1.1", "1.2", "1.3", "1.4", "1.5", "1.6", "1.7", "1.8"]

        if attributes['version'] not in SUPPORTED_VERSIONS:
            raise UnsupportedVersion("Unsupported version %s" % attributes['version'])

        self._validChildren = { 'rocket' : RocketElement,
                                'datatypes' : NullElement,
                                'simulations' : NullElement,
                              }
        self._knownTags = ["rocket", "datatypes", "simulations"]

class RocketElement(ComponentElement):

    def __init__(self, parent, tag, attributes, parentObj, filename, line):
        super().__init__(parent, tag, attributes, parentObj, filename, line)

        self._validChildren = { 'subcomponents' : SubElement,
                              }
        self._knownTags = ["subcomponents", "designer", "appearance", "motormount", "finpoints", "motorconfiguration", "flightconfiguration", "deploymentconfiguration", "separationconfiguration", "referencetype", "customreference", "revision"]

        self._feature = makeRocket(makeSustainer=False)

    def handleEndTag(self, tag, content):
        _tag = tag.lower().strip()
        if _tag == "designer":
            FreeCAD.ActiveDocument.CreatedBy = content
        elif _tag == "revision":
            pass
        else:
            super().handleEndTag(tag, content)

    def onComment(self, content):
        # FreeCAD.ActiveDocument.Comment = content
        self._feature._obj.Description = content

    def end(self):
        self._feature.enableEvents()
        return self._parent

class OpenRocketImporter(xml.sax.ContentHandler):
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
                print("Import file is .gzip format")
                OpenRocketImporter.importRocket(doc, orc, filename)
                doc.recompute(None,True,True)
                return
        except gzip.BadGzipFile:
            print("gzip.BadGzipFile")
            pass

        try:
            if zipfile.is_zipfile(filename):
                with ZipFile(filename) as orcZip:
                    print("Import file is .zip format")
                    for info in orcZip.infolist():
                        print("info name '%s'" % info.filename)
                        if re.match('.*\\.[oO][rR][kK]$', info.filename):
                            print("Match .ork")
                            with orcZip.open(info.filename) as orc:
                                OpenRocketImporter.importRocket(doc, orc, info.filename)
                        elif re.match('.*\\.[rR][kK][tT]$', info.filename):
                            with orcZip.open(info.filename) as orc:
                                OpenRocketImporter.importRocket(doc, orc, info.filename)
                return
        except zipfile.BadZipFile:
            print("zipfile.BadZipFile")
            pass

        print("Default plain file")
        with open(filename, "rb") as orc:
            OpenRocketImporter.importRocket(doc, orc, filename)

    def importRocket(doc, filestream, filename):
        # _msg("Importing %s..." % filename)
        orc = TextIOWrapper(filestream)

        # create an XMLReader
        parser = xml.sax.make_parser()

        # turn off namespaces
        parser.setFeature(xml.sax.handler.feature_namespaces, 0)

        # override the default ContextHandler
        handler = OpenRocketImporter(filename)
        parser.setContentHandler(handler)
        parser.parse(orc)
