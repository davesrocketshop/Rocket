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


"""Class for drawing rockets"""

__title__ = "FreeCAD Rocket View Provider"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

import FreeCAD
import FreeCADGui

from PySide import QtCore,QtGui
from pivy import coin

from Ui.ViewProviderGeoFeature import ViewProviderGeoFeature
from Ui.ViewProvider import ViewProvider
from Ui.TaskPanelRocket import TaskPanelRocket
from Ui.Widgets.WaitCursor import WaitCursor

translate = FreeCAD.Qt.translate

class ViewProviderRocket(ViewProvider):

    def __init__(self, vobj):
        super().__init__(vobj)

    def getIcon(self):
        return FreeCAD.getUserAppDataDir() + "Mod/Rocket/Resources/icons/Rocket_Rocket.svg"

    def setupContextMenu(self, viewObject, menu):
        """Add the component specific options to the context menu."""
        action1 = QtGui.QAction(translate("Rocket","Toggle active rocket"),menu)
        QtCore.QObject.connect(action1,QtCore.SIGNAL("triggered()"),self.toggleRocket)
        menu.addAction(action1)

    def toggleRocket(self):
        with WaitCursor():
            FreeCADGui.runCommand("Rocket_ToggleRocket")
            FreeCADGui.runCommand("Rocket_ToggleStage")

    def getDialog(self, obj, mode):
        return TaskPanelRocket(obj, mode)
