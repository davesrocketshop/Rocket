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

from Rocket.Importer.OpenRocket.SaxElement import Element, NullElement
from Rocket.Importer.Rocsim.BodyTubeElement import BodyTubeElement
from Rocket.Importer.Rocsim.NoseElement import NoseElement
from Rocket.Importer.Rocsim.TransitionElement import TransitionElement

from Ui.Commands.CmdStage import makeStage

class StageElement(Element):

    def __init__(self, parent, tag, attributes, parentObj, filename, line):
        super().__init__(parent, tag, attributes, parentObj, filename, line)

        self.stageCount = 1

        self._validChildren.update({'nosecone' : NoseElement,
                                'transition' : TransitionElement,
                                'bodytube' : BodyTubeElement,
                                'subassembly' : NullElement,
                              })
        # self._knownTags.extend(["stage1parts", "stage2parts", "stage3parts", "name", "stagecount", 
        #                         "stage1mass", "stage2mass", "stage3mass", "stage1cg", "stage2cg", "stage3cg", 
        #                         "displayflags", "viewtype", "viewstagecount", "viewtypeedit", "viewstagecountedit", 
        #                         "zoomfactor", "zoomfactoredit", "scrollposx", "scrollposy", "scrollposxedit", "scrollposyedit", 
        #                         "threedflags", "threedflagsedit", "lastserialnumber", "stage2cgalone", "stage1cgalone", 
        #                         "stage321cg", "stage32cg", "cpcalcflags", "cpsimflags", "useknownmass"])

    # def handleEndTag(self, tag, content):
    #     _tag = tag.lower().strip()
    #     if _tag == "stagecount":
    #         self.stageCount = int(content)
    #     else:
    #         super().handleEndTag(tag, content)

    def makeObject(self):
        self._feature = makeStage()
        if self._parentObj is not None:
            self._parentObj.addChild(self._feature)
