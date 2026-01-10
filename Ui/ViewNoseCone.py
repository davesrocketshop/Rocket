# SPDX-License-Identifier: LGPL-2.1-or-later
# SPDX-FileCopyrightText: 2021 David Carter <dcarter@davidcarter.ca>
# SPDX-File-Notice: Part of the Rocket addon.


"""Class for drawing nose cones"""

__title__ = "FreeCAD Nose Cones View Provider"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

import FreeCAD

from Ui.TaskPanelNoseCone import TaskPanelNoseCone
from Ui.ViewProvider import ViewProvider

translate = FreeCAD.Qt.translate

class ViewProviderNoseCone(ViewProvider):

    def __init__(self, vobj):
        super().__init__(vobj)

    def getIcon(self):
        return FreeCAD.getUserAppDataDir() + "Mod/Rocket/Resources/icons/Rocket_NoseCone.svg"

    def getDialog(self, obj, mode):
        return TaskPanelNoseCone(obj, mode)
