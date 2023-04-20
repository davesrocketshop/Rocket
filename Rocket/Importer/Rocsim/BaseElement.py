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

__title__ = "FreeCAD Rocksim Importer Common Component"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

from Rocket.Importer.OpenRocket.SaxElement import Element, NullElement

class BaseElement(Element):

    def __init__(self, parent, tag, attributes, parentObj, filename, line):
        super().__init__(parent, tag, attributes, parentObj, filename, line)

        # self._validChildren = { 'finish' : NullElement,
        #                         'material' : MaterialElement,
        #                       }

        self._componentTags = ["name", "knownmass", "density", "knowncg", "useknowncg", "densitytype"]

        self._materialType = None
        self._materialDensity = None

    # def handleTag(self, tag, attributes):
    #     _tag = tag.lower().strip()
    #     if _tag == "name":
    #         pass
    #     else:
    #         super().handleTag(tag, attributes)

    def handleEndTag(self, tag, content):
        _tag = tag.lower().strip()
        if _tag == "name":
            self.onName(content)
        else:
            super().handleEndTag(tag, content)

    def onName(self, content):
        if hasattr(self._feature, "setName"):
            self._feature.setName(content)
