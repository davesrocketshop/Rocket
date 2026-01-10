# SPDX-License-Identifier: LGPL-2.1-or-later
# SPDX-FileCopyrightText: 2021 David Carter <dcarter@davidcarter.ca>
# SPDX-File-Notice: Part of the Rocket addon.


"""Class for drawing ring tails"""

__title__ = "FreeCAD Ring Tail View Provider"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

import FreeCAD

from Ui.TaskPanelRingtail import TaskPanelRingtail
from Ui.ViewProvider import ViewProvider

class ViewProviderRingtail(ViewProvider):

    def __init__(self, vobj):
        super().__init__(vobj)

    def getIcon(self):
        return FreeCAD.getUserAppDataDir() + "Mod/Rocket/Resources/icons/Rocket_Ringtail.svg"

    def getDialog(self, obj, mode):
        return TaskPanelRingtail(obj, mode)
