# SPDX-License-Identifier: LGPL-2.1-or-later
# SPDX-File-Notice: Part of the Rocket addon.

################################################################################
#                                                                              #
#   © 2021 David Carter <dcarter@davidcarter.ca>                               #
#                                                                              #
#   This addon is free software: you can redistribute it and/or modify         #
#   it under the terms of the GNU Lesser General Public License as             #
#   published by the Free Software Foundation, either version 2.1              #
#   of the License, or (at your option) any later version.                     #
#                                                                              #
#   This addon is distributed in the hope that it will be useful,              #
#   but WITHOUT ANY WARRANTY; without even the implied warranty                #
#   of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.                    #
#   See the GNU Lesser General Public License for more details.                #
#                                                                              #
#   You should have received a copy of the GNU Lesser General Public           #
#   License along with this addon. If not, see https://www.gnu.org/licenses    #
#                                                                              #
################################################################################


"""Class for drawing wind tunnels"""

__title__ = "FreeCAD Wind Tunnel Handler"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

import FreeCAD
import Part

from Rocket.Utilities import validationError, _err

translate = FreeCAD.Qt.translate

class WindTunnelShapeHandler():
    def __init__(self, obj):

        # This gets changed when redrawn so it's very important to save a copy
        self._placement = FreeCAD.Placement(obj.Placement)

        self._radius = float(obj.Diameter) / 2.0
        self._length = float(obj.Length)
        self._obj = obj

    def isValidShape(self):

        # Perform some general validations
        if self._radius <= 0:
            validationError(translate('Rocket', "Wind tunnel diameter must be greater than zero"))
            return False
        if self._length <= 0:
            validationError(translate('Rocket', "Wind tunnel length must be greater than zero"))
            return False

        return True

    def draw(self):
        if not self.isValidShape():
            return

        try:
            self._obj.Shape = Part.makeCylinder(self._radius, self._length, FreeCAD.Vector(0, 0, 0), FreeCAD.Vector(1, 0, 0))
            self._obj.Placement = self._placement
        except Part.OCCError:
            _err(translate('Rocket', "Wind tunnel parameters produce an invalid shape"))
