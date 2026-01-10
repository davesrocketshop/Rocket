# SPDX-License-Identifier: LGPL-2.1-or-later
# SPDX-FileCopyrightText: 2021 David Carter <dcarter@davidcarter.ca>
# SPDX-File-Notice: Part of the Rocket addon.


"""Class for drawing launch guides"""

__title__ = "FreeCAD Launch Guide View Provider"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

import FreeCAD

from Ui.TaskPanelRailGuide import TaskPanelRailGuide
from Ui.TaskPanelRailButton import TaskPanelRailButton
from Ui.TaskPanelLaunchLug import TaskPanelLaunchLug
from Ui.ViewProvider import ViewProvider

class ViewProviderRailGuide(ViewProvider):

    def getIcon(self):
        return FreeCAD.getUserAppDataDir() + "Mod/Rocket/Resources/icons/Rocket_RailGuide.svg"

    def getDialog(self, obj, mode):
        return TaskPanelRailGuide(obj, mode)

class ViewProviderRailButton(ViewProvider):

    def getIcon(self):
        return FreeCAD.getUserAppDataDir() + "Mod/Rocket/Resources/icons/Rocket_RailButton.svg"

    def getDialog(self, obj, mode):
        return TaskPanelRailButton(obj, mode)

class ViewProviderLaunchLug(ViewProvider):

    def getIcon(self):
        return FreeCAD.getUserAppDataDir() + "Mod/Rocket/Resources/icons/Rocket_LaunchLug.svg"

    def getDialog(self, obj, mode):
        return TaskPanelLaunchLug(obj, mode)
