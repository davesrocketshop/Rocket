# SPDX-License-Identifier: LGPL-2.1-or-later
# SPDX-FileCopyrightText: 2021 David Carter <dcarter@davidcarter.ca>
# SPDX-File-Notice: Part of the Rocket addon.


"""Provides support for importing Open Rocket files."""

__title__ = "FreeCAD Open Rocket Importer"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

from Rocket.Importer.OpenRocket.SaxElement import NullElement, UnsupportedElement
from Rocket.Importer.OpenRocket.ComponentElement import ComponentElement
from Rocket.Importer.OpenRocket.TransitionElement import TransitionElement
from Rocket.Importer.OpenRocket.NoseElement import NoseElement
from Rocket.Importer.OpenRocket.CenteringRingElement import BulkheadElement, CenteringRingElement
from Rocket.Importer.OpenRocket.StageElement import StageElement
from Rocket.Importer.OpenRocket.BodyTubeElement import BodyTubeElement, TubeCouplerElement, EngineBlockElement
from Rocket.Importer.OpenRocket.InnerTubeElement import InnerTubeElement
from Rocket.Importer.OpenRocket.LaunchLugElement import LaunchLugElement
from Rocket.Importer.OpenRocket.TrapezoidalFinsetElement import TrapezoidalFinsetElement
from Rocket.Importer.OpenRocket.EllipticalFinsetElement import EllipticalFinsetElement
from Rocket.Importer.OpenRocket.TubeFinsetElement import TubeFinsetElement
from Rocket.Importer.OpenRocket.FreeformFinsetElement import FreeformFinsetElement

class SubElement(ComponentElement):

    def __init__(self, parent, tag, attributes, parentObj, filename, line):
        super().__init__(parent, tag, attributes, parentObj, filename, line)

        self._validChildren = { 'stage' : StageElement,
                                'nosecone' : NoseElement,
                                'bodytube' : BodyTubeElement,
                                'subcomponents' : SubElement,
                                'transition' : TransitionElement,
                                'trapezoidfinset' : TrapezoidalFinsetElement,
                                'ellipticalfinset' : EllipticalFinsetElement,
                                'freeformfinset' : FreeformFinsetElement,
                                'tubefinset' : TubeFinsetElement,
                                'launchlug' : LaunchLugElement,
                                'railbutton' : NullElement,
                                'engineblock' : EngineBlockElement,
                                'innertube' : InnerTubeElement,
                                'tubecoupler' : TubeCouplerElement,
                                'bulkhead' : BulkheadElement,
                                'centeringring' : CenteringRingElement,
                                'masscomponent' : NullElement,
                                'shockcord' : NullElement,
                                'parachute' : NullElement,
                                'streamer' : NullElement,
                                'boosterset' : UnsupportedElement,
                                'parallelstage' : UnsupportedElement,
                                'podset' : UnsupportedElement,
                              }
        self._knownTags = ["stage", "nosecone", "bodytube", "transition", "trapezoidfinset", "ellipticalfinset", "freeformfinset", "tubefinset", "launchlug", "railbutton",
                "engineblock", "innertube", "tubecoupler", "bulkhead", "centeringring", "masscomponent", "shockcord", "parachute", "streamer",
                "boosterset", "parallelstage", "podset"]
