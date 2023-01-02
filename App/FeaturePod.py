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
"""Class for rocket pods"""

__title__ = "FreeCAD Rocket Pod"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

# import FreeCAD

from PySide import QtCore
from DraftTools import translate

from App.RocketComponent import RocketComponent
from App.Constants import FEATURE_ROCKET, FEATURE_STAGE, FEATURE_PARALLEL_STAGE, FEATURE_POD

class FeaturePod(RocketComponent):

    def __init__(self, obj):
        super().__init__(obj)

        self.Type = FEATURE_POD

        if not hasattr(obj,"PodCount"):
            obj.addProperty('App::PropertyInteger', 'PodCount', 'Pod', translate('App::Property', 'Number of pods in a radial pattern')).PodCount = 1
        if not hasattr(obj,"PodSpacing"):
            obj.addProperty('App::PropertyAngle', 'PodSpacing', 'Pod', translate('App::Property', 'Angle between consecutive pods')).PodSpacing = 360

        if not hasattr(obj,"Group"):
            obj.addExtension("App::GroupExtensionPython")

    def execute(self,obj):
        if not hasattr(obj,'Shape'):
            return

    def eligibleChild(self, childType):
        return childType not in [FEATURE_ROCKET, FEATURE_STAGE, FEATURE_PARALLEL_STAGE]

    def onChildEdited(self):
        self._obj.Proxy.setEdited()
