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


"""Base class for drawing ogive transitions"""

__title__ = "FreeCAD Ogive Transition Handler"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

from Rocket.ShapeHandlers.TransitionShapeHandler import TransitionShapeHandler

class TransitionOgiveShapeHandler(TransitionShapeHandler):

    def isClippable(self) -> bool:
        # Clipped shape is the same as the unclipped
        return False

    def _radiusAt(self, r1 : float, r2 : float, length : float, pos : float) -> float:
        return self._ogiveRadiusAt(r1, r2, length, pos)