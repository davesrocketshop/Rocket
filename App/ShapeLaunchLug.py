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
"""Class for drawing body tubes"""

__title__ = "FreeCAD Body Tubes"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

from PySide import QtCore
    
from App.Constants import FEATURE_LAUNCH_LUG
from App.Constants import PROP_HIDDEN

from App.ShapeBodyTube import ShapeBodyTube

class ShapeLaunchLug(ShapeBodyTube):

    def __init__(self, obj):
        super().__init__(obj)
        self.Type = FEATURE_LAUNCH_LUG

        # Default set to 1/8" launch lug
        self._obj.OuterDiameter = 4.06
        self._obj.Thickness = 0.25
        self._obj.Length = 25.4

        obj.setEditorMode('MotorMount', PROP_HIDDEN)  # hide
        obj.setEditorMode('Overhang', PROP_HIDDEN)  # hide

    def eligibleChild(self, childType):
        return False

