# SPDX-License-Identifier: LGPL-2.1-or-later
# SPDX-FileCopyrightText: 2021 David Carter <dcarter@davidcarter.ca>
# SPDX-File-Notice: Part of the Rocket addon.


"""Class for drawing body tubes"""

__title__ = "FreeCAD Body Tube View Provider"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

import FreeCAD

from Ui.TaskPanelBodyTube import TaskPanelBodyTube
from Ui.ViewProvider import ViewProvider

class ViewProviderBodyTube(ViewProvider):

    def __init__(self, vobj):
        super().__init__(vobj)

    def getIcon(self):
        return FreeCAD.getUserAppDataDir() + "Mod/Rocket/Resources/icons/Rocket_BodyTube.svg"

    def getDialog(self, obj, mode):
        return TaskPanelBodyTube(obj, mode)

class ViewProviderInnerTube(ViewProviderBodyTube):

    def getIcon(self):
        return FreeCAD.getUserAppDataDir() + "Mod/Rocket/Resources/icons/Rocket_InnerTube.svg"

class ViewProviderCoupler(ViewProviderBodyTube):

    def getIcon(self):
        return FreeCAD.getUserAppDataDir() + "Mod/Rocket/Resources/icons/Rocket_Coupler.svg"

class ViewProviderEngineBlock(ViewProviderBodyTube):

    def getIcon(self):
        return FreeCAD.getUserAppDataDir() + "Mod/Rocket/Resources/icons/Rocket_EngineBlock.svg"
