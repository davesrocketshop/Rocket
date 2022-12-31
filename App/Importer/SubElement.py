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
"""Provides support for importing Open Rocket files."""

__title__ = "FreeCAD Open Rocket Importer"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

from App.Importer.SaxElement import NullElement
from App.Importer.ComponentElement import ComponentElement
from App.Importer.TransitionElement import TransitionElement
from App.Importer.NoseElement import NoseElement
from App.Importer.CenteringRingElement import CenteringRingElement
from App.Importer.StageElement import StageElement
from App.Importer.BodyTubeElement import BodyTubeElement, InnerTubeElement
from App.Importer.LaunchLugElement import LaunchLugElement
from App.Importer.TrapezoidalFinsetElement import TrapezoidalFinsetElement
from App.Importer.EllipticalFinsetElement import EllipticalFinsetElement
from App.Importer.TubeFinsetElement import TubeFinsetElement
from App.Importer.FreeformFinsetElement import FreeformFinsetElement

from App.Utilities import _msg

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
                                'engineblock' : BodyTubeElement,
                                'innertube' : InnerTubeElement,
                                'tubecoupler' : BodyTubeElement,
                                'bulkhead' : NullElement,
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
