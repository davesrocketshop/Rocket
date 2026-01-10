# SPDX-License-Identifier: LGPL-2.1-or-later
# SPDX-FileCopyrightText: 2021 David Carter <dcarter@davidcarter.ca>
# SPDX-File-Notice: Part of the Rocket addon.


"""Class for bulkheads"""

__title__ = "FreeCAD Bulkheads"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

from Rocket.FeatureBulkhead import FeatureBulkhead
from Rocket.Utilities import setGroup

class ShapeBulkhead:

    def onDocumentRestored(self, obj):
        obj.Proxy = FeatureBulkhead(obj)
        obj.Proxy._obj = obj
        setGroup(obj)

    def __setstate__(self, state):
        if state:
            self.version = state
