# SPDX-License-Identifier: LGPL-2.1-or-later
# SPDX-File-Notice: Part of the Rocket addon.

################################################################################
#                                                                              #
#   © 2021 David Carter <dcarter@davidcarter.ca>                               #
#                                                                              #
#   This addon is free software: you can redistribute it and/or modify         #
#   it under the terms of the GNU Lesser General Public License as             #
#   published by the Free Software Foundation, either version 2.1              #
#   of the License, or (at your option) any later version.                     #
#                                                                              #
#   This addon is distributed in the hope that it will be useful,              #
#   but WITHOUT ANY WARRANTY; without even the implied warranty                #
#   of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.                    #
#   See the GNU Lesser General Public License for more details.                #
#                                                                              #
#   You should have received a copy of the GNU Lesser General Public           #
#   License along with this addon. If not, see https://www.gnu.org/licenses    #
#                                                                              #
################################################################################


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
            if name == "single":
                self._feature._obj.Clustered = False
            elif name == "double":
                self._feature._obj.Clustered = True
                self._feature._obj.ClusterRadial = False
                self._feature._obj.ClusterRows = 1
                self._feature._obj.ClusterColumns = 2
            elif name == "3-row":
                self._feature._obj.Clustered = True
                self._feature._obj.ClusterRadial = False
                self._feature._obj.ClusterRows = 1
                self._feature._obj.ClusterColumns = 3
            elif name == "4-row":
                self._feature._obj.Clustered = True
                self._feature._obj.ClusterRadial = False
                self._feature._obj.ClusterRows = 1
                self._feature._obj.ClusterColumns = 4
            elif name == "3-ring":
                self._feature._obj.Clustered = True
                self._feature._obj.ClusterRadial = True
                self._feature._obj.ClusterRadialCount = 3
                self._feature._obj.ClusterIncludeCenter = False
            elif name == "4-ring":
                self._feature._obj.Clustered = True
                self._feature._obj.ClusterRadial = True
                self._feature._obj.ClusterRadialCount = 4
                self._feature._obj.ClusterIncludeCenter = False
            elif name == "5-ring":
                self._feature._obj.Clustered = True
                self._feature._obj.ClusterRadial = True
                self._feature._obj.ClusterRadialCount = 5
                self._feature._obj.ClusterIncludeCenter = False
            elif name == "6-ring":
                self._feature._obj.Clustered = True
                self._feature._obj.ClusterRadial = True
                self._feature._obj.ClusterRadialCount = 6
                self._feature._obj.ClusterIncludeCenter = False
            elif name == "3-star":
                self._feature._obj.Clustered = True
                self._feature._obj.ClusterRadial = True
                self._feature._obj.ClusterRadialCount = 3
                self._feature._obj.ClusterIncludeCenter = True
            elif name == "4-star":
                self._feature._obj.Clustered = True
                self._feature._obj.ClusterRadial = True
                self._feature._obj.ClusterRadialCount = 4
                self._feature._obj.ClusterIncludeCenter = True
            elif name == "5-star":
                self._feature._obj.Clustered = True
                self._feature._obj.ClusterRadial = True
                self._feature._obj.ClusterRadialCount = 5
                self._feature._obj.ClusterIncludeCenter = True
            elif name == "6-star":
                self._feature._obj.Clustered = True
                self._feature._obj.ClusterRadial = True
                self._feature._obj.ClusterRadialCount = 6
                self._feature._obj.ClusterIncludeCenter = True
            elif name == "9-grid":
                self._feature._obj.Clustered = True
                self._feature._obj.ClusterRadial = False
                self._feature._obj.ClusterRows = 3
                self._feature._obj.ClusterColumns = 3
            elif name == "9-star":
                self._feature._obj.Clustered = True
                self._feature._obj.ClusterRadial = True
                self._feature._obj.ClusterRadialCount = 8
                self._feature._obj.ClusterIncludeCenter = True
            else:
                _err(translate('Rocket', "Unknown cluster configuration: {}").format(name))
        except Exception as e:
            # _err(translate('Rocket', "Unknown cluster configuration"))
            _err(translate('Rocket', "Error occurred while setting cluster configuration: {}").format(e))

    def onClusterScale(self, value):
        self._feature._obj.ClusterScale = value

    def onClusterRotation(self, value):
        self._feature._obj.ClusterRotation = value
