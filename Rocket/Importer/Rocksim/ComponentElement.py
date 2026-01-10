# SPDX-License-Identifier: LGPL-2.1-or-later
# SPDX-FileCopyrightText: 2025 David Carter <dcarter@davidcarter.ca>
# SPDX-File-Notice: Part of the Rocket addon.


"""Provides support for importing Rocksim files."""

__title__ = "FreeCAD Rocksim Importer Common Component"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

import FreeCAD
import Materials

translate = FreeCAD.Qt.translate

from Rocket.Parts.PartDatabase import PartDatabase
from Rocket.Parts.Material import getUuid
from Rocket.Parts.Exceptions import MaterialNotFoundError

from Rocket.Importer.OpenRocket.SaxElement import Element
from Rocket.Constants import LOCATION_PARENT_TOP, LOCATION_PARENT_BOTTOM, LOCATION_BASE
from Rocket.Constants import MATERIAL_TYPE_BULK, MATERIAL_TYPE_SURFACE, MATERIAL_TYPE_LINE
from Rocket.position.AxialMethod import AXIAL_METHOD_MAP, BOTTOM

from Rocket.Utilities import _err

class ComponentElement(Element):

    def __init__(self, parent, tag, attributes, parentObj, filename, line):
        super().__init__(parent, tag, attributes, parentObj, filename, line)

        self._componentTags = ["name", "len", "xb", "locationmode", "abientcolor", "diffusecolor", "specularcolor",
                               "usesinglecolor", "simplecolormodel", "opacity"]
        self._knownTags = ["knownmass", "density", "knowncg", "useknowncg", "densitytype", "texture", "ambient",
                           "diffuse", "specular", "color", "finishcode", "material", "partmfg", "partno", "partdesc",
                           "calcmass", "calccg", "wettedsurface", "paintedsurface", "radialloc", "radialangle",
                           "specularpower", "serialno", "displayflags", "metricsflags", "producetemplate",
                           "templateunits", "removed", "station", "gluejointlength", "barrowmancna", "barrowmanxn",
                           "rocksimcna", "rocksimxn"]

        self._knownMass = 0
        self._knownCG = 0
        self._density = 0
        self._densityType = MATERIAL_TYPE_BULK
        self._ambientColor = 0
        self._diffuseColor = 0
        self._specularColor = 0
        self._texture = ""

        self._useKnownMass = False
        self._useKnownCG = False

        self._material = None

        self._appearance = FreeCAD.Material()

    # def handleTag(self, tag, attributes):
    #     _tag = tag.lower().strip()
    #     super().handleTag(tag, attributes)

    def handleEndTag(self, tag, content):
        _tag = tag.lower().strip()
        if _tag == "name":
            self.onName(content)
        elif _tag == "len":
            # print("\tlen {}".format(float(content)))
            self.onLength(float(content))
        elif _tag == "xb":
            self.onAxialOffset(float(content))
        elif _tag == "locationmode":
            self.onLocationMode(content)
        elif _tag == "radialangle":
            self.onAngleOffset(content)
        elif _tag == "abientcolor":
            self._appearance.AmbientColor = self.parseColor(content)
        elif _tag == "diffusecolor":
            self._appearance.DiffuseColor = self.parseColor(content)
        elif _tag == "specularcolor":
            self._appearance.SpecularColor = self.parseColor(content)
        elif _tag == "usesinglecolor":
            pass
        elif _tag == "simplecolormodel":
            pass
        elif _tag == "opacity":
            self._appearance.Transparency = 1.0 - float(content)
            pass
        elif _tag == "density":
            self._density = float(content)
        elif _tag == "densitytype":
            self._densityType = self.densityType(int(content))
        elif _tag == "material":
            self._material = content
        else:
            super().handleEndTag(tag, content)

    def densityType(self, content):
        if content == 0:
            return MATERIAL_TYPE_BULK
        elif content == 1:
            return MATERIAL_TYPE_SURFACE
        elif content == 2:
            return MATERIAL_TYPE_LINE
        return MATERIAL_TYPE_BULK

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
            self._feature._obj.Location = content
        if hasattr(self._feature._obj, "AxialOffset"):
            self._feature._obj.AxialOffset = content

    def onAngleOffset(self, content):
        if self._feature and hasattr(self._feature._obj, "AngleOffset"):
            self._feature._obj.AngleOffset = FreeCAD.Units.Quantity(content + " rad").Value

    def onLocationMode(self, content):
        mode = int(content)
        if mode == 0:
            self.onPositionType(LOCATION_PARENT_TOP)
        elif mode == 1:
            self.onPositionType(LOCATION_BASE)
        elif mode == 2:
            self.onPositionType(LOCATION_PARENT_BOTTOM)
        else:
            self.onPositionType(LOCATION_BASE)

    def onOverrideMass(self, content):
        pass

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

    def setMaterial(self, feature, material, type):
        database = PartDatabase(FreeCAD.getUserAppDataDir() + "Mod/Rocket/")
        connection = database.getConnection()
        try:
            uuid = getUuid(connection, material, type)

            materialManager = Materials.MaterialManager()
            feature._obj.ShapeMaterial = materialManager.getMaterial(uuid)
        except MaterialNotFoundError:
            _err(translate("Rocket", "Material '{}' not found - using default material").format(material))

    def parseColor(self, value):
        if value == "blue":
            return (0, 0, 255)
        elif value == "white":
            return (255, 255, 255)
        elif value == "red":
            return (255, 0, 0)
        elif value == "green":
            return (0, 255, 0)
        elif value == "black":
            return (0, 0, 0)
        elif(value.startswith("rgb(")):
            color = value.removeprefix("rgb(").removesuffix(")")
            # print("Color({})".format(color))
            return tuple(int(x) for x in color.split(","))
        return (255, 255, 255)

    def end(self):
        self.setMaterial(self._feature, self._material, self._densityType)

        if self._feature._obj.AxialMethod == BOTTOM:
            if hasattr(self._feature._obj, "Location"):
                self._feature._obj.Location = -self._feature._obj.Location
            if hasattr(self._feature._obj, "AxialOffset"):
                self._feature._obj.AxialOffset = -self._feature._obj.AxialOffset

        if hasattr(self._feature._obj.ViewObject, "ShapeAppearance"):
            self._feature._obj.ViewObject.ShapeAppearance = self._appearance

        return super().end()
