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
"""Provides support for importing Open Rocket files."""

__title__ = "FreeCAD Open Rocket Importer"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

import FreeCAD

from Rocket.Importer.OpenRocket.BodyTubeElement import BodyTubeElement
from Rocket.ClusterConfiguration import CONFIGURATIONS
from Ui.Commands.CmdBodyTube import makeInnerTube

from Rocket.Utilities import _err
from Rocket.Utilities import translate

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
