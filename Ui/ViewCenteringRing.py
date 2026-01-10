# SPDX-License-Identifier: LGPL-2.1-or-later
# SPDX-FileCopyrightText: 2021 David Carter <dcarter@davidcarter.ca>
# SPDX-File-Notice: Part of the Rocket addon.


"""Class for drawing centering rings"""

__title__ = "FreeCAD Centering Ring View Provider"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

import FreeCAD

from Ui.TaskPanelBulkhead import TaskPanelBulkhead
from Ui.ViewProvider import ViewProvider

class ViewProviderCenteringRing(ViewProvider):

    def __init__(self, vobj):
        super().__init__(vobj)

    def getIcon(self):
        return FreeCAD.getUserAppDataDir() + "Mod/Rocket/Resources/icons/Rocket_CenteringRing.svg"

    def getDialog(self, obj, mode):
        return TaskPanelBulkhead(obj, True, mode)
