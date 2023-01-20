# ***************************************************************************
# *   Copyright (c) 2021-2023 David Carter <dcarter@davidcarter.ca>         *
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
"""Class for drawing nose cones"""

__title__ = "FreeCAD Nose Cones"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

import FreeCAD
    
from App.FeatureNoseCone import FeatureNoseCone

from App.Utilities import _wrn

from DraftTools import translate

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
            return
        if hasattr(self, "version"):
            if self.version in ["2.0", "2.1"]:
                _migrate_from_2_0(obj)
                return

        obj.Proxy = FeatureNoseCone(obj)
        obj.Proxy._obj = obj

    def __setstate__(self, state):
        if state:
            self.version = state
