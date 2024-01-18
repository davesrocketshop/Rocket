# ***************************************************************************
# *   Copyright (c) 2021-2024 David Carter <dcarter@davidcarter.ca>         *
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
"""Provides support for importing Open Rocket files."""

__title__ = "FreeCAD Open Rocket Importer"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

from Rocket.Importer.OpenRocket.SaxElement import NullElement
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
                                'boosterset' : NullElement,
                                'parallelstage' : NullElement,
                                'podset' : NullElement,
                              }
        self._knownTags = ["stage", "nosecone", "bodytube", "transition", "trapezoidfinset", "ellipticalfinset", "freeformfinset", "tubefinset", "launchlug", "railbutton",
                "engineblock", "innertube", "tubecoupler", "bulkhead", "centeringring", "masscomponent", "shockcord", "parachute", "streamer", 
                "boosterset", "parallelstage", "podset"]
