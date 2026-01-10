# SPDX-License-Identifier: LGPL-2.1-or-later
# SPDX-FileCopyrightText: 2021 David Carter <dcarter@davidcarter.ca>
# SPDX-File-Notice: Part of the Rocket addon.


"""Class for drawing body tubes"""

__title__ = "FreeCAD Body Tubes"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

from Rocket.FeatureBodyTube import FeatureBodyTube
from Rocket.Utilities import setGroup

class ShapeBodyTube:

    def onDocumentRestored(self, obj):
        obj.Proxy = FeatureBodyTube(obj)
        obj.Proxy._obj = obj
        setGroup(obj)

    def __setstate__(self, state):
        if state:
            self.version = state
