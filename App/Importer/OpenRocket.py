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

import xml.sax
import FreeCAD
import FreeCADGui

from App.Exceptions import UnsupportedVersion

from App.Importer.SaxElement import Element, NullElement
from App.Importer.ComponentElement import ComponentElement
from App.Importer.NoseElement import NoseElement

from Ui.CmdBodyTube import makeBodyTube

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

        self._validChildren = { 'subcomponents' : SubComponentElement,
                              }
        self._knownTags = ["subcomponents", "designer", "appearance", "motormount", "finpoints", "motorconfiguration", "flightconfiguration", "deploymentconfiguration", "separationconfiguration", "referencetype", "customreference", "revision"]

        self._obj = FreeCAD.ActiveDocument.addObject("App::DocumentObjectGroupPython", "Rocket")

    def onName(self, content):
        self._obj.Label = content

class SubComponentElement(ComponentElement):

    def __init__(self, parent, tag, attributes, parentObj, filename, line):
        super().__init__(parent, tag, attributes, parentObj, filename, line)

        self._validChildren = { 'stage' : StageElement,
                                'nosecone' : NoseElement,
                                'bodytube' : BodyTubeElement,
                                'subcomponents' : SubComponentElement,
                                'transition' : NullElement,
                                'trapezoidfinset' : NullElement,
                                'ellipticalfinset' : NullElement,
                                'freeformfinset' : NullElement,
                                'tubefinset' : NullElement,
                                'launchlug' : NullElement,
                                'railbutton' : NullElement,
                                'engineblock' : NullElement,
                                'innertube' : NullElement,
                                'tubecoupler' : NullElement,
                                'bulkhead' : NullElement,
                                'centeringring' : NullElement,
                                'masscomponent' : NullElement,
                                'shockcord' : NullElement,
                                'parachute' : NullElement,
                                'streamer' : NullElement,
                                'boosterset' : NullElement,
                                'parallelstage' : NullElement,
                                'podset' : NullElement,
                              }
        self._knownTags = ["stage", "nosecone", "bodytube", "transition", "trapezoidfinset", "ellipticalfinset", "freeformfinset", "tubefinset", "launchlug", "railbutton",
                "engineblock", "innertube", "tubecoupler", "bulkhead", "centeringring", "masscomponent", "shockcord", "parachute", "streamer", 
                "boosterset", "parallelstage", "podset"]

class StageElement(ComponentElement):

    def __init__(self, parent, tag, attributes, parentObj, filename, line):
        super().__init__(parent, tag, attributes, parentObj, filename, line)

        self._validChildren = { 'subcomponents' : SubComponentElement,
                              }

        self._obj = FreeCAD.ActiveDocument.addObject("App::DocumentObjectGroupPython", "Rocket")
        if self._parentObj is not None:
            self._parentObj.addObject(self._obj)

    def onName(self, content):
            self._obj.Label = content

class BodyTubeElement(ComponentElement):

    def __init__(self, parent, tag, attributes, parentObj, filename, line):
        super().__init__(parent, tag, attributes, parentObj, filename, line)

        self._validChildren = { 'subcomponents' : SubComponentElement,
                              }
        self._knownTags = ["length", "thickness", "radius"]

        self._obj = makeBodyTube()
        if self._parentObj is not None:
            self._parentObj.addObject(self._obj)

    def handleEndTag(self, tag, content):
        _tag = tag.lower().strip()
        if _tag == "length":
            self._obj.Length = content + "m"
        elif _tag == "thickness":
            self._obj.Proxy.setScratch("thickness", content)
        elif _tag == "radius":
            self._obj.Proxy.setScratch("radius", content)
            if str(content).lower() == "auto":
                diameter = "0.0"
            else:
                diameter = float(content) * 2.0
            self._obj.OuterDiameter = str(diameter) + "m"
        else:
            super().handleEndTag(tag, content)

    def onName(self, content):
            self._obj.Label = content

    def end(self):
        # Auto diameters need to be calculated later
        if  self._obj.Proxy.getScratch("radius") != "auto":
            if self._obj.Proxy.isScratch("thickness"):
                thickness = float( self._obj.Proxy.getScratch("thickness"))
                diameter = float(self._obj.OuterDiameter) - 2.0 * thickness
            if diameter < 0:
                diameter = self._thickness
            self._obj.InnerDiameter = str(diameter) + "m"

        return super().end()

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
