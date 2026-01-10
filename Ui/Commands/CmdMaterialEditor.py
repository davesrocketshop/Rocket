# SPDX-License-Identifier: LGPL-2.1-or-later
# SPDX-FileCopyrightText: 2021 David Carter <dcarter@davidcarter.ca>
# SPDX-File-Notice: Part of the Rocket addon.


"""Class for editing materials"""

__title__ = "FreeCAD Materials"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

import FreeCAD
import FreeCADGui

translate = FreeCAD.Qt.translate

from Ui.Widgets.WaitCursor import WaitCursor

class CmdMaterialEditor:
    def Activated(self):
        with WaitCursor():
            FreeCADGui.addModule("MaterialEditor")
            FreeCADGui.doCommand("MaterialEditor.openEditor()")

    def IsActive(self):
        return True

    def GetResources(self):
        return {'MenuText': translate("Rocket", 'Material editor'),
                'ToolTip': translate("Rocket", 'Opens the FreeCAD material editor'),
                'Pixmap': "Arch_Material" }
