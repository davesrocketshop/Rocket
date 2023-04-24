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
"""Provides support for importing Rocsim files."""

__title__ = "FreeCAD Rocsim Importer"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

import FreeCAD

from Rocket.Importer.OpenRocket.SaxElement import NullElement
from Rocket.Importer.Rocsim.BaseElement import BaseElement
import Rocket.Importer.Rocsim as Rocsim
from Rocket.Importer.Rocsim.FinSetElement import FinSetElement

from Ui.Commands.CmdBodyTube import makeBodyTube, makeInnerTube

class AttachedPartsElement(BaseElement):

    def __init__(self, parent, tag, attributes, parentObj, filename, line):
        super().__init__(parent, tag, attributes, parentObj, filename, line)

        self._validChildren.update({ 'finset' : FinSetElement,
                                    'customfinset' : FinSetElement,
                                    'launchlug' : NullElement,
                                    'parachute' : NullElement,
                                    'streamer' : NullElement,
                                    'massobject' : NullElement,
                                    'ring' : NullElement,
                                    'bodytube' : Rocsim.BodyTubeElement.BodyTubeElement,
                                    'transition' : Rocsim.TransitionElement.TransitionElement,
                                    'nosecone' : Rocsim.NoseElement.NoseElement,
                                    'subassembly' : NullElement,
                                    'tubefinset' : NullElement,
                                    'externalpod' : NullElement,
                                    'ringtail' : NullElement,
                              })
        # self._knownTags.extend(["xb", "calcmass", "calccg", "radialloc", "radialangle", "locationmode", "len", 
        #                         "finishcode", "serialno", "shapecode", "constructiontype", "wallthickness", "shapeparameter", 
        #                         "attachedparts", "material", "od", "id", "ismotormount", "motordia", "engineoverhang", "isinsidetube"])
        