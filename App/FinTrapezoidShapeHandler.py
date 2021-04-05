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
"""Class for drawing fins"""

__title__ = "FreeCAD Fins"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"
    
import FreeCAD
import Part
# import Draft
# import math

from App.Constants import FIN_CROSS_SAME

from App.FinShapeHandler import FinShapeHandler

class FinTrapezoidShapeHandler(FinShapeHandler):

    def __init__(self, obj):
        super().__init__(obj)

    def _makeRootProfile(self):
        # Create the root profile, casting everything to float to avoid typing issues
        if self._obj.RootPerCent:
            rootLength2 = float(self._obj.RootLength2)
        else:
            rootLength2 = float(self._obj.RootChord) - float(self._obj.RootLength2)
        return self._makeChordProfile(self._obj.RootCrossSection, float(self._obj.RootChord), float(self._obj.RootChord), float(self._obj.RootThickness), 0.0, self._obj.RootPerCent, float(self._obj.RootLength1), rootLength2)

    def _makeTipProfile(self):
        # Create the tip profile, casting everything to float to avoid typing issues
        crossSection = self._obj.TipCrossSection
        if crossSection == FIN_CROSS_SAME:
            crossSection = self._obj.RootCrossSection
        if self._obj.TipPerCent:
            tipLength2 = float(self._obj.TipLength2)
        else:
            tipLength2 = float(self._obj.TipChord) - float(self._obj.TipLength2)
        return self._makeChordProfile(crossSection, float(self._obj.RootChord - self._obj.SweepLength), float(self._obj.TipChord), float(self._obj.TipThickness), float(self._obj.Height), self._obj.TipPerCent, float(self._obj.TipLength1), tipLength2)

    def isValidShape(self):
        # Add error checking here
        if self._obj.Ttw:
            if self._obj.TtwOffset >= self._obj.RootChord:
                _err(translate('Rocket', "Ttw offset must be less than the root chord"))
                return False
            if self._obj.TtwLength <= 0:
                _err(translate('Rocket', "Ttw length must be greater than 0"))
                return False
            if self._obj.TtwHeight <= 0:
                _err(translate('Rocket', "Ttw height must be greater than 0"))
                return False
            if self._obj.TtwThickness <= 0:
                _err(translate('Rocket', "Ttw thickness must be greater than 0"))
                return False
        return True

    def _makeProfiles(self):
        profiles = []
        profiles.append(self._makeRootProfile())
        profiles.append(self._makeTipProfile())
        return profiles
