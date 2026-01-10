# SPDX-License-Identifier: LGPL-2.1-or-later
# SPDX-FileCopyrightText: 2021 David Carter <dcarter@davidcarter.ca>
# SPDX-File-Notice: Part of the Rocket addon.


"""Class for drawing fin cans"""

__title__ = "FreeCAD Fin View Provider"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

import FreeCAD

from Ui.TaskPanelFinCan import TaskPanelFinCan
from Ui.ViewProvider import ViewProvider

class ViewProviderFinCan(ViewProvider):

    def __init__(self, vobj):
        super().__init__(vobj)

    def getIcon(self):
        return FreeCAD.getUserAppDataDir() + "Mod/Rocket/Resources/icons/Rocket_FinCan.svg"

    def getDialog(self, obj, mode):
        return TaskPanelFinCan(obj, mode)
