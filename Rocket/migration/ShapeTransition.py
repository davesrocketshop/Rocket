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
