# SPDX-License-Identifier: LGPL-2.1-or-later
# SPDX-File-Notice: Part of the Rocket addon.

################################################################################
#                                                                              #
#   © 2021 David Carter <dcarter@davidcarter.ca>                               #
#                                                                              #
#   This addon is free software: you can redistribute it and/or modify         #
#   it under the terms of the GNU Lesser General Public License as             #
#   published by the Free Software Foundation, either version 2.1              #
#   of the License, or (at your option) any later version.                     #
#                                                                              #
#   This addon is distributed in the hope that it will be useful,              #
#   but WITHOUT ANY WARRANTY; without even the implied warranty                #
#   of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.                    #
#   See the GNU Lesser General Public License for more details.                #
#                                                                              #
#   You should have received a copy of the GNU Lesser General Public           #
#   License along with this addon. If not, see https://www.gnu.org/licenses    #
#                                                                              #
################################################################################


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
