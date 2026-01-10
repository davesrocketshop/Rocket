# SPDX-License-Identifier: LGPL-2.1-or-later
# SPDX-FileCopyrightText: 2021 David Carter <dcarter@davidcarter.ca>
# SPDX-File-Notice: Part of the Rocket addon.


"""Class for drawing nose cones"""

__title__ = "FreeCAD Nose Cones"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

from Rocket.FeatureNoseCone import FeatureNoseCone

from Rocket.Utilities import _wrn, setGroup

def _migrate_from_1_0(obj):
    _wrn("Nose cone migrating object from 1.0")

    old = {}
    old["Radius"] = obj.Radius
    old["ShoulderRadius"] = obj.ShoulderRadius
    old["NoseType"] = obj.NoseType

    obj.removeProperty("Radius")
    obj.removeProperty("ShoulderRadius")
    obj.removeProperty("NoseType")

    obj.Proxy = FeatureNoseCone(obj)
    obj.Proxy._obj = obj

    obj.Diameter = 2.0 * old["Radius"]
    obj.ShoulderDiameter = 2.0 * old["ShoulderRadius"]
    obj.NoseType = old["NoseType"]

def _migrate_from_2_0(obj):
    _wrn("Nose cone migrating object from 2.0")

    blunted = False
    secant = False
    old = {}
    if hasattr(obj, 'BluntedRadius'):
        old["BluntedRadius"] = obj.BluntedRadius
        blunted = True
    if hasattr(obj, 'OgiveRadius'):
        old["OgiveRadius"] = obj.OgiveRadius
        secant = True
    old["NoseType"] = obj.NoseType

    obj.removeProperty("BluntedRadius")
    obj.removeProperty("OgiveRadius")
    obj.removeProperty("NoseType")

    obj.Proxy = FeatureNoseCone(obj)
    obj.Proxy._obj = obj

    if blunted:
        obj.BluntedDiameter = 2.0 * old["BluntedRadius"]
    if secant:
        obj.OgiveDiameter = 2.0 * old["OgiveRadius"]
    obj.NoseType = old["NoseType"]

class ShapeNoseCone:

    def onDocumentRestored(self, obj):
        if hasattr(obj, "Radius"):
            _migrate_from_1_0(obj)
            setGroup(obj)
            return
        if hasattr(self, "version"):
            if self.version in ["2.0", "2.1"]:
                _migrate_from_2_0(obj)
                setGroup(obj)
                return

        obj.Proxy = FeatureNoseCone(obj)
        setGroup(obj)
        obj.Proxy._obj = obj

    def __setstate__(self, state):
        if state:
            self.version = state
