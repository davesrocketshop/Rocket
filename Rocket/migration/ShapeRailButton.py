# SPDX-License-Identifier: LGPL-2.1-or-later
# SPDX-FileCopyrightText: 2021 David Carter <dcarter@davidcarter.ca>
# SPDX-File-Notice: Part of the Rocket addon.


"""Class for drawing rail buttons"""

__title__ = "FreeCAD Rail Buttons"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

from Rocket.FeatureRailButton import FeatureRailButton
from Rocket.Utilities import setGroup

class ShapeRailButton:

    def onDocumentRestored(self, obj):
        obj.Proxy = FeatureRailButton(obj)
        obj.Proxy._obj = obj
        setGroup(obj)

    def __setstate__(self, state):
        if state:
            self.version = state
