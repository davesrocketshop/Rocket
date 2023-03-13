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
import os
import pathlib
import importFCMat


"""
    A helper class for working with materials.
"""
class Material():
    _cards = None

    def __init__(self, obj):
        super().__init__(obj)


    @classmethod
    def searchPaths(cls):
        # look for cards in both resources dir and a Materials sub-folder in the user folder.
        # User cards with same name will override system cards
        paths = [pathlib.Path(FreeCAD.getResourceDir(), "Mod/Material/StandardMaterial")]
        ap = pathlib.Path(FreeCAD.getUserAppDataDir(), "Material")
        if ap.exists():
            paths.append(ap)

        # Look for Rocket WB defined materials
        ap = pathlib.Path(FreeCAD.getUserAppDataDir(), "Mod/Rocket/Resources/Material")
        if ap.exists():
            paths.append(ap)

        return paths

    @classmethod
    def materialDictionary(cls):
        if cls._cards is not None:
            return cls._cards

        cls._cards = {}
        for p in cls.searchPaths():
            for f in os.listdir(p):
                b,e = os.path.splitext(f)
                if e.upper() == ".FCMAT":
                    cls._cards[b] = p / f

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
            material = importFCMat.read(dict[name])

        if material is None:
            material = {}
        return material

    

