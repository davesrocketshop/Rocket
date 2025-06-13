# ***************************************************************************
# *   Copyright (c) 2025 David Carter <dcarter@davidcarter.ca>              *
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
"""Class for Dialog Utilities"""

__title__ = "FreeCAD Dialog Utilities"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

import FreeCAD

def saveDialog(dialog, dialogName):
    param = FreeCAD.ParamGet(f"User parameter:BaseApp/Preferences/Mod/Material/Resources/Modules/Rocket/Dialog/{dialogName}")

    geom = dialog.geometry()
    param.SetInt("Width", geom.width())
    param.SetInt("Height", geom.height())
    param.SetInt("x", geom.x())
    param.SetInt("y", geom.y())

def restoreDialog(dialog, dialogName, defaultWidth, defaultHeight):
    param = FreeCAD.ParamGet(f"User parameter:BaseApp/Preferences/Mod/Material/Resources/Modules/Rocket/Dialog/{dialogName}")
    width = param.GetInt("Width", defaultWidth)
    height = param.GetInt("Height", defaultHeight)
    x = param.GetInt("x", 100)
    y = param.GetInt("y", 100)

    dialog.move(x, y)
    dialog.resize(width, height)
