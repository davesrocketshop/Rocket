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

__title__ = "FreeCAD Open Rocket Importer Common Component"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

import FreeCAD

from App.Importer.SaxElement import Element, NullElement
from App.Constants import LOCATION_PARENT_TOP, LOCATION_PARENT_MIDDLE, LOCATION_PARENT_BOTTOM, \
    LOCATION_BASE, LOCATION_AFTER
from App.position.AxialMethod import AXIAL_METHOD_MAP

class ComponentElement(Element):

    def __init__(self, parent, tag, attributes, parentObj, filename, line):
        super().__init__(parent, tag, attributes, parentObj, filename, line)

        self._componentTags = ["name", "color", "linestyle", "position", "axialoffset", "overridemass", "overridecg", "overridecd", 
            "overridesubcomponents", "overridesubcomponentsmass", "overridesubcomponentscg", "overridesubcomponentscd", "comment", "preset", "finish", "material"]

    def handleTag(self, tag, attributes):
        _tag = tag.lower().strip()
        if _tag == "position":
            positionType = attributes["type"]
            print("positionType = %s" % (positionType))
            if positionType == "after":
                self.onPositionType(LOCATION_AFTER)
            elif positionType == "top":
                self.onPositionType(LOCATION_PARENT_TOP)
            elif positionType == "middle":
                self.onPositionType(LOCATION_PARENT_MIDDLE)
            elif positionType == "bottom":
                self.onPositionType(LOCATION_PARENT_BOTTOM)
            else:
                self.onPositionType(LOCATION_BASE)
        else:
            super().handleTag(tag, attributes)

    def handleEndTag(self, tag, content):
        _tag = tag.lower().strip()
        if _tag == "name":
            self.onName(content)
        elif _tag == "color":
            self.onColor(content)
        elif _tag == "linestyle":
            self.onLinestyle(content)
        elif _tag == "position":
            self.onAxialOffset(FreeCAD.Units.Quantity(content + " m").Value)
        elif _tag == "axialoffset":
            self.onAxialOffset(FreeCAD.Units.Quantity(content + " m").Value)
        elif _tag == "overridemass":
            self.onOverrideMass(FreeCAD.Units.Quantity(content + " kg").Value)
        elif _tag == "overridecg":
            self.onOverrideCG(FreeCAD.Units.Quantity(content + " m").Value)
        elif _tag == "overridecd":
            self.onOverrideCd(content)
        elif _tag == "overridesubcomponents":
            self.onOverrideSubcomponents(content)
        elif _tag == "overridesubcomponentsmass":
            self.onOverrideSubcomponentsMass(content)
        elif _tag == "overridesubcomponentscg":
            self.onOverrideSubcomponentsCG(content)
        elif _tag == "overridesubcomponentscd":
            self.onOverrideSubcomponentsCd(content)
        elif _tag == "comment":
            self.onComment(content)
        elif _tag == "preset":
            self.onPreset(content)
        else:
            super().handleEndTag(tag, content)

    def onName(self, content):
        if hasattr(self._feature, "setName"):
            self._feature.setName(content)

    def onColor(self, content):
        pass

    def onLinestyle(self, content):
        pass

    def onComment(self, content):
        if hasattr(self._feature, "setComment"):
            self._feature.setComment(content)

    def onPreset(self, content):
        pass

    def onPositionType(self, value):
        if hasattr(self._feature._obj, "LocationReference"):
            self._feature._obj.LocationReference = value
        if hasattr(self._feature._obj, "AxialMethod"):
            self._feature._obj.AxialMethod = AXIAL_METHOD_MAP[value]

    def onAxialOffset(self, content):
        if hasattr(self._feature._obj, "Location"):
            self._feature._obj.Location = -content
        if hasattr(self._feature._obj, "AxialOffset"):
            self._feature._obj.AxialOffset = -content

    def onOverrideMass(self, content):
        if hasattr(self._feature, "setOverrideMass"):
            self._feature.setOverrideMass(content)
        if hasattr(self._feature, "setMassOverridden"):
            self._feature.setMassOverridden(content > 0)

    def onOverrideCG(self, content):
        pass

    def onOverrideCd(self, content):
        pass

    def onOverrideSubcomponents(self, content):
        pass

    def onOverrideSubcomponentsMass(self, content):
        pass

    def onOverrideSubcomponentsCG(self, content):
        pass

    def onOverrideSubcomponentsCd(self, content):
        pass

class ExternalComponentElement(ComponentElement):

    def __init__(self, parent, tag, attributes, parentObj, filename, line):
        super().__init__(parent, tag, attributes, parentObj, filename, line)

        self._validChildren = { 'finish' : NullElement,
                                'material' : NullElement,
                                'appearance' : NullElement,
                              }


class BodyComponentElement(ExternalComponentElement):

    def __init__(self, parent, tag, attributes, parentObj, filename, line):
        super().__init__(parent, tag, attributes, parentObj, filename, line)

        self._knownTags.extend(["length"])


    def handleEndTag(self, tag, content):
        _tag = tag.lower().strip()
        if _tag == "length":
            self.onLength(FreeCAD.Units.Quantity(content + " m").Value)
        else:
            super().handleEndTag(tag, content)

    def onLength(self, content):
        if hasattr(self._feature, "setLength"):
            self._feature.setLength(content)
