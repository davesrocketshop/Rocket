# SPDX-License-Identifier: LGPL-2.1-or-later
# SPDX-FileCopyrightText: 2021 David Carter <dcarter@davidcarter.ca>
# SPDX-File-Notice: Part of the Rocket addon.


"""Provides support for importing Open Rocket files."""

__title__ = "FreeCAD Open Rocket Importer"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

import FreeCAD

from Rocket.Importer.OpenRocket.BodyTubeElement import BodyTubeElement
from Rocket.ClusterConfiguration import CONFIGURATIONS
from Ui.Commands.CmdBodyTube import makeInnerTube

from Rocket.Utilities import _err

translate = FreeCAD.Qt.translate

class InnerTubeElement(BodyTubeElement):

    def __init__(self, parent, tag, attributes, parentObj, filename, line):
        super().__init__(parent, tag, attributes, parentObj, filename, line)

        self._knownTags.extend(["radialposition", "radialdirection", "clusterconfiguration", "clusterscale", "clusterrotation"])

    def makeObject(self):
        self._feature = makeInnerTube()
        if self._parentObj:
            self._parentObj.addChild(self._feature)

    def handleEndTag(self, tag, content):
        _tag = tag.lower().strip()
        if _tag == "clusterconfiguration":
            self.onClusterConfiguration(content)
        elif _tag == "clusterscale":
            self.onClusterScale(float(content))
        elif _tag == "clusterrotation":
            self.onClusterRotation(FreeCAD.Units.Quantity(str(content) + " deg").Value)
        else:
            super().handleEndTag(tag, content)

    def onClusterConfiguration(self, name):
        try:
            # self._feature._obj.ClusterConfiguration = CONFIGURATIONS[name]
            pass # Not yet complete
        except:
            _err(translate('Rocket', "Unknown cluster configuration"))

    def onClusterScale(self, value):
        self._feature._obj.ClusterScale = value

    def onClusterRotation(self, value):
        self._feature._obj.ClusterRotation = value
