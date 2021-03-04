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

# Save the native open function to avoid collisions
if open.__module__ in ['__builtin__', 'io']:
    pythonopen = open

class OpenRocket(object):

    def __init__(self, doc):
        self._doc = doc
        self._rocket = None

    def create(self):
        if self._rocket is not None:
            self._rocket.create()

    def trace(self, method, message):
        trace = True
        if trace:
            _msg("%s:%s" % (method, message))

    def _toBoolean(self, value):
        if str(value).strip().lower() == "true":
            return True
        return False

    def processComponentTag(self, parent, child):
        # Tags common to all components
        SUPPORTED_TAGS = ["name", "color", "linestyle", "position", "axialoffset", "overridemass", "overridecg", "overridecd", 
            "overridesubcomponents", "comment", "preset"]

        tag = child.tag.strip().lower()
        if tag == "name": # Actually part of RocketComponent
            self.trace("processComponentTag", "Processing '%s'" % child.tag)
            parent._name = child.text
            return True
        elif tag == "comment": # Actually part of RocketComponent
            self.trace("processComponentTag", "Processing '%s'" % child.tag)
            parent._comment = child.text
            return True
        elif tag in SUPPORTED_TAGS:
            self.trace("processComponentTag", "unprocessed component tag '%s'" % (child.tag))
            return True

        return False # Tag was not handled

    def processNosecone(self, parent, context):
        # Tags that are recognized but currently ignored
        SUPPORTED_TAGS = ["manufacturer", "partno", "description", "thickness", "shape", "shapeclipped", "shapeparameter", "aftradius", "aftouterdiameter", "aftshoulderradius", "aftshoulderdiameter", "aftshoulderlength", "aftshoulderthickness", "aftshouldercapped", "length"]

        from App.Component.NoseconeComponent import NoseconeComponent
        nose = NoseconeComponent(self._doc)
        for child in context:
            tag = child.tag.strip().lower()
            if tag == "manufacturer":
                self.trace("processNosecone", "Processing '%s'" % child.tag)
                nose._manufacturer = child.text
            elif tag == "partno":
                self.trace("processNosecone", "Processing '%s'" % child.tag)
                nose._partNo = child.text
            elif tag == "description":
                self.trace("processNosecone", "Processing '%s'" % child.tag)
                nose._description = child.text
            elif tag == "thickness":
                self.trace("processNosecone", "Processing '%s'" % child.tag)
                nose._thickness = float(child.text)
            elif tag == "shape":
                self.trace("processNosecone", "Processing '%s'" % child.tag)
                nose._shape = child.text
            elif tag == "shapeclipped":
                self.trace("processNosecone", "Processing '%s'" % child.tag)
                nose._shapeClipped = self._toBoolean(child.text)
            elif tag == "shapeparameter":
                self.trace("processNosecone", "Processing '%s'" % child.tag)
                nose._shapeParameter = float(child.text)
            elif tag == "aftradius":
                self.trace("processNosecone", "Processing '%s'" % child.tag)
                nose._aftRadius = float(child.text)
            elif tag == "aftouterdiameter":
                self.trace("processNosecone", "Processing '%s'" % child.tag)
                nose._aftRadius = float(child.text) / 2.0
            elif tag == "aftshoulderradius":
                self.trace("processNosecone", "Processing '%s'" % child.tag)
                nose._aftShoulderRadius = float(child.text)
            elif tag == "aftshoulderdiameter":
                self.trace("processNosecone", "Processing '%s'" % child.tag)
                nose._aftShoulderRadius = 2.0 * float(child.text)
            elif tag == "aftshoulderlength":
                self.trace("processNosecone", "Processing '%s'" % child.tag)
                nose._aftShoulderLength = float(child.text)
            elif tag == "aftshoulderthickness":
                self.trace("processNosecone", "Processing '%s'" % child.tag)
                nose._aftShoulderThickness = float(child.text)
            elif tag == "aftshouldercapped":
                self.trace("processNosecone", "Processing '%s'" % child.tag)
                nose._aftShoulderCapped = self._toBoolean(child.text)
            elif tag == "length":
                self.trace("processNosecone", "Processing '%s'" % child.tag)
                nose._length = float(child.text)
            elif tag in SUPPORTED_TAGS:
                self.trace("processNosecone", "unprocessed tag '%s'" % (child.tag))
            elif not self.processComponentTag(nose, child):
                self.trace("processNosecone", "unrecognized tag '%s'" % (child.tag))

        return nose

    def processAxialStage(self, parent, context):
        # Tags that are recognized but currently ignored
        SUPPORTED_TAGS = []

        from App.Component.AxialStageComponent import AxialStageComponent
        stage = AxialStageComponent(self._doc)
        for child in context:
            tag = child.tag.strip().lower()
            if tag == "subcomponents":
                self.trace("processAxialStage", "Processing '%s'" % child.tag)
                self.processRocketSubComponents(stage, child)
            elif tag in SUPPORTED_TAGS:
                self.trace("processAxialStage", "unprocessed tag '%s'" % (child.tag))
            elif not self.processComponentTag(stage, child):
                self.trace("processAxialStage", "unrecognized tag '%s'" % (child.tag))

        return stage

    def processRocketSubComponents(self, parent, context):
        # Tags that are recognized but currently ignored
        SUPPORTED_TAGS = ["bodytube", "transition", "trapezoidfinset", "ellipticalfinset", "freeformfinset", "tubefinset", "launchlug", "railbutton",
                "engineblock", "innertube", "tubecoupler", "bulkhead", "centeringring", "masscomponent", "shockcord", "parachute", "streamer", 
                "boosterset", "parallelstage", "podset"]

        for child in context:
            tag = child.tag.strip().lower()
            if tag == 'stage':
                self.trace("processRocketSubComponents", "Processing '%s'" % child.tag)
                stage = self.processAxialStage(parent, child)
                if stage is not None:
                    parent.append(stage)
            elif tag == 'nosecone':
                self.trace("processRocketSubComponents", "Processing '%s'" % child.tag)
                nose = self.processNosecone(parent, child)
                if nose is not None:
                    parent.append(nose)
            elif tag in SUPPORTED_TAGS:
                self.trace("processRocketSubComponents", "unprocessed tag '%s'" % (child.tag))
            #elif not self.processComponentTag(parent, child):
            else:
                self.trace("processRocketSubComponents", "unrecognized tag '%s'" % (child.tag))

    def processRocket(self, context):
        # Tags that are recognized but currently ignored
        SUPPORTED_TAGS = ["motorconfiguration", "flightconfiguration", "deploymentconfiguration", "separationconfiguration", "referencetype", "customreference", "revision"]

        # Initialize rocket properties
        from App.Component.RocketComponent import RocketComponent
        rocket = RocketComponent(self._doc)
        for child in context:
            tag = child.tag.strip().lower()
            if tag == "subcomponents":
                self.trace("processRocket", "Processing '%s'" % child.tag)
                self.processRocketSubComponents(rocket, child)

            elif tag == "designer":
                self.trace("processRocket", "Processing '%s'" % child.tag)
                rocket._designer = child.tag

            elif tag == "appearance":
                self.trace("processRocket", "Processing '%s'" % child.tag)
            elif tag == "motormount":
                self.trace("processRocket", "Processing '%s'" % child.tag)
            elif tag == "finpoints":
                self.trace("processRocket", "Processing '%s'" % child.tag)
            elif tag in SUPPORTED_TAGS:
                self.trace("processRocket", "unprocessed tag '%s'" % (child.tag))
            elif not self.processComponentTag(rocket, child):
                self.trace("processRocket", "unrecognized tag '%s'" % (child.tag))

        self._rocket = rocket

    def process(self, ork):

        # Tags that are recognized but currently ignored
        SUPPORTED_TAGS = ["datatypes", "simulations"]
        SUPPORTED_VERSIONS = ["1.0", "1.1", "1.2", "1.3", "1.4", "1.5", "1.6", "1.7", "1.8"]

        root = ork.getroot()
        if root.tag != "openrocket":
            _err("unsupported root node %s" % (root.tag))
            return
        else:
            ork_version = root.get("version")
            ork_creator = root.get("creator")
            self.trace("process", "process(%s, %s)" % (ork_version, ork_creator))
            if ork_version not in SUPPORTED_VERSIONS:
                _err("unsupported version")
                return

            for child in root:
                tag = child.tag.strip().lower()
                if tag == "rocket":
                    self.trace("process", "Processing '%s'" % child.tag)
                    self.processRocket(child)
                elif tag in SUPPORTED_TAGS:
                    self.trace("process", "unprocessed tag '%s'" % (child.tag))
                elif not self.processComponentTag(parent, context):
                    self.trace("process", "unrecognized tag '%s'" % (child.tag))
