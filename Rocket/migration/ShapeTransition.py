# SPDX-License-Identifier: LGPL-2.1-or-later
# SPDX-FileCopyrightText: 2024 David Carter <dcarter@davidcarter.ca>
# SPDX-File-Notice: Part of the Rocket addon.


__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

from Rocket.FeatureTransition import FeatureTransition

from Rocket.Utilities import _wrn, setGroup

def _migrate_from_1_0(obj):
    _wrn("Transition migrating object from 1.0")

    old = {}
    old["ForeRadius"] = obj.ForeRadius
    old["AftRadius"] = obj.AftRadius
    old["CoreRadius"] = obj.CoreRadius
    old["ForeShoulderRadius"] = obj.ForeShoulderRadius
    old["AftShoulderRadius"] = obj.AftShoulderRadius

    obj.removeProperty("ForeRadius")
    obj.removeProperty("AftRadius")
    obj.removeProperty("CoreRadius")
    obj.removeProperty("ForeShoulderRadius")
    obj.removeProperty("AftShoulderRadius")

    obj.Proxy = FeatureTransition(obj)
    obj.Proxy._obj = obj

    obj.ForeDiameter = 2.0 * old["ForeRadius"]
    obj.AftDiameter = 2.0 * old["AftRadius"]
    obj.CoreDiameter = 2.0 * old["CoreRadius"]
    obj.ForeShoulderDiameter = 2.0 * old["ForeShoulderRadius"]
    obj.AftShoulderDiameter = 2.0 * old["AftShoulderRadius"]

class ShapeTransition:

    def onDocumentRestored(self, obj):
        if hasattr(obj, "ForeRadius"):
            _migrate_from_1_0(obj)
        else:
            # Update properties
            obj.Proxy = FeatureTransition(obj)
            obj.Proxy._obj = obj
        setGroup(obj)

    def __setstate__(self, state):
        if state:
            self.version = state
