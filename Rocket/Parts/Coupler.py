# SPDX-License-Identifier: LGPL-2.1-or-later
# SPDX-FileCopyrightText: 2021 David Carter <dcarter@davidcarter.ca>
# SPDX-File-Notice: Part of the Rocket addon.


"""Class for rocket part components"""

__title__ = "FreeCAD Open Rocket Part Coupler"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

from Rocket.Parts.BodyTube import BodyTube

class Coupler(BodyTube):

    def __init__(self):
        super().__init__()

        self._tubeType = "coupler"
