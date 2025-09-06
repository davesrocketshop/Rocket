# ***************************************************************************
# *   Copyright (c) 2021-2025 David Carter <dcarter@davidcarter.ca>         *
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
