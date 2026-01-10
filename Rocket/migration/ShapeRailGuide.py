# SPDX-License-Identifier: LGPL-2.1-or-later
# SPDX-FileCopyrightText: 2021 David Carter <dcarter@davidcarter.ca>
# SPDX-File-Notice: Part of the Rocket addon.


"""Class for drawing launch guides"""

__title__ = "FreeCAD Launch Guide"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

from Rocket.FeatureRailGuide import FeatureRailGuide
from Rocket.Utilities import setGroup

class ShapeRailGuide:

    def onDocumentRestored(self, obj):
        obj.Proxy = FeatureRailGuide(obj)
        obj.Proxy._obj = obj
        setGroup(obj)

    def __setstate__(self, state):
        if state:
            self.version = state
