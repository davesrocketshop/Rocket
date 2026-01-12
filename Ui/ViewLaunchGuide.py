# SPDX-License-Identifier: LGPL-2.1-or-later
# SPDX-File-Notice: Part of the Rocket addon.

################################################################################
#                                                                              #
#   © 2021 David Carter <dcarter@davidcarter.ca>                               #
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
