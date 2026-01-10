# SPDX-License-Identifier: LGPL-2.1-or-later
# SPDX-FileCopyrightText: 2025 David Carter <dcarter@davidcarter.ca>
# SPDX-File-Notice: Part of the Rocket addon.


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
