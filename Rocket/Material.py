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
"""Class for rocket materials"""

__title__ = "FreeCAD Rocket Materials"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

import FreeCAD
import pathlib

from materialtools.cardutils import import_materials, add_cards_from_a_dir


"""
    A helper class for working with materials.
"""
class Material():
    _cards = None
    _materials = None
    _icons = None
    _nameMap = None

    def __init__(self, obj):
        super().__init__(obj)

    @classmethod
    def getVersion(cls):
        v = FreeCAD.Version()
        version = float(v[0] + "." + v[1])
        return version

    @classmethod
    def materialDictionary(cls):
        if cls._cards is not None:
            return cls._materials, cls._cards, cls._icons

        cls._materials, cls._cards, cls._icons = import_materials()

        if cls.getVersion() < 0.21:
            # Look for Rocket WB defined materials
            ap = pathlib.Path(FreeCAD.getUserAppDataDir(), "Mod/Rocket/Resources/Material")
            if ap.exists():
                cls._materials, cls._cards, cls._icons = add_cards_from_a_dir(
                    cls._materials,
                    cls._cards,
                    cls._icons,
                    str(ap),
                    FreeCAD.getUserAppDataDir() + "Mod/Rocket/Resources/icons/RocketWorkbench.svg"
                )

        return cls._materials, cls._cards, cls._icons

    @classmethod
    def refreshMaterials(cls):
        """
            Recreate the dictionary, such as when a card is created or destroyed
        """
        cls._cards = None
        cls._nameMap = None
        cls.materialDictionary()

    @classmethod
    def getNameMap(cls):
        if cls._nameMap is not None:
            return cls._nameMap
        
        cls._nameMap = {}
        for path, name in cls._cards.items():
            cls._nameMap[name] = path

        return cls._nameMap

    @classmethod
    def lookup(cls, name):
        material = None

        # Ensure we have a dictionary
        _ = cls.materialDictionary()
        nameMap = cls.getNameMap()
        if nameMap is not None and name in nameMap:
            material = cls._materials[nameMap[name]]

        if material is None:
            material = {}
        return material

