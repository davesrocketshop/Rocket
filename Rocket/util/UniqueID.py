# ***************************************************************************
# *   Copyright (c) 2022-2025 David Carter <dcarter@davidcarter.ca>         *
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
"""Base class for rocket identifiers"""

__title__ = "FreeCAD Rocket Components"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

from uuid import uuid4

class UniqueID:

    _nextId = 1

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
    def next(cls):
        cls._nextId += 1
        return cls._nextId


    """ Return a new universally unique ID string. """
    @classmethod
    def uuid(cls):
        return uuid4()
