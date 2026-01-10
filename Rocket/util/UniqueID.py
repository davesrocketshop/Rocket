# SPDX-License-Identifier: LGPL-2.1-or-later
# SPDX-FileCopyrightText: 2022 David Carter <dcarter@davidcarter.ca>
# SPDX-File-Notice: Part of the Rocket addon.


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
