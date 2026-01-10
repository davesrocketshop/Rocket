# SPDX-License-Identifier: LGPL-2.1-or-later

# ***************************************************************************
# *   Copyright (c) 2025 David Carter <dcarter@davidcarter.ca>              *
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
"""Provides support for importing Rocksim files."""

__title__ = "FreeCAD Rocksim Importer"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

from Rocket.Importer.OpenRocket.SaxElement import UnsupportedElement, NullElement, Element

from Rocket.Importer.Rocksim.BodyTubeElement import InnerTubeElement
from Rocket.Importer.Rocksim.FinsetElement import FinsetElement
from Rocket.Importer.Rocksim.LaunchLugElement import LaunchLugElement
from Rocket.Importer.Rocksim.RingElement import RingElement
from Rocket.Importer.Rocksim.RingtailElement import RingtailElement
from Rocket.Importer.Rocksim.SubAssemblyElement import SubAssemblyElement
from Rocket.Importer.Rocksim.TransitionElement import TransitionElement
from Rocket.Importer.Rocksim.TubeFinsetElement import TubeFinsetElement

class AttachedPartsElement(Element):

    def __init__(self, parent, tag, attributes, parentObj, filename, line):
        super().__init__(parent, tag, attributes, parentObj, filename, line)

        self._validChildren = { 'finset' : FinsetElement,
                                'customfinset' : FinsetElement,
                                'launchlug' : LaunchLugElement,
                                'parachute' : NullElement,
                                'streamer' : NullElement,
                                'massobject' : NullElement,
                                'ring' : RingElement,
                                'bodytube' : InnerTubeElement,
                                'transition' : TransitionElement,
                                'subassembly' : SubAssemblyElement,
                                'tubefinset' : TubeFinsetElement,
                                'ringtail' : RingtailElement,
                                'externalpod' : UnsupportedElement,
                              }
        self._knownTags = ["finset", "customfinset", "launchlug", "parachute", "streamer", "massobject", "ring", "bodytube",
                           "transition", "subassembly", "tubefinset", "ringtail", "externalpod"]
