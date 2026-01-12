# SPDX-License-Identifier: LGPL-2.1-or-later
# SPDX-File-Notice: Part of the Rocket addon.

################################################################################
#                                                                              #
#   © 2022 David Carter <dcarter@davidcarter.ca>                               #
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


"""Base class for rocket identifiers"""

__title__ = "FreeCAD Rocket Components"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

from uuid import uuid4, UUID

class UniqueID:

    _nextId : int = 1

    """
    Return a positive integer ID unique during this program execution.
    <p>
    The following is guaranteed of the returned ID values:
    <ul>
     	<li>The value is unique during this program execution
     	<li>The value is positive
     	<li>The values are monotonically increasing
    </ul>
    <p>
    This method is thread-safe and fast.
    """
    @classmethod
    def next(cls) -> int:
        cls._nextId += 1
        return cls._nextId


    """ Return a new universally unique ID string. """
    @classmethod
    def uuid(cls) -> UUID:
        return uuid4()
