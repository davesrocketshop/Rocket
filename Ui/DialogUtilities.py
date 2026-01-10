# SPDX-License-Identifier: LGPL-2.1-or-later
# SPDX-FileCopyrightText: 2025 David Carter <dcarter@davidcarter.ca>
# SPDX-File-Notice: Part of the Rocket addon.


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
