# SPDX-License-Identifier: LGPL-2.1-or-later
# SPDX-FileCopyrightText: 2021 David Carter <dcarter@davidcarter.ca>
# SPDX-File-Notice: Part of the Rocket addon.


"""Class for recreating the parts database"""

__title__ = "FreeCAD Parts Database Generation"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

from Rocket.Parts.PartDatabase import PartDatabase

db = PartDatabase(".") # Current directory is the root directory
db.updateDatabase()
