# SPDX-License-Identifier: LGPL-2.1-or-later
# SPDX-File-Notice: Part of the Rocket addon.
# SPDX-FileCopyrightText: 2021 David Carter <dcarter@davidcarter.ca>


"""Class for rocket part components"""

__title__ = "FreeCAD Open Rocket Part Bulkhead"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

from Rocket.Parts.BodyTube import BodyTube

class Bulkhead(BodyTube):


    def __init__(self):
        super().__init__()

        self._ID = (0.0, "mm") # Not used, but must have units

        self._tubeType = "bulkhead"
