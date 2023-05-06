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
            return cls._cards

        materials, cards, icons = import_materials()

        if cls.getVersion() < 0.21:
            # Look for Rocket WB defined materials
            ap = pathlib.Path(FreeCAD.getUserAppDataDir(), "Mod/Rocket/Resources/Material")
            if ap.exists():
                materials, cards, icons = add_cards_from_a_dir(
                    materials,
                    cards,
                    icons,
                    str(ap),
                    FreeCAD.getUserAppDataDir() + "Mod/Rocket/Resources/icons/RocketWorkbench.svg"
                )

        cls._materials = {}
        cls._cards = {}
        for material, value in materials.items():
            p = pathlib.PurePath(material)
            b = p.stem
            cls._cards[b] = material
            cls._materials[b] = value

        return cls._cards

    @classmethod
    def refreshMaterials(cls):
        """
            Recreate the dictionary, such as when a card is created or destroyed
        """
        cls._cards = None
        cls.materialDictionary()

    @classmethod
    def lookup(cls, name):
        # Ensure we have a dictionary
        dict = cls.materialDictionary()
        if dict is not None and name in dict:
            material = cls._materials[name]

        if material is None:
            material = {}
        return material

