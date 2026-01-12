# SPDX-License-Identifier: LGPL-2.1-or-later
# SPDX-File-Notice: Part of the Rocket addon.

# ***************************************************************************
# *   Copyright (c) 2025 David Carter <dcarter@davidcarter.ca>              *
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
"""Provides support for importing Rocksim files."""

__title__ = "FreeCAD Rocksim Importer"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

from io import TextIOWrapper

import xml.sax
import FreeCAD

translate = FreeCAD.Qt.translate

from Rocket.Exceptions import UnsupportedVersion

from Rocket.Importer.OpenRocket.SaxElement import NullElement, Element
from Rocket.Importer.Rocksim.StageElement import StageElement

from Rocket.Utilities import _err

from Ui.Commands.CmdRocket import makeRocket

class RootElement(Element):

    def __init__(self, parent, tag, attributes, parentObj, filename, line):
        super().__init__(parent, tag, attributes, parentObj, filename, line)

        self._validChildren = {'rocksimdocument' : RocksimElement}

class RocksimElement(Element):

    def __init__(self, parent, tag, attributes, parentObj, filename, line):
        super().__init__(parent, tag, attributes, parentObj, filename, line)

        self._validChildren = { 'fileversion' : NullElement,
                                'designinformation' : DesignElement,
                                'simulationresultslist' : NullElement,
                              }

class DesignElement(Element):

    def __init__(self, parent, tag, attributes, parentObj, filename, line):
        super().__init__(parent, tag, attributes, parentObj, filename, line)

        self._validChildren = { 'rocketdesign' : RocketElement,
                                'motorconfiguration' : NullElement,
                              }

    def handleEndTag(self, tag, content):
        _tag = tag.lower().strip()
        if _tag == "designer":
            FreeCAD.ActiveDocument.CreatedBy = content
        elif _tag == "revision":
            pass
        else:
            super().handleEndTag(tag, content)

    def onComment(self, content):
        if hasattr(self._feature, "setComment"):
            self._feature.setComment(content)

    def end(self):
        # self._feature.enableEvents()
        return self._parent

class RocketElement(Element):

    def __init__(self, parent, tag, attributes, parentObj, filename, line):
        super().__init__(parent, tag, attributes, parentObj, filename, line)

        self._validChildren = { 'cd3' : NullElement,
                                'cd32' : NullElement,
                                'cd321' : NullElement,
                                'cb3' : NullElement,
                                'cb32' : NullElement,
                                'cb321' : NullElement,
                                'cna3' : NullElement,
                                'cna32' : NullElement,
                                'cna321' : NullElement,
                                'cp3' : NullElement,
                                'cp32' : NullElement,
                                'cp321' : NullElement,
                                'simulationeventlist' : NullElement,
                                'stage3parts' : StageElement,
                                'stage2parts' : StageElement,
                                'stage1parts' : StageElement,
                              }
        self._knownTags = ["calculatecd", "procalculatecd", "procalculatecn", "fixedcd", "fixedcd2",
                           "fixedcd3", "fixedcd2alone", "fixedcd3alone", "stagecount",
                           "stage3mass", "stage2mass", "stage1mass", "stage321cg", "stage32cg", "stage3cg", "stage2cgalone",
                           "stage1cgalone", "cpcalcflags", "launchguidelength", "useknownmass", "defaultfinish",
                           "finishmedium", "finishcoatcount", "gluetype", "cpsimflags", "lastserialnumber", "displayflags",
                           "metricsflags", "barromanxn", "barrowmancna", "rocksimxn", "rocksimcna", "rocksimcna90",
                           "rocksimxn90", "viewtype", "viewstagecount", "viewtypeedit", "viewstagecountedit", "zoomfactor",
                           "zoomfactoredit", "scrollposx", "scrollposy", "scrollposxedit", "scrollposyedit", "threedflags",
                           "threedflagsedit", "usemodelsprite", "staticmarginref", "userrefdiameter", "sidemarkerheight",
                           "sidedimensionheight", "basemarkerheight", "basedimensionheight", "showglidecp", "showgridtypeside",
                           "showgridtypebase", "gridspacing", "gridopacity", "gridcolor", "maxdiawithfins", "maxdiawithoutfins",
                           "maxlenwithfins", "maxlenwithoutfins", "minxextent", "maxxextent", "calculatedmaxstagedia",
                           "calculatedstagelen", "sideviewdims", "baseviewdims", "vertviewdims", "name", "stage3parts",
                           "stage2parts", "stage1parts", "camerastate", "spritepath", "spriteprefix", "comments", "designer",
                           "revisions"]

        self._feature = makeRocket(makeSustainer=False)
        self._stageCount = 1

    def handleEndTag(self, tag, content):
        _tag = tag.lower().strip()
        if _tag == "designer":
            FreeCAD.ActiveDocument.CreatedBy = content
        elif _tag == "comment":
            self.onComment(content)
        elif _tag == "revision":
            pass
        elif _tag == "stagecount":
            self._stageCount = int(content)
        else:
            super().handleEndTag(tag, content)

    def onComment(self, content):
        if hasattr(self._feature, "setComment"):
            self._feature.setComment(content)

    def testCreateChild(self, tag):
        _tag = tag.lower().strip()
        if _tag == "stage2parts":
            return self._stageCount > 1
        if _tag == "stage1parts":
            return self._stageCount > 2
        return super().testCreateChild(tag)

    def end(self):
        self._feature.enableEvents()
        return self._parent

class RocksimImporter(xml.sax.ContentHandler):
    def __init__(self, filename):
        self._filename = filename
        self._current = RootElement(None, "root", None, None, filename, 0)
        self._content = ''

    # Call when an element starts
    def startElement(self, tag, attributes):
        loc = self._locator
        if loc:
            line = loc.getLineNumber()
        if self._current.isChildElement(tag) and self._current.testCreateChild(tag):
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
        with open(filename, "rb") as rkt:
            RocksimImporter.importRocket(doc, rkt, filename)

    def importRocket(doc, filestream, filename):
        # _msg("Importing %s..." % filename)
        rkt = TextIOWrapper(filestream)

        # create an XMLReader
        parser = xml.sax.make_parser()

        # turn off namespaces
        parser.setFeature(xml.sax.handler.feature_namespaces, 0)

        # override the default ContextHandler
        handler = RocksimImporter(filename)
        parser.setContentHandler(handler)
        try:
            parser.parse(rkt)
        except UnsupportedVersion as ex:
            _err(ex._message)
        except Exception as ex:
            _err(translate("Rocket", "Unable to complete import"))
            _err(str(ex))
