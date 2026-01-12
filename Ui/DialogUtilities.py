# SPDX-License-Identifier: LGPL-2.1-or-later
# SPDX-File-Notice: Part of the Rocket addon.

################################################################################
#                                                                              #
#   © 2025 David Carter <dcarter@davidcarter.ca>                               #
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


"""Class for Dialog Utilities"""

__title__ = "FreeCAD Dialog Utilities"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

import FreeCAD

def getPreferencesLocation(dialogName):
    return f"User parameter:BaseApp/Preferences/Mod/Rocket/Dialog/{dialogName}"

def getParams(dialogName):
    return FreeCAD.ParamGet(getPreferencesLocation(dialogName))

def saveDialog(dialog, dialogName):
    param = getParams(dialogName)

    geom = dialog.geometry()
    param.SetInt("Width", geom.width())
    param.SetInt("Height", geom.height())
    param.SetInt("x", geom.x())
    param.SetInt("y", geom.y())

def restoreDialog(dialog, dialogName, defaultWidth, defaultHeight):
    param = getParams(dialogName)
    width = param.GetInt("Width", defaultWidth)
    height = param.GetInt("Height", defaultHeight)
    x = param.GetInt("x", 100)
    y = param.GetInt("y", 100)

    dialog.move(x, y)
    dialog.resize(width, height)
